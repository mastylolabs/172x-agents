#!/bin/sh
set -eu

DEFAULT_BASE_URL="https://agents.172x.ai/releases"
VERSION=""
BASE_URL="${AGENTS_172X_RELEASE_BASE_URL:-$DEFAULT_BASE_URL}"
TARGET=""
PREFIX="${AGENTS_172X_INSTALL_PREFIX:-$HOME/.local}"
DRY_RUN=0
FORCE=0

usage() {
    cat <<'EOF'
Usage: install.sh --version vMAJOR.MINOR.PATCH [options]

Options:
  --version VERSION   Immutable release tag to install (required)
  --base-url URL      Release root (default: https://agents.172x.ai/releases)
  --target TARGET     Override target, for example linux-x64 or darwin-arm64
  --prefix PATH       User-local install prefix (default: ~/.local)
  --dry-run           Print URLs and destination without downloading or writing
  --force             Replace an existing executable
  --help              Show this help
EOF
}

die() {
    printf '%s\n' "install.sh: $*" >&2
    exit 1
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --version)
            [ "$#" -ge 2 ] || die "--version requires a value"
            VERSION=$2
            shift 2
            ;;
        --base-url)
            [ "$#" -ge 2 ] || die "--base-url requires a value"
            BASE_URL=$2
            shift 2
            ;;
        --target)
            [ "$#" -ge 2 ] || die "--target requires a value"
            TARGET=$2
            shift 2
            ;;
        --prefix)
            [ "$#" -ge 2 ] || die "--prefix requires a value"
            PREFIX=$2
            shift 2
            ;;
        --dry-run)
            DRY_RUN=1
            shift
            ;;
        --force)
            FORCE=1
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            die "unknown option: $1"
            ;;
    esac
done

[ -n "$VERSION" ] || die "--version is required; pin an immutable release"
if ! printf '%s\n' "$VERSION" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'; then
    die "version must look like vMAJOR.MINOR.PATCH"
fi
case "$VERSION" in
    */*|*..*) die "version contains an unsafe path" ;;
esac

if [ -z "$TARGET" ]; then
    os=$(uname -s)
    arch=$(uname -m)
    case "$os:$arch" in
        Darwin:arm64|Darwin:aarch64) TARGET=darwin-arm64 ;;
        Darwin:x86_64|Darwin:amd64) TARGET=darwin-x64 ;;
        Linux:aarch64|Linux:arm64) TARGET=linux-arm64 ;;
        Linux:x86_64|Linux:amd64) TARGET=linux-x64 ;;
        *) die "unsupported platform: $os/$arch" ;;
    esac
fi

case "$TARGET" in
    darwin-arm64|darwin-x64|linux-arm64|linux-x64)
        archive="agents-$TARGET.tar.gz"
        ;;
    *) die "unsupported target: $TARGET" ;;
esac

BASE_URL=${BASE_URL%/}
archive_url="$BASE_URL/$VERSION/$archive"
checksum_url="$archive_url.sha256"
destination="$PREFIX/bin/agents"

if [ "$DRY_RUN" -eq 1 ]; then
    printf 'target:       %s\narchive:      %s\nchecksum:     %s\ndestination:  %s\n' \
        "$TARGET" "$archive_url" "$checksum_url" "$destination"
    exit 0
fi

command -v curl >/dev/null 2>&1 || die "curl is required"
tmpdir=$(mktemp -d "${TMPDIR:-/tmp}/172x-install.XXXXXX")
trap 'rm -rf "$tmpdir"' EXIT HUP INT TERM
archive_path="$tmpdir/$archive"
checksum_path="$tmpdir/$archive.sha256"
curl --fail --silent --show-error --location "$archive_url" --output "$archive_path"
curl --fail --silent --show-error --location "$checksum_url" --output "$checksum_path"

expected=$(awk 'NR == 1 { print $1; exit }' "$checksum_path")
case "$expected" in
    [0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]* ) ;;
    *) die "checksum file is malformed" ;;
esac
if command -v sha256sum >/dev/null 2>&1; then
    actual=$(sha256sum "$archive_path" | awk '{ print $1 }')
elif command -v shasum >/dev/null 2>&1; then
    actual=$(shasum -a 256 "$archive_path" | awk '{ print $1 }')
else
    die "sha256sum or shasum is required"
fi
[ "$actual" = "$expected" ] || die "checksum verification failed"

extract_dir="$tmpdir/extracted"
mkdir -p "$extract_dir"
entries=$(tar -tzf "$archive_path")
[ "$entries" = "agents" ] || die "release archive has unexpected contents"
tar -xzf "$archive_path" -C "$extract_dir"
[ -f "$extract_dir/agents" ] || die "release archive does not contain agents"
if [ -e "$destination" ] && [ "$FORCE" -ne 1 ]; then
    die "$destination already exists; use --force to replace it"
fi
[ -L "$destination" ] && die "$destination is a symbolic link; remove it before installing"
mkdir -p "$(dirname "$destination")"
staged_destination="$destination.tmp.$$"
cp "$extract_dir/agents" "$staged_destination"
chmod 0755 "$staged_destination"
mv -f "$staged_destination" "$destination"
printf 'installed %s to %s\n' "$VERSION" "$destination"
printf 'run: %s install codex --dry-run\n' "$destination"
