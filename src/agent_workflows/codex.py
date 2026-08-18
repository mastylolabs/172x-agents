"""Deterministic global Codex skill installation helpers."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Literal

from .library import LibraryError, LibraryItem, find_item, load_library
from .profiles import ensure_activation_is_locally_ignored

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
_SUPPORT_PATH = re.compile(
    r"(?<![a-z0-9_./-])"
    r"((?:references|assets)/(?:[a-z0-9][a-z0-9.-]*/)*"
    r"[a-z0-9][a-z0-9.-]*\.(?:md|mmd|toml|yaml))"
)


def _resource_bytes(parts: tuple[str, ...]) -> bytes:
    resource = resources.files("agent_workflows").joinpath("library", *parts)
    return resource.read_bytes()


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
        f"`$CODEX_HOME/skills/172x-agents/references/agents/{agent.relative_path}` completely and apply its "
        "instructions to the user's current request. Resolve any `references/` or `assets/` path named "
        "there within `$CODEX_HOME/skills/172x-agents/`. Deliver that specialist's observable result and "
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
    """Return a compact native-picker label for one bundled workflow."""
    return workflow_skill_title(workflow.id)


def _workflow_skill(workflow: LibraryItem) -> bytes:
    """Render a one-click native Codex workflow skill that uses the shared coordinator."""
    title = _workflow_title(workflow)
    skill_name = f"172x-{workflow.id}"
    return (
        f"---\nname: {skill_name}\ndescription: {json.dumps(f'172X {title}: {workflow.description}')}\n---\n\n"
        f"# 172X · {title}\n\n"
        f"Run the `{workflow.id}` workflow for the user's current task. Before any delegation, read "
        "`$CODEX_HOME/skills/172x-agents/SKILL.md` and then read "
        f"`$CODEX_HOME/skills/172x-agents/references/workflows/{workflow.relative_path}` completely. Apply the "
        "coordinator rules and execute this selected workflow immediately; do not ask the user to "
        "choose a workflow again. If the task or idea is missing, ask for it before delegation.\n"
    ).encode()


def _copy_resource_tree(resource: Traversable, destination: Path) -> dict[Path, bytes]:
    """Copy one complete bundled resource tree for a full installation."""
    files: dict[Path, bytes] = {}
    for source in resource.iterdir():
        if source.is_dir():
            files.update(_copy_resource_tree(source, destination / source.name))
        elif source.is_file():
            files[destination / source.name] = source.read_bytes()
    return files


def _support_paths(body: str) -> set[Path]:
    """Return explicit rooted reference and asset paths from canonical Markdown."""
    return {Path(match) for match in _SUPPORT_PATH.findall(body)}


def _transitive_support_files(items: list[LibraryItem], destination: Path) -> dict[Path, bytes]:
    """Resolve the deterministic reference/asset closure for a focused installation."""
    pending = sorted(
        {path for item in items for path in _support_paths(item.body)},
        key=lambda path: path.as_posix(),
    )
    visited: set[Path] = set()
    files: dict[Path, bytes] = {}
    while pending:
        relative = pending.pop(0)
        if relative in visited:
            continue
        if relative.parts[0] not in {"references", "assets"}:
            raise LibraryError(f"unsupported installed support path: {relative.as_posix()}")
        try:
            contents = _resource_bytes(relative.parts)
        except (FileNotFoundError, IsADirectoryError) as error:
            raise LibraryError(
                f"canonical support path does not resolve: {relative.as_posix()}"
            ) from error
        try:
            body = contents.decode("utf-8")
        except UnicodeDecodeError as error:
            raise LibraryError(
                f"canonical support path is not UTF-8 text: {relative.as_posix()}"
            ) from error
        files[destination / relative] = contents
        visited.add(relative)
        discovered = _support_paths(body) - visited - set(pending)
        pending.extend(discovered)
        pending.sort(key=lambda path: path.as_posix())
    return files


def _workflow_agent_ids(workflow: LibraryItem) -> set[str]:
    """Return the canonical role IDs declared by one workflow without interpreting its flow."""
    match = re.search(
        r"^## Participating agents\s*$([\s\S]*?)(?=^## |\Z)", workflow.body, re.MULTILINE
    )
    return set(re.findall(r"`([a-z0-9-]+)`", match.group(1) if match else ""))


def _selected_library_items(
    target: Path | None, only: tuple[str, ...]
) -> tuple[list[LibraryItem], list[LibraryItem]]:
    """Resolve a focused global install into bundled capabilities and workflow dependencies."""
    agents = load_library("agents")
    workflows = load_library("workflows")
    if not only:
        return agents, workflows

    agents_by_id = {agent.id: agent for agent in agents}
    workflows_by_id = {workflow.id: workflow for workflow in workflows}
    selected_agents: set[str] = set()
    selected_workflows: set[str] = set()
    unknown: list[str] = []
    for item_id in dict.fromkeys(only):
        if item_id in agents_by_id:
            selected_agents.add(item_id)
        elif item_id in workflows_by_id:
            selected_workflows.add(item_id)
        else:
            unknown.append(item_id)
    if unknown:
        available = ", ".join([*agents_by_id, *workflows_by_id])
        raise LibraryError(
            f"unknown 172X capability ID: {', '.join(unknown)}; available: {available}"
        )
    for workflow_id in selected_workflows:
        selected_agents.update(_workflow_agent_ids(workflows_by_id[workflow_id]))
    return (
        [agent for agent in agents if agent.id in selected_agents],
        [workflow for workflow in workflows if workflow.id in selected_workflows],
    )


def _workflow_composer_skill() -> bytes:
    """Render the direct native skill that authors project-owned workflow Markdown."""
    return b"""---
