"""Deterministic project-scoped Codex installation helpers."""

from __future__ import annotations

import json
import shutil
import subprocess
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Literal

from .library import LibraryError, LibraryItem, find_workflow, load_library, load_workflows
from .profiles import CONFIG_PATH, ProjectProfile, load_profile, project_toml

Action = Literal["CREATE", "UNCHANGED", "CONFLICT", "REPLACE", "DELETE"]

_RENAMED_AGENT_IDS = (
    "backend-architecture",
    "backend-implementation",
    "backend-review",
    "brief",
    "coding",
    "design-architecture-review",
    "discovery",
    "frontend-implementation",
    "frontend-review",
    "market-research",
    "pr-review",
    "product-specification",
    "qa",
    "security-review",
    "ux-ui-design",
)


def _resource_bytes(parts: tuple[str, ...]) -> bytes:
    resource = resources.files("agent_workflows").joinpath("library", *parts)
    return resource.read_bytes()


def codex_toml(agent: LibraryItem) -> bytes:
    """Render supported custom-agent fields as stable, human-readable TOML."""
    instructions = agent.body.replace("\\", "\\\\").replace('"', '\\"')
    return (
        f"name = {json.dumps(agent.name)}\n"
        f"description = {json.dumps(agent.description)}\n"
        f'developer_instructions = """{instructions}"""\n'
    ).encode()


def _skill_metadata(display_name: str, description: str, default_prompt: str) -> bytes:
    return (
        "interface:\n"
        f"  display_name: {json.dumps(display_name)}\n"
        f"  short_description: {json.dumps(description)}\n"
        f"  default_prompt: {json.dumps(default_prompt)}\n"
    ).encode()


def _agent_skill(agent: LibraryItem) -> bytes:
    """Render one direct-use native Codex skill backed by canonical agent Markdown."""
    skill_name = f"172x-{agent.id}"
    title = agent.name.removesuffix(" Agent")
    return (
        f"---\nname: {skill_name}\ndescription: {json.dumps(f'172X {title}: {agent.description}')}\n---\n\n"
        f"# 172X · {title}\n\n"
        "You are using this 172X specialist directly, not running a workflow. Before responding, read "
        f"`.agents/skills/172x-agents/references/agents/{agent.relative_path}` completely and apply its "
        "instructions to the user's current request. Resolve any `references/` or `assets/` path named "
        "there within `.agents/skills/172x-agents/`. Deliver that specialist's observable result and "
        "honor its evidence, handoff, and boundary rules. Do not claim that another agent, a provider, "
        "or a human completed an action unless it actually occurred.\n"
    ).encode()


def workflow_skill_title(workflow_id: str) -> str:
    """Return the short display label for one direct native workflow skill."""
    titles = {
        "dev": "Dev",
        "dev-loop": "Dev Loop",
        "idea-to-build": "Idea to Build",
        "idea-to-product": "Idea to Product",
    }
    return titles.get(workflow_id, workflow_id.replace("-", " ").title())


def _workflow_title(workflow: LibraryItem) -> str:
    """Return a compact native-picker label for bundled or project workflows."""
    if workflow.relative_path.startswith("custom/"):
        return workflow.name.removesuffix(" Workflow")
    return workflow_skill_title(workflow.id)


def _workflow_skill(workflow: LibraryItem) -> bytes:
    """Render a one-click native Codex workflow skill that uses the shared coordinator."""
    title = _workflow_title(workflow)
    skill_name = f"172x-{workflow.id}"
    return (
        f"---\nname: {skill_name}\ndescription: {json.dumps(f'172X {title}: {workflow.description}')}\n---\n\n"
        f"# 172X · {title}\n\n"
        f"Run the `{workflow.id}` workflow for the user's current task. Before any delegation, read "
        "`.agents/skills/172x-agents/SKILL.md` and then read "
        f"`.agents/skills/172x-agents/references/workflows/{workflow.relative_path}` completely. Apply the "
        "coordinator rules and execute this selected workflow immediately; do not ask the user to "
        "choose a workflow again. If the task or idea is missing, ask for it before delegation.\n"
    ).encode()


def _copy_resource_tree(resource: Traversable, destination: Path) -> dict[Path, bytes]:
    """Copy bundled Markdown references without adding a general resource framework."""
    files: dict[Path, bytes] = {}
    for source in resource.iterdir():
        if source.is_dir():
            files.update(_copy_resource_tree(source, destination / source.name))
        elif source.is_file():
            files[destination / source.name] = source.read_bytes()
    return files


