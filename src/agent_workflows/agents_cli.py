"""Standalone and pluggable command group for 172X Agents."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Annotated, cast

import typer

from .codex import (
    active_workflow,
    default_codex_home,
    install_codex,
    installed_capability_ids,
    launch_codex,
    managed_files,
    select_workflow,
    uninstall_codex,
)
from .library import (
    LibraryError,
    domains,
    find_item,
    find_workflow,
    load_library,
    load_workflows,
    validate_library,
)
from .profiles import (
    ProjectProfile,
    capability_rows,
    default_profile,
    ensure_activation_is_locally_ignored,
    language_tools,
    load_profile,
    prerequisite_rows,
    prerequisites_ok,
    write_activation,
)
from .providers import (
    MergeCapabilities,
    MergeGate,
    MergePolicy,
    ReviewerIdentity,
    ReviewerStatus,
    ReviewSubmission,
    SourceControlProvider,
    default_registry,
    source_control_provider,
)
from .providers.config import (
    local_project_config_path,
    shared_project_config_path,
    write_local_project_config,
)


class CodexOptionGroup(typer.core.TyperGroup):
    """Keep unknown root options for Codex while preserving normal subcommands."""

    def parse_args(self, ctx: typer._click.core.Context, args: list[str]) -> list[str]:
        remaining = typer._click.core.Command.parse_args(self, ctx, self._root_options_first(args))
        if remaining and remaining[0].startswith("-"):
            ctx._protected_args = []
            ctx.args = remaining
        elif remaining:
            ctx._protected_args, ctx.args = remaining[:1], remaining[1:]
        return ctx.args

    def _root_options_first(self, args: list[str]) -> list[str]:
        """Allow `agents --model X --workflow dev` without swallowing real subcommands."""
        if any(argument in self.commands for argument in args):
            return args
        root_options: list[str] = []
        codex_options: list[str] = []
        index = 0
        while index < len(args):
            argument = args[index]
            if argument in {"--workflow", "--target"} and index + 1 < len(args):
                root_options.extend((argument, args[index + 1]))
                index += 2
                continue
            if argument.startswith(("--workflow=", "--target=")) or argument == "--no-launch":
                root_options.append(argument)
            else:
                codex_options.append(argument)
            index += 1
        return [*root_options, *codex_options]


app = typer.Typer(
    help="Install and explore 172X Agents.",
    cls=CodexOptionGroup,
    invoke_without_command=True,
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
install_app = typer.Typer(help="Install global 172X Forge capabilities for a supported host.")
uninstall_app = typer.Typer(help="Remove global 172X Forge capabilities from a supported host.")
github_app = typer.Typer(
    help="Inspect guarded dev-loop pull-request gates and perform guarded merges."
)
app.add_typer(install_app, name="install")
app.add_typer(uninstall_app, name="uninstall")
app.add_typer(github_app, name="github")


def _target(target: Path | None) -> Path:
    return target if target is not None else Path.cwd()


def _operational_error(message: str) -> None:
    typer.echo(f"Error: {message}", err=True)
    raise typer.Exit(1)


def _activation_prompt(label: str, default: str) -> str:
    """Collect one provider setting interactively, using a safe default off a TTY."""
    if not sys.stdin.isatty():
        return default
    return cast(str, typer.prompt(label, default=default)).strip()


def _configure_local_provider(target: Path, *, dry_run: bool) -> tuple[str, Path | None]:
    """Initialize repository-local provider settings without writing tracked files."""
    local_path = local_project_config_path(target)
    if local_path is None or local_path.is_file():
        return ("UNCHANGED", local_path) if local_path is not None else ("SKIPPED", None)
    legacy_path = shared_project_config_path(target)
    if legacy_path is None:
        provider_name = _activation_prompt("Source-control provider", "github").casefold()
        base_branch = _activation_prompt("Merge base branch", "main")
        merge_method = _activation_prompt("Merge method (merge/rebase/squash)", "squash")
        reviewer_login = _activation_prompt("Independent reviewer login", "172x-reviewer-bot")
        token_env = _activation_prompt("Reviewer token environment variable", "REVIEWER_GH_TOKEN")
    else:
        provider_name = "github"
        base_branch = "main"
        merge_method = "squash"
        reviewer_login = "172x-reviewer-bot"
        token_env = "REVIEWER_GH_TOKEN"
    if provider_name != "github":
        raise LibraryError(
            f"provider '{provider_name}' is not implemented; supported provider: github"
        )
    return write_local_project_config(
        target,
        provider_name=provider_name,
        base_branch=base_branch,
        merge_method=merge_method,
        reviewer_login=reviewer_login,
        token_env=token_env,
        dry_run=dry_run,
    )


def _github_provider(target: Path) -> SourceControlProvider:
    """Resolve the configured source-control provider for a GitHub command group."""
    provider = source_control_provider(target)
    if provider.key.name != "github":
        raise LibraryError(
            f"this command requires source_control:github; configured provider is "
            f"{provider.key.qualified_name}"
        )
    return provider


def configured_reviewers(target: Path) -> tuple[ReviewerIdentity, ...]:
    """Compatibility facade for the configured provider's reviewer operations."""
    return _github_provider(target).reviews.configured_reviewers(target)


