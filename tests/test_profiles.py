from pathlib import Path

import pytest

from agent_workflows.library import LibraryError
from agent_workflows.profiles import (
    CONTEXT_PATH,
    active_gate_commands,
    capability_rows,
    default_profile,
    ensure_activation_is_locally_ignored,
    gate_probe_commands,
    load_contexts,
    load_profile,
    write_activation,
)


def test_activation_round_trips_as_ignored_local_context(tmp_path: Path) -> None:
    selected = default_profile(gate_tools=("ruff", "pytest"))

    action, path = write_activation(tmp_path, Path("."), selected)

    assert (action, path) == ("CREATE", CONTEXT_PATH)
    assert load_profile(tmp_path) == selected
    assert load_contexts(tmp_path)[0].path == Path(".")
    contents = (tmp_path / CONTEXT_PATH).read_text(encoding="utf-8")
    assert "intentionally ignored by Git" in contents
    assert 'gates = ["ruff", "pytest"]' in contents


def test_activation_supports_explicit_monorepo_project_paths(tmp_path: Path) -> None:
    package = tmp_path / "services" / "api"
    package.mkdir(parents=True)

    write_activation(tmp_path, Path("services/api"), default_profile(gate_tools=("ruff",)))

    assert load_profile(package).gate_tools == ("ruff",)
    with pytest.raises(LibraryError, match="no 172X activation context matches"):
        load_profile(tmp_path)


@pytest.mark.parametrize(
    "relative",
    (
        Path("services/api"),
        Path('services/quote"api'),
        Path(r"services/back\slash"),
    ),
)
def test_activation_toml_round_trips_repository_relative_paths(
    tmp_path: Path, relative: Path
) -> None:
    (tmp_path / relative).mkdir(parents=True)
    profile = default_profile(gate_tools=("ruff", "pytest"))

    write_activation(tmp_path, relative, profile)

    contexts = load_contexts(tmp_path)
    assert len(contexts) == 1
    assert contexts[0].path == relative
    assert contexts[0].profile == profile


@pytest.mark.parametrize("relative", (Path("../outside"), Path("/outside")))
def test_activation_still_rejects_traversal_and_absolute_paths(
    tmp_path: Path, relative: Path
) -> None:
    with pytest.raises(LibraryError, match="repository-relative.*must not contain"):
        write_activation(tmp_path, relative, default_profile(gate_tools=("ruff",)))


def test_activation_requires_explicit_force_for_a_changed_context(tmp_path: Path) -> None:
    write_activation(tmp_path, Path("."), default_profile(gate_tools=("ruff",)))

    with pytest.raises(LibraryError, match="rerun with --force"):
        write_activation(tmp_path, Path("."), default_profile(gate_tools=("pytest",)))

    action, _ = write_activation(
        tmp_path, Path("."), default_profile(gate_tools=("pytest",)), force=True
    )
    assert action == "REPLACE"
    assert load_profile(tmp_path).gate_tools == ("pytest",)


def test_activation_adds_only_a_local_git_exclude_entry(monkeypatch, tmp_path: Path) -> None:
    exclude = tmp_path / ".git" / "info" / "exclude"

    monkeypatch.setattr("agent_workflows.profiles.shutil.which", lambda value: "/usr/bin/git")
    monkeypatch.setattr(
        "agent_workflows.profiles.subprocess.run",
        lambda *_args, **_kwargs: type(
            "Result", (), {"returncode": 0, "stdout": ".git/info/exclude\n"}
        )(),
    )

    action, path = ensure_activation_is_locally_ignored(tmp_path) or (None, None)

    assert action == "CREATE"
    assert path == exclude.resolve()
    assert exclude.read_text(encoding="utf-8") == ".172x/\n"


def test_planned_language_is_not_activatable() -> None:
    with pytest.raises(LibraryError, match="planned but not implemented"):
        default_profile(language="rust")


def test_gate_commands_and_probes_use_existing_runner_without_installing(tmp_path: Path) -> None:
    (tmp_path / "uv.lock").write_text("version = 1\n", encoding="utf-8")
    profile = default_profile(gate_tools=("ruff", "pytest"))

    assert active_gate_commands(tmp_path, profile) == (
        ("uv", "run", "--no-sync", "ruff", "check", "."),
        ("uv", "run", "--no-sync", "pytest"),
    )
    assert gate_probe_commands(tmp_path, profile) == (
        ("uv", "run", "--no-sync", "ruff", "--version"),
        ("uv", "run", "--no-sync", "pytest", "--version"),
    )
    assert ("language", "rust", "planned") in capability_rows()
