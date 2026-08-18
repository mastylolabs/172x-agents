from pathlib import Path

import typer
from typer.testing import CliRunner

from agent_workflows import agents_cli
from agent_workflows.agents_cli import create_app, workflow_id_completions
from agent_workflows.codex import install_codex
from agent_workflows.github import MergeGate, MergePolicy
from agent_workflows.profiles import load_profile

runner = CliRunner()


def _global_home(monkeypatch, tmp_path: Path) -> Path:
    home = tmp_path / "codex-home"
    monkeypatch.setenv("CODEX_HOME", str(home))
    return home


def test_standalone_help_and_completion_generation_work(monkeypatch) -> None:
    monkeypatch.setenv("_TYPER_COMPLETE_TEST_DISABLE_SHELL_DETECTION", "1")

    help_result = runner.invoke(create_app(), ["--help"])
    completion_result = runner.invoke(create_app(), ["--show-completion", "bash"])

    assert help_result.exit_code == 0
    assert "activate" in help_result.output
    assert "Select a bundled" in help_result.output
    assert completion_result.exit_code == 0
    assert "complete" in completion_result.output


def test_workflow_commands_are_deterministic() -> None:
    listed = runner.invoke(create_app(), ["workflows"])
    shown = runner.invoke(create_app(), ["show", "dev"])
    unknown = runner.invoke(create_app(), ["show", "missing"])

    assert listed.exit_code == 0
    assert listed.output.index("dev") < listed.output.index("idea-to-product")
    assert shown.exit_code == 0
    assert "## Purpose" in shown.output
    assert unknown.exit_code == 2


