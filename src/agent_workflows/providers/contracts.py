"""Small, provider-neutral contracts used by the 172X integration layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Protocol


class ProviderFamily(StrEnum):
    """Stable integration domains understood by the provider registry."""

    SOURCE_CONTROL = "source_control"
    MODEL = "model"
    NOTIFICATION = "notification"
    ARTIFACT = "artifact"
    SECRET = "secret"
    MARKET_DATA = "market_data"


class ProviderCapability(StrEnum):
    """Observable operations a provider may expose."""

    REPOSITORY = "repository"
    CHANGE_REQUEST = "change_request"
    REVIEW = "review"
    MERGE = "merge"
    CAPABILITY_DISCOVERY = "capability_discovery"
    MODEL_COMPLETION = "model_completion"
    NOTIFICATION_SEND = "notification_send"
    ARTIFACT_READ = "artifact_read"
    ARTIFACT_WRITE = "artifact_write"
    SECRET_RESOLVE = "secret_resolve"
    MARKET_DATA_QUERY = "market_data_query"
    MARKET_DATA_STREAM = "market_data_stream"


@dataclass(frozen=True)
class ProviderKey:
    """A namespaced provider identity, such as ``source_control:github``."""

    family: ProviderFamily
    name: str

    def __post_init__(self) -> None:
        normalized = self.name.strip().casefold()
        if not normalized:
            raise ValueError("provider name must not be empty")
        object.__setattr__(self, "name", normalized)

    @property
    def qualified_name(self) -> str:
        """Return the stable registry key used in diagnostics and configuration."""
        return f"{self.family.value}:{self.name}"


@dataclass(frozen=True)
class ProviderDescriptor:
    """Provider metadata safe to display without credentials or network access."""

    key: ProviderKey
    capabilities: frozenset[ProviderCapability] = field(default_factory=frozenset)


@dataclass(frozen=True)
class ProviderCapabilities:
    """Live provider capability evidence for one repository target."""

    key: ProviderKey
    capabilities: frozenset[ProviderCapability]
    merge_methods: frozenset[str] = field(default_factory=frozenset)
    default_merge_method: str | None = None
    default_base_branch: str | None = None


@dataclass(frozen=True)
class MergeCapabilities:
    """Merge methods a provider currently permits for a repository."""

    methods: frozenset[str]
    default_method: str | None = None
    default_base_branch: str | None = None


@dataclass(frozen=True)
class MergePolicy:
    """Repository-owned merge choices consumed by every source-control provider."""

    base_branch: str
    merge_method: str
    merge_current_branch: bool


@dataclass(frozen=True)
class ReviewerIdentity:
    """Provider-specific login mapped to a separately exported token variable."""

    login: str
    token_env: str


@dataclass(frozen=True)
class ReviewerStatus:
    """Evidence that one configured reviewer authenticated and can access a repository."""

    reviewer: ReviewerIdentity
    authenticated_login: str
    repository_permission: str


@dataclass(frozen=True)
class ReviewSubmission:
    """Confirmed review action for one exact change-request revision."""

    change_request_number: int
    reviewer: str
    head_oid: str
    state: str

    @property
    def pr_number(self) -> int:
        """Backward-compatible GitHub terminology for existing callers."""
        return self.change_request_number


@dataclass(frozen=True)
class MergeGate:
    """Evidence captured immediately before a guarded merge attempt."""

    change_request_number: int
    url: str
    head_oid: str
    policy: MergePolicy
    reported_checks: int
    resolved_threads: int
    approved_reviewers: tuple[str, ...] = ()
    provider_capabilities: ProviderCapabilities | None = None

    @property
    def pr_number(self) -> int:
        """Backward-compatible GitHub terminology for existing callers."""
        return self.change_request_number


class CapabilityDiscovery(Protocol):
    """Discover live provider capabilities for a repository target."""

    def capabilities(self, target: Path) -> ProviderCapabilities:
        """Return provider capability evidence or raise a fail-closed domain error."""


class RepositoryOperations(Protocol):
    """Operations that identify and inspect a source-control repository."""

    def repository_name(self, target: Path) -> tuple[str, str]:
        """Return the provider owner and repository name."""


class ChangeRequestOperations(Protocol):
    """Operations over provider-neutral pull/merge/change requests."""

    def review_threads(self, target: Path, change_request_number: int) -> list[dict[str, Any]]:
        """Return all review threads for one change request."""

    def resolve_review_thread(
        self, target: Path, change_request_number: int, thread_id: str
    ) -> None:
        """Resolve one previously verified review thread."""


class ReviewOperations(Protocol):
    """Provider operations for reviewer identity, reports, and approval."""

    def configured_reviewers(self, target: Path) -> tuple[ReviewerIdentity, ...]:
        """Load committed reviewer mappings without reading token values."""

    def reviewer_status(self, target: Path, login: str) -> ReviewerStatus:
        """Verify one configured reviewer identity and repository permission."""

    def submit_review(
        self,
        target: Path,
        change_request_number: int,
        reviewer_login: str,
        head_oid: str,
        report: Path,
    ) -> ReviewSubmission:
        """Publish a non-approving report for one exact revision."""

    def approve_review(
        self,
        target: Path,
        change_request_number: int,
        reviewer_login: str,
        head_oid: str,
        report: Path,
    ) -> ReviewSubmission:
        """Publish and confirm an approval for one exact revision."""


class MergeOperations(Protocol):
    """Provider operations for policy discovery, gates, and guarded merges."""

    def merge_policy(self, target: Path) -> MergePolicy:
        """Load the repository-owned merge policy."""

    def merge_capabilities(self, target: Path) -> MergeCapabilities:
        """Return live merge-method evidence for the target repository."""

    def merge_gate(self, target: Path, change_request_number: int) -> MergeGate:
        """Evaluate all merge requirements for one exact current revision."""

    def merge_change_request(
        self, target: Path, change_request_number: int
    ) -> tuple[MergeGate, bool]:
        """Perform one guarded merge request and confirm its provider state."""


class SourceControlProvider(Protocol):
    """Composed source-control capabilities for one concrete provider."""

    @property
    def key(self) -> ProviderKey:
        """Return the provider identity."""

    @property
    def repository(self) -> RepositoryOperations:
        """Return repository operations."""

    @property
    def change_requests(self) -> ChangeRequestOperations:
        """Return change-request operations."""

    @property
    def reviews(self) -> ReviewOperations:
        """Return review operations."""

    @property
    def merges(self) -> MergeOperations:
        """Return merge operations."""

    @property
    def discovery(self) -> CapabilityDiscovery:
        """Return live capability discovery."""
