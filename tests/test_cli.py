from pathlib import Path

import typer
from typer.testing import CliRunner

from agent_workflows import agents_cli
from agent_workflows.agents_cli import create_app, workflow_id_completions
from agent_workflows.codex import install_configured_codex
from agent_workflows.github import MergeGate, MergePolicy
from agent_workflows.profiles import default_profile

runner = CliRunner()


def test_standalone_help_and_completion_generation_work(monkeypatch) -> None:
    monkeypatch.setenv("_TYPER_COMPLETE_TEST_DISABLE_SHELL_DETECTION", "1")
    app = create_app()

    help_result = runner.invoke(app, ["--help"])
    completion_result = runner.invoke(
        app,
        ["--show-completion", "bash"],
    )

    assert help_result.exit_code == 0
    assert "workflows" in help_result.output
    assert completion_result.exit_code == 0
    assert "complete" in completion_result.output


def test_workflow_commands_are_deterministic() -> None:
    app = create_app()

    listed = runner.invoke(app, ["workflows"])
    shown = runner.invoke(app, ["show", "dev"])
    unknown = runner.invoke(app, ["show", "missing"])

    assert listed.exit_code == 0
    assert listed.output.index("dev") < listed.output.index("idea-to-product")
    assert shown.exit_code == 0
    assert "## Purpose" in shown.output
    assert unknown.exit_code == 2
    assert "available" in unknown.output


def test_selection_without_launch_writes_expected_state(tmp_path: Path) -> None:
    app = create_app()
    install_configured_codex(tmp_path, default_profile())

    result = runner.invoke(
        app,
        ["--target", str(tmp_path), "--workflow", "dev", "--no-launch"],
    )

    assert result.exit_code == 0
    assert (tmp_path / ".172x/active-workflow").read_text(encoding="utf-8") == "dev\n"
    assert "172X · Dev" in result.output


def test_project_owned_workflow_lists_and_selects_without_launch(tmp_path: Path) -> None:
    app = create_app()
    workflow = tmp_path / ".172x/workflows/feedback-triage.md"
    workflow.parent.mkdir(parents=True)
    workflow.write_text(
        """---
id: feedback-triage
name: Feedback Triage Workflow
description: Converts validated feedback into a bounded engineering handoff.
version: 1
---
## Purpose
Turn feedback into an implementation handoff.
## Inputs
Feedback and repository context.
## Participating agents
- `discovery-specialist`
- `principal-engineer`
- `qa-engineer`
## Flow
1. `discovery-specialist` bounds the feedback.
2. `principal-engineer` implements the agreed work.
3. `qa-engineer` verifies it.
## Parallel work
None.
## Feedback loops
QA evidence returns to `principal-engineer` once.
## Human gates
The human approves scope and decides next steps.
## Completion criteria
A bounded handoff and QA evidence exist.
## Failure and escalation
Stop for ambiguous feedback.
""",
        encoding="utf-8",
    )
    install_configured_codex(tmp_path, default_profile())

    listed = runner.invoke(app, ["workflows", "--target", str(tmp_path)])
    selected = runner.invoke(
        app,
        ["--target", str(tmp_path), "--workflow", "feedback-triage", "--no-launch"],
    )

    assert listed.exit_code == 0
    assert "feedback-triage" in listed.output
    assert selected.exit_code == 0
    assert "172X · Feedback Triage" in selected.output
    assert (tmp_path / ".172x/active-workflow").read_text(encoding="utf-8") == "feedback-triage\n"


def test_launch_uses_selected_workflow(monkeypatch, tmp_path: Path) -> None:
    app = create_app()
    install_configured_codex(tmp_path, default_profile())
    launched: list[tuple[Path, str, tuple[str, ...]]] = []
    monkeypatch.setattr(
        agents_cli,
        "launch_codex",
        lambda target, workflow, options=(): launched.append((target, workflow, options)),
    )

    result = runner.invoke(app, ["--target", str(tmp_path), "--workflow", "dev"])

    assert result.exit_code == 0
    assert launched == [(tmp_path, "dev", ())]


