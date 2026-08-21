import json
import subprocess
from pathlib import Path

import pytest

from agent_workflows.github import (
    GitHubReviewer,
    approve_pull_request,
    configured_reviewers,
    merge_gate,
    merge_policy,
    merge_pull_request,
    resolve_review_thread,
    reviewer_status,
    submit_review,
)
from agent_workflows.library import LibraryError
from agent_workflows.profiles import default_profile, write_activation


def _enable_dev_loop(project: Path) -> None:
    write_activation(project, Path("."), default_profile())
    (project / "172x.toml").write_text(
        """[github.review]

[[github.review.reviewers]]
login = "172x-reviewer-bot"
token_env = "REVIEWER_GH_TOKEN"
""",
        encoding="utf-8",
    )


def _pr_json(*, checks: list[dict[str, object]] | None = None) -> dict[str, object]:
    return {
        "number": 17,
        "url": "https://github.com/172x/example/pull/17",
        "state": "OPEN",
        "isDraft": False,
        "baseRefName": "main",
        "mergeStateStatus": "CLEAN",
        "reviewDecision": "APPROVED",
        "statusCheckRollup": checks
        if checks is not None
        else [{"name": "tests", "status": "COMPLETED", "conclusion": "SUCCESS"}],
        "headRefOid": "abc123",
    }


