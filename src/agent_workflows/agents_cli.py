"""Standalone and pluggable command group for 172X Agents."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Annotated

import click
import typer

from .codex import (
    Action,
    active_workflow,
    codex_toml,
    install_configured_codex,
    integration_current,
    launch_codex,
    select_workflow,
)
from .github import merge_gate, merge_pull_request, resolve_review_thread, review_threads
from .library import LibraryError, domains, find_item, load_library, validate_library
from .profiles import (
    ProjectProfile,
    capability_rows,
    default_profile,
    gate_tools_declared,
    gate_install_command,
    install_gate_tools,
    language_tools,
    load_profile,
    prerequisite_rows,
    prerequisites_ok,
)

class CodexOptionGroup(typer.core.TyperGroup):
    """Keep unknown root options for Codex while preserving normal subcommands."""

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        remaining = click.Command.parse_args(self, ctx, self._root_options_first(args))
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
            if argument.startswith("--workflow=") or argument.startswith("--target="):
                root_options.append(argument)
            elif argument == "--no-launch":
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
install_app = typer.Typer(help="Create a reviewed 172X project profile and install a host integration.")
github_app = typer.Typer(help="Inspect guarded dev-loop pull-request gates and perform protected merges.")
app.add_typer(install_app, name="install")
app.add_typer(github_app, name="github")


def _target(target: Path | None) -> Path:
    return target if target is not None else Path.cwd()


def _operational_error(message: str) -> None:
    typer.echo(f"Error: {message}", err=True)
    raise typer.Exit(1)


def _profile(host: str, language: str, gate: tuple[str, ...]) -> ProjectProfile:
    tools = gate if gate else None
    return default_profile(host=host, language=language, gate_tools=tools)


def _check_profile_prerequisites(project: Path, profile: ProjectProfile) -> None:
    rows = prerequisite_rows(project, profile)
    if prerequisites_ok(rows):
        return
    failed = "; ".join(
        f"{label}: {detail}"
        for label, ok, detail in rows
        if not ok and label != "GitHub reviewer identity"
    )
    raise LibraryError(f"profile prerequisites are not ready: {failed}")


def _install_profiled_codex(
    target: Path,
    language: str,
    gate: tuple[str, ...],
    dry_run: bool,
    force: bool,
) -> tuple[list[tuple[Action, Path, bytes]], tuple[str, ...]]:
    profile = _profile("codex", language, gate)
    plan = install_configured_codex(target, profile, dry_run=True, force=force)
    tool_command = () if gate_tools_declared(target, profile) else gate_install_command(target, profile)
    if dry_run:
        return plan, tool_command
    if tool_command:
        typer.echo(f"Installing selected gate tools: {' '.join(tool_command)}")
        install_gate_tools(target, profile)
    _check_profile_prerequisites(target, profile)
    return install_configured_codex(target, profile, dry_run=False, force=force), tool_command


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
    target: Annotated[
        Path | None,
        typer.Option("--target", help="Target project directory.", file_okay=False, dir_okay=True),
    ] = None,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Validate and print the plan without writing files.")
    ] = False,
    force: Annotated[
        bool, typer.Option("--force", help="Replace a conflicting 172x.toml or managed file.")
    ] = False,
) -> None:
    """Guide creation of the only currently supported project profile when called bare."""
    if ctx.invoked_subcommand is not None:
        return
    host = typer.prompt("Coding host", default="codex").strip().casefold()
    language = typer.prompt("Programming language", default="python").strip().casefold()
    try:
        available_tools = language_tools(language)
    except LibraryError as error:
        _operational_error(str(error))
    tools_text = typer.prompt("Gate tools (comma-separated)", default=", ".join(available_tools))
    gate = tuple(tool.strip().casefold() for tool in tools_text.split(",") if tool.strip())
    if host != "codex":
        try:
            _profile(host, language, gate)
        except LibraryError as error:
            _operational_error(str(error))
    try:
        plan, tool_command = _install_profiled_codex(
            _target(target), language, gate, dry_run, force
        )
    except LibraryError as error:
        _operational_error(str(error))
    if dry_run and tool_command:
        typer.echo(f"Would install selected gate tools: {' '.join(tool_command)}")
    for action, path, _ in plan:
        typer.echo(f"{action} {path.as_posix()}")
    if dry_run:
        typer.echo("No files written.")


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
        find_item("workflows", workflow)
        select_workflow(_target(target), workflow)
    except LibraryError as error:
        if "unknown workflow ID" in str(error):
            raise typer.BadParameter(str(error), param_hint="--workflow") from error
        _operational_error(str(error))
    if no_launch:
        if ctx.args:
            raise typer.BadParameter("Codex options cannot be combined with --no-launch")
        typer.echo(f"Active workflow: {workflow}")
        typer.echo(f"In Codex, run: $172x run {workflow}")
        return
    try:
        launch_codex(_target(target), workflow, tuple(ctx.args))
    except FileNotFoundError as error:
        typer.echo(str(error), err=True)
        typer.echo(f"Active workflow: {workflow}")
        typer.echo(f"In Codex, run: $172x run {workflow}")
        raise typer.Exit(1) from error


@install_app.command("codex")
def install_codex_command(
    language: Annotated[str, typer.Argument(help="Programming language profile; Python is supported.")] = "python",
    target: Annotated[
        Path | None,
        typer.Option(
            "--target",
            help="Target project directory.",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print the plan without writing files."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Replace conflicting managed files."),
    ] = False,
    gate: Annotated[
        list[str] | None,
        typer.Option("--gate", help="Repeat a supported gate tool ID; defaults to the Python profile."),
    ] = None,
) -> None:
    """Install Codex plus a committed Python/Git/GitHub 172X project profile."""
    try:
        selected_gate = tuple(gate or ())
        if not selected_gate:
            available_tools = language_tools(language.casefold())
            tools_text = typer.prompt(
                "Gate tools to install (comma-separated)", default=", ".join(available_tools)
            )
            selected_gate = tuple(
                tool.strip().casefold() for tool in tools_text.split(",") if tool.strip()
            )
        plan, tool_command = _install_profiled_codex(
            _target(target), language.casefold(), selected_gate, dry_run, force
        )
    except LibraryError as error:
        _operational_error(str(error))
    if dry_run and tool_command:
        typer.echo(f"Would install selected gate tools: {' '.join(tool_command)}")
    for action, path, _ in plan:
        typer.echo(f"{action} {path.as_posix()}")
    if dry_run:
        typer.echo("No files written.")

@github_app.command("review-threads")
def github_review_threads(
    pr_number: Annotated[int, typer.Argument(min=1, help="Open pull request number.")],
    target: Annotated[
        Path | None,
        typer.Option("--target", help="GitHub repository directory.", file_okay=False, dir_okay=True),
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
        typer.Option("--target", help="GitHub repository directory.", file_okay=False, dir_okay=True),
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
        typer.Option("--target", help="GitHub repository directory.", file_okay=False, dir_okay=True),
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
    typer.echo(f"GitHub checks: {gate.passing_checks} passed")
    typer.echo(f"GitHub review threads: {gate.resolved_threads} resolved, 0 unresolved")


@github_app.command("merge")
def github_merge(
    pr_number: Annotated[int, typer.Argument(min=1, help="Open pull request number.")],
    target: Annotated[
        Path | None,
        typer.Option("--target", help="GitHub repository directory.", file_okay=False, dir_okay=True),
    ] = None,
) -> None:
    """Recheck the live gate, then make one protected merge request for the checked PR head."""
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
def list_agents(
    target: Annotated[
        Path | None,
        typer.Option(
            "--target",
            help="Project to inspect.",
            file_okay=False,
            dir_okay=True,
        ),
    ] = None,
) -> None:
    """List bundled agents and whether their generated Codex custom agent is current."""
    project = _target(target)
    typer.echo(f"{'ID':<25} {'NAME':<34} INSTALLED")
    for agent in load_library("agents"):
        expected = codex_toml(agent)
        installed = project / ".codex/agents" / f"172x-{agent.id}.toml"
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
def workflows() -> None:
    """List bundled workflows."""
    typer.echo(f"{'ID':<22} {'NAME':<40} DESCRIPTION")
    for workflow in load_library("workflows"):
        typer.echo(f"{workflow.id:<22} {workflow.name:<40} {workflow.description}")


@app.command("show")
def show(
    workflow_id: Annotated[
        str,
        typer.Argument(
            help="Bundled workflow ID.",
            autocompletion=workflow_id_completions,
        ),
    ],
) -> None:
    """Show canonical workflow Markdown without frontmatter."""
    try:
        workflow = find_item("workflows", workflow_id)
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
    """Perform read-only library, installation, selection, and executable checks."""
    project = _target(target)
    try:
        agents, _ = validate_library()
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
    skill_ok = integration_current(project) if project_ok else False
    active = active_workflow(project) if project_ok else None
    active_path = project.expanduser().resolve() / ".172x/active-workflow" if project_ok else None
    active_ok = active is not None or active_path is None or not active_path.exists()
    custom_current = 0
    if project_ok:
        for agent in agents:
            expected = codex_toml(agent)
            path = project.expanduser().resolve() / ".codex/agents" / f"172x-{agent.id}.toml"
            if path.is_file() and not path.is_symlink() and path.read_bytes() == expected:
                custom_current += 1
    typer.echo("Library:          OK")
    typer.echo(f"Target:           {'OK' if project_ok else 'FAIL'}")
    typer.echo(f"Codex skill: {'OK' if skill_ok else 'MISSING OR OUTDATED'}")
    typer.echo(
        f"Custom agents:    {'OK' if custom_current == len(agents) else 'MISSING OR OUTDATED'} ({custom_current}/{len(agents)})"
    )
    typer.echo(f"Active workflow:  {active if active is not None else 'NONE OR INVALID'}")
    executable_ok = shutil.which("codex") is not None
    typer.echo(f"Codex executable: {'OK' if executable_ok else 'NOT FOUND'}")
    prerequisite_ok = True
    if profile is not None:
        typer.echo(
            f"Project profile:  OK ({profile.host}/{profile.language}/{profile.scm}/{profile.provider})"
        )
        rows = prerequisite_rows(project, profile)
        for label, ok, detail in rows:
            state = "OK" if ok else "FAIL" if label != "GitHub reviewer identity" else "CHECK"
            typer.echo(f"{label}: {state} ({detail})")
        prerequisite_ok = prerequisites_ok(rows)
    elif profile_error is not None:
        typer.echo(f"Project profile:  MISSING OR INVALID ({profile_error})")
    if (
        not project_ok
        or not skill_ok
        or custom_current != len(agents)
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
