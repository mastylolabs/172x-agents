"""Generate the static Forge catalog from the canonical 172X Markdown library."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agent_workflows.library import (
    agent_domain,
    load_library,
    load_workflows,
    validate_library,
)

SECTION = re.compile(r"^## (?P<heading>.+?)\s*$([\s\S]*?)(?=^## |\Z)", re.MULTILINE)
LIST_PREFIX = re.compile(r"^(?:[-*]|\d+\.)\s+")


def section(body: str, heading: str) -> str:
    """Return one validated canonical Markdown section without its heading."""
    for match in SECTION.finditer(body):
        if match.group("heading") == heading:
            return match.group(0).split("\n", 1)[1].strip()
    raise ValueError(f"missing required section: {heading}")


def lines(value: str) -> list[str]:
    """Turn a Markdown section into concise display items without changing its meaning."""
    raw_lines = [line.strip() for line in value.splitlines() if line.strip()]
    listed = [LIST_PREFIX.sub("", line) for line in raw_lines if LIST_PREFIX.match(line)]
    if listed:
        return listed
    return [" ".join(raw_lines)] if raw_lines else []


def participant_ids(body: str) -> list[str]:
    return re.findall(r"`([a-z0-9-]+)`", section(body, "Participating agents"))


def source_revision() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() or "local"


def build_catalog() -> dict[str, Any]:
    validate_library()
    agents = load_library("agents")
    workflows = load_workflows()
    return {
        "revision": source_revision(),
        "agents": [
            {
                "slug": agent.id,
                "name": agent.name,
                "domain": agent_domain(agent).casefold(),
                "kind": "Specialist",
                "summary": agent.description,
                "useWhen": " ".join(lines(section(agent.body, "Use when"))),
                "badges": ["172X Reviewed", "Evidence required"],
                "reviewed": True,
                "evidenceRequired": True,
                "receive": lines(section(agent.body, "Deliverables")),
                "qualityBar": lines(section(agent.body, "Quality bar")),
                "evidence": lines(section(agent.body, "Evidence requirements")),
                "boundaries": lines(section(agent.body, "Boundaries")),
                "workflows": [
                    workflow.id
                    for workflow in workflows
                    if agent.id in participant_ids(workflow.body)
                ],
                "version": str(agent.version),
            }
            for agent in agents
        ],
        "workflows": [
            {
                "slug": workflow.id,
                "name": workflow.name.removesuffix(" Workflow"),
                "outcome": " ".join(lines(section(workflow.body, "Purpose"))),
                "summary": workflow.description,
                "steps": lines(section(workflow.body, "Flow")),
                "gates": [
                    *lines(section(workflow.body, "Feedback loops")),
                    *lines(section(workflow.body, "Human gates")),
                ],
                "agents": participant_ids(workflow.body),
                "version": str(workflow.version),
            }
            for workflow in workflows
        ],
    }


def main() -> None:
    destination = ROOT / "forge" / "src" / "data" / "catalog.generated.json"
    destination.write_text(
        json.dumps(build_catalog(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