def reviewer_status(target: Path, login: str) -> ReviewerStatus:
    """Compatibility facade for the configured provider's reviewer status operation."""
    return _github_provider(target).reviews.reviewer_status(target, login)


def submit_review(
    target: Path, pr_number: int, reviewer: str, head: str, report: Path
) -> ReviewSubmission:
    """Compatibility facade for provider-neutral review publication."""
    return _github_provider(target).reviews.submit_review(target, pr_number, reviewer, head, report)


def approve_pull_request(
    target: Path, pr_number: int, reviewer: str, head: str, report: Path
) -> ReviewSubmission:
    """Compatibility facade for provider-neutral approval publication."""
    return _github_provider(target).reviews.approve_review(
        target, pr_number, reviewer, head, report
    )


def review_threads(target: Path, pr_number: int) -> list[dict[str, object]]:
    """Compatibility facade for provider-neutral review-thread inspection."""
    return _github_provider(target).change_requests.review_threads(target, pr_number)


def resolve_review_thread(target: Path, pr_number: int, thread_id: str) -> None:
    """Compatibility facade for provider-neutral review-thread resolution."""
    _github_provider(target).change_requests.resolve_review_thread(target, pr_number, thread_id)


def merge_policy(target: Path) -> MergePolicy:
    """Compatibility facade for provider-neutral merge policy loading."""
    return _github_provider(target).merges.merge_policy(target)


def merge_capabilities(target: Path) -> MergeCapabilities:
    """Compatibility facade for live provider merge capabilities."""
    return _github_provider(target).merges.merge_capabilities(target)


def merge_gate(target: Path, pr_number: int) -> MergeGate:
    """Compatibility facade for the provider-neutral guarded merge gate."""
    return _github_provider(target).merges.merge_gate(target, pr_number)


def merge_pull_request(target: Path, pr_number: int) -> tuple[MergeGate, bool]:
    """Compatibility facade for the provider-neutral guarded merge operation."""
    return _github_provider(target).merges.merge_change_request(target, pr_number)


def _refresh_source(start: Path) -> Path:
    """Find the nearest 172X Agents checkout containing the canonical project metadata."""
    candidate = start.expanduser().resolve()
    if candidate.is_file():
        candidate = candidate.parent
    for directory in (candidate, *candidate.parents):
        metadata_path = directory / "pyproject.toml"
        if not metadata_path.is_file():
            continue
        try:
            metadata = tomllib.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as error:
            raise LibraryError(f"invalid project metadata: {metadata_path}") from error
        project = metadata.get("project")
        if isinstance(project, dict) and project.get("name") == "172x-agents":
            return directory
    raise LibraryError(
        "agents refresh must run inside a local 172x-agents checkout; "
        "use --source PATH to specify one"
    )


