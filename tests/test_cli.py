import subprocess
from pathlib import Path

import typer
from typer.testing import CliRunner

from agent_workflows import agents_cli
from agent_workflows.agents_cli import create_app, workflow_id_completions
from agent_workflows.codex import install_codex
from agent_workflows.github import (
    GitHubReviewer,
    MergeCapabilities,
    MergeGate,
    MergePolicy,
    ReviewerStatus,
    ReviewSubmission,
)
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
    assert "refresh" in help_result.output
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


def test_refresh_updates_local_cli_and_global_skills_from_checkout(
    monkeypatch, tmp_path: Path
) -> None:
    home = _global_home(monkeypatch, tmp_path)
    checkout = tmp_path / "172x-agents"
    nested = checkout / "src"
    nested.mkdir(parents=True)
    (checkout / "pyproject.toml").write_text(
        "[project]\nname = '172x-agents'\n",
        encoding="utf-8",
    )
    refreshed: list[Path] = []
    monkeypatch.setattr(agents_cli, "_refresh_editable_cli", refreshed.append)
    monkeypatch.chdir(nested)

    result = runner.invoke(create_app(), ["refresh"])

    assert result.exit_code == 0
    assert refreshed == [checkout]
    assert "Editable 'agents' CLI: refreshed" in result.output
    assert (home / "skills/172x-agents/SKILL.md").is_file()


def test_refresh_dry_run_does_not_write_or_install(tmp_path: Path) -> None:
    checkout = tmp_path / "172x-agents"
    checkout.mkdir()
    (checkout / "pyproject.toml").write_text(
        "[project]\nname = '172x-agents'\n",
        encoding="utf-8",
    )

    result = runner.invoke(create_app(), ["refresh", "--source", str(checkout), "--dry-run"])

    assert result.exit_code == 0
    assert "Would refresh the editable 'agents' CLI with uv." in result.output
    assert not (checkout / ".172x").exists()


def test_refresh_rejects_non_172x_agents_checkout(tmp_path: Path) -> None:
    project = tmp_path / "other-project"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        "[project]\nname = 'other-project'\n",
        encoding="utf-8",
    )

    result = runner.invoke(create_app(), ["refresh", "--source", str(project)])

    assert result.exit_code == 1
    assert "must run inside a local 172x-agents checkout" in result.output


def test_refresh_uses_uv_editable_force_install(monkeypatch, tmp_path: Path) -> None:
    checkout = tmp_path / "172x-agents"
    checkout.mkdir()
    calls: list[tuple[list[str], Path]] = []

    def fake_run(
        arguments: list[str],
        *,
        cwd: Path,
        shell: bool,
        check: bool,
        capture_output: bool,
        text: bool,
    ) -> subprocess.CompletedProcess[str]:
        calls.append((arguments, cwd))
        assert shell is False
        assert check is False
        assert capture_output is True
        assert text is True
        return subprocess.CompletedProcess(arguments, 0, "", "")

    monkeypatch.setattr(agents_cli.shutil, "which", lambda name: "/usr/local/bin/uv")
    monkeypatch.setattr(agents_cli.subprocess, "run", fake_run)

    agents_cli._refresh_editable_cli(checkout)

    assert calls == [
        (
            ["/usr/local/bin/uv", "tool", "install", "--editable", str(checkout), "--force"],
            checkout,
        )
    ]


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


def test_activation_initializes_provider_config_inside_git_metadata(tmp_path: Path) -> None:
    project = tmp_path / "project"
    project.mkdir()
    (project / ".git").mkdir()

    previous = Path.cwd()
    try:
        import os

        os.chdir(project)
        result = runner.invoke(create_app(), ["activate", "python", "--gate", "ruff"])
    finally:
        os.chdir(previous)

    assert result.exit_code == 0
    assert "CREATE local Git provider config:" in result.output
    assert (project / ".git/172x/config.toml").is_file()
    assert not (project / "172x.toml").exists()


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


