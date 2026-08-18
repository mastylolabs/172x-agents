from dataclasses import replace
from importlib import resources
from pathlib import Path

import pytest

from agent_workflows import library
from agent_workflows.library import (
    LibraryError,
    LibraryItem,
    find_item,
    load_evaluation_fixtures,
    load_library,
    parse_evaluation_fixture,
    validate_evaluations,
    validate_library,
)

EXPECTED_CATEGORIES = {
    "normal-success",
    "incomplete-or-conflicting-inputs",
    "tempting-scope-expansion",
    "insufficient-evidence",
    "boundary-or-authority-challenge",
    "handoff-completeness",
}


def test_every_agent_has_one_complete_v1_evaluation_fixture() -> None:
    agents = load_library("agents")
    fixtures = validate_evaluations(agents)
    expected_case_count = len(agents) * len(EXPECTED_CATEGORIES)

    assert [fixture.agent_id for fixture in fixtures] == [agent.id for agent in agents]
    assert len(fixtures) == len(agents)
    assert sum(len(fixture.cases) for fixture in fixtures) == expected_case_count
    assert len({case.id for fixture in fixtures for case in fixture.cases}) == expected_case_count
    for fixture in fixtures:
        assert fixture.schema_version == 1
        assert {case.category for case in fixture.cases} == EXPECTED_CATEGORIES
        for case in fixture.cases:
            assert case.expected_behaviors
            assert case.prohibited_behaviors
            assert case.evidence_expectations
            assert case.handoff_expectations


def test_evaluation_support_is_available_as_package_resources() -> None:
    root = resources.files("agent_workflows").joinpath("library")
    required = (
        "references/common/evidence-and-uncertainty.md",
        "references/common/handoff-envelope.md",
        "assets/quality/qa-report-template.md",
        "assets/quality/review-report-template.md",
        "evaluations/v1/README.md",
        "evaluations/v1/rubric.md",
    )

    for relative in required:
        assert root.joinpath(*relative.split("/")).is_file(), relative
    for fixture in load_evaluation_fixtures():
        assert root.joinpath("evaluations", "v1", "cases", f"{fixture.agent_id}.toml").is_file()


def test_fixture_parser_rejects_incomplete_case_schema(tmp_path) -> None:
    bundled = (
        resources.files("agent_workflows")
        .joinpath("library", "evaluations", "v1", "cases", "brief-author.toml")
        .read_text(encoding="utf-8")
    )
    invalid = tmp_path / "brief-author.toml"
    invalid.write_text(
        bundled.replace("expected_behaviors =", "unexpected_behaviors =", 1), encoding="utf-8"
    )

    with pytest.raises(LibraryError, match="case 1 fields are invalid"):
        parse_evaluation_fixture(invalid)


def test_fixture_parser_requires_exactly_one_case_per_category(tmp_path) -> None:
    bundled = (
        resources.files("agent_workflows")
        .joinpath("library", "evaluations", "v1", "cases", "brief-author.toml")
        .read_text(encoding="utf-8")
    )
    invalid = tmp_path / "brief-author.toml"
    invalid.write_text(
        bundled.replace('category = "handoff-completeness"', 'category = "normal-success"', 1),
        encoding="utf-8",
    )

    with pytest.raises(LibraryError, match="cover exactly these categories once"):
        parse_evaluation_fixture(invalid)


def test_evaluation_validation_rejects_missing_agent_fixture(monkeypatch) -> None:
    fixtures = load_evaluation_fixtures()
    monkeypatch.setattr(library, "load_evaluation_fixtures", lambda: fixtures[:-1])

    with pytest.raises(LibraryError, match="fixture coverage is invalid"):
        validate_evaluations(load_library("agents"))


def test_evaluation_validation_rejects_stale_agent_version(monkeypatch) -> None:
    fixtures = load_evaluation_fixtures()
    stale = [replace(fixtures[0], agent_version=fixtures[0].agent_version + 1), *fixtures[1:]]
    monkeypatch.setattr(library, "load_evaluation_fixtures", lambda: stale)

    with pytest.raises(LibraryError, match="does not match canonical version"):
        validate_evaluations(load_library("agents"))


