from pathlib import Path

import pytest

from agent_workflows.library import (
    LibraryError,
    domains,
    find_item,
    load_workflows,
    parse_markdown,
    validate_library,
)


def test_bundled_library_validates() -> None:
    agents, workflows = validate_library()

    assert [agent.id for agent in agents] == sorted(agent.id for agent in agents)
    assert {workflow.id for workflow in workflows} == {
        "dev",
        "dev-loop",
        "idea-to-build",
        "idea-to-product",
    }
    assert len(agents) == 17
    assert all(workflow.version == 2 for workflow in workflows)


def test_domains_are_markdown_defined_and_cover_each_agent_once() -> None:
    grouped = domains()

    assert list(grouped) == ["Product", "Design", "Platform", "Quality", "Security"]
    assert [agent.id for agent in grouped["Product"]] == [
        "brief-author",
        "discovery-specialist",
        "market-researcher",
        "product-specification-specialist",
    ]
    assert [agent.id for agent in grouped["Quality"]] == [
        "backend-reviewer",
        "design-architecture-reviewer",
        "frontend-reviewer",
        "pr-reviewer",
        "principal-codebase-reviewer",
        "qa-engineer",
    ]
    assert [agent.id for agent in grouped["Security"]] == ["security-reviewer"]


def test_dev_loop_defines_the_experimental_guarded_handoff_contract() -> None:
    workflow = find_item("workflows", "dev-loop")

    assert "`brief-author`" in workflow.body
    assert "No change-request number is an input" in workflow.body
    assert "every tool selected in the active local context" in workflow.body
    assert "`MF` (Must Fix), `NH` (Nice to Have), or `Q`" in workflow.body
    assert "at most two review-return trips" in workflow.body
    assert "developer explicitly activates the current project locally" in workflow.body
    assert "`.172x/contexts.toml` activation entry" in workflow.body
    assert (
        "The current prompt-only coordinator does not yet guarantee exactly-once delegation or "
        "reliable bounded completion."
    ) in workflow.body
    assert "assets/quality/qa-report-template.md" in workflow.body
    assert "assets/quality/review-report-template.md" in workflow.body


def test_idea_to_product_has_a_bounded_implementation_feedback_loop() -> None:
    workflow = find_item("workflows", "idea-to-product")
    normalized = " ".join(workflow.body.split())

    assert "each QA, specialist-review, or PR-review return consumes one" in normalized
    assert "After three cycles, stop and escalate to the human" in normalized
    assert "without silently dropping or weakening criteria" in normalized


def test_codex_skill_prevents_duplicate_stage_delegations() -> None:
    from importlib import resources

    skill = resources.files("agent_workflows").joinpath("library", "codex", "SKILL.md").read_text()

    assert "Dispatch exactly one active delegation" in skill
    assert "Do not dispatch a second `brief-author` agent" in skill
    assert "`references/common/handoff-envelope.md`" in skill
    assert "## Evidence and uncertainty" in skill
    assert "## Decisions and residual risks" in skill
    assert "Human/external-action state" in skill
    assert (
        "The current prompt-only coordinator does not yet guarantee exactly-once delegation or "
        "reliable bounded completion."
    ) in skill
    assert "including `custom/`" not in skill
    assert "`use <workflow>`: Confirm the named bundled workflow" in skill


def test_codex_skill_exposes_the_172x_catalog_front_door() -> None:
    from importlib import resources

    skill = resources.files("agent_workflows").joinpath("library", "codex", "SKILL.md").read_text()

    assert "name: 172x" in skill
    assert "`list`: Read the installed references and show two compact catalogs" in skill
    assert "Run a workflow with: $172x run <workflow-id>" in skill


