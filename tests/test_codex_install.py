import re
from pathlib import Path

import pytest

from agent_workflows.codex import (
    active_workflow,
    install_codex,
    installed_capability_ids,
    integration_current,
    managed_files,
    select_workflow,
    uninstall_codex,
)
from agent_workflows.library import LibraryError

SUPPORT_PATH = re.compile(
    r"(?<![a-z0-9_./-])"
    r"((?:references|assets)/(?:[a-z0-9][a-z0-9.-]*/)*"
    r"[a-z0-9][a-z0-9.-]*\.(?:md|mmd|toml|yaml))"
)


def test_global_install_is_idempotent_and_leaves_project_files_alone(tmp_path: Path) -> None:
    home = tmp_path / "codex-home"
    unrelated = home / "config.toml"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text("model = 'example'\n", encoding="utf-8")

    first = install_codex(home)
    second = install_codex(home)

    assert all(action == "CREATE" for action, _, _ in first)
    assert all(action == "UNCHANGED" for action, _, _ in second)
    assert unrelated.read_text(encoding="utf-8") == "model = 'example'\n"
    assert integration_current(home)
    assert len(installed_capability_ids(home)) == 21
    assert all((home / relative).is_file() for relative in managed_files())
    assert not (home / "agents").exists()
    assert (home / "skills/172x-principal-architect/SKILL.md").is_file()
    assert "172x-agents/references/agents/platform/principal-architect.md" in (
        home / "skills/172x-principal-architect/SKILL.md"
    ).read_text(encoding="utf-8")
    for workflow_id in ("dev", "dev-loop", "idea-to-build", "idea-to-product"):
        assert (home / f"skills/172x-agents/references/workflows/{workflow_id}.md").is_file()
    for support_path in (
        "references/common/evidence-and-uncertainty.md",
        "references/design/ux-ui-definition-of-done.md",
        "references/platform/change-discipline.md",
        "references/quality/review-findings.md",
        "references/security/threat-modeling.md",
        "assets/design/ux-ui-spec-template.md",
        "assets/quality/qa-report-template.md",
        "assets/security/threat-model-template.md",
    ):
        assert (home / "skills/172x-agents" / support_path).is_file()
    _assert_support_paths_are_closed(managed_files())


def test_focused_global_install_is_current_for_its_selected_capability(tmp_path: Path) -> None:
    home = tmp_path / "codex-home"

    install_codex(home, only=("principal-codebase-reviewer",))

    assert installed_capability_ids(home) == ("principal-codebase-reviewer",)


def test_global_install_dry_run_does_not_write_even_when_codex_home_is_absent(
    tmp_path: Path,
) -> None:
    home = tmp_path / "missing-codex-home"

    plan = install_codex(home, dry_run=True)

    assert plan
    assert not home.exists()


def test_focused_global_install_includes_only_selected_capability_and_shared_support(
    tmp_path: Path,
) -> None:
    home = tmp_path / "codex-home"

    install_codex(home, only=("principal-codebase-reviewer",))

    assert (home / "skills/172x-principal-codebase-reviewer/SKILL.md").is_file()
    assert not (home / "skills/172x-principal-engineer").exists()
    assert (
        home / "skills/172x-agents/references/agents/quality/principal-codebase-reviewer.md"
    ).is_file()
    assert (home / "skills/172x-agents/references/quality/testing-strategy.md").is_file()
    assert (home / "skills/172x-agents/references/platform/architecture-patterns.md").is_file()
    assert not (home / "skills/172x-agents/references/product/market-research-evidence.md").exists()
    assert not (home / "skills/172x-agents/references/security/threat-modeling.md").exists()
    assert not (home / "skills/172x-agents/references/workflows").exists()
    assert not (home / "skills/172x-agents/assets/design/ux-ui-spec-template.md").exists()
    assert not (home / "agents").exists()


@pytest.mark.parametrize("capability_id", ["principal-codebase-reviewer", "ux-ui-designer"])
def test_focused_agent_install_is_exact_idempotent_and_path_closed(
    tmp_path: Path, capability_id: str
) -> None:
    home = tmp_path / "codex-home"
    unrelated = home / "skills/unrelated/SKILL.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text("keep\n", encoding="utf-8")

    expected = managed_files(only=(capability_id,))
    first = install_codex(home, only=(capability_id,))
    second = install_codex(home, only=(capability_id,))

    installed = {
        path.relative_to(home) for path in home.rglob("*") if path.is_file() and path != unrelated
    }
    assert installed == set(expected)
    assert all(action == "CREATE" for action, _, _ in first)
    assert all(action == "UNCHANGED" for action, _, _ in second)
    assert unrelated.read_text(encoding="utf-8") == "keep\n"
    _assert_support_paths_are_closed(expected)


