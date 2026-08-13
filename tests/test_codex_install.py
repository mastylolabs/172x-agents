import tomllib
from pathlib import Path

import pytest

from agent_workflows.codex import (
    active_workflow,
    configured_integration_current,
    install_codex,
    install_configured_codex,
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
    skill_paths = sorted((tmp_path / ".agents/skills").glob("172x-*/SKILL.md"))
    direct_skills = [path for path in skill_paths if path.parent.name != "172x-agents"]
    workflow_skills = [
        path
        for path in direct_skills
        if path.parent.name
        in {"172x-dev", "172x-dev-loop", "172x-idea-to-build", "172x-idea-to-product"}
    ]
    assert len(direct_skills) == 21
    assert len(workflow_skills) == 4
    assert (
        (tmp_path / ".agents/skills/172x-brief-author/agents/openai.yaml")
        .read_text(encoding="utf-8")
        .startswith("interface:\n")
    )
    brief_skill = (tmp_path / ".agents/skills/172x-brief-author/SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "references/agents/product/brief-author.md" in brief_skill
    assert "Resolve any `references/` or `assets/` path" in brief_skill
    assert "Run the `dev-loop` workflow" in (
        tmp_path / ".agents/skills/172x-dev-loop/SKILL.md"
    ).read_text(encoding="utf-8")
    assert (
        tmp_path / ".agents/skills/172x-agents/references/platform/architecture-patterns.md"
    ).is_file()
    assert (
        tmp_path / ".agents/skills/172x-agents/assets/platform/system-context-template.mmd"
    ).is_file()


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


def test_force_refresh_removes_renamed_managed_agent_files(tmp_path: Path) -> None:
    legacy_skill = tmp_path / ".agents/skills/172x-brief/SKILL.md"
    legacy_skill.parent.mkdir(parents=True)
    legacy_skill.write_text("old managed skill\n", encoding="utf-8")
    legacy_toml = tmp_path / ".codex/agents/172x-brief.toml"
    legacy_toml.parent.mkdir(parents=True)
    legacy_toml.write_text('name = "old"\n', encoding="utf-8")

    with pytest.raises(LibraryError, match="172x-brief"):
        install_codex(tmp_path)

    install_codex(tmp_path, force=True)

    assert not legacy_skill.exists()
    assert not legacy_toml.exists()
    assert (tmp_path / ".agents/skills/172x-brief-author/SKILL.md").is_file()


def test_install_projects_a_valid_custom_workflow_as_a_native_skill(tmp_path: Path) -> None:
    workflow = tmp_path / ".172x/workflows/customer-feedback.md"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        """---
id: customer-feedback
name: Customer Feedback Workflow
description: Turns validated customer feedback into independently reviewed fixes.
version: 1
---
## Purpose
Turn validated feedback into a reviewable fix.

## Inputs
Customer feedback, repository context, and acceptance criteria.

## Participating agents
- `discovery-specialist`
- `principal-engineer`
- `qa-engineer`
- `pr-reviewer`

## Flow
1. `discovery-specialist` bounds the reported problem.
2. `principal-engineer` implements the agreed fix.
3. `qa-engineer` verifies the acceptance criteria.
4. `pr-reviewer` returns a local recommendation for the human.

## Parallel work
No work is parallel because each handoff is required.

## Feedback loops
QA or review evidence returns to `principal-engineer` at most twice.

## Human gates
The human approves proceeding after discovery and decides whether to merge.

## Completion criteria
The scope, implementation, QA evidence, review recommendation, and human decision exist.

## Failure and escalation
Stop for the human when feedback is ambiguous or two return cycles are exhausted.
""",
        encoding="utf-8",
    )

    install_codex(tmp_path)

    skill = (tmp_path / ".agents/skills/172x-customer-feedback/SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "# 172X · Customer Feedback" in skill
    assert "references/workflows/custom/customer-feedback.md" in skill
    assert (
        tmp_path / ".agents/skills/172x-agents/references/workflows/custom/customer-feedback.md"
    ).is_file()
    assert (tmp_path / ".agents/skills/172x-workflow-composer/SKILL.md").is_file()