name: 172x-workflow-composer
description: Create or revise a project-owned 172X workflow from the installed role catalog without adding a workflow runtime.
---

# 172X \xc2\xb7 Workflow Composer

Create a reviewable project-owned workflow, not an executable workflow engine.

1. Read `$CODEX_HOME/skills/172x-agents/SKILL.md`, then inspect `$CODEX_HOME/skills/172x-agents/references/agents/` to select only shipped roles needed for the user's goal.
2. Propose a concise flow with required handoffs, safe parallel work, feedback limits, and explicit human gates. Do not let an implementation role approve its own work. Do not invent agents, external actions, or a runtime.
3. Before writing, show the user the proposed workflow ID, title, participating roles, flow, feedback loops, and human gates. Require explicit approval when overwriting an existing project workflow.
4. After approval, create one Markdown file at `.172x/workflows/<workflow-id>.md`, using `$CODEX_HOME/skills/172x-agents/assets/workflows/custom-workflow-template.md`. The ID must be lowercase kebab-case and unique across bundled and project workflows. Fill every required section with concrete content.
5. Validate the result with `agents workflows --target .` and inspect it with `agents show <workflow-id> --target .`. In v0.1, project-owned workflows are local authoring, listing, and inspection material only; they are not selectable or runnable through the global Codex skills.