def test_focused_workflow_includes_its_declared_specialist_skills(tmp_path: Path) -> None:
    home = tmp_path / "codex-home"

    install_codex(home, only=("dev-loop",))

    for agent_id in ("brief-author", "principal-engineer", "qa-engineer", "pr-reviewer"):
        assert (home / "skills" / f"172x-{agent_id}/SKILL.md").is_file()
    assert (home / "skills/172x-dev-loop/SKILL.md").is_file()
    assert (home / "skills/172x-agents/references/workflows/dev-loop.md").is_file()
    assert not (home / "skills/172x-agents/references/workflows/dev.md").exists()
    assert not (home / "skills/172x-security-reviewer").exists()
    assert not (
        home / "skills/172x-agents/references/agents/security/security-reviewer.md"
    ).exists()
    assert not (home / "skills/172x-agents/references/security/threat-modeling.md").exists()
    _assert_support_paths_are_closed(managed_files(only=("dev-loop",)))


def test_focused_workflow_dry_run_is_exact_and_writes_nothing(tmp_path: Path) -> None:
    home = tmp_path / "missing-codex-home"

    plan = install_codex(home, only=("dev",), dry_run=True)

    assert {path for _, path, _ in plan} == set(managed_files(only=("dev",)))
    assert not home.exists()


def test_full_to_focused_reconciles_exact_managed_closure_and_preserves_unknown_files(
    tmp_path: Path,
) -> None:
    home = tmp_path / "codex-home"
    install_codex(home)
    unrelated = home / "skills/172x-principal-engineer/notes.md"
    unrelated.write_text("keep\n", encoding="utf-8")
    expected = managed_files(only=("ux-ui-designer",))

    dry_run = install_codex(home, only=("ux-ui-designer",), dry_run=True)

    assert any(action == "DELETE" for action, _, _ in dry_run)
    assert _installed_known_files(home) == set(managed_files())
    assert unrelated.read_text(encoding="utf-8") == "keep\n"

    install_codex(home, only=("ux-ui-designer",))
    repeated = install_codex(home, only=("ux-ui-designer",))

    assert _installed_known_files(home) == set(expected)
    assert all(
        (home / relative).read_bytes() == contents for relative, contents in expected.items()
    )
    assert unrelated.read_text(encoding="utf-8") == "keep\n"
    assert all(action == "UNCHANGED" for action, _, _ in repeated)


def test_focused_selection_reconciles_from_one_agent_to_another(tmp_path: Path) -> None:
    home = tmp_path / "codex-home"
    install_codex(home, only=("principal-codebase-reviewer",))
    unrelated = home / "skills/unrelated/SKILL.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text("keep\n", encoding="utf-8")
    expected = managed_files(only=("ux-ui-designer",))

    install_codex(home, only=("ux-ui-designer",))

    assert _installed_known_files(home) == set(expected)
    assert not (home / "skills/172x-principal-codebase-reviewer/SKILL.md").exists()
    assert unrelated.read_text(encoding="utf-8") == "keep\n"
    _assert_support_paths_are_closed(expected)


def test_modified_stale_file_conflicts_until_force_explicitly_removes_it(
    tmp_path: Path,
) -> None:
    home = tmp_path / "codex-home"
    install_codex(home, only=("principal-codebase-reviewer",))
    modified = home / "skills/172x-principal-codebase-reviewer/SKILL.md"
    modified.write_text("user modification\n", encoding="utf-8")
    unrelated = modified.parent / "notes.md"
    unrelated.write_text("keep\n", encoding="utf-8")

    with pytest.raises(LibraryError, match="172x-principal-codebase-reviewer/SKILL.md"):
        install_codex(home, only=("ux-ui-designer",))

    assert modified.read_text(encoding="utf-8") == "user modification\n"
    assert not (home / "skills/172x-ux-ui-designer").exists()

    dry_run = install_codex(home, only=("ux-ui-designer",), force=True, dry_run=True)

    assert ("DELETE", Path("skills/172x-principal-codebase-reviewer/SKILL.md"), b"") in dry_run
    assert modified.read_text(encoding="utf-8") == "user modification\n"

    install_codex(home, only=("ux-ui-designer",), force=True)

    assert _installed_known_files(home) == set(managed_files(only=("ux-ui-designer",)))
    assert not modified.exists()
    assert unrelated.read_text(encoding="utf-8") == "keep\n"


