# Distribution

172X Agents is distributed as a standalone command-line executable. End users do not need
Python, `pip`, `pipx`, or a project language runtime.

## Source of record

GitHub Releases are the source of record. Each versioned release contains one archive per
supported operating-system and architecture target, a `.sha256` file beside every archive,
`SHA256SUMS`, `manifest.json`, and the versioned installer scripts.

## Supported release targets

| Target | Archive | Executable |
| --- | --- | --- |
| `darwin-arm64` | `agents-darwin-arm64.tar.gz` | `agents` |
| `darwin-x64` | `agents-darwin-x64.tar.gz` | `agents` |
| `linux-arm64` | `agents-linux-arm64.tar.gz` | `agents` |
| `linux-x64` | `agents-linux-x64.tar.gz` | `agents` |
| `windows-x64` | `agents-windows-x64.zip` | `agents.exe` |

The build runner uses PyInstaller only while producing release artifacts. The resulting
executable contains the CLI and canonical library; PyInstaller is not an end-user dependency.

## Installation

The short Forge command installs the latest stable release:

```bash
curl -fsSL https://forge.172x.ai/install.sh | sh
```

Pin an exact release when reproducibility matters:

```bash
curl -fsSL https://forge.172x.ai/install.sh | sh -s -- --version v0.1.0
```

For an inspection-first install, download the installer from the same pinned GitHub Release that
contains the executable assets:

```bash
curl --fail --location --remote-name \
  https://github.com/mastylolabs/172x-agents/releases/download/v0.1.0/install.sh
sh install.sh --version v0.1.0
```

Windows convenience form:

```powershell
irm https://forge.172x.ai/install.ps1 | iex
```

Windows inspection-first form:

```powershell
irm https://github.com/mastylolabs/172x-agents/releases/download/v0.1.0/install.ps1 -OutFile install.ps1
.\install.ps1 -Version v0.1.0
```

The installer uses GitHub's latest stable release by default or an explicit `--version`/`-Version`
override. It downloads the archive and its checksum from the GitHub Release, verifies SHA-256
before writing, defaults to a user-local destination, supports `--dry-run`/`-DryRun`, and does not
install Python or modify project dependencies.

For a local fixture or mirror, override the release root:

```bash
sh install.sh --version v0.1.0 --base-url https://example.test/releases --dry-run
```

## Release process

Pushing a `vMAJOR.MINOR.PATCH` tag starts `.github/workflows/release.yml`. The workflow builds
all target executables, creates deterministic archives and checksums, generates and verifies the
manifest, and publishes the GitHub Release with the installer scripts attached.

No Cloudflare artifact bucket or deployment credential is required. The existing Forge Pages build
publishes the canonical installer scripts at `forge.172x.ai`; those scripts download the selected
binary and checksum directly from GitHub Releases.

## Optional PyPI compatibility

The existing manual PyPI workflow remains available for compatibility or maintainer experiments.
It is not the primary installation path and does not define the runtime requirements for 172X users.
