"""Read the deliberately small canonical Markdown library format."""

from __future__ import annotations

import re
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


_KEYS = {"id", "name", "description", "version"}
_ID = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_SCALAR = re.compile(r"([a-z]+):[ ]+(.+)\Z")
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
    for section in sections:
        if f"## {section}\n" not in item.body and f"## {section}\r\n" not in item.body:
            raise LibraryError(f"{item.source}: missing required section: {section}")


def validate_library() -> tuple[list[LibraryItem], list[LibraryItem]]:
    """Validate all canonical content relationships without interpreting workflows."""
    agents = load_library("agents")
    workflows = load_library("workflows")
    for agent in agents:
        _required_sections(agent, _AGENT_SECTIONS)
        agent_domain(agent)
    _validate_workflow_references(workflows)
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
