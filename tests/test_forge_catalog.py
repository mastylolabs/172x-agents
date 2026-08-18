import importlib.util
from pathlib import Path

from agent_workflows.library import load_library


def _catalog_module():
    source = Path(__file__).parents[1] / "scripts" / "generate_forge_catalog.py"
    spec = importlib.util.spec_from_file_location("forge_catalog", source)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_forge_catalog_is_derived_from_every_canonical_agent_and_workflow() -> None:
    catalog = _catalog_module().build_catalog()

    assert {agent["slug"] for agent in catalog["agents"]} == {
        agent.id for agent in load_library("agents")
    }
    assert {workflow["slug"] for workflow in catalog["workflows"]} == {
        workflow.id for workflow in load_library("workflows")
    }
    dev_loop = next(workflow for workflow in catalog["workflows"] if workflow["slug"] == "dev-loop")
    assert dev_loop["agents"] == [
        "brief-author",
        "principal-engineer",
        "qa-engineer",
        "pr-reviewer",
    ]
    for agent in catalog["agents"]:
        assert agent["useWhen"]
        assert agent["doNotUseWhen"]
        assert "**Use this agent when:**" not in agent["useWhen"]
        assert "**Do not use this agent when:**" not in agent["useWhen"]
        assert "**Do not use this agent when:**" not in agent["doNotUseWhen"]

    designer = next(agent for agent in catalog["agents"] if agent["slug"] == "ux-ui-designer")
    assert "approved brief or specification" in designer["useWhen"]
    assert "new brand/visual identity" in designer["doNotUseWhen"]
