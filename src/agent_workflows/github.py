"""Narrow, fail-closed GitHub CLI helpers for the autonomous dev loop."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .library import LibraryError
from .profiles import load_profile

_MERGE_METHOD_FLAGS = {"merge": "--merge", "rebase": "--rebase", "squash": "--squash"}
_PASSING_CHECK_STATES = {"SUCCESS", "NEUTRAL", "SKIPPED"}
_FAILING_CHECK_STATES = {
    "ACTION_REQUIRED",
    "CANCELLED",
    "FAILURE",
    "STALE",
    "STARTUP_FAILURE",
    "TIMED_OUT",
}

_REVIEW_THREADS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $cursor) {
        nodes {
          id
          isResolved
          comments(first: 1) {
            nodes {
              body
              path
              line
              url
              author { login }
            }
          }
        }
        pageInfo { hasNextPage endCursor }
      }
    }
  }
}
""".strip()

_RESOLVE_THREAD_MUTATION = """
mutation($threadId: ID!) {
  resolveReviewThread(input: {threadId: $threadId}) {
    thread { id isResolved }
  }
}
""".strip()


@dataclass(frozen=True)
class MergePolicy:
    """The repository-local choices that authorize a dev-loop GitHub action."""

    base_branch: str
    merge_method: str
    merge_current_branch: bool


@dataclass(frozen=True)
class MergeGate:
    """Evidence captured immediately before a guarded merge attempt."""

    pr_number: int
    url: str
    head_oid: str
    policy: MergePolicy
    passing_checks: int
    resolved_threads: int


def _project_directory(target: Path) -> Path:
    project = target.expanduser().resolve()
    if not project.is_dir():
        raise LibraryError(f"target project is not a directory: {target}")
    return project