def test_project_workflow_is_listable_and_showable_but_not_selectable(
    monkeypatch, tmp_path: Path
) -> None:
    home = _global_home(monkeypatch, tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    _write_project_workflow(project)
    install_codex(home)

    listed = runner.invoke(create_app(), ["workflows", "--target", str(project)])
    shown = runner.invoke(create_app(), ["show", "custom-check", "--target", str(project)])
    selected = runner.invoke(
        create_app(),
        ["--target", str(project), "--workflow", "custom-check", "--no-launch"],
    )

    assert listed.exit_code == 0
    assert "custom-check" in listed.output
    assert shown.exit_code == 0
    assert "Custom Check Workflow" in shown.output
    assert selected.exit_code == 2
    assert "unknown workflow ID 'custom-check'" in selected.output
    assert not (project / ".172x/active-workflow").exists()
    composer = (home / "skills/172x-workflow-composer/SKILL.md").read_text(encoding="utf-8")
    assert "not selectable or runnable" in composer


def test_global_install_is_language_neutral_and_supports_focused_capabilities(
    monkeypatch, tmp_path: Path
) -> None:
    home = _global_home(monkeypatch, tmp_path)

    result = runner.invoke(
        create_app(), ["install", "codex", "--only", "principal-codebase-reviewer"]
    )

    assert result.exit_code == 0
    assert "Gate tools" not in result.output
    assert (home / "skills/172x-principal-codebase-reviewer/SKILL.md").is_file()
    assert not (home / "skills/172x-principal-engineer").exists()
    assert not (tmp_path / ".172x").exists()


def test_global_install_dry_run_never_writes(monkeypatch, tmp_path: Path) -> None:
    home = _global_home(monkeypatch, tmp_path)

    result = runner.invoke(create_app(), ["install", "codex", "--dry-run"])

    assert result.exit_code == 0
    assert "No files written." in result.output
    assert not home.exists()


def test_global_uninstall_supports_dry_run_and_focused_capabilities(
    monkeypatch, tmp_path: Path
) -> None:
    home = _global_home(monkeypatch, tmp_path)
    install_codex(home)

    dry_run = runner.invoke(
        create_app(), ["uninstall", "codex", "--only", "principal-codebase-reviewer", "--dry-run"]
    )

    assert dry_run.exit_code == 0
    assert "DELETE skills/172x-principal-codebase-reviewer" in dry_run.output
    assert "No files deleted." in dry_run.output
    assert (home / "skills/172x-principal-codebase-reviewer/SKILL.md").is_file()

    result = runner.invoke(
        create_app(), ["uninstall", "codex", "--only", "principal-codebase-reviewer"]
    )

    assert result.exit_code == 0
    assert not (home / "skills/172x-principal-codebase-reviewer").exists()
    assert (home / "skills/172x-agents/SKILL.md").is_file()


def test_activation_records_local_context_without_installing_tools(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()

    previous = Path.cwd()
    try:
        import os

        os.chdir(project)
        result = runner.invoke(
            create_app(), ["activate", "python", "--gate", "ruff", "--gate", "pytest"]
        )
    finally:
        os.chdir(previous)

    assert result.exit_code == 0
    assert load_profile(project).gate_tools == ("ruff", "pytest")
    assert "No external tools" in result.output
    assert not (project / "pyproject.toml").exists()


def test_activation_supports_a_monorepo_subproject_path(tmp_path: Path) -> None:
    package = tmp_path / "services" / "api"
    package.mkdir(parents=True)
    previous = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        result = runner.invoke(
            create_app(), ["activate", "python", "--path", "services/api", "--gate", "ruff"]
        )
    finally:
        os.chdir(previous)

    assert result.exit_code == 0
    assert load_profile(package).gate_tools == ("ruff",)


def test_planned_language_cannot_be_activated(tmp_path: Path) -> None:
    previous = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        result = runner.invoke(create_app(), ["activate", "rust", "--gate", "clippy"])
    finally:
        os.chdir(previous)

    assert result.exit_code == 1
    assert "planned but not implemented" in result.output


def test_selection_without_launch_uses_global_install_and_writes_local_state(
    monkeypatch, tmp_path: Path
) -> None:
    home = _global_home(monkeypatch, tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    install_codex(home)

    result = runner.invoke(
        create_app(), ["--target", str(project), "--workflow", "dev", "--no-launch"]
    )

    assert result.exit_code == 0
    assert (project / ".172x/active-workflow").read_text(encoding="utf-8") == "dev\n"
    assert "172X · Dev" in result.output


def test_launch_uses_selected_workflow(monkeypatch, tmp_path: Path) -> None:
    home = _global_home(monkeypatch, tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    install_codex(home)
    launched: list[tuple[Path, str, tuple[str, ...]]] = []
    monkeypatch.setattr(
        agents_cli,
        "launch_codex",
        lambda target, workflow, options=(): launched.append((target, workflow, options)),
    )

    result = runner.invoke(create_app(), ["--target", str(project), "--workflow", "dev"])

    assert result.exit_code == 0
    assert launched == [(project, "dev", ())]


def test_workflow_completion_is_bounded_and_descriptive() -> None:
    assert workflow_id_completions("d") == [
        ("dev", "Coding, independent QA, and PR review with a human merge decision."),
        (
            "dev-loop",
            "Experimental brief-to-branch development, independent review, and guarded merge to main.",
        ),
    ]
    assert workflow_id_completions("missing") == []


def test_domains_and_capabilities_are_available() -> None:
    domains = runner.invoke(create_app(), ["domains"])
    capabilities = runner.invoke(create_app(), ["capabilities"])

    assert domains.exit_code == 0
    assert "Quality" in domains.output
    assert capabilities.exit_code == 0
    assert "rust" in capabilities.output
    assert "planned" in capabilities.output


def test_doctor_reports_global_install_and_local_activation(monkeypatch, tmp_path: Path) -> None:
    home = _global_home(monkeypatch, tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    install_codex(home)
    previous = Path.cwd()
    try:
        import os

        os.chdir(project)
        activated = runner.invoke(create_app(), ["activate", "python", "--gate", "ruff"])
    finally:
        os.chdir(previous)
    assert activated.exit_code == 0
    monkeypatch.setattr(
        agents_cli,
        "prerequisite_rows",
        lambda _target, _profile: (("Gate tool: ruff", True, "ruff --version"),),
    )
    monkeypatch.setattr("agent_workflows.agents_cli.shutil.which", lambda value: "/usr/bin/codex")

    result = runner.invoke(create_app(), ["doctor", "--target", str(project)])

    assert result.exit_code == 0
    assert "Global Forge:     OK (complete" in result.output
    assert "Activation:       OK (python; gates: ruff)" in result.output


def test_guarded_github_commands_are_exposed_without_running_a_real_merge(
    monkeypatch, tmp_path: Path
) -> None:
    gate = MergeGate(
        pr_number=17,
        url="https://github.com/172x/example/pull/17",
        head_oid="abc123",
        policy=MergePolicy(base_branch="main", merge_method="squash", merge_current_branch=True),
        reported_checks=2,
        resolved_threads=3,
    )
    monkeypatch.setattr(agents_cli, "merge_gate", lambda target, number: gate)
    monkeypatch.setattr(agents_cli, "merge_pull_request", lambda target, number: (gate, True))

    checked = runner.invoke(create_app(), ["github", "gate", "17", "--target", str(tmp_path)])
    merged = runner.invoke(create_app(), ["github", "merge", "17", "--target", str(tmp_path)])

    assert checked.exit_code == 0
    assert "eligible for dev-loop merge" in checked.output
    assert merged.exit_code == 0
    assert "Merged PR #17 into main" in merged.output


def test_agents_app_mounts_beneath_the_172x_product_name() -> None:
    root = typer.Typer()
    root.add_typer(create_app(), name="agents")

    result = runner.invoke(root, ["agents", "workflows"])

    assert result.exit_code == 0
    assert "Development Workflow" in result.output


def _write_project_workflow(project: Path) -> None:
    workflow = project / ".172x/workflows/custom-check.md"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        """---
id: custom-check
name: Custom Check Workflow
description: A valid local workflow for inspection.
version: 1
---
## Purpose
Inspect a project-owned workflow.

## Inputs
An identified task.

## Participating agents
- `qa-engineer`

## Flow
1. `qa-engineer` checks the supplied artifact.

## Parallel work
No work runs in parallel.

## Feedback loops
One evidence return is allowed before human escalation.

## Human gates
The human decides what to do with the inspection result.

## Completion criteria
The inspection result and human decision are recorded.

## Failure and escalation
Stop when evidence is missing or the return limit is reached.
""",
        encoding="utf-8",
    )