@pytest.mark.parametrize(
    ("body", "message"),
    [
        ("## First\nA\n## First\nB\n## Second\nC\n", "duplicate required section"),
        ("## Second\nB\n## First\nA\n", "required sections are out of order"),
    ],
)
def test_required_sections_are_unique_and_ordered(body: str, message: str) -> None:
    item = LibraryItem(
        id="example",
        name="Example",
        description="Example document.",
        version=1,
        body=body,
        source="example.md",
    )

    with pytest.raises(LibraryError, match=message):
        library._required_sections(item, ("First", "Second"))


def test_internal_reference_and_asset_paths_must_resolve() -> None:
    agent = find_item("agents", "brief-author")
    broken = replace(
        agent,
        body=agent.body + "\nRead `references/common/not-a-real-reference.md`.\n",
    )

    with pytest.raises(LibraryError, match="unresolved internal path"):
        library._validate_internal_paths([broken], load_library("workflows"))


@pytest.mark.parametrize("unknown_id", ["invented-specialist", "idea-to-unknown"])
def test_role_and_workflow_references_must_resolve_outside_handoffs(unknown_id: str) -> None:
    agents = load_library("agents")
    original = find_item("agents", "brief-author")
    broken = replace(
        original,
        body=original.body.replace(
            "## Use when\n",
            f"## Use when\nRoute a separate question to `{unknown_id}`.\n\n",
            1,
        ),
    )
    modified = [broken if agent.id == broken.id else agent for agent in agents]

    with pytest.raises(LibraryError, match=f"unknown agent or workflow IDs: {unknown_id}"):
        library._validate_referenced_ids(modified, load_library("workflows"))


