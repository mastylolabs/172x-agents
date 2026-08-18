import importlib.util
import json
import os
import stat
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


package_release = _load_script("package_release")
release_manifest = _load_script("release_manifest")


def _executable(path: Path) -> Path:
    path.write_bytes(b"standalone agents test binary\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def test_package_release_creates_archive_and_checksum(tmp_path: Path) -> None:
    binary = _executable(tmp_path / "agents")
    output = tmp_path / "release"

    archive, checksum = package_release.package(binary, "linux-x64", output)

    assert archive.name == "agents-linux-x64.tar.gz"
    assert checksum.read_text(encoding="ascii").endswith(f"  {archive.name}\n")
    with tarfile.open(archive, "r:gz") as tar:
        assert tar.getnames() == ["agents"]
        extracted = tar.extractfile("agents")
        assert extracted is not None
        assert extracted.read() == binary.read_bytes()


def test_package_release_creates_windows_zip(tmp_path: Path) -> None:
    binary = tmp_path / "agents.exe"
    binary.write_bytes(b"windows test binary\n")

    archive, _ = package_release.package(binary, "windows-x64", tmp_path / "release")

    with zipfile.ZipFile(archive) as zipped:
        assert zipped.namelist() == ["agents.exe"]
        assert zipped.read("agents.exe") == binary.read_bytes()


def test_manifest_creation_and_verification_are_closed_to_artifacts(tmp_path: Path) -> None:
    release = tmp_path / "release"
    binary = _executable(tmp_path / "agents")
    package_release.package(binary, "linux-x64", release)
    windows = tmp_path / "agents.exe"
    windows.write_bytes(b"windows test binary\n")
    package_release.package(windows, "windows-x64", release)

    manifest = release_manifest.build_manifest(
        "v0.1.0", release, "https://github.com/mastylolabs/172x-agents/releases/download/v0.1.0"
    )
    manifest_path = release / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    release_manifest.verify_manifest(manifest_path, release)
    assert {artifact["filename"] for artifact in manifest["artifacts"]} == {
        "agents-linux-x64.tar.gz",
        "agents-windows-x64.zip",
    }


def test_manifest_rejects_checksum_changes(tmp_path: Path) -> None:
    release = tmp_path / "release"
    binary = _executable(tmp_path / "agents")
    package_release.package(binary, "linux-x64", release)
    manifest = release_manifest.build_manifest(
        "v0.1.0", release, "https://example.test/releases/v0.1.0"
    )
    manifest_path = release / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    (release / "agents-linux-x64.tar.gz").write_bytes(b"changed")

    with pytest.raises(ValueError, match="checksum mismatch"):
        release_manifest.verify_manifest(manifest_path, release)


def test_installers_support_pinned_dry_run() -> None:
    env = os.environ.copy()
    env.pop("AGENTS_172X_RELEASE_BASE_URL", None)
    result = subprocess.run(
        [
            "sh",
            str(ROOT / "install.sh"),
            "--version",
            "v0.1.0",
            "--target",
            "linux-x64",
            "--dry-run",
        ],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    assert "agents-linux-x64.tar.gz" in result.stdout
    assert "v0.1.0" in result.stdout
    assert "github.com/mastylolabs/172x-agents/releases/download" in result.stdout


def test_install_sh_verifies_and_installs_local_fixture(tmp_path: Path) -> None:
    release_root = tmp_path / "releases"
    binary = _executable(tmp_path / "fixture-agents")
    package_release.package(binary, "linux-x64", release_root / "v0.1.0")
    prefix = tmp_path / "prefix"

    subprocess.run(
        [
            "sh",
            str(ROOT / "install.sh"),
            "--version",
            "v0.1.0",
            "--target",
            "linux-x64",
            "--base-url",
            release_root.as_uri(),
            "--prefix",
            str(prefix),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert (prefix / "bin/agents").read_bytes() == binary.read_bytes()


def test_install_sh_has_valid_posix_syntax() -> None:
    subprocess.run(["sh", "-n", str(ROOT / "install.sh")], check=True)


def test_invalid_manifest_version_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="vMAJOR.MINOR.PATCH"):
        release_manifest.build_manifest("latest", tmp_path, "https://example.test")


def test_manifest_rejects_inconsistent_artifact_metadata(tmp_path: Path) -> None:
    release = tmp_path / "release"
    binary = _executable(tmp_path / "agents")
    package_release.package(binary, "linux-x64", release)
    manifest = release_manifest.build_manifest(
        "v0.1.0", release, "https://example.test/releases/v0.1.0"
    )
    manifest["artifacts"][0]["url"] = "https://other.example/agents-linux-x64.tar.gz"
    manifest_path = release / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="manifest URL"):
        release_manifest.verify_manifest(manifest_path, release)


def test_install_sh_rejects_non_semver_version() -> None:
    result = subprocess.run(
        ["sh", str(ROOT / "install.sh"), "--version", "v1x.2.3", "--dry-run"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "version must look like" in result.stderr
