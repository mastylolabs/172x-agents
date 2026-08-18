"""Create and verify the versioned 172X standalone release manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ARTIFACT_RE = re.compile(
    r"^agents-(?P<os>darwin|linux|windows)-(?P<arch>arm64|x64)\.(?P<format>tar\.gz|zip)$"
)
VERSION_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_files(directory: Path) -> list[tuple[re.Match[str], Path]]:
    artifacts: list[tuple[re.Match[str], Path]] = []
    for path in sorted(directory.iterdir()):
        match = ARTIFACT_RE.fullmatch(path.name)
        if match:
            artifacts.append((match, path))
    if not artifacts:
        raise ValueError(f"no release archives found in {directory}")
    return artifacts


def build_manifest(version: str, directory: Path, base_url: str) -> dict[str, Any]:
    if not VERSION_RE.fullmatch(version):
        raise ValueError("version must use a vMAJOR.MINOR.PATCH tag")
    normalized_base = base_url.rstrip("/")
    artifacts: list[dict[str, Any]] = []
    seen_targets: set[tuple[str, str]] = set()
    for match, path in _artifact_files(directory):
        target = (match.group("os"), match.group("arch"))
        if target in seen_targets:
            raise ValueError(f"duplicate release target: {target[0]}-{target[1]}")
        seen_targets.add(target)
        artifacts.append(
            {
                "os": target[0],
                "arch": target[1],
                "format": match.group("format"),
                "filename": path.name,
                "url": f"{normalized_base}/{path.name}",
                "sha256": _sha256(path),
                "size": path.stat().st_size,
            }
        )
    return {
        "schema_version": 1,
        "product": "172x-agents",
        "version": version,
        "base_url": normalized_base,
        "artifacts": artifacts,
    }


def verify_manifest(manifest_path: Path, directory: Path) -> None:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("product") != "172x-agents":
        raise ValueError("unsupported release manifest")
    if not VERSION_RE.fullmatch(manifest.get("version", "")):
        raise ValueError("manifest has an invalid version")
    base_url = manifest.get("base_url")
    if not isinstance(base_url, str) or not base_url:
        raise ValueError("manifest must contain a base_url")
    artifacts = manifest.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("manifest must contain artifacts")
    seen_filenames: set[str] = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise TypeError("manifest artifact must be an object")
        filename = artifact.get("filename")
        if not isinstance(filename, str) or Path(filename).name != filename:
            raise ValueError("manifest artifact filename must be a plain filename")
        match = ARTIFACT_RE.fullmatch(filename)
        if match is None:
            raise ValueError(f"manifest artifact filename is unsupported: {filename}")
        if filename in seen_filenames:
            raise ValueError(f"duplicate manifest artifact: {filename}")
        seen_filenames.add(filename)
        if artifact.get("os") != match.group("os") or artifact.get("arch") != match.group("arch"):
            raise ValueError(f"manifest target fields do not match {filename}")
        if artifact.get("format") != match.group("format"):
            raise ValueError(f"manifest format does not match {filename}")
        if artifact.get("url") != f"{base_url.rstrip('/')}/{filename}":
            raise ValueError(f"manifest URL does not match {filename}")
        if not isinstance(artifact.get("sha256"), str) or not re.fullmatch(
            r"[0-9a-f]{64}", artifact["sha256"]
        ):
            raise ValueError(f"manifest checksum is malformed for {filename}")
        if not isinstance(artifact.get("size"), int) or artifact["size"] < 0:
            raise ValueError(f"manifest size is malformed for {filename}")
        path = directory / filename
        if not path.is_file():
            raise FileNotFoundError(path)
        actual = _sha256(path)
        if actual != artifact.get("sha256"):
            raise ValueError(f"checksum mismatch for {filename}")
        if path.stat().st_size != artifact.get("size"):
            raise ValueError(f"size mismatch for {filename}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create")
    create.add_argument("--version", required=True)
    create.add_argument("--artifacts-dir", type=Path, required=True)
    create.add_argument("--base-url", required=True)
    create.add_argument("--output", type=Path, required=True)
    verify = subparsers.add_parser("verify")
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--artifacts-dir", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "create":
        manifest = build_manifest(args.version, args.artifacts_dir, args.base_url)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(args.output)
    else:
        verify_manifest(args.manifest, args.artifacts_dir)
        print(f"verified {args.manifest}")


if __name__ == "__main__":
    main()
