"""Read the deliberately small canonical Markdown library format."""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, replace
from importlib import resources
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Protocol


class TextFile(Protocol):
    def read_text(self, encoding: str = "utf-8") -> str: ...

    @property
    def name(self) -> str: ...


class LibraryError(ValueError):
    """A path-specific canonical library validation error."""


@dataclass(frozen=True)
class LibraryItem:
    id: str
    name: str
    description: str
    version: int
    body: str
    source: str
    relative_path: str = ""


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    category: str
    title: str
    scenario: str
    expected_behaviors: tuple[str, ...]
    prohibited_behaviors: tuple[str, ...]
    evidence_expectations: tuple[str, ...]
    handoff_expectations: tuple[str, ...]


@dataclass(frozen=True)
class EvaluationFixture:
    schema_version: int
    agent_id: str
    agent_version: int
    cases: tuple[EvaluationCase, ...]
    source: str


_KEYS = {"id", "name", "description", "version"}
_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_SCALAR = re.compile(r"([a-z]+):[ ]+(.+)\Z")
_SECTION_HEADING = re.compile(r"^## (?P<heading>[^\r\n]+?)\s*$", re.MULTILINE)
_ROLE_OR_WORKFLOW_LIKE_ID = re.compile(
    r"(?:"
    r"(?:[a-z0-9]+-)*(?:author|specialist|researcher|designer|architect|"
    r"engineer|reviewer|feasibility|workflow|loop)"
    r"|dev"
    r"|idea-to-[a-z0-9-]+"
    r")\Z"
)
_INTERNAL_PATH = re.compile(
    r"(?<![a-z0-9_./-])"
    r"((?:references|assets)/(?:[a-z0-9][a-z0-9.-]*/)*"
    r"[a-z0-9][a-z0-9.-]*\.(?:md|mmd|toml|yaml))"
)
_AGENT_SECTIONS = (
    "Domain",
    "Mission",
    "Use when",
    "Inputs",
    "Process",
    "Decision rules",
    "Deliverables",
    "Deliverable format",
    "Quality bar",
    "Evidence requirements",
    "Handoff contract",
    "Boundaries",
)
_WORKFLOW_SECTIONS = (
    "Purpose",
    "Inputs",
    "Participating agents",
    "Flow",
    "Parallel work",
    "Feedback loops",
    "Human gates",
    "Completion criteria",
    "Failure and escalation",
)
_DOMAINS = ("Product", "Design", "Platform", "Quality", "Security")
_EVALUATION_SCHEMA_VERSION = 1
_EVALUATION_CATEGORIES = (
    "normal-success",
    "incomplete-or-conflicting-inputs",
    "tempting-scope-expansion",
    "insufficient-evidence",
    "boundary-or-authority-challenge",
    "handoff-completeness",
)
_EVALUATION_KEYS = {"schema_version", "agent_id", "agent_version", "cases"}
_EVALUATION_CASE_KEYS = {
    "id",
    "category",
    "title",
    "scenario",
    "expected_behaviors",
    "prohibited_behaviors",
    "evidence_expectations",
    "handoff_expectations",
}
_REQUIRED_SUPPORT_FILES = (
    "references/common/evidence-and-uncertainty.md",
    "references/common/handoff-envelope.md",
    "assets/quality/qa-report-template.md",
    "assets/quality/review-report-template.md",
    "evaluations/v1/README.md",
    "evaluations/v1/rubric.md",
)


def parse_markdown(source: TextFile | Path) -> LibraryItem:
    """Parse one canonical document without attempting general YAML support."""
    path = str(source)
    lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise LibraryError(f"{path}: frontmatter must begin with ---")
    try:
        closing = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as error:
        raise LibraryError(f"{path}: frontmatter closing --- is missing") from error

    values: dict[str, str] = {}
    for line in lines[1:closing]:
        match = _SCALAR.fullmatch(line.rstrip("\r\n"))
        if not match:
            raise LibraryError(f"{path}: frontmatter values must be single-line scalars")
        key, value = match.groups()
        if key not in _KEYS:
            raise LibraryError(f"{path}: unsupported frontmatter key {key!r}")
        if key in values:
            raise LibraryError(f"{path}: duplicate frontmatter key {key!r}")
        if (
            not value.strip()
            or value != value.strip()
            or value.startswith(("-", "[", "{", "|", ">"))
        ):
            raise LibraryError(f"{path}: invalid scalar value for {key!r}")
        values[key] = value

    if set(values) != _KEYS:
        missing = ", ".join(sorted(_KEYS - set(values)))
        unexpected = ", ".join(sorted(set(values) - _KEYS))
        detail = f"missing {missing}" if missing else f"unexpected {unexpected}"
        raise LibraryError(
            f"{path}: frontmatter must contain exactly id, name, description, version ({detail})"
        )
    if not _ID.fullmatch(values["id"]):
        raise LibraryError(f"{path}: invalid id {values['id']!r}")
    if not values["version"].isdigit() or int(values["version"]) < 1:
        raise LibraryError(f"{path}: version must be a positive integer")

    return LibraryItem(
        id=values["id"],
        name=values["name"],
        description=values["description"],
        version=int(values["version"]),
        body="".join(lines[closing + 1 :]),
        source=path,
    )


