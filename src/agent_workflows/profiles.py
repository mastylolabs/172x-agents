"""Supported 172X project profiles and their committed configuration."""

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

CONFIG_PATH = Path("172x.toml")
SUPPORTED_HOST = "codex"
SUPPORTED_LANGUAGE = "python"
SUPPORTED_SCM = "git"
SUPPORTED_PROVIDER = "github"
PLANNED_HOSTS = ("claude", "gemini")
PLANNED_LANGUAGES = ("c++", "java", "c#", "rust")
PLANNED_PROVIDERS = ("gitlab", "bitbucket")
PYPI_SIMPLE_INDEX = "https://pypi.org/simple"


@dataclass(frozen=True)
class ProjectProfile:
    """The minimal project-owned choices that make a workflow reproducible."""

    host: str
    language: str
    scm: str
    provider: str
    gate_tools: tuple[str, ...]
    change_request_kind: str
    base_branch: str
    merge_method: str
    merge_current_branch: bool


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
    """Return safe argument-list gate commands selected by the active profile."""
    data = _language_data(profile.language)
    commands: list[tuple[str, ...]] = []
    for tool in profile.gate_tools:
        value = data.get(tool)
        if not isinstance(value, dict):
            raise LibraryError(f"invalid bundled language profile tool: {tool}")
        command = value.get("command")
        if not isinstance(command, list) or not command or not all(isinstance(part, str) for part in command):
            raise LibraryError(f"invalid bundled language profile command: {tool}")
        commands.append(tuple(command))
    return tuple(commands)


def language_runner(target: Path, profile: ProjectProfile) -> tuple[str, ...]:
    """Prefer the repository's existing Python command convention, when recognizable."""
    project = target.expanduser().resolve()
    if profile.language != "python":
        return ()
    if (project / "uv.lock").is_file():
        return ("uv", "run")
    if (project / "poetry.lock").is_file():
        return ("poetry", "run")
    if (project / "hatch.toml").is_file():
        return ("hatch", "run")
    pyproject = project / "pyproject.toml"
    if pyproject.is_file():
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            return ()
        if isinstance(data.get("tool"), dict) and "hatch" in data["tool"]:
            return ("hatch", "run")
    return ()


def uv_workspace_root(target: Path) -> Path | None:
    """Return a parent UV workspace that explicitly includes this project, if any."""
    project = target.expanduser().resolve()
    for candidate in (project, *project.parents):
        pyproject = candidate / "pyproject.toml"
        if not pyproject.is_file():
            continue
        try:
            data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError):
            continue
        tool = data.get("tool")
        uv = tool.get("uv") if isinstance(tool, dict) else None
        workspace = uv.get("workspace") if isinstance(uv, dict) else None
        members = workspace.get("members") if isinstance(workspace, dict) else None
        if candidate == project:
            if isinstance(members, list):
                return candidate
            continue
        if not isinstance(members, list) or not all(isinstance(member, str) for member in members):
            continue
        if any(member.resolve() == project for member in _workspace_members(candidate, members)):
            return candidate
    return None


def _workspace_members(root: Path, members: list[str]) -> tuple[Path, ...]:
    paths: list[Path] = []
    for pattern in members:
        paths.extend(root.glob(pattern))
    return tuple(paths)


def active_gate_commands(target: Path, profile: ProjectProfile) -> tuple[tuple[str, ...], ...]:
    """Return selected safe gate commands prefixed by the detected project runner."""
    runner = language_runner(target, profile)
    return tuple((*runner, *command) for command in gate_commands(profile))


def gate_install_command(target: Path, profile: ProjectProfile) -> tuple[str, ...]:
    """Return the safe project-local command that adds selected Python gate dependencies."""
    project = target.expanduser().resolve()
    workspace_root = uv_workspace_root(project)
    if workspace_root is not None and workspace_root != project:
        raise LibraryError(
            f"refusing to install gate tools because this project is a UV workspace member of {workspace_root}; "
            "UV would resolve that whole workspace. Move the playground outside the workspace or remove it from "
            "the parent [tool.uv.workspace].members list, then retry."
        )
    runner = language_runner(project, profile)
    if runner[:1] == ("uv",):
        return ("uv", "add", "--dev", "--default-index", PYPI_SIMPLE_INDEX, *profile.gate_tools)
    if runner[:1] == ("poetry",):
        return ("poetry", "add", "--group", "dev", *profile.gate_tools)
    if profile.language == "python" and (project / "pyproject.toml").is_file() and shutil.which("uv"):
        return ("uv", "add", "--dev", "--default-index", PYPI_SIMPLE_INDEX, *profile.gate_tools)
    raise LibraryError(
        "cannot safely install selected Python gate tools: use an existing uv or Poetry project, "
        "or add the tools through this repository's package manager first"
    )