def test_global_install_conflicts_are_all_or_nothing_and_force_is_namespaced(
    tmp_path: Path,
) -> None:
    home = tmp_path / "codex-home"
    conflicting = home / "skills/172x-agents/SKILL.md"
    conflicting.parent.mkdir(parents=True)
    conflicting.write_text("user content\n", encoding="utf-8")
    unrelated = home / "skills/other/SKILL.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text("keep\n", encoding="utf-8")

    with pytest.raises(LibraryError, match="conflicts"):
        install_codex(home)

    assert conflicting.read_text(encoding="utf-8") == "user content\n"
    install_codex(home, force=True)
    assert conflicting.read_text(encoding="utf-8") != "user content\n"
    assert unrelated.read_text(encoding="utf-8") == "keep\n"


def test_global_install_refuses_managed_path_symlinks(tmp_path: Path) -> None:
    home = tmp_path / "codex-home"
    outside = tmp_path / "outside"
    home.mkdir()
    outside.mkdir()
    (home / "skills").symlink_to(outside, target_is_directory=True)

    with pytest.raises(LibraryError, match="conflicts"):
        install_codex(home)

    assert list(outside.iterdir()) == []


def test_global_uninstall_removes_only_known_forge_skills_and_dry_run_is_safe(
    tmp_path: Path,
) -> None:
    home = tmp_path / "codex-home"
    unrelated = home / "skills/another-skill/SKILL.md"
    unrelated.parent.mkdir(parents=True)
    unrelated.write_text("keep\n", encoding="utf-8")
    install_codex(home)

    dry_run = uninstall_codex(home, dry_run=True)

    assert any(
        action == "DELETE" and path == Path("skills/172x-agents") for action, path, _ in dry_run
    )
    assert (home / "skills/172x-principal-architect/SKILL.md").is_file()

    uninstall_codex(home)

    assert unrelated.read_text(encoding="utf-8") == "keep\n"
    assert not (home / "skills/172x-agents").exists()
    assert not (home / "skills/172x-principal-architect").exists()


def test_global_uninstall_can_target_one_capability_and_refuses_modified_skill(
    tmp_path: Path,
) -> None:
    home = tmp_path / "codex-home"
    install_codex(home)

    uninstall_codex(home, only=("principal-architect",))

    assert not (home / "skills/172x-principal-architect").exists()
    assert (home / "skills/172x-agents/SKILL.md").is_file()
    modified = home / "skills/172x-principal-engineer/SKILL.md"
    modified.write_text("modified\n", encoding="utf-8")

    with pytest.raises(LibraryError, match="uninstall has conflicts"):
        uninstall_codex(home, only=("principal-engineer",))

    uninstall_codex(home, only=("principal-engineer",), force=True)

    assert not modified.exists()


def test_workflow_selection_uses_global_install_and_local_selection_state(
    monkeypatch, tmp_path: Path
) -> None:
    home = tmp_path / "codex-home"
    project = tmp_path / "project"
    project.mkdir()
    monkeypatch.setenv("CODEX_HOME", str(home))

    with pytest.raises(LibraryError, match="agents install codex"):
        select_workflow(project, "dev")

    install_codex(home)
    path = select_workflow(project, "dev")

    assert path.read_text(encoding="utf-8") == "dev\n"
    assert active_workflow(project) == "dev"


def test_workflow_selection_keeps_local_state_out_of_git_status(
    monkeypatch, tmp_path: Path
) -> None:
    home = tmp_path / "codex-home"
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").mkdir()
    monkeypatch.setenv("CODEX_HOME", str(home))
    install_codex(home)
    monkeypatch.setattr("agent_workflows.profiles.shutil.which", lambda value: "/usr/bin/git")
    monkeypatch.setattr(
        "agent_workflows.profiles.subprocess.run",
        lambda *_args, **_kwargs: type(
            "Result", (), {"returncode": 0, "stdout": ".git/info/exclude\n"}
        )(),
    )

    select_workflow(project, "dev")

    assert (project / ".git/info/exclude").read_text(encoding="utf-8") == ".172x/\n"


def _assert_support_paths_are_closed(files: dict[Path, bytes]) -> None:
    support_root = Path("skills/172x-agents")
    for relative, contents in files.items():
        if relative.suffix not in {".md", ".mmd", ".toml", ".yaml"}:
            continue
        for support_path in SUPPORT_PATH.findall(contents.decode("utf-8")):
            assert support_root / support_path in files, (relative, support_path)


def _installed_known_files(home: Path) -> set[Path]:
    return {relative for relative in managed_files() if (home / relative).is_file()}
