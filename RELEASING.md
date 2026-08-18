# Releasing 172X Agents

The primary distribution is a standalone executable published through GitHub Releases. PyPI remains
an optional, maintainer-controlled compatibility channel and is never published on a pull request
or a merge to `main`.

## Primary standalone release

1. Change the project version in `pyproject.toml` and refresh `uv.lock` when needed.
2. Merge the version change to `main` after local and GitHub checks pass.
3. Create and push an annotated `vMAJOR.MINOR.PATCH` tag.
4. Let `release.yml` build the macOS, Linux, and Windows executables, generate deterministic
   archives, checksums, and `manifest.json`, and publish the GitHub Release.
5. Verify the GitHub assets, checksums, and manifest before announcing the release.

No Cloudflare credentials or artifact mirror are involved in the release process. Forge is a
separate Cloudflare Pages catalog and is not the binary distribution origin.

## One-time PyPI and GitHub setup

Complete these steps after `.github/workflows/publish-pypi.yml` has merged to `main`, before the
first release.

1. In GitHub repository settings, create an environment named `pypi`, restrict deployments to
   `main`, and require approval from `zmastylo`. Do not add a PyPI API token as a repository or
   environment secret.
2. In PyPI, configure a GitHub Actions Trusted Publisher for:

   ```text
   Owner: mastylolabs
   Repository: 172x-agents
   Workflow: publish-pypi.yml
   Environment: pypi
   ```

   For an existing PyPI project, add this publisher under the project's Publishing settings. For the
   first release, create a pending publisher with the same values. A pending publisher does not
   reserve the package name; it activates only when the first release succeeds.

Trusted Publishing exchanges GitHub's workflow identity for a short-lived PyPI credential. The
repository stores no long-lived PyPI credential.

## Release procedure

1. Change the project version in `pyproject.toml` and refresh `uv.lock` when needed.
2. Merge the version change to `main` after CI passes.
3. In GitHub Actions, open **Publish 172X Agents to PyPI** and select `main`.
4. Enter the exact `pyproject.toml` version and type this confirmation exactly:

   ```text
   PUBLISH 172x-agents
   ```

5. Let the workflow rerun its complete release checks and build the wheel and source distribution.
6. Approve the waiting `pypi` environment deployment. This is the final maintainer decision before
   PyPI receives the distributions.

The workflow rejects non-`main` runs, mismatched versions, missing confirmation, concurrent
publishes, and duplicate uploads. It does not create tags, GitHub Releases, PyPI API tokens, or
automatic release triggers.