def gate_tools_declared(target: Path, profile: ProjectProfile) -> bool:
    """Return whether all selected Python gate tools are already project dependencies."""
    pyproject = target.expanduser().resolve() / "pyproject.toml"
    if not pyproject.is_file():
        return False
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return False

    declared: set[str] = set()

    def collect(values: object) -> None:
        if isinstance(values, list):
            for value in values:
                if isinstance(value, str):
                    declared.add(value.split(";", 1)[0].split("[", 1)[0].split("=", 1)[0].split(">", 1)[0].split("<", 1)[0].split("~", 1)[0].strip().casefold())

    project = data.get("project")
    if isinstance(project, dict):
        collect(project.get("dependencies"))
        optional = project.get("optional-dependencies")
        if isinstance(optional, dict):
            for values in optional.values():
                collect(values)
    groups = data.get("dependency-groups")
    if isinstance(groups, dict):
        for values in groups.values():
            collect(values)
    tool = data.get("tool")
    poetry = tool.get("poetry") if isinstance(tool, dict) else None
    if isinstance(poetry, dict):
        dev_dependencies = poetry.get("dev-dependencies")
        if isinstance(dev_dependencies, dict):
            declared.update(str(name).casefold() for name in dev_dependencies)
        poetry_groups = poetry.get("group")
        if isinstance(poetry_groups, dict):
            for group in poetry_groups.values():
                dependencies = group.get("dependencies") if isinstance(group, dict) else None
                if isinstance(dependencies, dict):
                    declared.update(str(name).casefold() for name in dependencies)

    return set(profile.gate_tools).issubset(declared)


def install_gate_tools(target: Path, profile: ProjectProfile) -> tuple[str, ...]:
    """Add the selected known gate tools through the repository's detected package manager."""
    project = target.expanduser().resolve()
    if gate_tools_declared(project, profile):
        return ()
    command = gate_install_command(project, profile)
    if shutil.which(command[0]) is None:
        raise LibraryError(f"required package manager is not on PATH: {command[0]}")
    try:
        completed = subprocess.run(
            command,
            cwd=project,
            shell=False,
            check=False,
            timeout=180,
        )
    except subprocess.TimeoutExpired as error:
        raise LibraryError(
            "timed out after 180 seconds while installing selected gate tools; check package-index access"
        ) from error
    if completed.returncode != 0:
        raise LibraryError(
            "could not install selected gate tools; see the package-manager output above for details"
        )
    return command


def capability_message(kind: str, value: str) -> str:
    """Explain the supported first release without presenting future work as usable."""
    planned = {
        "host": PLANNED_HOSTS,
        "language": PLANNED_LANGUAGES,
        "provider": PLANNED_PROVIDERS,
    }.get(kind, ())
    if value in planned:
        return f"{kind} '{value}' is planned but not implemented; supported {kind}: " + {
            "host": SUPPORTED_HOST,
            "language": SUPPORTED_LANGUAGE,
            "provider": SUPPORTED_PROVIDER,
        }.get(kind, "none")
    return f"unsupported {kind}: {value}"


def validate_profile(profile: ProjectProfile) -> None:
    """Reject any project profile that names an unsupported first-release capability."""
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
        raise LibraryError(f"unsupported {profile.language} gate tool(s): {', '.join(unknown_tools)}")
    if profile.change_request_kind != "pull_request":
        raise LibraryError("change-request kind must be pull_request for the GitHub provider")
    if profile.base_branch != "main":
        raise LibraryError("change-request base_branch must be main in the first release")
    if profile.merge_method not in {"merge", "rebase", "squash"}:
        raise LibraryError("change-request merge_method must be merge, rebase, or squash")


def default_profile(
    *,
    host: str = SUPPORTED_HOST,
    language: str = SUPPORTED_LANGUAGE,
    gate_tools: tuple[str, ...] | None = None,
) -> ProjectProfile:
    """Build the supported default selection for a new project."""
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


def project_toml(profile: ProjectProfile) -> bytes:
    """Render the sole committed project configuration in a stable reviewed form."""
    validate_profile(profile)
    tools = ", ".join(f'"{tool}"' for tool in profile.gate_tools)
    return (
        "# 172X project profile. Commit this file so the team runs the same loop.\n\n"
        "[host]\n"
        f'id = "{profile.host}"\n\n'
        "[language]\n"
        f'id = "{profile.language}"\n\n'
        "[scm]\n"
        f'id = "{profile.scm}"\n\n'
        "[provider]\n"
        f'id = "{profile.provider}"\n\n'
        "[gate]\n"
        f"tools = [{tools}]\n\n"
        "[change_request]\n"
        f'kind = "{profile.change_request_kind}"\n'
        f'base_branch = "{profile.base_branch}"\n'
        f'merge_method = "{profile.merge_method}"\n'
        f"merge_current_branch = {'true' if profile.merge_current_branch else 'false'}\n"
    ).encode()


def _table(data: dict[str, object], name: str) -> dict[str, object]:
    value = data.get(name)
    if not isinstance(value, dict):
        raise LibraryError(f"172x.toml must contain a [{name}] table")
    return value