def library_directory(kind: str) -> Traversable:
    if kind not in {"agents", "workflows"}:
        raise ValueError(f"unknown library kind: {kind}")
    return resources.files("agent_workflows").joinpath("library", kind)


def load_library(kind: str) -> list[LibraryItem]:
    """Load bundled items in deterministic ID order and reject duplicate IDs."""
    root = library_directory(kind)
    items = [
        replace(item, relative_path=relative.as_posix())
        for relative, file in _markdown_files(root)
        for item in [parse_markdown(file)]
    ]
    items.sort(key=lambda item: item.id)
    ids = [item.id for item in items]
    if len(ids) != len(set(ids)):
        duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
        raise LibraryError(f"{kind}: duplicate IDs: {', '.join(duplicates)}")
    return items


def _markdown_files(
    directory: Traversable, prefix: Path = Path()
) -> list[tuple[Path, Traversable]]:
    """Return canonical Markdown files recursively in a stable order."""
    files: list[tuple[Path, Traversable]] = []
    for child in sorted(directory.iterdir(), key=lambda entry: entry.name):
        relative = prefix / child.name
        if child.is_dir():
            files.extend(_markdown_files(child, relative))
        elif child.is_file() and child.name.endswith(".md"):
            files.append((relative, child))
    return files


def find_item(kind: str, item_id: str) -> LibraryItem:
    for item in load_library(kind):
        if item.id == item_id:
            return item
    available = ", ".join(item.id for item in load_library(kind))
    raise LibraryError(f"unknown {kind[:-1]} ID {item_id!r}; available: {available}")


def load_project_workflows(target: Path) -> list[LibraryItem]:
    """Load project-owned workflow Markdown from the documented custom-workflow directory."""
    directory = target.expanduser().resolve() / ".172x" / "workflows"
    if not directory.exists():
        return []
    if not directory.is_dir() or directory.is_symlink():
        raise LibraryError(f"project workflow directory must be a real directory: {directory}")
    items = [
        replace(item, relative_path=(Path("custom") / source.relative_to(directory)).as_posix())
        for source in sorted(directory.rglob("*.md"))
        if source.is_file() and not source.is_symlink()
        for item in [parse_markdown(source)]
    ]
    return _unique_items("project workflows", items)


def load_workflows(target: Path | None = None) -> list[LibraryItem]:
    """Load bundled workflows plus validated project-owned workflows when a target is supplied."""
    workflows = load_library("workflows")
    if target is not None:
        workflows.extend(load_project_workflows(target))
    workflows = _unique_items("workflows", workflows)
    _validate_workflow_references(workflows)
    return workflows


def find_workflow(target: Path, workflow_id: str) -> LibraryItem:
    """Find one bundled or project-owned workflow by ID."""
    for workflow in load_workflows(target):
        if workflow.id == workflow_id:
            return workflow
    available = ", ".join(workflow.id for workflow in load_workflows(target))
    raise LibraryError(f"unknown workflow ID {workflow_id!r}; available: {available}")


def _required_sections(item: LibraryItem, sections: tuple[str, ...]) -> None:
    headings = [match.group("heading").strip() for match in _SECTION_HEADING.finditer(item.body)]
    for section in sections:
        count = headings.count(section)
        if count == 0:
            raise LibraryError(f"{item.source}: missing required section: {section}")
        if count > 1:
            raise LibraryError(f"{item.source}: duplicate required section: {section}")
    required_in_document = [heading for heading in headings if heading in sections]
    if required_in_document != list(sections):
        expected = ", ".join(sections)
        actual = ", ".join(required_in_document)
        raise LibraryError(
            f"{item.source}: required sections are out of order "
            f"(expected: {expected}; found: {actual})"
        )


