"""Create a deterministic platform archive and checksum for a built executable."""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import tarfile
import zipfile
from pathlib import Path

TARGETS = {
    "darwin-arm64": ("tar.gz", "agents"),
    "darwin-x64": ("tar.gz", "agents"),
    "linux-arm64": ("tar.gz", "agents"),
    "linux-x64": ("tar.gz", "agents"),
    "windows-x64": ("zip", "agents.exe"),
}


def _archive_name(target: str, archive_format: str) -> str:
    suffix = "tar.gz" if archive_format == "tar.gz" else "zip"
    return f"agents-{target}.{suffix}"


def _tar_filter(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mode = stat.S_IFREG | 0o755
    return info


def _write_archive(binary: Path, target: str, output: Path) -> None:
    archive_format, member_name = TARGETS[target]
    output.parent.mkdir(parents=True, exist_ok=True)
    if archive_format == "tar.gz":
        with tarfile.open(output, "w:gz", compresslevel=9) as archive:
            archive.add(binary, arcname=member_name, filter=_tar_filter)
        return

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        info = zipfile.ZipInfo(member_name, date_time=(1980, 1, 1, 0, 0, 0))
        info.create_system = 3
        info.external_attr = 0o100755 << 16
        archive.writestr(info, binary.read_bytes())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package(binary: Path, target: str, output_dir: Path) -> tuple[Path, Path]:
    if target not in TARGETS:
        raise ValueError(f"unsupported target: {target}")
    if not binary.is_file():
        raise FileNotFoundError(binary)
    if target != "windows-x64" and not os.access(binary, os.X_OK):
        raise ValueError(f"Unix executable is not executable: {binary}")

    archive = output_dir / _archive_name(target, TARGETS[target][0])
    _write_archive(binary, target, archive)
    checksum = output_dir / f"{archive.name}.sha256"
    checksum.write_text(f"{_sha256(archive)}  {archive.name}\n", encoding="ascii")
    return archive, checksum


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--target", choices=sorted(TARGETS), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    archive, checksum = package(args.binary, args.target, args.output_dir)
    print(archive)
    print(checksum)


if __name__ == "__main__":
    main()
