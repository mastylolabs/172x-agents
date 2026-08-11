"""Deterministic project-scoped Codex installation helpers."""

from __future__ import annotations

import json
import shutil
import subprocess
from importlib import resources
from pathlib import Path
from typing import Literal

from .library import LibraryError, LibraryItem, find_item, library_directory, load_library
from .profiles import CONFIG_PATH, ProjectProfile, load_profile, project_toml

Action = Literal["CREATE", "UNCHANGED", "CONFLICT", "REPLACE"]


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


def managed_files() -> dict[Path, bytes]:
    """Return every owned installation path and its expected bytes."""
    files: dict[Path, bytes] = {
        Path(".agents/skills/172x-agents/SKILL.md"): _resource_bytes(("codex", "SKILL.md")),
        Path(".agents/skills/172x-agents/agents/openai.yaml"): _resource_bytes(
            ("codex", "agents", "openai.yaml")
        ),
    }
    for kind in ("agents", "workflows"):
        for source in library_directory(kind).iterdir():
            if source.name.endswith(".md"):
                files[Path(".agents/skills/172x-agents/references") / kind / source.name] = (
                    source.read_bytes()
                )
    for agent in load_library("agents"):
        files[Path(".codex/agents") / f"172x-{agent.id}.toml"] = codex_toml(agent)
    return dict(sorted(files.items(), key=lambda item: item[0].as_posix()))


def configured_codex_files(profile: ProjectProfile) -> dict[Path, bytes]:
    """Return the Codex installation plus its reviewed project profile."""
    files = managed_files()
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
    return plan


def _conflict_error(plan: list[tuple[Action, Path, bytes]]) -> LibraryError:
    """Name every managed conflict so a user can make an informed force decision."""
    conflicts = [path.as_posix() for action, path, _ in plan if action == "CONFLICT"]
    return LibraryError(
        "installation has conflicts in managed paths: "
        + ", ".join(conflicts)
        + "; rerun with --force only if replacing those 172X-managed files is intended"
    )


def install_plan(target: Path, force: bool = False) -> list[tuple[Action, Path, bytes]]:
    """Return the Codex installation plan for compatibility with the public API."""
    return _install_plan(target, managed_files(), force=force)


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
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(contents)
    return plan


def install_configured_codex(
    target: Path, profile: ProjectProfile, dry_run: bool = False, force: bool = False
) -> list[tuple[Action, Path, bytes]]:
    """Install Codex content and one project-owned 172X profile atomically by plan."""
    target = _target_directory(target)
    plan = _install_plan(target, configured_codex_files(profile), force=force)
    if any(action == "CONFLICT" for action, _, _ in plan):
        raise _conflict_error(plan)
    if dry_run:
        return plan
    for action, relative, contents in plan:
        if action == "UNCHANGED":
            continue
        destination = _safe_destination(target, relative)
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
            for action, _, _ in _install_plan(target, configured_codex_files(profile))
        )
    except LibraryError:
        return False


def select_workflow(target: Path, workflow_id: str) -> Path:
    """Persist one validated workflow ID; this is selection, not run state."""
    find_item("workflows", workflow_id)
    target = _target_directory(target)
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
        find_item("workflows", value[:-1])
    except LibraryError:
        return None
    return value[:-1]


def launch_codex(target: Path, workflow_id: str, codex_options: tuple[str, ...] = ()) -> None:
    """Launch Codex with a validated workflow prompt and user-supplied CLI options."""
    if shutil.which("codex") is None:
        raise FileNotFoundError("The 'codex' executable was not found on PATH.")
    prompt = (
        f"$172x run {workflow_id}. Ask me for the task or idea if it is not already clear."
    )
    subprocess.run(["codex", *codex_options, prompt], cwd=target, shell=False, check=False)
