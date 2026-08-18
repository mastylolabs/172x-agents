"""Local, advisory 172X activation contexts and gate diagnostics."""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
import tomllib
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from .library import LibraryError

CONTEXT_PATH = Path(".172x/contexts.toml")
SUPPORTED_HOST = "codex"
SUPPORTED_LANGUAGE = "python"
SUPPORTED_SCM = "git"
SUPPORTED_PROVIDER = "github"
PLANNED_HOSTS = ("claude", "gemini")
PLANNED_LANGUAGES = ("c++", "java", "c#", "rust", "typescript")
PLANNED_PROVIDERS = ("gitlab", "bitbucket")


@dataclass(frozen=True)
class ProjectProfile:
    """The selected local language and quality contract for one project path."""

    host: str
    language: str
    scm: str
    provider: str
    gate_tools: tuple[str, ...]
    change_request_kind: str
    base_branch: str
    merge_method: str
    merge_current_branch: bool


@dataclass(frozen=True)
class ActivationContext:
    """One local activation entry rooted at a repository-relative path."""

    path: Path
    profile: ProjectProfile


def _resource_text(parts: tuple[str, ...]) -> str:
    resource = resources.files("agent_workflows").joinpath("library", *parts)
    return resource.read_text(encoding="utf-8")


def _language_data(language: str) -> dict[str, object]:
    try:
        parsed = tomllib.loads(_resource_text(("profiles", "languages", f"{language}.toml")))
    except FileNotFoundError as error:
        raise LibraryError(capability_message("language", language)) from error
    if not isinstance(parsed, dict):
        raise LibraryError(f"invalid bundled language profile: {language}")
    return parsed


def language_tools(language: str) -> tuple[str, ...]:
    """Return the supported named gate tools for one implemented language profile."""
    data = _language_data(language)
    tools = data.get("gate_tools")
    if not isinstance(tools, list) or not all(isinstance(tool, str) for tool in tools):
        raise LibraryError(f"invalid bundled language profile: {language}")
    return tuple(tools)


def gate_commands(profile: ProjectProfile) -> tuple[tuple[str, ...], ...]:
    """Return fixed argument-list gate commands for the selected local contract."""
    data = _language_data(profile.language)
    commands: list[tuple[str, ...]] = []
    for tool in profile.gate_tools:
        value = data.get(tool)
        if not isinstance(value, dict):
            raise LibraryError(f"invalid bundled language profile tool: {tool}")
        command = value.get("command")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(part, str) for part in command)
        ):
            raise LibraryError(f"invalid bundled language profile command: {tool}")
        commands.append(tuple(command))
    return tuple(commands)


def language_runner(target: Path, profile: ProjectProfile) -> tuple[str, ...]:
    """Recognize a project's runner without installing or selecting its package manager."""
    project = target.expanduser().resolve()
    if profile.language != "python":
        return ()
    if (project / "uv.lock").is_file():
        return ("uv", "run", "--no-sync")
    if (project / "poetry.lock").is_file():
        return ("poetry", "run")
    return ()


def active_gate_commands(target: Path, profile: ProjectProfile) -> tuple[tuple[str, ...], ...]:
    """Return selected fixed gate commands prefixed only by a detected existing runner."""
    runner = language_runner(target, profile)
    return tuple((*runner, *command) for command in gate_commands(profile))


def gate_probe_commands(target: Path, profile: ProjectProfile) -> tuple[tuple[str, ...], ...]:
    """Return lightweight non-mutating availability probes for selected gate tools."""
    runner = language_runner(target, profile)
    return tuple((*runner, tool, "--version") for tool in profile.gate_tools)