def _run_gh(target: Path, arguments: list[str]) -> str:
    if shutil.which("gh") is None:
        raise LibraryError(
            "GitHub CLI is not installed or not on PATH; install gh and authenticate it."
        )
    completed = subprocess.run(
        ["gh", *arguments],
        cwd=target,
        shell=False,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown GitHub CLI error"
        raise LibraryError(f"GitHub CLI command failed: {detail}")
    return completed.stdout


def _gh_json(target: Path, arguments: list[str]) -> dict[str, Any]:
    output = _run_gh(target, arguments)
    try:
        result = json.loads(output)
    except json.JSONDecodeError as error:
        raise LibraryError(
            "GitHub CLI returned invalid JSON; cannot evaluate the merge gate."
        ) from error
    if not isinstance(result, dict):
        raise LibraryError(
            "GitHub CLI returned an unexpected JSON result; cannot evaluate the merge gate."
        )
    return result


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise LibraryError(f"GitHub did not return {label}; cannot evaluate the merge gate.")
    return value


def merge_policy(target: Path) -> MergePolicy:
    """Read dev-loop merge choices from the reviewed project profile."""
    profile = load_profile(_project_directory(target))
    return MergePolicy(
        base_branch=profile.base_branch,
        merge_method=profile.merge_method,
        merge_current_branch=profile.merge_current_branch,
    )


def _require_authenticated_gh(target: Path) -> None:
    _run_gh(target, ["auth", "status"])


def _repository_name(target: Path) -> tuple[str, str]:
    repository = _gh_json(target, ["repo", "view", "--json", "nameWithOwner"])
    name_with_owner = _required_string(repository.get("nameWithOwner"), "repository name")
    owner, separator, name = name_with_owner.partition("/")
    if not separator or not owner or not name:
        raise LibraryError(
            "GitHub returned an invalid repository name; cannot evaluate the merge gate."
        )
    return owner, name


def review_threads(target: Path, pr_number: int) -> list[dict[str, Any]]:
    """Return all review threads for a PR through the authenticated GitHub CLI."""
    project = _project_directory(target)
    _require_authenticated_gh(project)
    owner, name = _repository_name(project)
    threads: list[dict[str, Any]] = []
    cursor: str | None = None
    while True:
        arguments = [
            "api",
            "graphql",
            "-f",
            f"query={_REVIEW_THREADS_QUERY}",
            "-F",
            f"owner={owner}",
            "-F",
            f"name={name}",
            "-F",
            f"number={pr_number}",
        ]
        if cursor is not None:
            arguments.extend(["-F", f"cursor={cursor}"])
        response = _gh_json(project, arguments)
        try:
            connection = response["data"]["repository"]["pullRequest"]["reviewThreads"]
            page_threads = connection["nodes"]
            page_info = connection["pageInfo"]
        except (KeyError, TypeError) as error:
            raise LibraryError(
                "GitHub returned incomplete review-thread data; cannot evaluate the merge gate."
            ) from error
        if not isinstance(page_threads, list) or not isinstance(page_info, dict):
            raise LibraryError(
                "GitHub returned invalid review-thread data; cannot evaluate the merge gate."
            )
        if not all(isinstance(thread, dict) for thread in page_threads):
            raise LibraryError(
                "GitHub returned invalid review-thread data; cannot evaluate the merge gate."
            )
        threads.extend(page_threads)
        has_next_page = page_info.get("hasNextPage")
        next_cursor = page_info.get("endCursor")
        if has_next_page is False:
            return threads
        if has_next_page is not True or not isinstance(next_cursor, str) or not next_cursor:
            raise LibraryError(
                "GitHub returned invalid review-thread pagination; cannot evaluate the merge gate."
            )
        cursor = next_cursor


def _check_name(check: dict[str, Any]) -> str:
    for key in ("name", "workflowName", "context"):
        value = check.get(key)
        if isinstance(value, str) and value:
            return value
    return "unnamed check"


def _check_state(check: dict[str, Any]) -> str:
    for key in ("conclusion", "state", "status"):
        value = check.get(key)
        if isinstance(value, str) and value:
            normalized = value.upper()
            if normalized in _PASSING_CHECK_STATES:
                return "passed"
            if normalized in _FAILING_CHECK_STATES:
                return "failed"
    return "pending"


def merge_gate(target: Path, pr_number: int) -> MergeGate:
    """Fail closed unless the live GitHub PR satisfies every merge requirement."""
    if pr_number < 1:
        raise LibraryError("pull request number must be a positive integer")
    project = _project_directory(target)
    policy = merge_policy(project)
    _require_authenticated_gh(project)
    pull_request = _gh_json(
        project,
        [
            "pr",
            "view",
            str(pr_number),
            "--json",
            "number,url,state,isDraft,baseRefName,mergeStateStatus,reviewDecision,statusCheckRollup,headRefOid",
        ],
    )
    if pull_request.get("state") != "OPEN":
        raise LibraryError("pull request is not open")
    if pull_request.get("isDraft") is not False:
        raise LibraryError("pull request is a draft")
    if pull_request.get("baseRefName") != policy.base_branch:
        raise LibraryError(f"pull request does not target {policy.base_branch}")
    if pull_request.get("mergeStateStatus") != "CLEAN":
        raise LibraryError("pull request is not currently clean and mergeable")
    if pull_request.get("reviewDecision") != "APPROVED":
        raise LibraryError("pull request does not have GitHub's APPROVED review decision")
    checks = pull_request.get("statusCheckRollup")
    if not isinstance(checks, list) or not checks:
        raise LibraryError("pull request has no reported GitHub checks; refusing autonomous merge")
    failed_checks: list[str] = []
    pending_checks: list[str] = []
    for check in checks:
        if not isinstance(check, dict):
            raise LibraryError(
                "GitHub returned invalid check data; cannot evaluate the merge gate."
            )
        state = _check_state(check)
        if state == "failed":
            failed_checks.append(_check_name(check))
        elif state != "passed":
            pending_checks.append(_check_name(check))
    if failed_checks:
        raise LibraryError(f"pull request has failing checks: {', '.join(failed_checks)}")
    if pending_checks:
        raise LibraryError(f"pull request has non-passing checks: {', '.join(pending_checks)}")
    threads = review_threads(project, pr_number)
    unresolved = [thread for thread in threads if thread.get("isResolved") is not True]
    if unresolved:
        raise LibraryError(f"pull request has {len(unresolved)} unresolved GitHub review thread(s)")
    return MergeGate(
        pr_number=pr_number,
        url=_required_string(pull_request.get("url"), "pull request URL"),
        head_oid=_required_string(pull_request.get("headRefOid"), "pull request head commit"),
        policy=policy,
        passing_checks=len(checks),
        resolved_threads=len(threads),
    )


def resolve_review_thread(target: Path, pr_number: int, thread_id: str) -> None:
    """Resolve one verified review thread after checking its PR membership and opt-in."""
    if not thread_id:
        raise LibraryError("review thread ID must not be empty")
    merge_policy(target)
    thread = next(
        (item for item in review_threads(target, pr_number) if item.get("id") == thread_id), None
    )
    if thread is None:
        raise LibraryError("review thread does not belong to this pull request")
    if thread.get("isResolved") is True:
        raise LibraryError("review thread is already resolved")
    project = _project_directory(target)
    response = _gh_json(
        project,
        [
            "api",
            "graphql",
            "-f",
            f"query={_RESOLVE_THREAD_MUTATION}",
            "-F",
            f"threadId={thread_id}",
        ],
    )
    try:
        resolved = response["data"]["resolveReviewThread"]["thread"]
    except (KeyError, TypeError) as error:
        raise LibraryError("GitHub did not confirm review-thread resolution") from error
    if (
        not isinstance(resolved, dict)
        or resolved.get("id") != thread_id
        or resolved.get("isResolved") is not True
    ):
        raise LibraryError("GitHub did not confirm review-thread resolution")


def merge_pull_request(target: Path, pr_number: int) -> tuple[MergeGate, bool]:
    """Run the live gate, then make one protected GitHub merge request for the checked head."""
    project = _project_directory(target)
    gate = merge_gate(project, pr_number)
    _run_gh(
        project,
        [
            "pr",
            "merge",
            str(pr_number),
            _MERGE_METHOD_FLAGS[gate.policy.merge_method],
            "--match-head-commit",
            gate.head_oid,
        ],
    )
    current = _gh_json(project, ["pr", "view", str(pr_number), "--json", "state,mergedAt"])
    return gate, current.get("state") == "MERGED" and current.get("mergedAt") is not None
