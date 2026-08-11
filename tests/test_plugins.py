from importlib import metadata

import typer

from agent_workflows.agents_cli import create_app


def test_agents_registers_standalone_commands_and_umbrella_plugin() -> None:
    distribution = metadata.distribution("172x-agents")
    scripts = {
        entry_point.name: entry_point.value
        for entry_point in distribution.entry_points
        if entry_point.group == "console_scripts"
    }
    plugins = {
        entry_point.name: entry_point.value
        for entry_point in distribution.entry_points
        if entry_point.group == "172x.commands"
    }

    assert scripts == {
        "172x-agents": "agent_workflows.agents_cli:main",
        "agents": "agent_workflows.agents_cli:main",
    }
    assert plugins == {"agents": "agent_workflows.agents_cli:create_app"}
    assert "172x" not in scripts


def test_agents_plugin_factory_returns_product_command_group() -> None:
    assert isinstance(create_app(), typer.Typer)
