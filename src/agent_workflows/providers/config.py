"""Local provider and merge configuration loading for one Git checkout."""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

from ..library import LibraryError
from .contracts import MergePolicy, ProviderFamily, ProviderKey

_PROJECT_CONFIG = Path("172x.toml")
_LOCAL_CONFIG = Path("172x/config.toml")
_MERGE_METHODS = {"merge", "rebase", "squash"}
_ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _toml_string(value: str) -> str:
    """Encode a TOML basic string with the standard-library JSON encoder."""
    return json.dumps(value, ensure_ascii=False)


def _linked_worktree_metadata(entry: Path, repository_root: Path) -> Path | None:
    """Resolve a worktree .git pointer without following untrusted symlink entries."""
    if entry.is_symlink() or not entry.is_file():
        return None
    try:
        marker = entry.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not marker.startswith("gitdir:"):
        return None
    raw_path = marker.removeprefix("gitdir:").strip()
    if not raw_path:
        return None
    git_directory = Path(raw_path)
    if not git_directory.is_absolute():
        git_directory = repository_root / git_directory
    if git_directory.is_dir() and not git_directory.is_symlink():
        return git_directory.resolve()
    return None


def _git_metadata_directory(project: Path) -> Path | None:
    """Find the nearest repository metadata directory, including linked worktrees."""
    for candidate in (project, *project.parents):
        entry = candidate / ".git"
        if entry.is_dir() and not entry.is_symlink():
            return entry.resolve()
        linked = _linked_worktree_metadata(entry, candidate)
        if linked is not None:
            return linked
    return None


def local_project_config_path(target: Path) -> Path | None:
    """Return the repository-local 172X config path, if the target is in a Git checkout."""
    project = target.expanduser().resolve()
    if not project.is_dir():
        raise LibraryError(f"target project is not a directory: {target}")
    git_directory = _git_metadata_directory(project)
    return None if git_directory is None else git_directory / _LOCAL_CONFIG


def shared_project_config_path(target: Path) -> Path | None:
    """Find the legacy root config retained for backwards compatibility."""
    project = target.expanduser().resolve()
    if not project.is_dir():
        raise LibraryError(f"target project is not a directory: {target}")
    for candidate in (project, *project.parents):
        path = candidate / _PROJECT_CONFIG
        if path.is_file() and not path.is_symlink():
            return path
    return None


def project_config_path(target: Path) -> Path | None:
    """Prefer local Git metadata, then fall back to the legacy root config."""
    local = local_project_config_path(target)
    if local is not None and local.is_file() and not local.is_symlink():
        return local
    return shared_project_config_path(target)


def render_local_project_config(
    *,
    provider_name: str,
    base_branch: str,
    merge_method: str,
    reviewer_login: str,
    token_env: str,
) -> bytes:
    """Render the non-secret local provider configuration collected by activation."""
    normalized_provider = provider_name.strip().casefold()
    normalized_branch = base_branch.strip()
    normalized_method = merge_method.strip().casefold()
    normalized_login = reviewer_login.strip()
    normalized_token_env = token_env.strip()
    if not normalized_provider:
        raise LibraryError("source-control provider must be a non-empty string")
    if not normalized_branch:
        raise LibraryError("merge base branch must be a non-empty string")
    if normalized_method not in _MERGE_METHODS:
        raise LibraryError("merge method must be merge, rebase, or squash")
    if not normalized_login:
        raise LibraryError("reviewer login must be a non-empty string")
    if not _ENVIRONMENT_NAME.fullmatch(normalized_token_env):
        raise LibraryError("reviewer token environment variable is invalid")
    lines = (
        "# Local 172X provider configuration. This file lives under .git and is not committed.\n",
        "\n[provider]\n",
        'family = "source_control"\n',
        f"name = {_toml_string(normalized_provider)}\n",
        "\n[merge]\n",
        f"base_branch = {_toml_string(normalized_branch)}\n",
        f"method = {_toml_string(normalized_method)}\n",
        "merge_current_branch = true\n",
        f"\n[{normalized_provider}.review]\n",
        f"\n[[{normalized_provider}.review.reviewers]]\n",
        f"login = {_toml_string(normalized_login)}\n",
        f"token_env = {_toml_string(normalized_token_env)}\n",
    )
    return "".join(lines).encode("utf-8")


def _migrate_legacy_config(path: Path) -> bytes:
    """Keep legacy values while replacing repository-oriented comments for local storage."""
    try:
        contents = path.read_text(encoding="utf-8")
    except OSError as error:
        raise LibraryError(f"could not read legacy project configuration: {path}") from error
    body = "\n".join(line for line in contents.splitlines() if not line.lstrip().startswith("#"))
    return (
        "# Local 172X provider configuration migrated from legacy project settings.\n\n"
        f"{body.rstrip()}\n"
    ).encode()