def validate_library() -> tuple[list[LibraryItem], list[LibraryItem]]:
    """Validate all canonical content relationships without interpreting workflows."""
    agents = load_library("agents")
    workflows = load_library("workflows")
    for agent in agents:
        _required_sections(agent, _AGENT_SECTIONS)
        agent_domain(agent)
    _validate_workflow_references(workflows)
    _validate_referenced_ids(agents, workflows)
    _validate_handoff_recipients(agents, workflows)
    _validate_required_support_files()
    _validate_internal_paths(agents, workflows)
    validate_evaluations(agents)
    return agents, workflows


def _unique_items(kind: str, items: list[LibraryItem]) -> list[LibraryItem]:
    items.sort(key=lambda item: item.id)
    ids = [item.id for item in items]
    if len(ids) != len(set(ids)):
        duplicates = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
        raise LibraryError(f"{kind}: duplicate IDs: {', '.join(duplicates)}")
    return items


def _validate_workflow_references(workflows: list[LibraryItem]) -> None:
    known_agents = {agent.id for agent in load_library("agents")}
    reserved_skill_ids = known_agents | {"workflow-composer"}
    for workflow in workflows:
        if workflow.id in reserved_skill_ids:
            raise LibraryError(
                f"{workflow.source}: workflow ID conflicts with a reserved 172X skill: {workflow.id}"
            )
        _required_sections(workflow, _WORKFLOW_SECTIONS)
        participating = _section_text(workflow.body, "Participating agents")
        referenced = set(re.findall(r"`([a-z0-9-]+)`", participating))
        unknown = sorted(referenced - known_agents)
        if unknown:
            raise LibraryError(
                f"{workflow.source}: unknown participating agents: {', '.join(unknown)}"
            )


def _validate_handoff_recipients(agents: list[LibraryItem], workflows: list[LibraryItem]) -> None:
    known_agents = {agent.id for agent in agents}
    known_workflows = {workflow.id for workflow in workflows}
    known_recipients = known_agents | known_workflows | {"human", "user"}
    for agent in agents:
        handoff = _section_text(agent.body, "Handoff contract")
        referenced = set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`", handoff))
        recipient_like = {
            value for value in referenced if _ROLE_OR_WORKFLOW_LIKE_ID.fullmatch(value)
        }
        unknown = sorted(recipient_like - known_recipients)
        if unknown:
            raise LibraryError(f"{agent.source}: unknown handoff recipients: {', '.join(unknown)}")
        has_named_recipient = bool(referenced & known_recipients) or bool(
            re.search(r"\b(?:human|user)\b", handoff, re.IGNORECASE)
        )
        if not has_named_recipient:
            raise LibraryError(
                f"{agent.source}: handoff contract must name a receiving agent or human"
            )


def _validate_referenced_ids(agents: list[LibraryItem], workflows: list[LibraryItem]) -> None:
    """Reject unknown role- or workflow-like IDs anywhere in canonical operating content."""
    known_ids = {item.id for item in (*agents, *workflows)}
    documents = [(item.source, item.body) for item in (*agents, *workflows)]
    for kind in ("references", "assets"):
        for relative, resource_file in _resource_files(_library_resource(kind)):
            if resource_file.name.endswith(".md"):
                documents.append(
                    (
                        f"{kind}/{relative.as_posix()}",
                        resource_file.read_text(encoding="utf-8"),
                    )
                )
    for source, body in documents:
        referenced = set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)*)`", body))
        identifier_like = {
            value for value in referenced if _ROLE_OR_WORKFLOW_LIKE_ID.fullmatch(value)
        }
        unknown = sorted(identifier_like - known_ids)
        if unknown:
            raise LibraryError(f"{source}: unknown agent or workflow IDs: {', '.join(unknown)}")


def _library_resource(relative: str) -> Traversable:
    resource = resources.files("agent_workflows").joinpath("library")
    for part in Path(relative).parts:
        resource = resource.joinpath(part)
    return resource


def _validate_required_support_files() -> None:
    for relative in _REQUIRED_SUPPORT_FILES:
        if not _library_resource(relative).is_file():
            raise LibraryError(f"library: missing required packaged resource: {relative}")


