"""Standalone and pluggable command group for 172X Agents."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Annotated

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
from .github import merge_gate, merge_pull_request, resolve_review_thread, review_threads
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
        str, typer.Argument(help="Language profile for this project path; Python is supported.")
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
    """Record a local quality contract without installing or changing external developer tools."""
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
        action, relative = write_activation(Path.cwd(), path, profile, dry_run=dry_run, force=force)
        exclude = ensure_activation_is_locally_ignored(Path.cwd(), dry_run=dry_run)
    except LibraryError as error:
        _operational_error(str(error))
    typer.echo(f"{action} {relative.as_posix()}")
    if exclude is not None:
        exclude_action, exclude_path = exclude
        typer.echo(f"{exclude_action} local Git exclude: {exclude_path}")
    typer.echo("No external tools, dependencies, or package-manager files were changed.")


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
    typer.echo(f"GitHub checks: {gate.reported_checks} reported, all passing")
    typer.echo(f"GitHub review threads: {gate.resolved_threads} resolved, 0 unresolved")


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
            state = "OK" if ok else "FAIL" if label != "GitHub reviewer identity" else "CHECK"
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
