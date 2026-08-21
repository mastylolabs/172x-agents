"""Deterministic provider registration and source-control resolution."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..library import LibraryError
from .config import selected_source_control_provider
from .contracts import (
    ProviderCapability,
    ProviderDescriptor,
    ProviderFamily,
    ProviderKey,
    SourceControlProvider,
)


@dataclass
class ProviderRegistry:
    """Registry for concrete providers and their advertised capabilities."""

    _descriptors: dict[ProviderKey, ProviderDescriptor] = field(default_factory=dict)
    _source_control: dict[str, SourceControlProvider] = field(default_factory=dict)

    def register_descriptor(self, descriptor: ProviderDescriptor) -> None:
        """Register metadata for a provider family without creating an adapter."""
        if descriptor.key in self._descriptors:
            raise LibraryError(f"duplicate provider: {descriptor.key.qualified_name}")
        self._descriptors[descriptor.key] = descriptor

    def register_source_control(self, provider: SourceControlProvider) -> None:
        """Register one source-control provider without replacing a duplicate silently."""
        if provider.key.family is not ProviderFamily.SOURCE_CONTROL:
            raise LibraryError("source-control registry received a non-source-control provider")
        if provider.key.name in self._source_control:
            raise LibraryError(f"duplicate source-control provider: {provider.key.name}")
        descriptor = ProviderDescriptor(
            key=provider.key,
            capabilities=frozenset(
                {
                    ProviderCapability.REPOSITORY,
                    ProviderCapability.CHANGE_REQUEST,
                    ProviderCapability.REVIEW,
                    ProviderCapability.MERGE,
                    ProviderCapability.CAPABILITY_DISCOVERY,
                }
            ),
        )
        self.register_descriptor(descriptor)
        self._source_control[provider.key.name] = provider

    def source_control(self, name: str) -> SourceControlProvider:
        """Return a registered source-control provider by case-insensitive name."""
        normalized = name.strip().casefold()
        try:
            return self._source_control[normalized]
        except KeyError as error:
            available = ", ".join(sorted(self._source_control)) or "none"
            raise LibraryError(
                f"source-control provider '{name}' is not installed; available: {available}"
            ) from error

    def descriptors(self, family: ProviderFamily | None = None) -> tuple[ProviderDescriptor, ...]:
        """Return registered provider metadata in stable order."""
        values = tuple(self._descriptors.values())
        selected = (
            values
            if family is None
            else tuple(item for item in values if item.key.family is family)
        )
        return tuple(sorted(selected, key=lambda item: item.key.qualified_name))


def default_registry() -> ProviderRegistry:
    """Build the built-in registry without loading credentials or contacting a provider."""
    from .source_control.github import build_github_provider

    registry = ProviderRegistry()
    registry.register_source_control(build_github_provider())
    return registry


def source_control_provider(target: Path) -> SourceControlProvider:
    """Resolve the target project's configured source-control provider."""
    selected = selected_source_control_provider(target)
    return default_registry().source_control(selected.name)