def capability_message(kind: str, value: str) -> str:
    """Explain the supported first release without presenting planned work as usable."""
    planned = {
        "host": PLANNED_HOSTS,
        "language": PLANNED_LANGUAGES,
        "provider": PLANNED_PROVIDERS,
    }.get(kind, ())
    if value in planned:
        supported = {
            "host": SUPPORTED_HOST,
            "language": SUPPORTED_LANGUAGE,
            "provider": SUPPORTED_PROVIDER,
        }
        return f"{kind} '{value}' is planned but not implemented; supported {kind}: {supported.get(kind, 'none')}"
    return f"unsupported {kind}: {value}"


def validate_profile(profile: ProjectProfile) -> None:
    """Reject unsupported activation choices and arbitrary gate commands."""
    if profile.host != SUPPORTED_HOST:
        raise LibraryError(capability_message("host", profile.host))
    if profile.language != SUPPORTED_LANGUAGE:
        raise LibraryError(capability_message("language", profile.language))
    if profile.scm != SUPPORTED_SCM:
        raise LibraryError("unsupported SCM: git is the only supported SCM")
    if profile.provider != SUPPORTED_PROVIDER:
        raise LibraryError(capability_message("provider", profile.provider))
    supported_tools = set(language_tools(profile.language))
    if not profile.gate_tools or len(set(profile.gate_tools)) != len(profile.gate_tools):
        raise LibraryError("gate tools must be a non-empty set of unique supported tool IDs")
    unknown_tools = [tool for tool in profile.gate_tools if tool not in supported_tools]
    if unknown_tools:
        raise LibraryError(
            f"unsupported {profile.language} gate tool(s): {', '.join(unknown_tools)}"
        )
    if profile.change_request_kind != "pull_request" or profile.base_branch != "main":
        raise LibraryError(
            "the supported GitHub change-request policy is pull requests targeting main"
        )
    if profile.merge_method not in {"merge", "rebase", "squash"}:
        raise LibraryError("change-request merge_method must be merge, rebase, or squash")


def default_profile(
    *,
    host: str = SUPPORTED_HOST,
    language: str = SUPPORTED_LANGUAGE,
    gate_tools: tuple[str, ...] | None = None,
) -> ProjectProfile:
    """Build the supported local activation selection without modifying external tools."""
    profile = ProjectProfile(
        host=host,
        language=language,
        scm=SUPPORTED_SCM,
        provider=SUPPORTED_PROVIDER,
        gate_tools=gate_tools if gate_tools is not None else language_tools(language),
        change_request_kind="pull_request",
        base_branch="main",
        merge_method="squash",
        merge_current_branch=True,
    )
    validate_profile(profile)
    return profile


def _context_path_value(path: Path) -> str:
    return "." if path == Path(".") else path.as_posix()


def _toml_string(value: str) -> str:
    """Encode one TOML basic string with the compatible stdlib JSON encoder."""
    return json.dumps(value, ensure_ascii=False)


def contexts_toml(contexts: tuple[ActivationContext, ...]) -> bytes:
    """Render local-only activation data in a deliberately small stable TOML format."""
    if not contexts:
        raise LibraryError("at least one local activation context is required")
    lines = [
        "# Local 172X activation state. This file is intentionally ignored by Git.\n",
        "version = 1\n",
    ]
    for context in contexts:
        validate_profile(context.profile)
        if context.path.is_absolute() or ".." in context.path.parts:
            raise LibraryError(
                "activation paths must be repository-relative and must not contain '..'"
            )
        tools = ", ".join(_toml_string(tool) for tool in context.profile.gate_tools)
        lines.extend(
            (
                "\n[[contexts]]\n",
                f"path = {_toml_string(_context_path_value(context.path))}\n",
                f"language = {_toml_string(context.profile.language)}\n",
                f"gates = [{tools}]\n",
            )
        )
    return "".join(lines).encode()