def _string(table: dict[str, object], key: str, table_name: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value:
        raise LibraryError(f"172x.toml [{table_name}].{key} must be a non-empty string")
    return value


def load_profile(target: Path) -> ProjectProfile:
    """Load and validate the committed project profile without accepting extra policy."""
    project = target.expanduser().resolve()
    path = project / CONFIG_PATH
    if not path.is_file() or path.is_symlink():
        raise LibraryError("172X project profile is missing; run: agents install codex python")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise LibraryError(f"invalid 172X project profile: {path}") from error
    if set(data) != {"host", "language", "scm", "provider", "gate", "change_request"}:
        raise LibraryError("172x.toml must contain only the documented 172X profile tables")
    host = _table(data, "host")
    language = _table(data, "language")
    scm = _table(data, "scm")
    provider = _table(data, "provider")
    gate = _table(data, "gate")
    change_request = _table(data, "change_request")
    if set(host) != {"id"} or set(language) != {"id"} or set(scm) != {"id"} or set(provider) != {"id"}:
        raise LibraryError("host, language, scm, and provider tables must contain only id")
    if set(gate) != {"tools"}:
        raise LibraryError("gate table must contain only its documented fields")
    if set(change_request) != {"kind", "base_branch", "merge_method", "merge_current_branch"}:
        raise LibraryError("change_request table must contain only its documented fields")
    tools = gate.get("tools")
    if not isinstance(tools, list) or not all(isinstance(tool, str) for tool in tools):
        raise LibraryError("172x.toml [gate].tools must be an array of tool IDs")
    merge_current_branch = change_request.get("merge_current_branch")
    if not isinstance(merge_current_branch, bool):
        raise LibraryError("172x.toml [change_request].merge_current_branch must be true or false")
    profile = ProjectProfile(
        host=_string(host, "id", "host"),
        language=_string(language, "id", "language"),
        scm=_string(scm, "id", "scm"),
        provider=_string(provider, "id", "provider"),
        gate_tools=tuple(tools),
        change_request_kind=_string(change_request, "kind", "change_request"),
        base_branch=_string(change_request, "base_branch", "change_request"),
        merge_method=_string(change_request, "merge_method", "change_request"),
        merge_current_branch=merge_current_branch,
    )
    validate_profile(profile)
    return profile


def detected_platform() -> str:
    """Return the host platform label used in capability diagnostics."""
    return "macos" if platform.system() == "Darwin" else platform.system().lower() or "unknown"


def _command_output(target: Path, arguments: list[str]) -> tuple[bool, str]:
    completed = subprocess.run(
        arguments,
        cwd=target,
        shell=False,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0, completed.stdout


def prerequisite_rows(target: Path, profile: ProjectProfile) -> tuple[tuple[str, bool, str], ...]:
    """Inspect the real local prerequisites without changing project state."""
    project = target.expanduser().resolve()
    if not project.is_dir():
        return (("Target", False, f"not a directory: {target}"),)
    validate_profile(profile)
    rows: list[tuple[str, bool, str]] = []
    rows.append(("Platform", detected_platform() == "macos", f"detected {detected_platform()}; macos is supported"))
    rows.append(("Host executable", shutil.which(profile.host) is not None, profile.host))
    git_available = shutil.which("git") is not None
    rows.append(("Git executable", git_available, "git"))
    git_repository = git_available and _command_output(
        project, ["git", "rev-parse", "--is-inside-work-tree"]
    )[0]
    rows.append(("Git repository", git_repository, "working tree required"))
    remote_ok = git_repository and _command_output(project, ["git", "remote", "get-url", "origin"])[0]
    rows.append(("Git remote", remote_ok, "origin required"))
    gh_available = shutil.which("gh") is not None
    rows.append(("GitHub CLI", gh_available, "gh"))
    github_auth = gh_available and _command_output(project, ["gh", "auth", "status"])[0]
    rows.append(("GitHub authentication", github_auth, "authenticated gh account required"))
    permission_ok = False
    if github_auth:
        permission_ok, permission_output = _command_output(
            project, ["gh", "repo", "view", "--json", "viewerPermission"]
        )
        if permission_ok:
            try:
                permission = json.loads(permission_output).get("viewerPermission")
            except json.JSONDecodeError:
                permission = None
            permission_ok = permission in {"ADMIN", "MAINTAIN", "WRITE"}
    rows.append(
        (
            "GitHub repository permission",
            permission_ok,
            "write, maintain, or admin access required for branch and change-request actions",
        )
    )
    for tool, command in zip(profile.gate_tools, active_gate_commands(project, profile), strict=True):
        executable = command[0]
        rows.append((f"Gate tool: {tool}", shutil.which(executable) is not None, " ".join(command)))
    rows.append(
        (
            "GitHub reviewer identity",
            False,
            "configure an eligible independent reviewer bot or credential when branch rules require it",
        )
    )
    return tuple(rows)


def prerequisites_ok(rows: tuple[tuple[str, bool, str], ...]) -> bool:
    """Allow the manual reviewer-identity diagnostic without masking other setup failures."""
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