def test_principal_architect_has_pattern_guidance_and_mermaid_assets() -> None:
    from importlib import resources

    architect = find_item("agents", "principal-architect")
    patterns = (
        resources.files("agent_workflows")
        .joinpath("library", "references", "platform", "architecture-patterns.md")
        .read_text()
    )
    assert architect.relative_path == "platform/principal-architect.md"
    assert "architecture-patterns.md" in architect.body
    assert "system-context-template.mmd" in architect.body
    for pattern in ("Modular monolith", "Ports and adapters", "Pub/sub", "Event sourcing"):
        assert f"## {pattern}" in patterns
    assert (
        resources.files("agent_workflows")
        .joinpath("library", "assets", "platform", "event-flow-template.mmd")
        .is_file()
    )


def test_principal_codebase_reviewer_assesses_intent_and_determinism() -> None:
    reviewer = find_item("agents", "principal-codebase-reviewer")

    assert reviewer.relative_path == "quality/principal-codebase-reviewer.md"
    assert "intended-versus-actual behavior matrix" in reviewer.body
    assert "deterministic systems" in reviewer.body
    assert "Do not implement fixes" in reviewer.body


def test_project_workflow_rejects_reserved_skill_ids(tmp_path: Path) -> None:
    workflow = tmp_path / ".172x/workflows/invalid.md"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        """---
id: workflow-composer
name: Invalid Workflow
description: Invalid project workflow.
version: 1
---
## Purpose
Invalid.
## Inputs
Task.
## Participating agents
- `missing-agent`
## Flow
1. Invalid.
## Parallel work
None.
## Feedback loops
None.
## Human gates
Human decides.
## Completion criteria
Never.
## Failure and escalation
Stop.
""",
        encoding="utf-8",
    )

    with pytest.raises(LibraryError, match="reserved 172X skill"):
        load_workflows(tmp_path)


def test_project_workflow_rejects_unknown_agents(tmp_path: Path) -> None:
    workflow = tmp_path / ".172x/workflows/invalid.md"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        """---
id: invalid-workflow
name: Invalid Workflow
description: Invalid project workflow.
version: 1
---
## Purpose
Invalid.
## Inputs
Task.
## Participating agents
- `missing-agent`
## Flow
1. Invalid.
## Parallel work
None.
## Feedback loops
None.
## Human gates
Human decides.
## Completion criteria
Never.
## Failure and escalation
Stop.
""",
        encoding="utf-8",
    )

    with pytest.raises(LibraryError, match="unknown participating agents: missing-agent"):
        load_workflows(tmp_path)


@pytest.mark.parametrize(
    "frontmatter",
    [
        "id: qa\nname: QA\ndescription: Test\nversion: 1\nextra: no",  # unknown key
        "id: qa\nid: another\nname: QA\ndescription: Test\nversion: 1",  # duplicate
        "id: QA\nname: QA\ndescription: Test\nversion: 1",  # invalid ID
        "id: qa\nname: QA\ndescription: Test\nversion: 0",  # invalid version
        "id: qa\nname: QA\ndescription: [not a scalar]\nversion: 1",  # list syntax
    ],
)
def test_parser_rejects_invalid_flat_frontmatter(tmp_path: Path, frontmatter: str) -> None:
    path = tmp_path / "bad.md"
    path.write_text(f"---\n{frontmatter}\n---\nbody\n", encoding="utf-8")

    with pytest.raises(LibraryError, match="bad.md"):
        parse_markdown(path)


def test_parser_requires_closing_delimiter(tmp_path: Path) -> None:
    path = tmp_path / "bad.md"
    path.write_text("---\nid: qa\nname: QA\ndescription: Test\nversion: 1\n", encoding="utf-8")

    with pytest.raises(LibraryError, match="bad.md"):
        parse_markdown(path)


def test_parser_returns_frontmatter_and_body(tmp_path: Path) -> None:
    path = tmp_path / "qa.md"
    path.write_text(
        "---\nid: qa\nname: QA Agent\ndescription: Verifies behavior.\nversion: 1\n---\n## Mission\nTest\n",
        encoding="utf-8",
    )

    item = parse_markdown(path)

    assert item.id == "qa"
    assert item.version == 1
    assert item.body == "## Mission\nTest\n"
