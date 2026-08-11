import tomllib
from pathlib import Path

import pytest

from agent_workflows.codex import (
    active_workflow,
    configured_integration_current,
    install_configured_codex,
    install_codex,
    managed_files,
    select_workflow,
)
from agent_workflows.library import LibraryError
from agent_workflows.profiles import default_profile


def test_install_generates_parseable_toml_and_is_idempotent(tmp_path: Path) -> None:
    unrelated = tmp_path / ".codex" / "keep.toml"
    unrelated.parent.mkdir()
    unrelated.write_text("keep = true\n", encoding="utf-8")

    first = install_codex(tmp_path)
    second = install_codex(tmp_path)

    assert all(action == "CREATE" for action, _, _ in first)
    assert all(action == "UNCHANGED" for action, _, _ in second)
    assert unrelated.read_text(encoding="utf-8") == "keep = true\n"
    for relative in managed_files():
        assert (tmp_path / relative).is_file()
    for path in (tmp_path / ".codex/agents").glob("172x-*.toml"):
        parsed = tomllib.loads(path.read_text(encoding="utf-8"))
        assert set(parsed) == {"name", "description", "developer_instructions"}
        assert parsed["developer_instructions"].startswith("## Domain\n")
        assert "\\n" not in path.read_text(encoding="utf-8")


def test_dry_run_does_not_write(tmp_path: Path) -> None:
    plan = install_codex(tmp_path, dry_run=True)

    assert plan
    assert not (tmp_path / ".agents").exists()
    assert not (tmp_path / ".codex").exists()


def test_conflicts_are_all_or_nothing_and_force_is_managed_only(tmp_path: Path) -> None:
    conflicting = tmp_path / ".agents/skills/172x-agents/SKILL.md"
    conflicting.parent.mkdir(parents=True)
    conflicting.write_text("user content\n", encoding="utf-8")
    unrelated = tmp_path / ".agents/skills/other/SKILL.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text("keep\n", encoding="utf-8")

    with pytest.raises(LibraryError, match="conflicts"):
        install_codex(tmp_path)

    assert conflicting.read_text(encoding="utf-8") == "user content\n"
    assert not (tmp_path / ".codex/agents").exists()
    install_codex(tmp_path, force=True)
    assert conflicting.read_text(encoding="utf-8") != "user content\n"
    assert unrelated.read_text(encoding="utf-8") == "keep\n"


def test_workflow_selection_requires_current_installation(tmp_path: Path) -> None:
    with pytest.raises(LibraryError, match="agents install codex"):
        select_workflow(tmp_path, "dev")

    install_configured_codex(tmp_path, default_profile())
    path = select_workflow(tmp_path, "dev")

    assert path.read_text(encoding="utf-8") == "dev\n"
    assert active_workflow(tmp_path) == "dev"


def test_install_refuses_managed_path_symlinks(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_path / ".agents").symlink_to(outside, target_is_directory=True)

    with pytest.raises(LibraryError, match="conflicts"):
        install_codex(tmp_path)

    assert list(outside.iterdir()) == []


def test_configured_install_owns_profile_as_well_as_codex_files(tmp_path: Path) -> None:
    first = install_configured_codex(tmp_path, default_profile())
    second = install_configured_codex(tmp_path, default_profile())

    assert all(action == "CREATE" for action, _, _ in first)
    assert all(action == "UNCHANGED" for action, _, _ in second)
    assert configured_integration_current(tmp_path)
    (tmp_path / "172x.toml").write_text("user configuration\n", encoding="utf-8")
    assert not configured_integration_current(tmp_path)
    with pytest.raises(LibraryError, match="conflicts in managed paths.*172x.toml"):
        install_configured_codex(tmp_path, default_profile())
