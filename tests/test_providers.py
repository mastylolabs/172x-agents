from pathlib import Path

import pytest

from agent_workflows.library import LibraryError
from agent_workflows.providers import (
    ProviderCapability,
    ProviderDescriptor,
    ProviderFamily,
    ProviderKey,
    ProviderRegistry,
    default_registry,
    source_control_provider,
)
from agent_workflows.providers.config import (
    configured_merge_policy,
    local_project_config_path,
    project_config,
    project_config_path,
    selected_source_control_provider,
    write_local_project_config,
)


def test_provider_key_is_namespaced_and_normalized() -> None:
    key = ProviderKey(ProviderFamily.SOURCE_CONTROL, " GitHub ")

    assert key.name == "github"
    assert key.qualified_name == "source_control:github"


def test_provider_registry_lists_capabilities_without_network_access() -> None:
    registry = default_registry()

    descriptors = registry.descriptors(ProviderFamily.SOURCE_CONTROL)

    assert len(descriptors) == 1
    assert descriptors[0].key.qualified_name == "source_control:github"
    assert ProviderCapability.MERGE in descriptors[0].capabilities


def test_provider_registry_can_register_metadata_for_future_families() -> None:
    registry = ProviderRegistry()
    descriptor = ProviderDescriptor(
        key=ProviderKey(ProviderFamily.MODEL, "example"),
        capabilities=frozenset(),
    )

    registry.register_descriptor(descriptor)

    assert registry.descriptors(ProviderFamily.MODEL) == (descriptor,)
    with pytest.raises(LibraryError, match="duplicate provider"):
        registry.register_descriptor(descriptor)


def test_source_control_provider_defaults_to_github_for_existing_projects(tmp_path: Path) -> None:
    selected = selected_source_control_provider(tmp_path)
    provider = source_control_provider(tmp_path)

    assert selected == ProviderKey(ProviderFamily.SOURCE_CONTROL, "github")
    assert provider.key == selected


def test_source_control_provider_can_be_selected_in_project_config(tmp_path: Path) -> None:
    (tmp_path / "172x.toml").write_text(
        '[provider]\nfamily = "source_control"\nname = "github"\n',
        encoding="utf-8",
    )

    assert selected_source_control_provider(tmp_path) == ProviderKey(
        ProviderFamily.SOURCE_CONTROL, "github"
    )


def test_local_git_config_takes_precedence_over_legacy_root_config(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / "172x.toml").write_text(
        '[provider]\nfamily = "source_control"\nname = "github"\n',
        encoding="utf-8",
    )
    local = tmp_path / ".git/172x/config.toml"
    local.parent.mkdir()
    local.write_text(
        '[provider]\nfamily = "source_control"\nname = "github"\n\n[merge]\nmethod = "rebase"\n',
        encoding="utf-8",
    )

    assert local_project_config_path(tmp_path) == local
    assert project_config_path(tmp_path) == local
    assert project_config(tmp_path)["merge"]["method"] == "rebase"


def test_activation_writes_provider_config_under_git_metadata(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()

    action, path = write_local_project_config(tmp_path)

    expected = tmp_path / ".git/172x/config.toml"
    assert (action, path) == ("CREATE", expected)
    assert expected.is_file()
    assert not (tmp_path / "172x.toml").exists()
    assert project_config(tmp_path)["github"]["review"]["reviewers"][0]["login"] == (
        "172x-reviewer-bot"
    )


def test_legacy_root_config_is_migrated_to_local_git_metadata(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    legacy = tmp_path / "172x.toml"
    legacy.write_text(
        '[provider]\nid = "github"\n\n[change_request]\nmerge_method = "squash"\n',
        encoding="utf-8",
    )

    action, path = write_local_project_config(tmp_path)

    assert action == "CREATE"
    assert path == tmp_path / ".git/172x/config.toml"
    assert path.read_text(encoding="utf-8").startswith(
        "# Local 172X provider configuration migrated"
    )
    assert project_config(tmp_path)["change_request"]["merge_method"] == "squash"


def test_legacy_project_provider_and_change_request_keys_remain_compatible(
    tmp_path: Path,
) -> None:
    (tmp_path / "172x.toml").write_text(
        '[provider]\nid = "github"\n\n'
        '[change_request]\nbase_branch = "main"\nmerge_method = "rebase"\n'
        "merge_current_branch = false\n",
        encoding="utf-8",
    )

    selected = selected_source_control_provider(tmp_path)
    policy = configured_merge_policy(
        tmp_path,
        fallback_base_branch="main",
        fallback_merge_method="squash",
        merge_current_branch=True,
    )

    assert selected == ProviderKey(ProviderFamily.SOURCE_CONTROL, "github")
    assert policy.merge_method == "rebase"
    assert policy.merge_current_branch is False


def test_provider_config_rejects_non_source_control_selection(tmp_path: Path) -> None:
    (tmp_path / "172x.toml").write_text(
        '[provider]\nfamily = "model"\nname = "example"\n',
        encoding="utf-8",
    )

    with pytest.raises(LibraryError, match="source-control operations"):
        selected_source_control_provider(tmp_path)


def test_merge_policy_reads_explicit_repository_method(tmp_path: Path) -> None:
    (tmp_path / "172x.toml").write_text(
        '[merge]\nbase_branch = "trunk"\nmethod = "REBASE"\n',
        encoding="utf-8",
    )

    policy = configured_merge_policy(
        tmp_path,
        fallback_base_branch="main",
        fallback_merge_method="squash",
        merge_current_branch=True,
    )

    assert policy.base_branch == "trunk"
    assert policy.merge_method == "rebase"
    assert policy.merge_current_branch is True