def _workflow_composer_skill() -> bytes:
    """Render the direct native skill that authors project-owned workflow Markdown."""
    return b"""---
name: 172x-workflow-composer
description: Create or revise a project-owned 172X workflow from the installed role catalog without adding a workflow runtime.
---

# 172X \xc2\xb7 Workflow Composer

Create a reviewable project-owned workflow, not an executable workflow engine.

1. Read `.agents/skills/172x-agents/SKILL.md`, then inspect `.agents/skills/172x-agents/references/agents/` to select only shipped roles needed for the user's goal.
2. Propose a concise flow with required handoffs, safe parallel work, feedback limits, and explicit human gates. Do not let an implementation role approve its own work. Do not invent agents, external actions, or a runtime.
3. Before writing, show the user the proposed workflow ID, title, participating roles, flow, feedback loops, and human gates. Require explicit approval when overwriting an existing project workflow.
4. After approval, create one Markdown file at `.172x/workflows/<workflow-id>.md`, using `.agents/skills/172x-agents/assets/workflows/custom-workflow-template.md`. The ID must be lowercase kebab-case and unique across bundled and project workflows. Fill every required section with concrete content.
5. Validate the result with `agents workflows --target .` and refresh native skills with `agents install codex python --force`. Report the new direct picker entry as `172X \xc2\xb7 <workflow name without Workflow>`.

Never write bundled library files, `.codex/config.toml`, credentials, or arbitrary workflow graphs. Do not activate or run the new workflow unless the user asks separately.
"""


def managed_files(target: Path | None = None) -> dict[Path, bytes]:
    """Return every owned installation path and its expected bytes."""
    files: dict[Path, bytes] = {
        Path(".agents/skills/172x-agents/SKILL.md"): _resource_bytes(("codex", "SKILL.md")),
        Path(".agents/skills/172x-agents/agents/openai.yaml"): _resource_bytes(
            ("codex", "agents", "openai.yaml")
        ),
    }
    composer_root = Path(".agents/skills/172x-workflow-composer")
    files[composer_root / "SKILL.md"] = _workflow_composer_skill()
    files[composer_root / "agents/openai.yaml"] = _skill_metadata(
        "172X · Workflow Composer",
        "Compose a project-owned workflow from the installed 172X roles.",
        "Create a 172X workflow for the current project.",
    )
    for kind in ("agents", "workflows"):
        source_root = resources.files("agent_workflows").joinpath("library", kind)
        files.update(
            _copy_resource_tree(source_root, Path(".agents/skills/172x-agents/references") / kind)
        )
    reference_root = resources.files("agent_workflows").joinpath("library", "references")
    files.update(_copy_resource_tree(reference_root, Path(".agents/skills/172x-agents/references")))
    asset_root = resources.files("agent_workflows").joinpath("library", "assets")
    files.update(_copy_resource_tree(asset_root, Path(".agents/skills/172x-agents/assets")))
    for agent in load_library("agents"):
        files[Path(".codex/agents") / f"172x-{agent.id}.toml"] = codex_toml(agent)
        skill_root = Path(".agents/skills") / f"172x-{agent.id}"
        files[skill_root / "SKILL.md"] = _agent_skill(agent)
        files[skill_root / "agents/openai.yaml"] = _skill_metadata(
            f"172X · {agent.name.removesuffix(' Agent')}",
            agent.description,
            f"Use the 172X {agent.name.removesuffix(' Agent')} specialist for this task.",
        )
    for workflow in load_workflows(target):
        if workflow.relative_path.startswith("custom/"):
            files[
                Path(".agents/skills/172x-agents/references/workflows") / workflow.relative_path
            ] = Path(workflow.source).read_bytes()
        skill_root = Path(".agents/skills") / f"172x-{workflow.id}"
        title = _workflow_title(workflow)
        files[skill_root / "SKILL.md"] = _workflow_skill(workflow)
        files[skill_root / "agents/openai.yaml"] = _skill_metadata(
            f"172X · {title}",
            workflow.description,
            f"Run the 172X {title} workflow for the current task.",
        )
    return dict(sorted(files.items(), key=lambda item: item[0].as_posix()))


def configured_codex_files(
    profile: ProjectProfile, target: Path | None = None
) -> dict[Path, bytes]:
    """Return the Codex installation plus its reviewed project profile."""
    files = managed_files(target)
    files[CONFIG_PATH] = project_toml(profile)
    return dict(sorted(files.items(), key=lambda item: item[0].as_posix()))


def _target_directory(target: Path) -> Path:
    resolved = target.expanduser().resolve()
    if not resolved.is_dir():
        raise LibraryError(f"target project is not a directory: {target}")
    return resolved


def _safe_destination(target: Path, relative: Path) -> Path:
    destination = target / relative
    current = target
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise LibraryError(f"managed path must not be a symlink: {current}")
    return destination


