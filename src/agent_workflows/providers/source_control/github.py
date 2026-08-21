"""GitHub source-control adapter backed by the existing guarded implementation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ... import github as github_api
from ..contracts import (
    CapabilityDiscovery,
    ChangeRequestOperations,
    MergeCapabilities,
    MergeGate,
    MergeOperations,
    MergePolicy,
    ProviderCapabilities,
    ProviderFamily,
    ProviderKey,
    RepositoryOperations,
    ReviewerIdentity,
    ReviewerStatus,
    ReviewOperations,
    ReviewSubmission,
    SourceControlProvider,
)


@dataclass(frozen=True)
class GitHubRepositoryOperations(RepositoryOperations):
    """GitHub repository identity operations."""

    def repository_name(self, target: Path) -> tuple[str, str]:
        return github_api.repository_name(target)


@dataclass(frozen=True)
class GitHubChangeRequestOperations(ChangeRequestOperations):
    """GitHub pull-request thread operations."""

    def review_threads(self, target: Path, change_request_number: int) -> list[dict[str, object]]:
        return github_api.review_threads(target, change_request_number)

    def resolve_review_thread(
        self, target: Path, change_request_number: int, thread_id: str
    ) -> None:
        github_api.resolve_review_thread(target, change_request_number, thread_id)


@dataclass(frozen=True)
class GitHubReviewOperations(ReviewOperations):
    """GitHub reviewer identity and review submission operations."""

    def configured_reviewers(self, target: Path) -> tuple[ReviewerIdentity, ...]:
        return github_api.configured_reviewers(target)

    def reviewer_status(self, target: Path, login: str) -> ReviewerStatus:
        return github_api.reviewer_status(target, login)

    def submit_review(
        self,
        target: Path,
        change_request_number: int,
        reviewer_login: str,
        head_oid: str,
        report: Path,
    ) -> ReviewSubmission:
        return github_api.submit_review(
            target, change_request_number, reviewer_login, head_oid, report
        )

    def approve_review(
        self,
        target: Path,
        change_request_number: int,
        reviewer_login: str,
        head_oid: str,
        report: Path,
    ) -> ReviewSubmission:
        return github_api.approve_pull_request(
            target, change_request_number, reviewer_login, head_oid, report
        )


@dataclass(frozen=True)
class GitHubMergeOperations(MergeOperations):
    """GitHub guarded merge operations."""

    def merge_policy(self, target: Path) -> MergePolicy:
        return github_api.merge_policy(target)

    def merge_capabilities(self, target: Path) -> MergeCapabilities:
        return github_api.merge_capabilities(target)

    def merge_gate(self, target: Path, change_request_number: int) -> MergeGate:
        return github_api.merge_gate(target, change_request_number)

    def merge_change_request(
        self, target: Path, change_request_number: int
    ) -> tuple[MergeGate, bool]:
        return github_api.merge_pull_request(target, change_request_number)


@dataclass(frozen=True)
class GitHubCapabilityDiscovery(CapabilityDiscovery):
    """Live GitHub repository capability discovery."""

    def capabilities(self, target: Path) -> ProviderCapabilities:
        return github_api.provider_capabilities(target)


@dataclass(frozen=True)
class GitHubProvider:
    """Composed GitHub source-control provider."""

    key: ProviderKey
    repository: GitHubRepositoryOperations
    change_requests: GitHubChangeRequestOperations
    reviews: GitHubReviewOperations
    merges: GitHubMergeOperations
    discovery: GitHubCapabilityDiscovery


def build_github_provider() -> SourceControlProvider:
    """Construct the built-in GitHub adapter bundle."""
    key = ProviderKey(ProviderFamily.SOURCE_CONTROL, "github")
    return GitHubProvider(
        key=key,
        repository=GitHubRepositoryOperations(),
        change_requests=GitHubChangeRequestOperations(),
        reviews=GitHubReviewOperations(),
        merges=GitHubMergeOperations(),
        discovery=GitHubCapabilityDiscovery(),
    )