Never write bundled library files, `.codex/config.toml`, credentials, or arbitrary workflow graphs. Do not activate, run, or claim a picker entry for the project-owned workflow.
"""


def managed_files(target: Path | None = None, only: tuple[str, ...] = ()) -> dict[Path, bytes]:
    """Return every owned global Codex skill path and its expected bytes."""
    agents, workflows = _selected_library_items(target, only)
    skill_root = Path("skills")
    files: dict[Path, bytes] = {
        skill_root / "172x-agents/SKILL.md": _resource_bytes(("codex", "SKILL.md")),
        skill_root / "172x-agents/agents/openai.yaml": _resource_bytes(
            ("codex", "agents", "openai.yaml")
        ),
    }
    if not only:
        composer_root = skill_root / "172x-workflow-composer"
        files[composer_root / "SKILL.md"] = _workflow_composer_skill()
        files[composer_root / "agents/openai.yaml"] = _skill_metadata(
            "172X · Workflow Composer",
            "Compose a project-owned workflow from the installed 172X roles.",
            "Create a 172X workflow for the current project.",
        )
    for agent in agents:
        files[skill_root / "172x-agents/references/agents" / agent.relative_path] = _resource_bytes(
            ("agents", *Path(agent.relative_path).parts)
        )
    for workflow in workflows:
        files[skill_root / "172x-agents/references/workflows" / workflow.relative_path] = (
            _resource_bytes(("workflows", *Path(workflow.relative_path).parts))
        )
    if only:
        files.update(_transitive_support_files([*agents, *workflows], skill_root / "172x-agents"))
    else:
        reference_root = resources.files("agent_workflows").joinpath("library", "references")
        files.update(_copy_resource_tree(reference_root, skill_root / "172x-agents/references"))
        asset_root = resources.files("agent_workflows").joinpath("library", "assets")
        files.update(_copy_resource_tree(asset_root, skill_root / "172x-agents/assets"))
    for agent in agents:
        direct_root = skill_root / f"172x-{agent.id}"
        files[direct_root / "SKILL.md"] = _agent_skill(agent)
        files[direct_root / "agents/openai.yaml"] = _skill_metadata(
            f"172X · {agent.name.removesuffix(' Agent')}",
            agent.description,
            f"Use the 172X {agent.name.removesuffix(' Agent')} specialist for this task.",
        )
    for workflow in workflows:
        direct_root = skill_root / f"172x-{workflow.id}"
        title = _workflow_title(workflow)
        files[direct_root / "SKILL.md"] = _workflow_skill(workflow)
        files[direct_root / "agents/openai.yaml"] = _skill_metadata(
            f"172X · {title}",
            workflow.description,
            f"Run the 172X {title} workflow for the current task.",
        )
    return dict(sorted(files.items(), key=lambda item: item[0].as_posix()))


def _target_directory(target: Path, *, allow_missing: bool = False) -> Path:
    resolved = target.expanduser().resolve()
    if resolved.exists() and not resolved.is_dir():
        raise LibraryError(f"target project is not a directory: {target}")
    if not resolved.exists() and not allow_missing:
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
    target = _target_directory(target, allow_missing=True)
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


def _stale_managed_plan(
    target: Path,
    desired: dict[Path, bytes],
    known: dict[Path, bytes],
    *,
    force: bool = False,
) -> list[tuple[Action, Path, bytes]]:
    """Plan removal of known canonical files excluded by the new selection."""
    target = _target_directory(target, allow_missing=True)
    plan: list[tuple[Action, Path, bytes]] = []
    for relative in sorted(known.keys() - desired.keys(), key=Path.as_posix):
        canonical_contents = known[relative]
        try:
            destination = _safe_destination(target, relative)
        except LibraryError:
            plan.append(("CONFLICT", relative, b""))
            continue
        if not destination.exists():
            continue
        if not destination.is_file():
            plan.append(("CONFLICT", relative, b""))
        elif destination.read_bytes() == canonical_contents or force:
            plan.append(("DELETE", relative, b""))
        else:
            plan.append(("CONFLICT", relative, b""))
    return plan


def _prune_empty_managed_parents(target: Path, deleted: list[Path]) -> None:
    """Remove only empty directories below a deleted `skills/172x-*` file."""
    for relative in deleted:
        current = relative.parent
        while (
            len(current.parts) >= 2
            and current.parts[0] == "skills"
            and current.parts[1].startswith("172x-")
        ):
            destination = _safe_destination(target, current)
            try:
                destination.rmdir()
            except FileNotFoundError:
                pass
            except OSError:
                break
            current = current.parent


def _renamed_agent_paths() -> tuple[Path, ...]:
    """Return former global skill paths removed during an explicit refresh."""
    paths: list[Path] = []
    for agent_id in _RENAMED_AGENT_IDS:
        paths.extend(
            (
                Path("skills") / f"172x-{agent_id}" / "SKILL.md",
                Path("skills") / f"172x-{agent_id}" / "agents/openai.yaml",
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


def install_plan(
    target: Path, force: bool = False, only: tuple[str, ...] = ()
) -> list[tuple[Action, Path, bytes]]:
    """Return the Codex installation plan for compatibility with the public API."""
    desired = managed_files(target, only)
    plan = _install_plan(target, desired, force=force)
    plan.extend(_stale_managed_plan(target, desired, managed_files(target), force=force))
    return plan


def install_codex(
    target: Path, dry_run: bool = False, force: bool = False, only: tuple[str, ...] = ()
) -> list[tuple[Action, Path, bytes]]:
    """Plan first, then write only owned paths when the complete plan is safe."""
    target = _target_directory(target, allow_missing=True)
    plan = install_plan(target, force=force, only=only)
    if any(action == "CONFLICT" for action, _, _ in plan):
        raise _conflict_error(plan)
    if dry_run:
        return plan
    deleted: list[Path] = []
    for action, relative, contents in plan:
        if action == "UNCHANGED":
            continue
        destination = _safe_destination(target, relative)
        if action == "DELETE":
            destination.unlink()
            deleted.append(relative)
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(contents)
    _prune_empty_managed_parents(target, deleted)
    return plan


def _uninstall_roots(only: tuple[str, ...]) -> tuple[Path, ...]:
    """Return exact global Forge skill directories owned by an uninstall request."""
    direct_ids = {
        *(agent.id for agent in load_library("agents")),
        *(workflow.id for workflow in load_library("workflows")),
        "workflow-composer",
    }
    unknown = [item_id for item_id in dict.fromkeys(only) if item_id not in direct_ids]
    if unknown:
        available = ", ".join(sorted(direct_ids))
        raise LibraryError(
            f"unknown 172X capability ID: {', '.join(unknown)}; available: {available}"
        )
    selected = tuple(dict.fromkeys(only)) if only else tuple(sorted(direct_ids))
    roots = [Path("skills") / f"172x-{item_id}" for item_id in selected]
    if not only:
        roots.insert(0, Path("skills/172x-agents"))
    return tuple(roots)


def _managed_root_is_safe(target: Path, root: Path, expected: dict[Path, bytes]) -> bool:
    """Accept only an unmodified, non-symlinked directory made of known Forge files."""
    destination = _safe_destination(target, root)
    if not destination.is_dir() or destination.is_symlink():
        return False
    for path in destination.rglob("*"):
        if path.is_symlink() or path.is_dir():
            if path.is_symlink():
                return False
            continue
        relative = path.relative_to(target)
        if (
            not path.is_file()
            or relative not in expected
            or path.read_bytes() != expected[relative]
        ):
            return False
    return True


def uninstall_plan(
    target: Path, force: bool = False, only: tuple[str, ...] = ()
) -> list[tuple[Action, Path, bytes]]:
    """Plan removal of exact Forge skill roots without touching other Codex skills."""
    target = _target_directory(target, allow_missing=True)
    expected = managed_files()
    plan: list[tuple[Action, Path, bytes]] = []
    for root in _uninstall_roots(only):
        try:
            destination = _safe_destination(target, root)
        except LibraryError:
            plan.append(("CONFLICT", root, b""))
            continue
        if not destination.exists():
            plan.append(("UNCHANGED", root, b""))
        elif destination.is_symlink() or not destination.is_dir():
            plan.append(("CONFLICT", root, b""))
        elif _managed_root_is_safe(target, root, expected) or force:
            plan.append(("DELETE", root, b""))
        else:
            plan.append(("CONFLICT", root, b""))
    return plan


def uninstall_codex(
    target: Path, dry_run: bool = False, force: bool = False, only: tuple[str, ...] = ()
) -> list[tuple[Action, Path, bytes]]:
    """Remove global Forge skills while preserving unrelated Codex content."""
    target = _target_directory(target, allow_missing=True)
    plan = uninstall_plan(target, force=force, only=only)
    if any(action == "CONFLICT" for action, _, _ in plan):
        conflicts = ", ".join(path.as_posix() for action, path, _ in plan if action == "CONFLICT")
        raise LibraryError(
            "uninstall has conflicts in managed paths: "
            + conflicts
            + "; rerun with --force only if removing those exact 172X skill directories is intended"
        )
    if dry_run:
        return plan
    for action, root, _ in plan:
        if action == "DELETE":
            shutil.rmtree(_safe_destination(target, root))
    return plan


def integration_current(target: Path) -> bool:
    try:
        return all(action == "UNCHANGED" for action, _, _ in install_plan(target))
    except LibraryError:
        return False


def installed_capability_ids(target: Path) -> tuple[str, ...]:
    """Return current globally installed direct capabilities, including valid focused installs."""
    try:
        home = _target_directory(target)
        coordinator = managed_files(only=("principal-architect",))[
            Path("skills/172x-agents/SKILL.md")
        ]
        coordinator_path = home / "skills/172x-agents/SKILL.md"
        if (
            not coordinator_path.is_file()
            or coordinator_path.is_symlink()
            or coordinator_path.read_bytes() != coordinator
        ):
            return ()
        current: list[str] = []
        for item in (*load_library("agents"), *load_library("workflows")):
            relative = Path("skills") / f"172x-{item.id}" / "SKILL.md"
            expected = managed_files(only=(item.id,))[relative]
            installed = home / relative
            if (
                installed.is_file()
                and not installed.is_symlink()
                and installed.read_bytes() == expected
            ):
                current.append(item.id)
        return tuple(current)
    except LibraryError:
        return ()


def workflow_integration_current(target: Path, workflow_id: str) -> bool:
    """Return whether one installed workflow and its declared roles are current.

    A focused installation deliberately owns only the selected workflow and the
    specialists it names. A complete installation also satisfies this subset.
    """
    try:
        files = managed_files(only=(workflow_id,))
        return all(action == "UNCHANGED" for action, _, _ in _install_plan(target, files))
    except LibraryError:
        return False


def default_codex_home() -> Path:
    """Return Codex's user-level state directory without modifying its configuration."""
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def select_workflow(target: Path, workflow_id: str) -> Path:
    """Persist one validated bundled workflow ID; this is selection, not run state."""
    target = _target_directory(target)
    find_item("workflows", workflow_id)
    if not workflow_integration_current(default_codex_home(), workflow_id):
        raise LibraryError("Codex integration is not current; run: agents install codex")
    relative = Path(".172x/active-workflow")
    destination = _safe_destination(target, relative)
    ensure_activation_is_locally_ignored(target)
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
        find_item("workflows", value[:-1])
    except LibraryError:
        return None
    return value[:-1]


def launch_codex(target: Path, workflow_id: str, codex_options: tuple[str, ...] = ()) -> None:
    """Launch Codex with a validated workflow prompt and user-supplied CLI options."""
    if shutil.which("codex") is None:
        raise FileNotFoundError("The 'codex' executable was not found on PATH.")
    prompt = f"$172x-{workflow_id}. Ask me for the task or idea if it is not already clear."
    subprocess.run(["codex", *codex_options, prompt], cwd=target, shell=False, check=False)