def test_role_references_in_support_markdown_must_resolve(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    broken = tmp_path / "broken.md"
    broken.write_text("Send this artifact to `invented-reviewer`.\n", encoding="utf-8")
    monkeypatch.setattr(
        library,
        "_resource_files",
        lambda _root: [(Path("broken.md"), broken)],
    )

    with pytest.raises(LibraryError, match="unknown agent or workflow IDs: invented-reviewer"):
        library._validate_referenced_ids(load_library("agents"), load_library("workflows"))


@pytest.mark.parametrize("recipient", ["invented-specialist", "invented-workflow"])
def test_handoff_recipient_must_be_a_known_agent_workflow_or_human(recipient: str) -> None:
    agents = load_library("agents")
    original = find_item("agents", "brief-author")
    broken = replace(
        original,
        body=original.body.replace(
            "## Handoff contract\n",
            f"## Handoff contract\nSend the result to `{recipient}`.\n\n",
            1,
        ),
    )
    modified = [broken if agent.id == broken.id else agent for agent in agents]

    with pytest.raises(LibraryError, match=f"unknown handoff recipients: {recipient}"):
        library._validate_handoff_recipients(modified, load_library("workflows"))


def test_full_library_validation_includes_evaluation_and_support_checks() -> None:
    agents, workflows = validate_library()

    assert len(agents) == 17
    assert len(workflows) == 4


def test_development_pilot_v2_uses_shared_references_and_assets() -> None:
    expected_paths = {
        "principal-engineer": {
            "references/platform/change-discipline.md",
            "references/common/evidence-and-uncertainty.md",
            "references/common/handoff-envelope.md",
        },
        "qa-engineer": {
            "references/quality/testing-strategy.md",
            "references/common/evidence-and-uncertainty.md",
            "references/common/handoff-envelope.md",
            "assets/quality/qa-report-template.md",
        },
        "pr-reviewer": {
            "references/quality/review-findings.md",
            "references/common/evidence-and-uncertainty.md",
            "references/common/handoff-envelope.md",
            "assets/quality/review-report-template.md",
        },
    }
    fixture_versions = {
        fixture.agent_id: fixture.agent_version for fixture in load_evaluation_fixtures()
    }

    for agent_id, paths in expected_paths.items():
        agent = find_item("agents", agent_id)
        assert agent.version == 2
        assert fixture_versions[agent_id] == 2
        assert "**Use this agent when:**" in agent.body
        assert "**Do not use this agent when:**" in agent.body
        assert "**Blockers" in agent.body
        assert "**Safe labeled assumptions:**" in agent.body
        assert "**Calibration:**" in agent.body
        assert all(path in agent.body for path in paths)

    qa = find_item("agents", "qa-engineer")
    assert (
        "In `dev-loop`, independently rerun every selected local `.172x/contexts.toml` gate tool "
        "using the repository's existing environment."
    ) in qa.body


def test_platform_security_and_specialist_review_v2_use_supporting_material() -> None:
    expected_paths = {
        "principal-architect": {
            "references/platform/system-design-workflow.md",
            "references/platform/architecture-patterns.md",
            "references/platform/technology-decision-guide.md",
            "assets/platform/architecture-template.md",
        },
        "technical-feasibility": {
            "references/platform/feasibility-experiments.md",
            "assets/platform/feasibility-assessment-template.md",
        },
        "backend-engineer": {"references/platform/backend-delivery.md"},
        "frontend-engineer": {"references/platform/frontend-delivery.md"},
        "backend-reviewer": {
            "references/platform/backend-delivery.md",
            "references/quality/review-findings.md",
            "assets/quality/review-report-template.md",
        },
        "frontend-reviewer": {
            "references/platform/frontend-delivery.md",
            "references/quality/review-findings.md",
            "assets/quality/review-report-template.md",
        },
        "design-architecture-reviewer": {
            "references/platform/system-design-workflow.md",
            "references/platform/architecture-patterns.md",
            "references/quality/review-findings.md",
            "assets/quality/design-architecture-matrix-template.md",
        },
        "principal-codebase-reviewer": {
            "references/quality/testing-strategy.md",
            "references/quality/review-findings.md",
            "references/platform/architecture-patterns.md",
        },
        "security-reviewer": {
            "references/security/threat-modeling.md",
            "references/quality/review-findings.md",
            "assets/security/threat-model-template.md",
        },
    }
    fixture_versions = {
        fixture.agent_id: fixture.agent_version for fixture in load_evaluation_fixtures()
    }

    for agent_id, paths in expected_paths.items():
        agent = find_item("agents", agent_id)
        assert agent.version == 2
        assert fixture_versions[agent_id] == 2
        assert "**Use this agent when:**" in agent.body
        assert "**Do not use this agent when:**" in agent.body
        assert "**Blockers" in agent.body
        assert "**Safe labeled assumptions:**" in agent.body
        assert "**Calibration:**" in agent.body
        assert "references/common/evidence-and-uncertainty.md" in agent.body
        assert "references/common/handoff-envelope.md" in agent.body
        assert all(path in agent.body for path in paths)
        handoff = agent.body.split("## Handoff contract\n", 1)[1].split("\n## Boundaries", 1)[0]
        assert all(
            field in handoff.lower()
            for field in ("artifact", "criteria", "evidence", "assum", "decision", "risk")
        )


def test_checkpoint_four_support_is_available_as_package_resources() -> None:
    root = resources.files("agent_workflows").joinpath("library")
    required = (
        "references/platform/backend-delivery.md",
        "references/platform/frontend-delivery.md",
        "references/platform/feasibility-experiments.md",
        "references/security/threat-modeling.md",
        "assets/platform/feasibility-assessment-template.md",
        "assets/quality/design-architecture-matrix-template.md",
        "assets/security/threat-model-template.md",
    )

    for relative in required:
        assert root.joinpath(*relative.split("/")).is_file(), relative

    deep_references = required[:4]
    for relative in deep_references:
        content = root.joinpath(*relative.split("/")).read_text(encoding="utf-8")
        assert all(
            heading in content
            for heading in (
                "## Required inputs",
                "## Staged method",
                "## Normal and failure paths",
                "## Common mistakes",
                "## Calibration",
                "## Evidence expectations",
                "## Escalation triggers",
                "## Related assets",
            )
        )

    for relative in required[4:]:
        content = root.joinpath(*relative.split("/")).read_text(encoding="utf-8")
        assert all(
            heading in content
            for heading in (
                "### Facts",
                "### Observations",
                "### Inferences",
                "### Assumptions",
                "### Decisions",
                "### Unknowns",
                "## Handoff envelope",
            )
        )
        assert "residual risk" in content.lower()


def test_product_and_design_v2_use_deep_references_and_assets() -> None:
    expected_paths = {
        "brief-author": {
            "references/product/build-brief-guidance.md",
            "assets/product/build-brief-template.md",
        },
        "discovery-specialist": {"references/product/discovery-methods.md"},
        "market-researcher": {"references/product/market-research-evidence.md"},
        "product-specification-specialist": {
            "references/product/specification-quality.md",
            "assets/product/product-specification-template.md",
        },
        "ux-ui-designer": {
            "references/design/ux-ui-definition-of-done.md",
            "assets/design/ux-ui-spec-template.md",
        },
    }
    fixture_versions = {
        fixture.agent_id: fixture.agent_version for fixture in load_evaluation_fixtures()
    }

    for agent_id, paths in expected_paths.items():
        agent = find_item("agents", agent_id)
        assert agent.version == 2
        assert fixture_versions[agent_id] == 2
        assert "**Use this agent when:**" in agent.body
        assert "**Do not use this agent when:**" in agent.body
        assert "**Blockers" in agent.body
        assert "**Safe labeled assumptions:**" in agent.body
        assert "**Calibration:**" in agent.body
        assert "references/common/evidence-and-uncertainty.md" in agent.body
        assert "references/common/handoff-envelope.md" in agent.body
        assert all(path in agent.body for path in paths)
        handoff = agent.body.split("## Handoff contract\n", 1)[1].split("\n## Boundaries", 1)[0]
        assert all(
            field in handoff.lower()
            for field in ("artifact", "criteria", "evidence", "assum", "decision", "risk")
        )

    designer = find_item("agents", "ux-ui-designer")
    for required_scope in (
        "user flows",
        "interaction and screen/component requirements",
        "responsive behavior",
        "content requirements",
        "states",
        "accessibility criteria",
        "design-system-compatible UI guidance",
    ):
        assert required_scope in designer.body
    normalized_designer = " ".join(designer.body.split())
    assert (
        "create a new brand or visual system without authoritative material" in normalized_designer
    )


def test_checkpoint_five_support_and_traceability_are_packaged() -> None:
    root = resources.files("agent_workflows").joinpath("library")
    references = (
        "references/product/build-brief-guidance.md",
        "references/product/discovery-methods.md",
        "references/product/market-research-evidence.md",
        "references/product/specification-quality.md",
        "references/design/ux-ui-definition-of-done.md",
    )
    assets = (
        "assets/product/build-brief-template.md",
        "assets/product/product-specification-template.md",
        "assets/design/ux-ui-spec-template.md",
    )

    for relative in references:
        content = root.joinpath(*relative.split("/")).read_text(encoding="utf-8")
        assert all(
            heading in content
            for heading in (
                "## Required inputs",
                "## Staged method",
                "## Normal and failure paths",
                "## Common mistakes",
                "## Calibration",
                "## Evidence expectations",
                "## Escalation triggers",
                "## Related assets",
            )
        )

    for relative in assets:
        content = root.joinpath(*relative.split("/")).read_text(encoding="utf-8")
        assert all(
            heading in content
            for heading in (
                "### Facts",
                "### Observations",
                "### Inferences",
                "### Assumptions",
                "### Decisions",
                "### Unknowns",
                "## Handoff envelope",
            )
        )
        assert "residual risk" in content.lower()

    specification = root.joinpath(
        "assets", "product", "product-specification-template.md"
    ).read_text(encoding="utf-8")
    ux_ui = root.joinpath("assets", "design", "ux-ui-spec-template.md").read_text(encoding="utf-8")
    architecture = root.joinpath("assets", "platform", "architecture-template.md").read_text(
        encoding="utf-8"
    )
    review_matrix = root.joinpath(
        "assets", "quality", "design-architecture-matrix-template.md"
    ).read_text(encoding="utf-8")
    assert "Requirement and criterion IDs" in specification
    assert "UX flow/state and content need" in specification
    assert "Architecture contract owner" in specification
    assert "Requirement and criterion IDs" in ux_ui
    assert "Data/API/authorization need" in ux_ui
    assert "## Architecture reconciliation" in ux_ui
    assert "Requirement and criterion IDs" in architecture
    assert "UX/UI flow and state/data need" in architecture
    assert "Interface/data/authorization contract" in architecture
    assert "Requirement/criterion IDs and user step" in review_matrix

    fixture_versions = {
        fixture.agent_id: fixture.agent_version for fixture in load_evaluation_fixtures()
    }
    for agent_id in ("frontend-engineer", "design-architecture-reviewer"):
        agent = find_item("agents", agent_id)
        assert agent.version == 2
        assert fixture_versions[agent_id] == 2
        assert "references/design/ux-ui-definition-of-done.md" in agent.body