def _validate_local_config_destination(destination: Path) -> None:
    """Reject symlinked or non-regular local configuration destinations."""
    if destination.is_symlink() or (
        destination.parent.exists() and destination.parent.is_symlink()
    ):
        raise LibraryError(f"172X provider config path must not be a symlink: {destination}")
    if destination.exists() and not destination.is_file():
        raise LibraryError(f"172X provider config path is not a regular file: {destination}")


def _local_config_contents(
    target: Path,
    destination: Path,
    *,
    provider_name: str,
    base_branch: str,
    merge_method: str,
    reviewer_login: str,
    token_env: str,
) -> bytes:
    """Choose migrated legacy bytes or render a new local configuration."""
    legacy = shared_project_config_path(target)
    if legacy is not None and legacy != destination:
        return _migrate_legacy_config(legacy)
    return render_local_project_config(
        provider_name=provider_name,
        base_branch=base_branch,
        merge_method=merge_method,
        reviewer_login=reviewer_login,
        token_env=token_env,
    )


def write_local_project_config(
    target: Path,
    *,
    provider_name: str = "github",
    base_branch: str = "main",
    merge_method: str = "squash",
    reviewer_login: str = "172x-reviewer-bot",
    token_env: str = "REVIEWER_GH_TOKEN",
    dry_run: bool = False,
    force: bool = False,
) -> tuple[str, Path | None]:
    """Create local Git config, migrating a legacy root config when one exists."""
    destination = local_project_config_path(target)
    if destination is None:
        return "SKIPPED", None
    _validate_local_config_destination(destination)
    existed = destination.exists()
    if existed and not force:
        return "UNCHANGED", destination
    contents = _local_config_contents(
        target,
        destination,
        provider_name=provider_name,
        base_branch=base_branch,
        merge_method=merge_method,
        reviewer_login=reviewer_login,
        token_env=token_env,
    )
    if dry_run:
        return "REPLACE" if existed else "CREATE", destination
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(contents)
    return "REPLACE" if existed else "CREATE", destination


def project_config(target: Path) -> dict[str, Any]:
    """Load project configuration without interpreting provider-specific sections."""
    path = project_config_path(target)
    if path is None:
        return {}
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise LibraryError(f"invalid project configuration: {path}") from error
    if not isinstance(data, dict):
        raise LibraryError(f"invalid project configuration: {path}")
    return data


def selected_source_control_provider(target: Path) -> ProviderKey:
    """Resolve the configured source-control provider with GitHub compatibility fallback."""
    data = project_config(target)
    provider = data.get("provider")
    if provider is None:
        return ProviderKey(ProviderFamily.SOURCE_CONTROL, "github")
    if not isinstance(provider, dict):
        raise LibraryError("local 172X config [provider] must be a table")
    family = provider.get("family", ProviderFamily.SOURCE_CONTROL.value)
    name = provider.get("name", provider.get("id"))
    if not isinstance(family, str) or not family.strip():
        raise LibraryError("local 172X config [provider].family must be a non-empty string")
    if not isinstance(name, str) or not name.strip():
        raise LibraryError("local 172X config [provider].name must be a non-empty string")
    try:
        provider_family = ProviderFamily(family.strip().casefold())
    except ValueError as error:
        raise LibraryError(f"unsupported provider family: {family}") from error
    if provider_family is not ProviderFamily.SOURCE_CONTROL:
        raise LibraryError("source-control operations require [provider].family = 'source_control'")
    return ProviderKey(provider_family, name)


def configured_merge_policy(
    target: Path,
    *,
    fallback_base_branch: str,
    fallback_merge_method: str,
    merge_current_branch: bool,
) -> MergePolicy:
    """Load explicit repository merge policy while preserving v0.1 profile defaults."""
    data = project_config(target)
    merge = data.get("merge")
    if merge is None:
        legacy_change_request = data.get("change_request")
        merge = legacy_change_request if isinstance(legacy_change_request, dict) else None
    if merge is None:
        return MergePolicy(
            base_branch=fallback_base_branch,
            merge_method=fallback_merge_method,
            merge_current_branch=merge_current_branch,
        )
    if not isinstance(merge, dict):
        raise LibraryError("local 172X config [merge] must be a table")
    base_branch = merge.get("base_branch", fallback_base_branch)
    method = merge.get("method", merge.get("merge_method", fallback_merge_method))
    configured_current_branch = merge.get("merge_current_branch", merge_current_branch)
    if not isinstance(base_branch, str) or not base_branch.strip():
        raise LibraryError("local 172X config [merge].base_branch must be a non-empty string")
    normalized_method = method.strip().casefold() if isinstance(method, str) else ""
    if normalized_method not in _MERGE_METHODS:
        raise LibraryError("local 172X config [merge].method must be merge, rebase, or squash")
    if not isinstance(configured_current_branch, bool):
        raise LibraryError("local 172X config [merge].merge_current_branch must be a boolean")
    return MergePolicy(
        base_branch=base_branch.strip(),
        merge_method=normalized_method,
        merge_current_branch=configured_current_branch,
    )