def _validate_internal_paths(agents: list[LibraryItem], workflows: list[LibraryItem]) -> None:
    documents = [(item.source, item.body) for item in (*agents, *workflows)]
    for kind in ("references", "assets", "evaluations"):
        root = _library_resource(kind)
        for relative, resource_file in _resource_files(root):
            if resource_file.name.endswith((".md", ".toml")):
                documents.append(
                    (
                        f"{kind}/{relative.as_posix()}",
                        resource_file.read_text(encoding="utf-8"),
                    )
                )
    for document_source, body in documents:
        for relative in sorted(set(_INTERNAL_PATH.findall(body))):
            if not _library_resource(relative).is_file():
                raise LibraryError(f"{document_source}: unresolved internal path: {relative}")


def _resource_files(
    directory: Traversable, prefix: Path = Path()
) -> list[tuple[Path, Traversable]]:
    files: list[tuple[Path, Traversable]] = []
    for child in sorted(directory.iterdir(), key=lambda entry: entry.name):
        relative = prefix / child.name
        if child.is_dir():
            files.extend(_resource_files(child, relative))
        elif child.is_file():
            files.append((relative, child))
    return files


def _exact_keys(table: Mapping[str, object], expected: set[str], source: str, subject: str) -> None:
    actual = set(table)
    if actual == expected:
        return
    details: list[str] = []
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing:
        details.append(f"missing {', '.join(missing)}")
    if unexpected:
        details.append(f"unexpected {', '.join(unexpected)}")
    raise LibraryError(f"{source}: {subject} fields are invalid ({'; '.join(details)})")


def _evaluation_string(table: Mapping[str, object], key: str, source: str) -> str:
    value = table[key]
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise LibraryError(f"{source}: evaluation field {key!r} must be a non-empty string")
    return value


def _evaluation_strings(table: Mapping[str, object], key: str, source: str) -> tuple[str, ...]:
    value = table[key]
    if not isinstance(value, list) or not value:
        raise LibraryError(f"{source}: evaluation field {key!r} must be a non-empty string array")
    if any(
        not isinstance(entry, str) or not entry.strip() or entry != entry.strip() for entry in value
    ):
        raise LibraryError(f"{source}: evaluation field {key!r} must contain non-empty strings")
    strings = tuple(entry for entry in value if isinstance(entry, str))
    if len(strings) != len(set(strings)):
        raise LibraryError(f"{source}: evaluation field {key!r} contains duplicate behaviors")
    return strings


