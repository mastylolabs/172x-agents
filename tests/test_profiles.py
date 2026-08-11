from pathlib import Path

import pytest

from agent_workflows.library import LibraryError
from agent_workflows.profiles import (
    PYPI_SIMPLE_INDEX,
    active_gate_commands,
    capability_rows,
    default_profile,
    gate_install_command,
    gate_commands,
    gate_tools_declared,
    load_profile,
    project_toml,
)


def test_project_profile_round_trips_with_selected_gate_tools(tmp_path: Path) -> None:
    selected = default_profile(gate_tools=("ruff", "pytest"))
    (tmp_path / "172x.toml").write_bytes(project_toml(selected))

    loaded = load_profile(tmp_path)

    assert loaded == selected
    assert gate_commands(loaded) == (("ruff", "check", "."), ("pytest",))
    assert ("host", "codex", "supported") in capability_rows()
    assert ("provider", "bitbucket", "planned") in capability_rows()


def test_profile_rejects_planned_language_without_making_it_selectable() -> None:
    with pytest.raises(LibraryError, match="planned but not implemented"):
        default_profile(language="rust")


def test_python_gate_commands_reuse_the_repository_runner(tmp_path: Path) -> None:
    (tmp_path / "uv.lock").write_text("version = 1\n", encoding="utf-8")

    commands = active_gate_commands(tmp_path, default_profile(gate_tools=("ruff", "pytest")))

    assert commands == (("uv", "run", "ruff", "check", "."), ("uv", "run", "pytest"))


def test_python_gate_install_uses_uv_for_a_project_with_a_pyproject(monkeypatch, tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname = 'example'\n", encoding="utf-8")
    monkeypatch.setattr("agent_workflows.profiles.shutil.which", lambda value: "/usr/local/bin/uv")

    command = gate_install_command(tmp_path, default_profile(gate_tools=("mypy", "radon")))

    assert command == ("uv", "add", "--dev", "--default-index", PYPI_SIMPLE_INDEX, "mypy", "radon")


def test_declared_gate_tools_are_not_reinstalled(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'example'\n\n[dependency-groups]\ndev = ['mypy>=1', 'ruff', 'radon', 'pytest']\n",
        encoding="utf-8",
    )

    assert gate_tools_declared(tmp_path, default_profile())


def test_gate_install_refuses_to_resolve_an_unrelated_parent_uv_workspace(
    monkeypatch, tmp_path: Path
) -> None:
    project = tmp_path / "sandbox" / "playground"
    project.mkdir(parents=True)
    project_pyproject = project / "pyproject.toml"
    project_pyproject.write_text("[project]\nname = 'playground'\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        "[tool.uv.workspace]\nmembers = ['sandbox/playground']\n", encoding="utf-8"
    )
    monkeypatch.setattr("agent_workflows.profiles.shutil.which", lambda value: "/usr/local/bin/uv")

    with pytest.raises(LibraryError, match="UV workspace member"):
        gate_install_command(project, default_profile())
