# Getting started

## Install the CLI

Install the latest stable standalone CLI; Python, `pip`, and `pipx` are not required:

```bash
curl -fsSL https://forge.172x.ai/install.sh | sh
```

Windows users can use the pinned PowerShell installer:

```powershell
irm https://forge.172x.ai/install.ps1 | iex
```

See the [distribution contract](DISTRIBUTION.md) for checksum verification, pinned installation,
and the release process.

To contribute from a local checkout instead:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,docs]"
```

For ongoing development of 172X Agents itself, keep the user-level CLI and Codex skills aligned
with the checkout:

```bash
cd ~/dev/code/172x-agents
agents refresh
```

The command may also be run with `--source PATH` and previewed with `--dry-run`. If the currently
installed CLI does not yet know `refresh`, run `uv tool install --editable . --force` once, then use
`agents refresh` for subsequent source changes.

## Install Forge

Install Forge once for your Codex user profile:

```bash
agents install codex
```

To install a focused capability:

```bash
agents install codex --only principal-architect
```

The installer writes only global, namespaced Codex skills. It does not select a language, prompt
for gates, write project files, install tools, modify dependencies, or choose a package manager.
For a preview that writes nothing, add `--dry-run`.

## Activate a project quality contract

From a project root, optionally record the language and expected gate IDs that Forge should check:

```bash
agents activate rust
```

Activation writes ignored `.172x/contexts.toml` only and adds `.172x/` to the repository's local
`.git/info/exclude` when Git is available. It asks for expected gates but never installs or changes
them. In a monorepo, select the package path explicitly:

```bash
agents activate python --path services/api
```

Python and Rust are activatable today. Claude, Gemini, other languages, Linux, and Windows are
planned; use `agents capabilities` to see the current boundary. Rust uses `cargo fmt`,
`cargo clippy`, and `cargo test` as its default gates.

Use `agents providers` to see the registered integration families and implemented capabilities.
GitHub is the first source-control adapter; the workflow contracts are provider-neutral.

Run a read-only readiness check before a workflow:

```bash
agents doctor
```

It reports global Forge status, local activation, expected gate availability, Git/provider
prerequisites, and the independent-reviewer identity requirement. It never installs anything.

Before using the guarded source-control review path, run `agents activate rust`. It asks for the
provider, merge policy, independent reviewer login, and token environment-name mapping. The
defaults are GitHub, `main`, `squash`, `172x-reviewer-bot`, and `REVIEWER_GH_TOKEN`; it then creates
`.git/172x/config.toml` for the currently implemented GitHub adapter:

```toml
[provider]
family = "source_control"
name = "github"

[merge]
base_branch = "main"
method = "squash"

[github.review]

[[github.review.reviewers]]
login = "172x-reviewer-bot"
token_env = "REVIEWER_GH_TOKEN"
```

The file is local Git metadata and does not appear in the working tree. The token environment
variable is never written to the repository. The reviewer list is authoritative, so every configured
identity must approve the exact current pull-request head. This is one-time setup for a project
using `dev-loop` or the explicit GitHub review/approval commands; it is not required to run the
standalone PR Reviewer locally. A standalone local recommendation must not be described as a
provider approval.

## Pick a workflow

For human-controlled development:

```bash
agents --workflow dev
```

For a documented idea that needs UX/UI and backend work:

```bash
agents --workflow idea-to-build
```

For the experimental guarded development cycle:

```bash
agents --workflow dev-loop
```

`dev-loop` takes your task, makes a Brief Author handoff, normalizes a clean current non-main branch
when the local activation permits it, creates a new task branch, runs the selected engineering gate, opens a
provider change request, gets independent QA/review, addresses Must Fix findings, and requests a merge
only after the live provider gate passes. It does not ask for a change-request number. It is
experimental until repeated live runs demonstrate reliable stage handoffs; see
[experimental status](DEV_LOOP_VALIDATION.md).

The reviewer labels findings `MF` (Must Fix), `NH` (Nice to Have), or `Q` (clarification). Principal Engineer must fix MF; it may decline NH with an explanation in the pull request; Q needs an answer or user direction. The workflow stops after two review-return trips instead of spinning forever.

## Existing Codex session

In an already-open Codex session, open `/skills` and select a direct 172X entry such as **172X · Dev Loop**, **172X · Brief Author**, or **172X · Principal Architect**. The native picker scrolls and activates the selected workflow or specialist for the current task.

The optional catalog skill remains available for text browsing:

```text
$172x run dev-loop
```

Use `$172x use idea-to-build` to select the next workflow. `$172x list` shows the installed workflows and specialist-agent catalog. `/workflow` is not a native Codex command.

## Compose a project workflow

Select **172X · Workflow Composer** from `/skills` when the bundled workflows do not fit. It proposes a workflow using only installed roles and waits for approval before writing local `.172x/workflows/<workflow-id>.md`. Then validate it:

```bash
agents workflows --target .
agents show <workflow-id> --target .
```

Project-owned workflows are authoring, listing, and inspection material in v0.1. They do not gain a
global picker entry and cannot be selected with `agents --workflow` or run with `$172x run`.
