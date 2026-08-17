# Distribution

172X Agents is distributed as host-ready content and a standalone command-line executable. End
users do not need Python, `pip`, `pipx`, or a project language runtime to install the 172X CLI.

## Source of record and mirror

GitHub Releases are the release source of record. Each versioned release contains one archive per
supported operating-system and architecture target, a `.sha256` file beside every archive, and a
`manifest.json` describing the exact artifact bytes.

The release also contains an aggregate `SHA256SUMS` file for independent bulk verification.

Cloudflare R2 mirrors the same immutable release files at:

```text
https://agents.172x.ai/releases/<version>/
```

The installer defaults to that custom domain. A release must not be considered available until the
GitHub assets, Cloudflare objects, checksums, and manifest agree.

## Supported release targets

| Target | Archive | Executable |
| --- | --- | --- |
| `darwin-arm64` | `agents-darwin-arm64.tar.gz` | `agents` |
| `darwin-x64` | `agents-darwin-x64.tar.gz` | `agents` |
| `linux-arm64` | `agents-linux-arm64.tar.gz` | `agents` |
| `linux-x64` | `agents-linux-x64.tar.gz` | `agents` |
| `windows-x64` | `agents-windows-x64.zip` | `agents.exe` |

The build runner uses PyInstaller only while producing release artifacts. The resulting executable
contains the CLI and canonical library; PyInstaller is not an end-user dependency.

## Pinned installation

The recommended path downloads the installer, inspects it locally, and runs it with an explicit
release version:

```bash
curl --fail --location --remote-name https://agents.172x.ai/install.sh
sh install.sh --version v0.1.0
```

The convenience form is also supported:

```bash
curl -fsSL https://agents.172x.ai/install.sh | sh -s -- --version v0.1.0
```

On Windows, save and inspect the script before running it:

```powershell
irm https://agents.172x.ai/install.ps1 -OutFile install.ps1
.\install.ps1 -Version v0.1.0
```

The PowerShell pipeline form is available when interactive convenience is preferred:

```powershell
& ([scriptblock]::Create((irm https://agents.172x.ai/install.ps1))) -Version v0.1.0
```

Every installer requires a pinned version, downloads the archive and its checksum, verifies
SHA-256 before writing, defaults to a user-local destination, supports `--dry-run`/`-DryRun`, and
does not install Python or modify project dependencies.

For testing a mirror or a local fixture, override the release root:

```bash
sh install.sh --version v0.1.0 --base-url https://example.test/releases --dry-run
```

## Release process

Pushing a `vMAJOR.MINOR.PATCH` tag starts `.github/workflows/release.yml`. The workflow builds all
target executables, creates deterministic archives and checksums, generates and verifies the
manifest, and publishes the GitHub Release. Cloudflare mirroring remains a deliberate release
step so the maintainer can verify the destination and cache state before announcing the install
URL.

Upload each generated release file to the R2 bucket with a scoped Cloudflare credential. Wrangler
v4 remote object writes use the explicit `--remote` flag:

```bash
wrangler r2 object put 172x-agents-releases/releases/v0.1.0/manifest.json \
  --file release/manifest.json --remote
```

Repeat for each archive and `.sha256` file. Confirm the same bytes and checksums through both
GitHub and `https://agents.172x.ai` before publishing release notes.

The R2 bucket must be connected to the `agents.172x.ai` custom domain, served over HTTPS, and not
exposed through the rate-limited `r2.dev` development URL. Keep Cloudflare credentials out of the
repository and release artifacts.

The repository-root `install.sh` and `install.ps1` files must also be uploaded to the bucket root;
the release workflow attaches those exact scripts to the GitHub Release for source-of-record
comparison. Keep the scripts and release objects publicly readable, but grant the upload credential
write access only to this bucket and prefix.

## Optional PyPI compatibility

The existing manual PyPI workflow remains available for compatibility or maintainer experiments.
It is not the primary installation path and does not define the runtime requirements for 172X users.