def test_rust_language_can_be_activated(tmp_path: Path) -> None:
    previous = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        result = runner.invoke(create_app(), ["activate", "rust", "--gate", "clippy"])
    finally:
        os.chdir(previous)

    assert result.exit_code == 0
    assert load_profile(tmp_path).language == "rust"
    assert load_profile(tmp_path).gate_tools == ("clippy",)


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


def test_providers_lists_registered_provider_capabilities() -> None:
    result = runner.invoke(create_app(), ["providers"])

    assert result.exit_code == 0
    assert "source_control:github" in result.output
    assert "change_request" in result.output
    assert "merge" in result.output


def test_github_merge_policy_reports_provider_compatibility(monkeypatch, tmp_path: Path) -> None:
    from types import SimpleNamespace

    provider = SimpleNamespace(
        key=SimpleNamespace(name="github", qualified_name="source_control:github"),
        merges=SimpleNamespace(
            merge_policy=lambda target: MergePolicy(
                base_branch="main", merge_method="rebase", merge_current_branch=True
            ),
            merge_capabilities=lambda target: MergeCapabilities(
                methods=frozenset({"rebase"}), default_method="rebase"
            ),
        ),
    )
    monkeypatch.setattr(agents_cli, "_github_provider", lambda target: provider)

    result = runner.invoke(create_app(), ["github", "merge-policy", "--target", str(tmp_path)])

    assert result.exit_code == 0
    assert "Configured method: rebase" in result.output
    assert "Provider allowed methods: rebase" in result.output
    assert "Provider default base branch: unknown" in result.output
    assert "Compatibility: PASS" in result.output


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
        change_request_number=17,
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


def test_reviewer_commands_expose_configured_identity_without_secret_values(
    monkeypatch, tmp_path: Path
) -> None:
    (tmp_path / "172x.toml").write_text(
        """[github.review]

[[github.review.reviewers]]
login = "172x-reviewer-bot"
token_env = "REVIEWER_GH_TOKEN"
""",
        encoding="utf-8",
    )
    monkeypatch.setenv("REVIEWER_GH_TOKEN", "secret-value")
    listed = runner.invoke(create_app(), ["github", "reviewers", "--target", str(tmp_path)])

    monkeypatch.setattr(
        agents_cli,
        "reviewer_status",
        lambda target, login: ReviewerStatus(
            reviewer=GitHubReviewer(login=login, token_env="REVIEWER_GH_TOKEN"),
            authenticated_login=login,
            repository_permission="WRITE",
        ),
    )
    status = runner.invoke(
        create_app(),
        ["github", "reviewer-status", "--reviewer", "172x-reviewer-bot", "--target", str(tmp_path)],
    )

    assert listed.exit_code == 0
    assert "172x-reviewer-bot" in listed.output
    assert "secret-value" not in listed.output
    assert status.exit_code == 0
    assert "Repository permission: WRITE" in status.output


def test_review_and_approve_commands_forward_exact_head_and_report(
    monkeypatch, tmp_path: Path
) -> None:
    report = tmp_path / "report.md"
    report.write_text("# Report\n", encoding="utf-8")
    submission = ReviewSubmission(
        change_request_number=17,
        reviewer="172x-reviewer-bot",
        head_oid="abc123",
        state="COMMENTED",
    )
    approval = ReviewSubmission(
        change_request_number=17,
        reviewer="172x-reviewer-bot",
        head_oid="abc123",
        state="APPROVED",
    )
    monkeypatch.setattr(agents_cli, "submit_review", lambda *args: submission)
    monkeypatch.setattr(agents_cli, "approve_pull_request", lambda *args: approval)

    reviewed = runner.invoke(
        create_app(),
        [
            "github",
            "review",
            "17",
            "--reviewer",
            "172x-reviewer-bot",
            "--head",
            "abc123",
            "--report",
            str(report),
        ],
    )
    approved = runner.invoke(
        create_app(),
        [
            "github",
            "approve",
            "17",
            "--reviewer",
            "172x-reviewer-bot",
            "--head",
            "abc123",
            "--report",
            str(report),
        ],
    )

    assert reviewed.exit_code == 0
    assert "COMMENTED" in reviewed.output
    assert approved.exit_code == 0
    assert "APPROVED" in approved.output


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