def test_workflow_launch_forwards_codex_options(monkeypatch, tmp_path: Path) -> None:
    app = create_app()
    install_configured_codex(tmp_path, default_profile())
    launched: list[tuple[str, ...]] = []
    monkeypatch.setattr(
        agents_cli,
        "launch_codex",
        lambda target, workflow, options=(): launched.append(options),
    )

    result = runner.invoke(
        app,
        [
            "--workflow",
            "dev",
            "--target",
            str(tmp_path),
            "--model",
            "gpt-5.4",
            "--ask-for-approval",
            "never",
        ],
    )

    assert result.exit_code == 0
    assert launched == [("--model", "gpt-5.4", "--ask-for-approval", "never")]


def test_workflow_launch_accepts_unknown_codex_option_before_workflow(
    monkeypatch, tmp_path: Path
) -> None:
    app = create_app()
    install_configured_codex(tmp_path, default_profile())
    launched: list[tuple[str, ...]] = []
    monkeypatch.setattr(
        agents_cli,
        "launch_codex",
        lambda target, workflow, options=(): launched.append(options),
    )

    result = runner.invoke(
        app,
        ["--yolo", "--workflow", "dev", "--target", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert launched == [("--yolo",)]


def test_missing_codex_keeps_selection_and_explains_next_step(monkeypatch, tmp_path: Path) -> None:
    app = create_app()
    install_configured_codex(tmp_path, default_profile())
    monkeypatch.setattr(
        agents_cli,
        "launch_codex",
        lambda target, workflow, options=(): (_ for _ in ()).throw(FileNotFoundError("not found")),
    )

    result = runner.invoke(app, ["--target", str(tmp_path), "--workflow", "dev"])

    assert result.exit_code == 1
    assert (tmp_path / ".172x/active-workflow").read_text(encoding="utf-8") == "dev\n"
    assert "172X · Dev" in result.output


def test_agents_app_mounts_beneath_the_172x_product_name() -> None:
    root = typer.Typer()
    root.add_typer(create_app(), name="agents")

    result = runner.invoke(root, ["agents", "workflows"])

    assert result.exit_code == 0
    assert "Development Workflow" in result.output


def test_workflow_completion_is_bounded_and_descriptive() -> None:
    assert workflow_id_completions("d") == [
        ("dev", "Coding, independent QA, and PR review with a human merge decision."),
        (
            "dev-loop",
            "Experimental brief-to-branch development, independent review, and protected merge to main.",
        ),
    ]
    assert workflow_id_completions("IDEA") == [
        (
            "idea-to-build",
            "Turns a documented vision into reviewed UX and architecture, implementation, QA, and a human decision.",
        ),
        ("idea-to-product", "Discovery through evidence-backed review and human approval."),
    ]
    assert workflow_id_completions("missing") == []


def test_domains_are_available() -> None:
    app = create_app()

    domains = runner.invoke(app, ["domains"])

    assert domains.exit_code == 0
    assert "Quality" in domains.output
    assert "Security" in domains.output


def test_guarded_github_commands_are_exposed_without_running_a_real_merge(
    monkeypatch, tmp_path: Path
) -> None:
    app = create_app()
    gate = MergeGate(
        pr_number=17,
        url="https://github.com/172x/example/pull/17",
        head_oid="abc123",
        policy=MergePolicy(base_branch="main", merge_method="squash", merge_current_branch=True),
        passing_checks=2,
        resolved_threads=3,
    )
    monkeypatch.setattr(agents_cli, "merge_gate", lambda target, number: gate)
    monkeypatch.setattr(agents_cli, "merge_pull_request", lambda target, number: (gate, True))

    checked = runner.invoke(app, ["github", "gate", "17", "--target", str(tmp_path)])
    merged = runner.invoke(app, ["github", "merge", "17", "--target", str(tmp_path)])

    assert checked.exit_code == 0
    assert "eligible for dev-loop merge" in checked.output
    assert "GitHub checks: 2 passed" in checked.output
    assert merged.exit_code == 0
    assert "Merged PR #17 into main" in merged.output


def test_profiled_codex_install_writes_reviewed_project_config(monkeypatch, tmp_path: Path) -> None:
    app = create_app()
    monkeypatch.setattr(agents_cli, "_check_profile_prerequisites", lambda target, profile: None)
    monkeypatch.setattr(
        agents_cli,
        "gate_install_command",
        lambda target, profile: ("uv", "add", "--dev", *profile.gate_tools),
    )
    monkeypatch.setattr(
        agents_cli, "install_gate_tools", lambda target, profile: ("uv", "add", "--dev")
    )

    result = runner.invoke(
        app,
        [
            "install",
            "codex",
            "python",
            "--gate",
            "mypy",
            "--gate",
            "ruff",
            "--target",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    profile = (tmp_path / "172x.toml").read_text(encoding="utf-8")
    assert 'id = "codex"' in profile
    assert 'id = "python"' in profile
    assert 'id = "github"' in profile


def test_profiled_install_rejects_planned_capabilities_and_lists_statuses(
    monkeypatch, tmp_path: Path
) -> None:
    app = create_app()
    monkeypatch.setattr(agents_cli, "_check_profile_prerequisites", lambda target, profile: None)

    unsupported = runner.invoke(app, ["install", "codex", "rust", "--target", str(tmp_path)])
    listed = runner.invoke(app, ["capabilities"])

    assert unsupported.exit_code == 1
    assert "planned but not implemented" in unsupported.output
    assert listed.exit_code == 0
    assert "bitbucket" in listed.output
    assert "planned" in listed.output


def test_guided_install_uses_supported_defaults(monkeypatch, tmp_path: Path) -> None:
    app = create_app()
    monkeypatch.setattr(agents_cli, "_check_profile_prerequisites", lambda target, profile: None)
    monkeypatch.setattr(
        agents_cli,
        "gate_install_command",
        lambda target, profile: ("uv", "add", "--dev", *profile.gate_tools),
    )
    monkeypatch.setattr(
        agents_cli, "install_gate_tools", lambda target, profile: ("uv", "add", "--dev")
    )

    result = runner.invoke(
        app,
        ["install", "--target", str(tmp_path)],
        input="codex\npython\nmypy, ruff\n",
    )

    assert result.exit_code == 0
    config = (tmp_path / "172x.toml").read_text(encoding="utf-8")
    assert 'tools = ["mypy", "ruff"]' in config


def test_codex_install_prompts_for_and_installs_default_gate_tools(
    monkeypatch, tmp_path: Path
) -> None:
    app = create_app()
    installed: list[tuple[str, ...]] = []
    monkeypatch.setattr(agents_cli, "_check_profile_prerequisites", lambda target, profile: None)
    monkeypatch.setattr(
        agents_cli,
        "gate_install_command",
        lambda target, profile: ("uv", "add", "--dev", *profile.gate_tools),
    )
    monkeypatch.setattr(
        agents_cli,
        "install_gate_tools",
        lambda target, profile: installed.append(profile.gate_tools) or ("uv", "add", "--dev"),
    )

    result = runner.invoke(
        app,
        ["install", "codex", "python", "--target", str(tmp_path)],
        input="\n",
    )

    assert result.exit_code == 0
    assert "Gate tools to install" in result.output
    assert installed == [("mypy", "ruff", "radon", "pytest")]
    assert "Installing selected gate tools: uv add --dev mypy ruff radon pytest" in result.output


def test_install_does_not_treat_reviewer_identity_check_as_a_prerequisite(
    monkeypatch, tmp_path: Path
) -> None:
    profile = default_profile()
    monkeypatch.setattr(
        agents_cli,
        "prerequisite_rows",
        lambda target, selected: (("GitHub reviewer identity", False, "configure one"),),
    )

    agents_cli._check_profile_prerequisites(tmp_path, profile)
