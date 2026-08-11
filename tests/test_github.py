import json
import subprocess
from pathlib import Path

import pytest

from agent_workflows.github import merge_gate, merge_policy, merge_pull_request, resolve_review_thread
from agent_workflows.library import LibraryError
from agent_workflows.profiles import default_profile, project_toml


def _enable_dev_loop(project: Path) -> None:
    (project / "172x.toml").write_bytes(project_toml(default_profile()))


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


def _mock_gh(monkeypatch, *, pr: dict[str, object], threads: dict[str, object], merged: bool = True):
    calls: list[list[str]] = []
    state = {"merged": False}

    monkeypatch.setattr("agent_workflows.github.shutil.which", lambda _: "/usr/local/bin/gh")

    def run(arguments, **_kwargs):
        calls.append(arguments)
        command = arguments[1:]
        if command[:2] == ["auth", "status"]:
            return subprocess.CompletedProcess(arguments, 0, "authenticated\n", "")
        if command[:3] == ["repo", "view", "--json"]:
            return subprocess.CompletedProcess(arguments, 0, json.dumps({"nameWithOwner": "172x/example"}), "")
        if command[:3] == ["pr", "view", "17"]:
            if command[-1] == "state,mergedAt":
                result = {"state": "MERGED" if state["merged"] else "OPEN", "mergedAt": "now" if state["merged"] else None}
            else:
                result = pr
            return subprocess.CompletedProcess(arguments, 0, json.dumps(result), "")
        if command[:3] == ["api", "graphql", "-f"]:
            query = command[3]
            if "resolveReviewThread" in query:
                return subprocess.CompletedProcess(
                    arguments,
                    0,
                    json.dumps({"data": {"resolveReviewThread": {"thread": {"id": "PRRT_1", "isResolved": True}}}}),
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
    with pytest.raises(LibraryError, match="profile is missing"):
        merge_policy(tmp_path)

    (tmp_path / "172x.toml").write_text(
        "[host]\nid = \"codex\"\n\n[language]\nid = \"python\"\n\n[scm]\nid = \"git\"\n\n"
        "[provider]\nid = \"github\"\n\n[gate]\ntools = [\"mypy\"]\n\n"
        "[change_request]\nkind = \"pull_request\"\nbase_branch = \"release\"\nmerge_method = \"squash\"\nmerge_current_branch = true\n",
        encoding="utf-8",
    )
    with pytest.raises(LibraryError, match="base_branch must be main"):
        merge_policy(tmp_path)


def test_dev_loop_policy_handles_any_clean_current_branch_by_default(tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)

    policy = merge_policy(tmp_path)

    assert policy.merge_current_branch is True
    (tmp_path / "172x.toml").write_bytes(
        project_toml(default_profile()).replace(b"merge_current_branch = true", b"merge_current_branch = false")
    )
    assert merge_policy(tmp_path).merge_current_branch is False


def test_merge_gate_requires_live_github_evidence(monkeypatch, tmp_path: Path) -> None:
    _enable_dev_loop(tmp_path)
    calls = _mock_gh(monkeypatch, pr=_pr_json(), threads=_thread_response())

    gate = merge_gate(tmp_path, 17)

    assert gate.pr_number == 17
    assert gate.passing_checks == 1
    assert gate.resolved_threads == 1
    assert ["gh", "auth", "status"] in calls
    assert ["gh", "pr", "view", "17", "--json", "number,url,state,isDraft,baseRefName,mergeStateStatus,reviewDecision,statusCheckRollup,headRefOid"] in calls


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


def test_merge_rechecks_gate_and_pins_checked_head_without_bypass(monkeypatch, tmp_path: Path) -> None:
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

    assert any("resolveReviewThread" in command[4] for command in calls if command[1:3] == ["api", "graphql"])