def _refresh_editable_cli(source: Path) -> None:
    """Replace the user-level CLI tool with an editable install from one local checkout."""
    uv = shutil.which("uv")
    if uv is None:
        raise LibraryError("agents refresh requires 'uv' on PATH")
    completed = subprocess.run(
        [uv, "tool", "install", "--editable", str(source), "--force"],
        cwd=source,
        shell=False,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown uv error"
        raise LibraryError(f"editable CLI refresh failed: {detail}")


@app.command("refresh")
def refresh(
    source: Annotated[
        Path | None,
        typer.Option(
            "--source",
            help="Local 172x-agents checkout; defaults to the current directory or its parents.",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Show the refresh plan without changing the CLI or skills."),
    ] = False,
) -> None:
    """Refresh the editable CLI and global Codex skills from local 172X Agents source."""
    try:
        checkout = _refresh_source(source or Path.cwd())
        home = default_codex_home()
        if dry_run:
            typer.echo(f"Source: {checkout}")
            typer.echo("Would refresh the editable 'agents' CLI with uv.")
            typer.echo(f"Would refresh global Codex skills under: {home}")
            return
        _refresh_editable_cli(checkout)
        plan = install_codex(home, force=True)
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo(f"Source: {checkout}")
    typer.echo("Editable 'agents' CLI: refreshed")
    typer.echo(f"Codex home: {home}")
    for action, path, _ in plan:
        typer.echo(f"{action} {path.as_posix()}")


def workflow_id_completions(incomplete: str) -> list[tuple[str, str]]:
    """Complete bundled workflow IDs without writes, network calls, or host startup."""
    normalized = incomplete.casefold()
    return [
        (workflow.id, workflow.description)
        for workflow in load_library("workflows")
        if workflow.id.casefold().startswith(normalized)
    ]


@install_app.callback(invoke_without_command=True)
def install(
    ctx: typer.Context,
) -> None:
    """Install Forge globally once, then activate language contexts per project."""
    if ctx.invoked_subcommand is not None:
        return
    typer.echo("Run: agents install codex")


@app.callback(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def agents(
    ctx: typer.Context,
    workflow: Annotated[
        str | None,
        typer.Option(
            "--workflow",
            help="Select a bundled workflow.",
            autocompletion=workflow_id_completions,
        ),
    ] = None,
    target: Annotated[
        Path | None,
        typer.Option(
            "--target",
            help="Target project directory.",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
    no_launch: Annotated[
        bool,
        typer.Option("--no-launch", help="Select without starting Codex."),
    ] = False,
) -> None:
    """Select a workflow when no subcommand has been requested."""
    if workflow is None:
        if ctx.args:
            raise typer.BadParameter("Codex options require --workflow")
        if no_launch:
            raise typer.BadParameter("--no-launch requires --workflow")
        return
    if ctx.invoked_subcommand is not None:
        raise typer.BadParameter("--workflow cannot be combined with an agents subcommand")
    try:
        selected = find_item("workflows", workflow)
        select_workflow(_target(target), workflow)
    except LibraryError as error:
        if "unknown workflow ID" in str(error):
            raise typer.BadParameter(str(error), param_hint="--workflow") from error
        _operational_error(str(error))
    if no_launch:
        if ctx.args:
            raise typer.BadParameter("Codex options cannot be combined with --no-launch")
        typer.echo(f"Active workflow: {workflow}")
        typer.echo(
            f"In Codex, select 172X · {selected.name.removesuffix(' Workflow')} from /skills."
        )
        return
    try:
        launch_codex(_target(target), workflow, tuple(ctx.args))
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        typer.echo(f"Active workflow: {workflow}")
        typer.echo(
            f"In Codex, select 172X · {selected.name.removesuffix(' Workflow')} from /skills."
        )
        raise typer.Exit(1) from error


@install_app.command("codex")
def install_codex_command(
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print the global installation plan without writing files."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Replace conflicting 172X-managed global skill files."),
    ] = False,
    only: Annotated[
        list[str] | None,
        typer.Option(
            "--only",
            help="Repeat a bundled agent or workflow ID to install only those capabilities.",
        ),
    ] = None,
) -> None:
    """Install all, or selected, Forge capabilities into the current user's Codex skills."""
    try:
        home = default_codex_home()
        plan = install_codex(home, dry_run=dry_run, force=force, only=tuple(only or ()))
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo(f"Codex home: {home}")
    for action, path, _ in plan:
        typer.echo(f"{action} {path.as_posix()}")
    if dry_run:
        typer.echo("No files written.")


@uninstall_app.command("codex")
def uninstall_codex_command(
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print the global removal plan without deleting files."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Remove modified 172X-managed global skill directories."),
    ] = False,
    only: Annotated[
        list[str] | None,
        typer.Option(
            "--only",
            help="Repeat a direct bundled capability ID to remove only that global skill.",
        ),
    ] = None,
) -> None:
    """Remove all, or selected, Forge capabilities from the current user's Codex skills."""
    try:
        home = default_codex_home()
        plan = uninstall_codex(home, dry_run=dry_run, force=force, only=tuple(only or ()))
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo(f"Codex home: {home}")
    for action, path, _ in plan:
        typer.echo(f"{action} {path.as_posix()}")
    if dry_run:
        typer.echo("No files deleted.")


@app.command("activate")
def activate(
    language: Annotated[
        str,
        typer.Argument(
            help="Language profile for this project path; Python and Rust are supported."
        ),
    ] = "python",
    path: Annotated[
        Path,
        typer.Option(
            "--path", help="Repository-relative project path to activate.", file_okay=False
        ),
    ] = Path("."),
    gate: Annotated[
        list[str] | None,
        typer.Option(
            "--gate", help="Repeat an expected gate tool ID; defaults to the language profile."
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print the local activation change without writing it."),
    ] = False,
    force: Annotated[
        bool, typer.Option("--force", help="Replace an existing activation at this project path.")
    ] = False,
) -> None:
    """Record local gates and initialize repository-local 172X provider settings."""
    try:
        normalized_language = language.casefold()
        selected_gates = tuple(gate or ())
        if not selected_gates:
            available_tools = language_tools(normalized_language)
            prompt = typer.prompt(
                "Expected gate tools (comma-separated)", default=", ".join(available_tools)
            )
            selected_gates = tuple(
                item.strip().casefold() for item in prompt.split(",") if item.strip()
            )
        profile = default_profile(language=normalized_language, gate_tools=selected_gates)
        config_action, config_path = _configure_local_provider(Path.cwd(), dry_run=dry_run)
        action, relative = write_activation(Path.cwd(), path, profile, dry_run=dry_run, force=force)
        exclude = ensure_activation_is_locally_ignored(Path.cwd(), dry_run=dry_run)
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo(f"{action} {relative.as_posix()}")
    if config_path is None:
        typer.echo("SKIPPED local Git provider config: target is not a Git repository")
    else:
        typer.echo(f"{config_action} local Git provider config: {config_path}")
    if exclude is not None:
        exclude_action, exclude_path = exclude
        typer.echo(f"{exclude_action} local Git exclude: {exclude_path}")
    typer.echo(
        "No external tools, dependencies, package-manager files, or tracked files were changed."
    )


@github_app.command("review-threads")
def github_review_threads(
    pr_number: Annotated[int, typer.Argument(min=1, help="Open pull request number.")],
    target: Annotated[
        Path | None,
        typer.Option(
            "--target", help="GitHub repository directory.", file_okay=False, dir_okay=True
        ),
    ] = None,
) -> None:
    """Print current GitHub review threads for an open pull request."""
    try:
        threads = review_threads(_target(target), pr_number)
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo(json.dumps(threads, indent=2, sort_keys=True))


@github_app.command("resolve-thread")
def github_resolve_thread(
    pr_number: Annotated[int, typer.Argument(min=1, help="Open pull request number.")],
    thread_id: Annotated[str, typer.Argument(help="Unresolved GitHub review-thread node ID.")],
    target: Annotated[
        Path | None,
        typer.Option(
            "--target", help="GitHub repository directory.", file_okay=False, dir_okay=True
        ),
    ] = None,
) -> None:
    """Resolve one independently verified GitHub review thread after repository opt-in."""
    try:
        resolve_review_thread(_target(target), pr_number, thread_id)
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo(f"Resolved GitHub review thread {thread_id} on PR #{pr_number}.")


@github_app.command("reviewers")
def github_reviewers(
    target: Annotated[
        Path | None,
        typer.Option(
            "--target", help="GitHub repository directory.", file_okay=False, dir_okay=True
        ),
    ] = None,
) -> None:
    """List committed GitHub reviewers without printing token values."""
    try:
        reviewers = configured_reviewers(_target(target))
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo("Configured GitHub reviewers:")
    for reviewer in reviewers:
        state = "token set" if os.environ.get(reviewer.token_env) else "token missing"
        typer.echo(f"- {reviewer.login} (token_env={reviewer.token_env}; {state})")


@github_app.command("reviewer-status")
def github_reviewer_status(
    reviewer: Annotated[str, typer.Option("--reviewer", help="Configured reviewer login.")],
    target: Annotated[
        Path | None,
        typer.Option(
            "--target", help="GitHub repository directory.", file_okay=False, dir_okay=True
        ),
    ] = None,
) -> None:
    """Verify a configured reviewer token's GitHub identity and repository access."""
    try:
        status = reviewer_status(_target(target), reviewer)
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo(f"Reviewer: {status.reviewer.login}")
    typer.echo(f"Authenticated as: {status.authenticated_login}")
    typer.echo(f"Repository permission: {status.repository_permission}")


@github_app.command("review")
def github_review(
    pr_number: Annotated[int, typer.Argument(min=1, help="Open pull request number.")],
    reviewer: Annotated[str, typer.Option("--reviewer", help="Configured reviewer login.")],
    head: Annotated[str, typer.Option("--head", help="Exact pull-request head commit OID.")],
    report: Annotated[Path, typer.Option("--report", help="Markdown review report file.")],
    target: Annotated[
        Path | None,
        typer.Option(
            "--target", help="GitHub repository directory.", file_okay=False, dir_okay=True
        ),
    ] = None,
) -> None:
    """Publish a non-approving review report through the configured reviewer identity."""
    try:
        submission = submit_review(_target(target), pr_number, reviewer, head, report)
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo(
        f"Submitted {submission.state} review for PR #{submission.pr_number} "
        f"as {submission.reviewer} on {submission.head_oid}."
    )


@github_app.command("approve")
def github_approve(
    pr_number: Annotated[int, typer.Argument(min=1, help="Open pull request number.")],
    reviewer: Annotated[str, typer.Option("--reviewer", help="Configured reviewer login.")],
    head: Annotated[str, typer.Option("--head", help="Exact pull-request head commit OID.")],
    report: Annotated[Path, typer.Option("--report", help="Markdown approval report file.")],
    target: Annotated[
        Path | None,
        typer.Option(
            "--target", help="GitHub repository directory.", file_okay=False, dir_okay=True
        ),
    ] = None,
) -> None:
    """Submit and confirm an independent approval for the exact pull-request head."""
    try:
        submission = approve_pull_request(_target(target), pr_number, reviewer, head, report)
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo(
        f"Submitted {submission.state} review for PR #{submission.pr_number} "
        f"as {submission.reviewer} on {submission.head_oid}."
    )


@github_app.command("gate")
def github_gate(
    pr_number: Annotated[int, typer.Argument(min=1, help="Open pull request number.")],
    target: Annotated[
        Path | None,
        typer.Option(
            "--target", help="GitHub repository directory.", file_okay=False, dir_okay=True
        ),
    ] = None,
) -> None:
    """Fail unless an opted-in PR currently meets every dev-loop merge gate."""
    try:
        gate = merge_gate(_target(target), pr_number)
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo(f"PR #{gate.pr_number} is eligible for dev-loop merge.")
    typer.echo(f"URL: {gate.url}")
    typer.echo(f"Base branch: {gate.policy.base_branch}")
    typer.echo(f"Merge method: {gate.policy.merge_method}")
    if gate.provider_capabilities is not None:
        methods = ", ".join(sorted(gate.provider_capabilities.merge_methods))
        typer.echo(f"Provider allowed merge methods: {methods}")
    typer.echo(f"GitHub checks: {gate.reported_checks} reported, all passing")
    typer.echo(f"GitHub review threads: {gate.resolved_threads} resolved, 0 unresolved")
    typer.echo(
        "Configured reviewer approvals: "
        + (", ".join(gate.approved_reviewers) if gate.approved_reviewers else "none")
    )


@github_app.command("merge-policy")
def github_merge_policy(
    target: Annotated[
        Path | None,
        typer.Option(
            "--target", help="GitHub repository directory.", file_okay=False, dir_okay=True
        ),
    ] = None,
) -> None:
    """Show the configured merge policy and live GitHub compatibility evidence."""
    project = _target(target)
    try:
        provider = _github_provider(project)
        policy = provider.merges.merge_policy(project)
        capabilities = provider.merges.merge_capabilities(project)
    except LibraryError as error:
        _operational_error(str(error))
    compatible = policy.merge_method in capabilities.methods
    typer.echo(f"Provider: source_control:{provider.key.name}")
    typer.echo(f"Base branch: {policy.base_branch}")
    typer.echo(f"Configured method: {policy.merge_method}")
    typer.echo(
        "Provider allowed methods: "
        + (", ".join(sorted(capabilities.methods)) if capabilities.methods else "none")
    )
    typer.echo(f"Provider default method: {capabilities.default_method or 'unknown'}")
    typer.echo("Provider default base branch: " + (capabilities.default_base_branch or "unknown"))
    typer.echo(f"Compatibility: {'PASS' if compatible else 'BLOCKED'}")
    if not compatible:
        raise typer.Exit(1)


@github_app.command("merge")
def github_merge(
    pr_number: Annotated[int, typer.Argument(min=1, help="Open pull request number.")],
    target: Annotated[
        Path | None,
        typer.Option(
            "--target", help="GitHub repository directory.", file_okay=False, dir_okay=True
        ),
    ] = None,
) -> None:
    """Recheck the live gate, then make one guarded merge request for the checked PR head."""
    try:
        gate, merged = merge_pull_request(_target(target), pr_number)
    except LibraryError as error:
        _operational_error(str(error))
    if merged:
        typer.echo(f"Merged PR #{gate.pr_number} into {gate.policy.base_branch}: {gate.url}")
    else:
        typer.echo(
            f"GitHub accepted the merge request for PR #{gate.pr_number}, but it is not merged yet. "
            "A repository merge queue may still be processing it."
        )


@app.command("list")
def list_agents() -> None:
    """List bundled agents and whether their global Codex skill is current."""
    home = default_codex_home()
    typer.echo(f"{'ID':<25} {'NAME':<34} INSTALLED")
    for agent in load_library("agents"):
        expected = managed_files(only=(agent.id,))[Path("skills") / f"172x-{agent.id}" / "SKILL.md"]
        installed = home / "skills" / f"172x-{agent.id}" / "SKILL.md"
        current = (
            installed.is_file()
            and not installed.is_symlink()
            and installed.read_bytes() == expected
        )
        typer.echo(f"{agent.id:<25} {agent.name:<34} {'yes' if current else 'no'}")


@app.command("domains")
def list_domains() -> None:
    """List Markdown-defined agent domains and their specialist roles."""
    for domain, agents in domains().items():
        typer.echo(f"{domain}: {', '.join(agent.id for agent in agents)}")


@app.command("providers")
def providers() -> None:
    """List registered provider families and implemented capabilities."""
    typer.echo(f"{'PROVIDER':<28} CAPABILITIES")
    for descriptor in default_registry().descriptors():
        capabilities = ", ".join(sorted(capability.value for capability in descriptor.capabilities))
        typer.echo(f"{descriptor.key.qualified_name:<28} {capabilities}")


@app.command("capabilities")
def capabilities() -> None:
    """List what is implemented now and what is only a planned contribution point."""
    typer.echo(f"{'KIND':<12} {'ID':<22} STATUS")
    for kind, identifier, status in capability_rows():
        typer.echo(f"{kind:<12} {identifier:<22} {status}")


@app.command("workflows")
def workflows(
    target: Annotated[
        Path | None,
        typer.Option(
            "--target",
            help="Project whose custom workflows to include.",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
) -> None:
    """List bundled workflows and validated project-owned workflows."""
    typer.echo(f"{'ID':<22} {'NAME':<40} DESCRIPTION")
    try:
        available = load_workflows(_target(target))
    except LibraryError as error:
        _operational_error(str(error))
    for workflow in available:
        typer.echo(f"{workflow.id:<22} {workflow.name:<40} {workflow.description}")


@app.command("show")
def show(
    workflow_id: Annotated[
        str,
        typer.Argument(
            help="Bundled or project-owned workflow ID.",
            autocompletion=workflow_id_completions,
        ),
    ],
    target: Annotated[
        Path | None,
        typer.Option(
            "--target", help="Project whose workflow to show.", file_okay=False, dir_okay=True
        ),
    ] = None,
) -> None:
    """Show bundled or project-owned workflow Markdown without frontmatter."""
    try:
        workflow = find_workflow(_target(target), workflow_id)
    except LibraryError as error:
        raise typer.BadParameter(str(error), param_hint="WORKFLOW_ID") from error
    typer.echo(f"{workflow.name} ({workflow.id})\n{workflow.description}\n")
    typer.echo(workflow.body, nl=False)


@app.command("doctor")
def doctor(
    target: Annotated[
        Path | None,
        typer.Option(
            "--target",
            help="Project to diagnose.",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
) -> None:
    """Perform read-only global-installation, activation, and executable checks."""
    project = _target(target)
    try:
        validate_library()
        project_ok = project.expanduser().resolve().is_dir()
    except LibraryError as error:
        _operational_error(str(error))
    profile: ProjectProfile | None = None
    profile_error: str | None = None
    if project_ok:
        try:
            profile = load_profile(project)
        except LibraryError as error:
            profile_error = str(error)
    home = default_codex_home()
    installed_capabilities = installed_capability_ids(home) if home.is_dir() else ()
    skill_ok = bool(installed_capabilities)
    active = active_workflow(project) if project_ok else None
    active_path = project.expanduser().resolve() / ".172x/active-workflow" if project_ok else None
    active_ok = active is not None or active_path is None or not active_path.exists()
    typer.echo("Library:          OK")
    typer.echo(f"Target:           {'OK' if project_ok else 'FAIL'}")
    if skill_ok:
        total = len(load_library("agents")) + len(load_library("workflows"))
        scope = "complete" if len(installed_capabilities) == total else "focused"
        typer.echo(f"Global Forge:     OK ({scope} {len(installed_capabilities)}/{total}; {home})")
    else:
        typer.echo(f"Global Forge:     MISSING OR OUTDATED ({home})")
    typer.echo(f"Active workflow:  {active if active is not None else 'NONE OR INVALID'}")
    executable_ok = shutil.which("codex") is not None
    typer.echo(f"Codex executable: {'OK' if executable_ok else 'NOT FOUND'}")
    prerequisite_ok = True
    if profile is not None:
        typer.echo(
            f"Activation:       OK ({profile.language}; gates: {', '.join(profile.gate_tools)})"
        )
        rows = prerequisite_rows(project, profile)
        for label, ok, detail in rows:
            state = "OK" if ok else "FAIL" if not label.endswith("reviewer identity") else "CHECK"
            typer.echo(f"{label}: {state} ({detail})")
        prerequisite_ok = prerequisites_ok(rows)
    elif profile_error is not None:
        typer.echo(f"Activation:       NONE OR INVALID ({profile_error})")
    if (
        not project_ok
        or not skill_ok
        or not active_ok
        or not executable_ok
        or not prerequisite_ok
        or profile_error is not None
    ):
        raise typer.Exit(1)


def create_app() -> typer.Typer:
    """Return the product command group for the public 172X plugin contract."""
    return app


def main() -> None:
    """Run 172X Agents as a standalone command."""
    app()