def parse_evaluation_fixture(source: TextFile | Path) -> EvaluationFixture:
    """Parse one deliberately small v1 TOML evaluation fixture."""
    path = str(source)
    try:
        parsed = tomllib.loads(source.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as error:
        raise LibraryError(f"{path}: invalid evaluation TOML: {error}") from error
    _exact_keys(parsed, _EVALUATION_KEYS, path, "evaluation fixture")

    schema_version = parsed["schema_version"]
    agent_version = parsed["agent_version"]
    if type(schema_version) is not int or schema_version != _EVALUATION_SCHEMA_VERSION:
        raise LibraryError(f"{path}: schema_version must be {_EVALUATION_SCHEMA_VERSION}")
    if type(agent_version) is not int or agent_version < 1:
        raise LibraryError(f"{path}: agent_version must be a positive integer")
    agent_id = _evaluation_string(parsed, "agent_id", path)
    if not _ID.fullmatch(agent_id):
        raise LibraryError(f"{path}: invalid evaluation agent_id {agent_id!r}")
    if source.name != f"{agent_id}.toml":
        raise LibraryError(f"{path}: fixture filename must be {agent_id}.toml")

    raw_cases = parsed["cases"]
    if not isinstance(raw_cases, list) or not raw_cases:
        raise LibraryError(f"{path}: cases must be a non-empty array of tables")
    cases: list[EvaluationCase] = []
    for index, raw_case in enumerate(raw_cases, 1):
        if not isinstance(raw_case, dict):
            raise LibraryError(f"{path}: case {index} must be a TOML table")
        _exact_keys(raw_case, _EVALUATION_CASE_KEYS, path, f"case {index}")
        case_id = _evaluation_string(raw_case, "id", path)
        category = _evaluation_string(raw_case, "category", path)
        if not _ID.fullmatch(case_id):
            raise LibraryError(f"{path}: invalid evaluation case id {case_id!r}")
        if category not in _EVALUATION_CATEGORIES:
            available = ", ".join(_EVALUATION_CATEGORIES)
            raise LibraryError(
                f"{path}: unknown evaluation category {category!r}; expected: {available}"
            )
        cases.append(
            EvaluationCase(
                id=case_id,
                category=category,
                title=_evaluation_string(raw_case, "title", path),
                scenario=_evaluation_string(raw_case, "scenario", path),
                expected_behaviors=_evaluation_strings(raw_case, "expected_behaviors", path),
                prohibited_behaviors=_evaluation_strings(raw_case, "prohibited_behaviors", path),
                evidence_expectations=_evaluation_strings(raw_case, "evidence_expectations", path),
                handoff_expectations=_evaluation_strings(raw_case, "handoff_expectations", path),
            )
        )
    case_ids = [case.id for case in cases]
    if len(case_ids) != len(set(case_ids)):
        raise LibraryError(f"{path}: evaluation case IDs must be unique")
    categories = [case.category for case in cases]
    if len(categories) != len(_EVALUATION_CATEGORIES) or set(categories) != set(
        _EVALUATION_CATEGORIES
    ):
        raise LibraryError(
            f"{path}: cases must cover exactly these categories once: "
            f"{', '.join(_EVALUATION_CATEGORIES)}"
        )
    return EvaluationFixture(
        schema_version=schema_version,
        agent_id=agent_id,
        agent_version=agent_version,
        cases=tuple(cases),
        source=path,
    )


def load_evaluation_fixtures() -> list[EvaluationFixture]:
    """Load packaged v1 fixtures in deterministic agent-ID order."""
    directory = _library_resource("evaluations/v1/cases")
    if not directory.is_dir():
        raise LibraryError("library: missing packaged evaluation directory: evaluations/v1/cases")
    fixtures = [
        parse_evaluation_fixture(source)
        for source in sorted(directory.iterdir(), key=lambda entry: entry.name)
        if source.is_file() and source.name.endswith(".toml")
    ]
    fixtures.sort(key=lambda fixture: fixture.agent_id)
    return fixtures


def validate_evaluations(
    agents: list[LibraryItem] | None = None,
) -> list[EvaluationFixture]:
    """Validate fixture coverage without executing or scoring model behavior."""
    canonical_agents = agents if agents is not None else load_library("agents")
    fixtures = load_evaluation_fixtures()
    fixture_ids = [fixture.agent_id for fixture in fixtures]
    if len(fixture_ids) != len(set(fixture_ids)):
        duplicates = sorted(
            {fixture_id for fixture_id in fixture_ids if fixture_ids.count(fixture_id) > 1}
        )
        raise LibraryError(f"evaluations: duplicate agent fixtures: {', '.join(duplicates)}")
    canonical_by_id = {agent.id: agent for agent in canonical_agents}
    missing = sorted(set(canonical_by_id) - set(fixture_ids))
    unknown = sorted(set(fixture_ids) - set(canonical_by_id))
    if missing or unknown:
        details: list[str] = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if unknown:
            details.append(f"unknown {', '.join(unknown)}")
        raise LibraryError(f"evaluations: fixture coverage is invalid ({'; '.join(details)})")
    case_ids = [case.id for fixture in fixtures for case in fixture.cases]
    if len(case_ids) != len(set(case_ids)):
        duplicates = sorted({case_id for case_id in case_ids if case_ids.count(case_id) > 1})
        raise LibraryError(f"evaluations: duplicate case IDs: {', '.join(duplicates)}")
    for fixture in fixtures:
        expected_version = canonical_by_id[fixture.agent_id].version
        if fixture.agent_version != expected_version:
            raise LibraryError(
                f"{fixture.source}: agent_version {fixture.agent_version} does not match "
                f"canonical version {expected_version}"
            )
    return fixtures


def agent_domain(agent: LibraryItem) -> str:
    """Return the agent's Markdown-defined domain from the small supported catalog."""
    domain = _section_text(agent.body, "Domain").strip()
    if domain not in _DOMAINS:
        available = ", ".join(_DOMAINS)
        raise LibraryError(f"{agent.source}: domain must be one of: {available}")
    return domain


def domains() -> dict[str, list[LibraryItem]]:
    """Group validated bundled agents by their Markdown-defined domain."""
    grouped: dict[str, list[LibraryItem]] = {domain: [] for domain in _DOMAINS}
    for agent in load_library("agents"):
        grouped[agent_domain(agent)].append(agent)
    return {domain: agents for domain, agents in grouped.items() if agents}


def _section_text(body: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$([\s\S]*?)(?=^## |\Z)", body, re.MULTILINE)
    return match.group(1) if match else ""
