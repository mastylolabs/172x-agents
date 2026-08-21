"""Narrow, fail-closed GitHub CLI helpers for the autonomous dev loop."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tomllib
from pathlib import Path
from typing import Any

from .library import LibraryError
from .profiles import load_profile
from .providers.config import configured_merge_policy, project_config_path
from .providers.contracts import (
    MergeCapabilities,
    MergeGate,
    MergePolicy,
    ProviderCapabilities,
    ProviderCapability,
    ProviderFamily,
    ProviderKey,
    ReviewerIdentity,
    ReviewerStatus,
    ReviewSubmission,
)

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

_ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

__all__ = [
    "GitHubReviewer",
    "MergeCapabilities",
    "MergeGate",
    "MergePolicy",
    "ReviewSubmission",
    "ReviewerStatus",
    "approve_pull_request",
    "configured_reviewers",
    "merge_capabilities",
    "merge_gate",
    "merge_policy",
    "merge_pull_request",
    "provider_capabilities",
    "repository_name",
    "resolve_review_thread",
    "review_threads",
    "reviewer_status",
    "submit_review",
]


GitHubReviewer = ReviewerIdentity


def _project_directory(target: Path) -> Path:
    project = target.expanduser().resolve()
    if not project.is_dir():
        raise LibraryError(f"target project is not a directory: {target}")
    return project


def _run_gh(target: Path, arguments: list[str], *, token: str | None = None) -> str:
    if shutil.which("gh") is None:
        raise LibraryError(
            "GitHub CLI is not installed or not on PATH; install gh and authenticate it."
        )
    environment: dict[str, str] | None = None
    if token is not None:
        environment = os.environ.copy()
        environment["GH_TOKEN"] = token
    completed = subprocess.run(
        ["gh", *arguments],
        cwd=target,
        shell=False,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown GitHub CLI error"
        raise LibraryError(f"GitHub CLI command failed: {detail}")
    return completed.stdout


def _gh_json(target: Path, arguments: list[str], *, token: str | None = None) -> dict[str, Any]:
    output = _run_gh(target, arguments, token=token)
    try:
        result = json.loads(output)
    except json.JSONDecodeError as error:
        raise LibraryError(
            "GitHub CLI returned invalid JSON; cannot evaluate the GitHub action."
        ) from error
    if not isinstance(result, dict):
        raise LibraryError(
            "GitHub CLI returned an unexpected JSON result; cannot evaluate the GitHub action."
        )
    return result


def _project_config_path(target: Path) -> Path:
    path = project_config_path(target)
    if path is not None:
        return path
    raise LibraryError(
        "GitHub review configuration is missing; run 'agents activate <language>' to configure "
        "the local .git/172x/config.toml"
    )


def _non_empty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LibraryError(f"GitHub review configuration requires a non-empty {label}")
    return value.strip()


def configured_reviewers(target: Path) -> tuple[GitHubReviewer, ...]:
    """Load the committed reviewer identities without reading any secret values."""
    path = _project_config_path(target)
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise LibraryError(f"invalid GitHub review configuration: {path}") from error
    github = data.get("github")
    review = github.get("review") if isinstance(github, dict) else None
    reviewers = review.get("reviewers") if isinstance(review, dict) else None
    if not isinstance(reviewers, list) or not reviewers:
        raise LibraryError(
            "local 172X config [github.review].reviewers must contain at least one reviewer"
        )
    parsed: list[GitHubReviewer] = []
    seen: set[str] = set()
    for index, value in enumerate(reviewers, start=1):
        if not isinstance(value, dict) or set(value) != {"login", "token_env"}:
            raise LibraryError(
                f"local 172X config reviewer {index} must contain only login and token_env"
            )
        login = _non_empty_string(value.get("login"), f"reviewer {index} login")
        token_env = _non_empty_string(value.get("token_env"), f"reviewer {index} token_env")
        if not _ENVIRONMENT_NAME.fullmatch(token_env):
            raise LibraryError(f"reviewer {index} token_env is not a valid environment name")
        normalized_login = login.casefold()
        if normalized_login in seen:
            raise LibraryError(f"duplicate GitHub reviewer login: {login}")
        seen.add(normalized_login)
        parsed.append(GitHubReviewer(login=login, token_env=token_env))
    return tuple(parsed)


def _reviewer_credential(target: Path, login: str) -> tuple[GitHubReviewer, str]:
    requested = _non_empty_string(login, "reviewer login")
    reviewer = next(
        (
            item
            for item in configured_reviewers(target)
            if item.login.casefold() == requested.casefold()
        ),
        None,
    )
    if reviewer is None:
        raise LibraryError(f"GitHub reviewer is not configured: {requested}")
    token = os.environ.get(reviewer.token_env)
    if not token:
        raise LibraryError(
            f"GitHub reviewer token environment variable is not set: {reviewer.token_env}"
        )
    return reviewer, token


def _reviewer_user(target: Path, reviewer: GitHubReviewer, token: str) -> str:
    authenticated = _run_gh(target, ["api", "user", "--jq", ".login"], token=token).strip()
    if not authenticated:
        raise LibraryError(f"GitHub reviewer token did not identify a user: {reviewer.login}")
    if authenticated.casefold() != reviewer.login.casefold():
        raise LibraryError(
            f"GitHub reviewer token belongs to '{authenticated}', expected '{reviewer.login}'"
        )
    return authenticated


def reviewer_status(target: Path, login: str) -> ReviewerStatus:
    """Verify a configured token maps to the expected GitHub login and repository access."""
    project = _project_directory(target)
    reviewer, token = _reviewer_credential(project, login)
    authenticated = _reviewer_user(project, reviewer, token)
    repository = _gh_json(
        project,
        ["repo", "view", "--json", "viewerPermission"],
        token=token,
    )
    permission = repository.get("viewerPermission")
    if not isinstance(permission, str) or not permission:
        raise LibraryError("GitHub did not return reviewer repository permission")
    if permission not in {"WRITE", "MAINTAIN", "ADMIN"}:
        raise LibraryError(
            f"GitHub reviewer '{reviewer.login}' lacks review permission: {permission}"
        )
    return ReviewerStatus(
        reviewer=reviewer,
        authenticated_login=authenticated,
        repository_permission=permission,
    )


def _required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise LibraryError(f"GitHub did not return {label}; cannot evaluate the merge gate.")
    return value


def merge_policy(target: Path) -> MergePolicy:
    """Read the repository-owned merge choices after local activation is present."""
    project = _project_directory(target)
    profile = load_profile(project)
    return configured_merge_policy(
        project,
        fallback_base_branch=profile.base_branch,
        fallback_merge_method=profile.merge_method,
        merge_current_branch=profile.merge_current_branch,
    )


def _require_authenticated_gh(target: Path) -> None:
    _run_gh(target, ["auth", "status"])


def _repository_name(target: Path, *, token: str | None = None) -> tuple[str, str]:
    repository = _gh_json(
        target,
        ["repo", "view", "--json", "nameWithOwner"],
        token=token,
    )
    name_with_owner = _required_string(repository.get("nameWithOwner"), "repository name")
    owner, separator, name = name_with_owner.partition("/")
    if not separator or not owner or not name:
        raise LibraryError(
            "GitHub returned an invalid repository name; cannot evaluate the merge gate."
        )
    return owner, name


def repository_name(target: Path) -> tuple[str, str]:
    """Return the configured GitHub repository owner and name."""
    return _repository_name(target)


def provider_capabilities(target: Path) -> ProviderCapabilities:
    """Discover live GitHub capabilities needed by the guarded source-control workflow."""
    project = _project_directory(target)
    repository = _gh_json(
        project,
        [
            "repo",
            "view",
            "--json",
            "nameWithOwner,defaultBranchRef,mergeCommitAllowed,rebaseMergeAllowed,squashMergeAllowed,viewerDefaultMergeMethod",
        ],
    )
    name_with_owner = _required_string(repository.get("nameWithOwner"), "repository name")
    default_branch = repository.get("defaultBranchRef")
    default_branch_name = default_branch.get("name") if isinstance(default_branch, dict) else None
    if not isinstance(default_branch_name, str) or not default_branch_name:
        raise LibraryError("GitHub did not return the repository default branch")
    method_flags = {
        "merge": "mergeCommitAllowed",
        "rebase": "rebaseMergeAllowed",
        "squash": "squashMergeAllowed",
    }
    allowed_methods = frozenset(
        method for method, field in method_flags.items() if repository.get(field) is True
    )
    if not allowed_methods:
        raise LibraryError(
            f"GitHub repository {name_with_owner} does not allow any supported merge method"
        )
    default_method_value = repository.get("viewerDefaultMergeMethod")
    default_method = (
        default_method_value.casefold()
        if isinstance(default_method_value, str) and default_method_value
        else None
    )
    if default_method is not None and default_method not in allowed_methods:
        default_method = None
    return ProviderCapabilities(
        key=ProviderKey(ProviderFamily.SOURCE_CONTROL, "github"),
        capabilities=frozenset(
            {
                ProviderCapability.REPOSITORY,
                ProviderCapability.CHANGE_REQUEST,
                ProviderCapability.REVIEW,
                ProviderCapability.MERGE,
                ProviderCapability.CAPABILITY_DISCOVERY,
            }
        ),
        merge_methods=allowed_methods,
        default_merge_method=default_method,
        default_base_branch=default_branch_name,
    )


def merge_capabilities(target: Path) -> MergeCapabilities:
    """Return the live GitHub merge-method capabilities for a repository."""
    capabilities = provider_capabilities(target)
    return MergeCapabilities(
        methods=capabilities.merge_methods,
        default_method=capabilities.default_merge_method,
        default_base_branch=capabilities.default_base_branch,
    )


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


def _read_review_report(report: Path) -> Path:
    path = report.expanduser().resolve()
    if not path.is_file() or path.is_symlink():
        raise LibraryError(f"review report is not a regular file: {report}")
    try:
        contents = path.read_text(encoding="utf-8")
    except OSError as error:
        raise LibraryError(f"could not read review report: {report}") from error
    if not contents.strip():
        raise LibraryError(f"review report is empty: {report}")
    if len(contents.encode("utf-8")) > 1_000_000:
        raise LibraryError("review report exceeds the 1 MB provider body limit")
    return path


def _reviewer_pull_request(
    target: Path,
    pr_number: int,
    head_oid: str,
    reviewer: GitHubReviewer,
    token: str,
) -> dict[str, Any]:
    if pr_number < 1:
        raise LibraryError("pull request number must be a positive integer")
    expected_head = _non_empty_string(head_oid, "pull request head")
    _reviewer_user(target, reviewer, token)
    pull_request = _gh_json(
        target,
        ["pr", "view", str(pr_number), "--json", "number,state,isDraft,headRefOid,author"],
        token=token,
    )
    if pull_request.get("state") != "OPEN":
        raise LibraryError("pull request is not open")
    if pull_request.get("isDraft") is not False:
        raise LibraryError("pull request is a draft")
    actual_head = _required_string(pull_request.get("headRefOid"), "pull request head commit")
    if actual_head != expected_head:
        raise LibraryError(
            f"pull request head changed: expected {expected_head}, found {actual_head}"
        )
    author = pull_request.get("author")
    author_login = author.get("login") if isinstance(author, dict) else None
    if not isinstance(author_login, str) or not author_login:
        raise LibraryError("GitHub did not return the pull-request author")
    if author_login.casefold() == reviewer.login.casefold():
        raise LibraryError("configured GitHub reviewer is the pull-request author")
    return pull_request


def _reviewer_reviews(target: Path, pr_number: int, token: str) -> list[dict[str, Any]]:
    response = _gh_json(
        target,
        ["pr", "view", str(pr_number), "--json", "reviews"],
        token=token,
    )
    reviews = response.get("reviews")
    if not isinstance(reviews, list) or not all(isinstance(item, dict) for item in reviews):
        raise LibraryError("GitHub returned invalid pull-request review data")
    return reviews


def _latest_reviewer_state(
    reviews: list[dict[str, Any]], reviewer: GitHubReviewer, head_oid: str
) -> str | None:
    matches: list[tuple[str, int, str]] = []
    for index, review in enumerate(reviews):
        author = review.get("author")
        login = author.get("login") if isinstance(author, dict) else None
        commit = review.get("commit")
        commit_oid = commit.get("oid") if isinstance(commit, dict) else None
        state = review.get("state")
        if (
            isinstance(login, str)
            and login.casefold() == reviewer.login.casefold()
            and commit_oid == head_oid
            and isinstance(state, str)
        ):
            submitted_at = review.get("submittedAt")
            matches.append((submitted_at if isinstance(submitted_at, str) else "", index, state))
    if not matches:
        return None
    matches.sort(key=lambda item: (item[0], item[1]))
    return matches[-1][2].upper()


def _submit_review(
    target: Path,
    pr_number: int,
    reviewer_login: str,
    head_oid: str,
    report: Path,
    action: str,
    expected_state: str,
) -> ReviewSubmission:
    project = _project_directory(target)
    reviewer, token = _reviewer_credential(project, reviewer_login)
    report_path = _read_review_report(report)
    _reviewer_pull_request(project, pr_number, head_oid, reviewer, token)
    _run_gh(
        project,
        ["pr", "review", str(pr_number), action, "--body-file", str(report_path)],
        token=token,
    )
    reviews = _reviewer_reviews(project, pr_number, token)
    actual_state = _latest_reviewer_state(reviews, reviewer, head_oid)
    if actual_state != expected_state:
        raise LibraryError(
            f"GitHub did not confirm {expected_state.lower()} review from '{reviewer.login}' "
            f"on head {head_oid}"
        )
    return ReviewSubmission(
        change_request_number=pr_number,
        reviewer=reviewer.login,
        head_oid=head_oid,
        state=actual_state,
    )


def submit_review(
    target: Path, pr_number: int, reviewer_login: str, head_oid: str, report: Path
) -> ReviewSubmission:
    """Publish a non-approving review report for one exact pull-request head."""
    return _submit_review(
        target,
        pr_number,
        reviewer_login,
        head_oid,
        report,
        "--comment",
        "COMMENTED",
    )


def approve_pull_request(
    target: Path, pr_number: int, reviewer_login: str, head_oid: str, report: Path
) -> ReviewSubmission:
    """Submit and confirm an independent approval for one exact pull-request head."""
    return _submit_review(
        target,
        pr_number,
        reviewer_login,
        head_oid,
        report,
        "--approve",
        "APPROVED",
    )


def _configured_approvals(target: Path, pr_number: int, head_oid: str) -> tuple[str, ...]:
    approved: list[str] = []
    for reviewer in configured_reviewers(target):
        _, token = _reviewer_credential(target, reviewer.login)
        _reviewer_pull_request(target, pr_number, head_oid, reviewer, token)
        state = _latest_reviewer_state(
            _reviewer_reviews(target, pr_number, token), reviewer, head_oid
        )
        if state != "APPROVED":
            raise LibraryError(
                f"configured reviewer '{reviewer.login}' has not approved pull-request head "
                f"{head_oid}"
            )
        approved.append(reviewer.login)
    return tuple(approved)


def merge_gate(target: Path, pr_number: int) -> MergeGate:
    """Fail closed unless the live GitHub PR satisfies every merge requirement."""
    if pr_number < 1:
        raise LibraryError("pull request number must be a positive integer")
    project = _project_directory(target)
    policy = merge_policy(project)
    _require_authenticated_gh(project)
    capabilities = provider_capabilities(project)
    if policy.merge_method not in capabilities.merge_methods:
        allowed = ", ".join(sorted(capabilities.merge_methods))
        raise LibraryError(
            f"configured merge method '{policy.merge_method}' is not allowed by GitHub; "
            f"allowed methods: {allowed}"
        )
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
    if checks is None:
        checks = []
    if not isinstance(checks, list):
        raise LibraryError("GitHub returned invalid check data; cannot evaluate the merge gate.")
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
    approved_reviewers = _configured_approvals(
        project,
        pr_number,
        _required_string(pull_request.get("headRefOid"), "pull request head commit"),
    )
    return MergeGate(
        change_request_number=pr_number,
        url=_required_string(pull_request.get("url"), "pull request URL"),
        head_oid=_required_string(pull_request.get("headRefOid"), "pull request head commit"),
        policy=policy,
        reported_checks=len(checks),
        resolved_threads=len(threads),
        approved_reviewers=approved_reviewers,
        provider_capabilities=capabilities,
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
    """Run the live gate, then make one guarded GitHub merge request for the checked head."""
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