def _thread_response(*, unresolved: bool = False) -> dict[str, object]:
    return {
        "data": {
            "repository": {
                "pullRequest": {
                    "reviewThreads": {
                        "nodes": [
                            {
                                "id": "PRRT_1",
                                "isResolved": not unresolved,
                                "comments": {"nodes": []},
                            }
                        ],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        }
    }


def _mock_gh(
    monkeypatch,
    *,
    pr: dict[str, object],
    threads: dict[str, object],
    merged: bool = True,
    merge_methods: tuple[str, ...] = ("merge", "rebase", "squash"),
    default_merge_method: str = "SQUASH",
):
    calls: list[list[str]] = []
    state = {"merged": False}
    review_state = {"value": "APPROVED"}

    monkeypatch.setattr("agent_workflows.github.shutil.which", lambda _: "/usr/local/bin/gh")
    monkeypatch.setenv("REVIEWER_GH_TOKEN", "reviewer-secret")

    def run(arguments, **_kwargs):
        calls.append(arguments)
        command = arguments[1:]
        if command[:2] == ["auth", "status"]:
            return subprocess.CompletedProcess(arguments, 0, "authenticated\n", "")
        if command[:3] == ["api", "user", "--jq"]:
            return subprocess.CompletedProcess(arguments, 0, "172x-reviewer-bot\n", "")
        if command[:3] == ["repo", "view", "--json"]:
            if command[-1] == "viewerPermission":
                return subprocess.CompletedProcess(
                    arguments, 0, json.dumps({"viewerPermission": "WRITE"}), ""
                )
            if command[-1] == (
                "nameWithOwner,defaultBranchRef,mergeCommitAllowed,rebaseMergeAllowed,"
                "squashMergeAllowed,viewerDefaultMergeMethod"
            ):
                return subprocess.CompletedProcess(
                    arguments,
                    0,
                    json.dumps(
                        {
                            "nameWithOwner": "172x/example",
                            "defaultBranchRef": {"name": "main"},
                            "mergeCommitAllowed": "merge" in merge_methods,
                            "rebaseMergeAllowed": "rebase" in merge_methods,
                            "squashMergeAllowed": "squash" in merge_methods,
                            "viewerDefaultMergeMethod": default_merge_method,
                        }
                    ),
                    "",
                )
            return subprocess.CompletedProcess(
                arguments, 0, json.dumps({"nameWithOwner": "172x/example"}), ""
            )
        if command[:3] == ["pr", "view", "17"]:
            if command[-1] == "state,mergedAt":
                result = {
                    "state": "MERGED" if state["merged"] else "OPEN",
                    "mergedAt": "now" if state["merged"] else None,
                }
            elif command[-1] == "reviews":
                result = {
                    "reviews": [
                        {
                            "author": {"login": "172x-reviewer-bot"},
                            "state": review_state["value"],
                            "commit": {"oid": "abc123"},
                            "submittedAt": "2026-08-19T00:00:00Z",
                        }
                    ]
                }
            elif command[-1] == "number,state,isDraft,headRefOid,author":
                result = {**pr, "author": {"login": "principal-engineer"}}
            else:
                result = pr
            return subprocess.CompletedProcess(arguments, 0, json.dumps(result), "")
        if command[:3] == ["pr", "review", "17"]:
            review_state["value"] = "APPROVED" if "--approve" in command else "COMMENTED"
            return subprocess.CompletedProcess(arguments, 0, "", "")
        if command[:3] == ["api", "graphql", "-f"]:
            query = command[3]
            if "resolveReviewThread" in query:
                return subprocess.CompletedProcess(
                    arguments,
                    0,
                    json.dumps(
                        {
                            "data": {
                                "resolveReviewThread": {
                                    "thread": {"id": "PRRT_1", "isResolved": True}
                                }
                            }
                        }
                    ),
                    "",
                )
            return subprocess.CompletedProcess(arguments, 0, json.dumps(threads), "")
        if command[:3] == ["pr", "merge", "17"]:
            state["merged"] = merged
            return subprocess.CompletedProcess(arguments, 0, "", "")
        raise AssertionError(f"unexpected gh command: {arguments}")

    monkeypatch.setattr("agent_workflows.github.subprocess.run", run)
    return calls


def test_merge_policy_requires_exact_repository_opt_in(tmp_path: Path) -> None:
    with pytest.raises(LibraryError, match="activation is missing"):
        merge_policy(tmp_path)


def test_dev_loop_policy_handles_any_clean_current_branch_by_default(tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)

    policy = merge_policy(tmp_path)

    assert policy.merge_current_branch is True
    assert policy.base_branch == "main"
    assert policy.merge_method == "squash"


def test_provider_capabilities_report_live_merge_methods(monkeypatch, tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)
    _mock_gh(
        monkeypatch,
        pr=_pr_json(),
        threads=_thread_response(),
        merge_methods=("rebase",),
        default_merge_method="REBASE",
    )

    from agent_workflows.github import merge_capabilities, provider_capabilities

    capabilities = provider_capabilities(tmp_path)
    merge = merge_capabilities(tmp_path)

    assert capabilities.default_base_branch == "main"
    assert capabilities.merge_methods == frozenset({"rebase"})
    assert merge.default_method == "rebase"


def test_explicit_rebase_policy_is_accepted_when_provider_allows_only_rebase(
    monkeypatch, tmp_path: Path
) -> None:
    _enable_dev_loop(tmp_path)
    config = (tmp_path / "172x.toml").read_text(encoding="utf-8")
    (tmp_path / "172x.toml").write_text(
        '[merge]\nmethod = "rebase"\n\n' + config,
        encoding="utf-8",
    )
    _mock_gh(
        monkeypatch,
        pr=_pr_json(),
        threads=_thread_response(),
        merge_methods=("rebase",),
        default_merge_method="REBASE",
    )

    gate = merge_gate(tmp_path, 17)

    assert gate.policy.merge_method == "rebase"
    assert gate.provider_capabilities is not None
    assert gate.provider_capabilities.merge_methods == frozenset({"rebase"})


def test_merge_gate_blocks_policy_not_allowed_by_provider(monkeypatch, tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)
    _mock_gh(
        monkeypatch,
        pr=_pr_json(),
        threads=_thread_response(),
        merge_methods=("rebase",),
        default_merge_method="REBASE",
    )

    with pytest.raises(LibraryError, match="configured merge method 'squash'.*rebase"):
        merge_gate(tmp_path, 17)


def test_merge_gate_requires_live_github_evidence(monkeypatch, tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)
    calls = _mock_gh(monkeypatch, pr=_pr_json(), threads=_thread_response())

    gate = merge_gate(tmp_path, 17)

    assert gate.pr_number == 17
    assert gate.reported_checks == 1
    assert gate.resolved_threads == 1
    assert ["gh", "auth", "status"] in calls
    assert [
        "gh",
        "pr",
        "view",
        "17",
        "--json",
        "number,url,state,isDraft,baseRefName,mergeStateStatus,reviewDecision,statusCheckRollup,headRefOid",
    ] in calls


def test_merge_gate_rejects_non_passing_checks_without_merge(monkeypatch, tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)
    calls = _mock_gh(
        monkeypatch,
        pr=_pr_json(checks=[{"name": "tests", "status": "COMPLETED", "conclusion": "FAILURE"}]),
        threads=_thread_response(),
    )

    with pytest.raises(LibraryError, match="failing checks: tests"):
        merge_pull_request(tmp_path, 17)

    assert not any(command[1:3] == ["pr", "merge"] for command in calls)


@pytest.mark.parametrize("checks", [[], None])
def test_merge_gate_allows_a_repository_with_no_reported_checks(
    monkeypatch, tmp_path: Path, checks: list[dict[str, object]] | None
) -> None:
    _enable_dev_loop(tmp_path)
    pull_request = _pr_json(checks=[])
    pull_request["statusCheckRollup"] = checks
    _mock_gh(monkeypatch, pr=pull_request, threads=_thread_response())

    gate = merge_gate(tmp_path, 17)

    assert gate.reported_checks == 0


def test_merge_rechecks_gate_and_pins_checked_head_without_bypass(
    monkeypatch, tmp_path: Path
) -> None:
    _enable_dev_loop(tmp_path)
    calls = _mock_gh(monkeypatch, pr=_pr_json(), threads=_thread_response())

    gate, merged = merge_pull_request(tmp_path, 17)

    assert merged is True
    merge_command = next(command for command in calls if command[1:3] == ["pr", "merge"])
    assert merge_command == [
        "gh",
        "pr",
        "merge",
        "17",
        "--squash",
        "--match-head-commit",
        gate.head_oid,
    ]
    assert "--admin" not in merge_command
    assert "--auto" not in merge_command


def test_merge_gate_rejects_unresolved_threads_and_resolution_checks_membership(
    monkeypatch, tmp_path: Path
) -> None:
    _enable_dev_loop(tmp_path)
    calls = _mock_gh(monkeypatch, pr=_pr_json(), threads=_thread_response(unresolved=True))

    with pytest.raises(LibraryError, match="unresolved GitHub review thread"):
        merge_gate(tmp_path, 17)
    with pytest.raises(LibraryError, match="does not belong"):
        resolve_review_thread(tmp_path, 17, "PRRT_other")
    resolve_review_thread(tmp_path, 17, "PRRT_1")

    assert any(
        "resolveReviewThread" in command[4]
        for command in calls
        if command[1:3] == ["api", "graphql"]
    )


def test_configured_reviewers_are_loaded_without_secret_values(tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)

    assert configured_reviewers(tmp_path) == (
        GitHubReviewer(login="172x-reviewer-bot", token_env="REVIEWER_GH_TOKEN"),
    )


def test_configured_reviewers_use_list_length_as_required_reviewer_count(tmp_path: Path) -> None:
    (tmp_path / "172x.toml").write_text(
        """[github.review]

[[github.review.reviewers]]
login = "172x-reviewer-bot"
token_env = "REVIEWER_GH_TOKEN"

[[github.review.reviewers]]
login = "172x-second-reviewer"
token_env = "SECOND_REVIEWER_TOKEN"
""",
        encoding="utf-8",
    )

    reviewers = configured_reviewers(tmp_path)

    assert [item.login for item in reviewers] == ["172x-reviewer-bot", "172x-second-reviewer"]


def test_configured_reviewers_reject_duplicate_logins(tmp_path: Path) -> None:
    (tmp_path / "172x.toml").write_text(
        """[github.review]

[[github.review.reviewers]]
login = "172x-reviewer-bot"
token_env = "REVIEWER_GH_TOKEN"

[[github.review.reviewers]]
login = "172x-reviewer-bot"
token_env = "SECOND_REVIEWER_TOKEN"
""",
        encoding="utf-8",
    )

    with pytest.raises(LibraryError, match="duplicate GitHub reviewer login"):
        configured_reviewers(tmp_path)


def test_reviewer_status_verifies_identity_and_permission(monkeypatch, tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)
    _mock_gh(monkeypatch, pr=_pr_json(), threads=_thread_response())

    status = reviewer_status(tmp_path, "172x-reviewer-bot")

    assert status.authenticated_login == "172x-reviewer-bot"
    assert status.repository_permission == "WRITE"


def test_submit_review_uses_named_token_and_exact_head(monkeypatch, tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)
    report = tmp_path / "review.md"
    report.write_text("# Review\n\nCOMMENTED\n", encoding="utf-8")
    calls = _mock_gh(monkeypatch, pr=_pr_json(), threads=_thread_response())

    submission = submit_review(tmp_path, 17, "172x-reviewer-bot", "abc123", report)

    assert submission.state == "COMMENTED"
    review_command = next(command for command in calls if command[1:3] == ["pr", "review"])
    assert review_command[3:] == ["17", "--comment", "--body-file", str(report.resolve())]


def test_approve_review_confirms_provider_approval(monkeypatch, tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)
    report = tmp_path / "approval.md"
    report.write_text("# Approval\n\nAPPROVED\n", encoding="utf-8")
    _mock_gh(monkeypatch, pr=_pr_json(), threads=_thread_response())

    submission = approve_pull_request(tmp_path, 17, "172x-reviewer-bot", "abc123", report)

    assert submission.state == "APPROVED"


def test_reviewer_action_rejects_stale_head(monkeypatch, tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)
    report = tmp_path / "review.md"
    report.write_text("# Review\n", encoding="utf-8")
    _mock_gh(monkeypatch, pr=_pr_json(), threads=_thread_response())

    with pytest.raises(LibraryError, match="head changed"):
        submit_review(tmp_path, 17, "172x-reviewer-bot", "stale", report)