def _install_plan(
    target: Path, files: dict[Path, bytes], force: bool = False
) -> list[tuple[Action, Path, bytes]]:
    target = _target_directory(target)
    plan: list[tuple[Action, Path, bytes]] = []
    for relative, contents in files.items():
        try:
            destination = _safe_destination(target, relative)
        except LibraryError:
            plan.append(("CONFLICT", relative, contents))
            continue
        if not destination.exists():
            action: Action = "CREATE"
        elif destination.is_file() and destination.read_bytes() == contents:
            action = "UNCHANGED"
        else:
            action = "REPLACE" if force else "CONFLICT"
        plan.append((action, relative, contents))
    for relative in _renamed_agent_paths():
        try:
            destination = _safe_destination(target, relative)
        except LibraryError:
            plan.append(("CONFLICT", relative, b""))
            continue
        if destination.exists():
            action = "DELETE" if force else "CONFLICT"
            plan.append((action, relative, b""))
    return plan


def _renamed_agent_paths() -> tuple[Path, ...]:
    """Return former v0.1 generated agent files removed during an explicit refresh."""
    paths: list[Path] = []
    for agent_id in _RENAMED_AGENT_IDS:
        paths.extend(
            (
                Path(".codex/agents") / f"172x-{agent_id}.toml",
                Path(".agents/skills") / f"172x-{agent_id}" / "SKILL.md",
                Path(".agents/skills") / f"172x-{agent_id}" / "agents/openai.yaml",
            )
        )
    return tuple(paths)


def _conflict_error(plan: list[tuple[Action, Path, bytes]]) -> LibraryError:
    """Name every managed conflict so a user can make an informed force decision."""
    conflicts = [path.as_posix() for action, path, _ in plan if action == "CONFLICT"]
    return LibraryError(
        "installation has conflicts in managed paths: "
        + ", ".join(conflicts)
        + "; rerun with --force only if replacing or removing those 172X-managed files is intended"
    )


def install_plan(target: Path, force: bool = False) -> list[tuple[Action, Path, bytes]]:
    """Return the Codex installation plan for compatibility with the public API."""
    return _install_plan(target, managed_files(target), force=force)


def install_codex(
    target: Path, dry_run: bool = False, force: bool = False
) -> list[tuple[Action, Path, bytes]]:
    """Plan first, then write only owned paths when the complete plan is safe."""
    target = _target_directory(target)
    plan = install_plan(target, force=force)
    if any(action == "CONFLICT" for action, _, _ in plan):
        raise _conflict_error(plan)
    if dry_run:
        return plan
    for action, relative, contents in plan:
        if action == "UNCHANGED":
            continue
        destination = _safe_destination(target, relative)
        if action == "DELETE":
            destination.unlink()
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(contents)
    return plan


def install_configured_codex(
    target: Path, profile: ProjectProfile, dry_run: bool = False, force: bool = False
) -> list[tuple[Action, Path, bytes]]:
    """Install Codex content and one project-owned 172X profile atomically by plan."""
    target = _target_directory(target)
    plan = _install_plan(target, configured_codex_files(profile, target), force=force)
    if any(action == "CONFLICT" for action, _, _ in plan):
        raise _conflict_error(plan)
    if dry_run:
        return plan
    for action, relative, contents in plan:
        if action == "UNCHANGED":
            continue
        destination = _safe_destination(target, relative)
        if action == "DELETE":
            destination.unlink()
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(contents)
    return plan


def integration_current(target: Path) -> bool:
    try:
        return all(action == "UNCHANGED" for action, _, _ in install_plan(target))
    except LibraryError:
        return False


def configured_integration_current(target: Path) -> bool:
    """Return whether the Codex installation and committed project profile are current."""
    try:
        profile = load_profile(_target_directory(target))
        return all(
            action == "UNCHANGED"
            for action, _, _ in _install_plan(target, configured_codex_files(profile, target))
        )
    except LibraryError:
        return False


def select_workflow(target: Path, workflow_id: str) -> Path:
    """Persist one validated workflow ID; this is selection, not run state."""
    target = _target_directory(target)
    find_workflow(target, workflow_id)
    if not configured_integration_current(target):
        raise LibraryError("Codex integration is not current; run: agents install codex")
    relative = Path(".172x/active-workflow")
    destination = _safe_destination(target, relative)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(f"{workflow_id}\n", encoding="utf-8")
    return destination


def active_workflow(target: Path) -> str | None:
    target = _target_directory(target)
    path = target / ".172x/active-workflow"
    if not path.exists() or path.is_symlink():
        return None
    value = path.read_text(encoding="utf-8")
    if not value.endswith("\n") or value.count("\n") != 1:
        return None
    try:
        find_workflow(target, value[:-1])
    except LibraryError:
        return None
    return value[:-1]


def launch_codex(target: Path, workflow_id: str, codex_options: tuple[str, ...] = ()) -> None:
    """Launch Codex with a validated workflow prompt and user-supplied CLI options."""
    if shutil.which("codex") is None:
        raise FileNotFoundError("The 'codex' executable was not found on PATH.")
    prompt = f"$172x-{workflow_id}. Ask me for the task or idea if it is not already clear."
    subprocess.run(["codex", *codex_options, prompt], cwd=target, shell=False, check=False)