def _parse_contexts(path: Path) -> tuple[ActivationContext, ...]:
    if not path.is_file() or path.is_symlink():
        raise LibraryError(f"172X activation is missing: {path}")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise LibraryError(f"invalid 172X activation: {path}") from error
    if set(data) != {"version", "contexts"} or data.get("version") != 1:
        raise LibraryError(
            ".172x/contexts.toml must contain only version = 1 and [[contexts]] entries"
        )
    entries = data.get("contexts")
    if not isinstance(entries, list) or not entries:
        raise LibraryError(".172x/contexts.toml must contain at least one [[contexts]] entry")
    contexts: list[ActivationContext] = []
    seen: set[Path] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "language", "gates"}:
            raise LibraryError("each 172X context must contain only path, language, and gates")
        raw_path = entry.get("path")
        language = entry.get("language")
        gates = entry.get("gates")
        if not isinstance(raw_path, str) or not raw_path:
            raise LibraryError("172X context path must be a non-empty relative path")
        relative = Path(raw_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise LibraryError(
                "172X context path must be repository-relative and must not contain '..'"
            )
        relative = Path(".") if raw_path == "." else relative
        if relative in seen:
            raise LibraryError(f"duplicate 172X activation context path: {relative}")
        if (
            not isinstance(language, str)
            or not isinstance(gates, list)
            or not all(isinstance(gate, str) for gate in gates)
        ):
            raise LibraryError("172X context language and gates are invalid")
        profile = default_profile(language=language, gate_tools=tuple(gates))
        contexts.append(ActivationContext(path=relative, profile=profile))
        seen.add(relative)
    return tuple(contexts)


def load_contexts(root: Path) -> tuple[ActivationContext, ...]:
    """Load local activation contexts from one selected repository root."""
    return _parse_contexts(root.expanduser().resolve() / CONTEXT_PATH)


def _activation_root_and_relative(target: Path) -> tuple[Path, Path]:
    project = target.expanduser().resolve()
    if not project.is_dir():
        raise LibraryError(f"target project is not a directory: {target}")
    for root in (project, *project.parents):
        activation = root / CONTEXT_PATH
        if activation.exists():
            return root, project.relative_to(root)
    raise LibraryError("172X activation is missing; run: agents activate python")


def load_profile(target: Path) -> ProjectProfile:
    """Load the activation context that exactly matches a selected project directory."""
    root, relative = _activation_root_and_relative(target)
    for context in load_contexts(root):
        if context.path == relative:
            return context.profile
    raise LibraryError(
        f"no 172X activation context matches {relative.as_posix() or '.'}; run: agents activate python"
    )


def write_activation(
    root: Path,
    relative: Path,
    profile: ProjectProfile,
    *,
    dry_run: bool = False,
    force: bool = False,
) -> tuple[str, Path]:
    """Create or replace one explicit local activation without touching dependency files."""
    workspace = root.expanduser().resolve()
    if not workspace.is_dir():
        raise LibraryError(f"activation root is not a directory: {root}")
    if relative.is_absolute() or ".." in relative.parts:
        raise LibraryError("activation path must be repository-relative and must not contain '..'")
    context_path = Path(".") if relative == Path(".") else relative
    if not (workspace / context_path).is_dir():
        raise LibraryError(f"activation target is not a directory: {context_path}")
    validate_profile(profile)
    destination = workspace / CONTEXT_PATH
    if destination.is_symlink() or (
        destination.parent.exists() and destination.parent.is_symlink()
    ):
        raise LibraryError(f"172X activation path must not be a symlink: {destination}")
    contexts = list(_parse_contexts(destination)) if destination.exists() else []
    index = next(
        (item for item, context in enumerate(contexts) if context.path == context_path), None
    )
    replacement = ActivationContext(path=context_path, profile=profile)
    if index is not None:
        if contexts[index] == replacement:
            return "UNCHANGED", CONTEXT_PATH
        if not force:
            raise LibraryError(
                f"172X activation already exists for {context_path}; rerun with --force to replace it"
            )
        contexts[index] = replacement
        action = "REPLACE"
    else:
        contexts.append(replacement)
        action = "CREATE"
    contents = contexts_toml(tuple(contexts))
    if dry_run:
        return action, CONTEXT_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(contents)
    return action, CONTEXT_PATH


def ensure_activation_is_locally_ignored(
    root: Path, *, dry_run: bool = False
) -> tuple[str, Path] | None:
    """Add only `.172x/` to this repository's local Git exclude file when available."""
    workspace = root.expanduser().resolve()
    if shutil.which("git") is None:
        return None
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--git-path", "info/exclude"],
            cwd=workspace,
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    raw_path = completed.stdout.strip()
    if not raw_path:
        return None
    exclude = Path(raw_path)
    if not exclude.is_absolute():
        exclude = workspace / exclude
    exclude = exclude.resolve()
    existing = exclude.read_text(encoding="utf-8") if exclude.is_file() else ""
    if ".172x/" in {line.strip() for line in existing.splitlines()}:
        return "UNCHANGED", exclude
    if dry_run:
        return "CREATE" if not exclude.exists() else "UPDATE", exclude
    exclude.parent.mkdir(parents=True, exist_ok=True)
    suffix = "" if not existing or existing.endswith("\n") else "\n"
    exclude.write_text(f"{existing}{suffix}.172x/\n", encoding="utf-8")
    return "CREATE" if not existing else "UPDATE", exclude


def detected_platform() -> str:
    """Return the host platform label used in capability diagnostics."""
    return "macos" if platform.system() == "Darwin" else platform.system().lower() or "unknown"


def _command_output(target: Path, arguments: tuple[str, ...]) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            list(arguments),
            cwd=target,
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    return completed.returncode == 0, completed.stdout or completed.stderr


def prerequisite_rows(target: Path, profile: ProjectProfile) -> tuple[tuple[str, bool, str], ...]:
    """Inspect configured gates and dev-loop prerequisites without changing local state."""
    project = target.expanduser().resolve()
    if not project.is_dir():
        return (("Target", False, f"not a directory: {target}"),)
    validate_profile(profile)
    rows: list[tuple[str, bool, str]] = []
    rows.append(
        (
            "Platform",
            detected_platform() == "macos",
            f"detected {detected_platform()}; macos is supported",
        )
    )
    rows.append(("Host executable", shutil.which(profile.host) is not None, profile.host))
    for tool, command in zip(
        profile.gate_tools, gate_probe_commands(project, profile), strict=True
    ):
        ok, _ = _command_output(project, command)
        rows.append((f"Gate tool: {tool}", ok, " ".join(command)))
    git_available = shutil.which("git") is not None
    rows.append(("Git executable", git_available, "git"))
    git_repository = (
        git_available and _command_output(project, ("git", "rev-parse", "--is-inside-work-tree"))[0]
    )
    rows.append(("Git repository", git_repository, "working tree required for dev-loop"))
    gh_available = shutil.which("gh") is not None
    rows.append(("GitHub CLI", gh_available, "gh (needed only for dev-loop GitHub actions)"))
    rows.append(
        (
            "GitHub reviewer identity",
            False,
            "configure an eligible independent reviewer when branch rules require it",
        )
    )
    return tuple(rows)


def prerequisites_ok(rows: tuple[tuple[str, bool, str], ...]) -> bool:
    """Keep advisory doctor rows separate from an explicit dev-loop decision."""
    return all(ok for label, ok, _ in rows if label != "GitHub reviewer identity")


def capability_rows() -> tuple[tuple[str, str, str], ...]:
    """List real and planned extension points without treating planned as installable."""
    return (
        ("host", "codex", "supported"),
        *(("host", value, "planned") for value in PLANNED_HOSTS),
        ("language", "python", "supported"),
        *(("language", value, "planned") for value in PLANNED_LANGUAGES),
        ("scm", "git", "supported"),
        ("provider", "github", "supported"),
        *(("provider", value, "planned") for value in PLANNED_PROVIDERS),
        ("platform", "macos", "supported"),
        ("platform", "linux", "planned"),
        ("platform", "windows", "planned"),
    )
