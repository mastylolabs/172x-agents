# CLI contract

`agents` and `172x-agents` expose the same small command group. The optional, separately
installed root CLI may load it as `172x agents`.

The CLI installs and diagnoses integrations; Codex coordinates workflow steps. It does not run an
agent runtime, call model APIs, manage credentials, or provision external development tools. The
explicit `agents refresh` command may update the isolated user-level 172X CLI tool from a validated
local checkout.

## Install Forge once

```text
agents install codex [--only CAPABILITY_ID]... [--dry-run] [--force]
```

This is a personal, global installation. It writes only Forge-managed skills beneath the current
Codex home (normally `~/.codex/skills/172x-*`). It does not select a language, prompt for gates,
write project files, edit `.codex/config.toml`, install Codex, or authenticate Codex.

Use repeatable `--only` values for a focused installation:

```bash
agents install codex --only principal-architect
agents install codex --only principal-architect --only principal-engineer
agents install codex --only dev-loop
```

Omit `--only` to install the complete official library. A selected workflow includes its declared
specialists; a selected specialist includes required shared material. `--force` can replace only
conflicting 172X-managed global skill files. Changing selections removes stale canonical files that
still match bundled bytes, preserves unknown files, and treats a modified stale file as a conflict
unless `--force` explicitly authorizes removal.

Global installation ships Codex skills. It does not write a guessed global custom-agent TOML
location; support for that Codex projection must be verified before it is implemented.

## Refresh a local development checkout

```text
agents refresh [--source PATH] [--dry-run]
```

Run this from a local `172x-agents` checkout after changing its source. The command validates the
checkout, refreshes the user-level editable CLI with `uv tool install --editable ... --force`, and
then refreshes all managed Codex skills under `$CODEX_HOME/skills/172x-*`. `--source` can identify a
checkout when the current directory is elsewhere; `--dry-run` performs no writes. It never changes
the project tree, dependencies, external development tools, or credentials. If the installed CLI
predates `refresh`, bootstrap it once from the checkout with `uv tool install --editable . --force`.

## Uninstall Forge

```text
agents uninstall codex [--only CAPABILITY_ID]... [--dry-run] [--force]
```

This removes only exact Forge-managed global skill directories beneath the current Codex home. It
never removes project files, `.172x/` state, external tools, or unrelated Codex skills. Omit
`--only` to remove the complete Forge installation; use it to remove one direct capability:

```bash
agents uninstall codex
agents uninstall codex --only principal-architect
agents uninstall codex --dry-run
```

The command refuses a modified or unsafe Forge skill directory unless `--force` explicitly
confirms that removing that exact namespaced directory is intended.

## Activate a local quality contract

```text
agents activate [python|rust] [--path RELATIVE_PATH] [--gate TOOL]... [--dry-run] [--force]
```

Activation records the developer's expected language and gate IDs in ignored local state:

```text
.172x/contexts.toml
```

When the target is a Git repository, activation adds `.172x/` only to that repository's local
`.git/info/exclude`; it never edits a committed `.gitignore`.

When `--gate` is omitted, activation asks which supported Python gates the project expects. It
never adds, removes, upgrades, or selects external tools or a package manager. `--path` is
repository-relative and lets a monorepo record a selected package:

```bash
agents activate python --path services/api
```

Python and Rust are activatable today. TypeScript and other languages are planned and are rejected
rather than appearing to work. Rust defaults to `fmt`, `clippy`, and `test`, each mapped to a fixed
`cargo` command.

## Diagnostics

```text
agents doctor [--target PATH]
```

`doctor` is read-only. It validates the bundled library, global Forge skills, Codex availability,
local activation, selected gate availability, and relevant Git/provider prerequisites. It reports
missing gates with evidence and guidance; it does not install anything.

## Library and workflows

```text
agents list
agents domains
agents capabilities
agents providers
agents workflows [--target PATH]
agents show WORKFLOW_ID [--target PATH]
agents --workflow WORKFLOW_ID [--target PATH] [--no-launch]
```

`list` reports whether globally installed specialist skills are current. `domains`, `workflows`,
and `show` read the bundled Markdown catalog; the latter two also recognize validated local
workflow Markdown at `.172x/workflows/` when a target is supplied.

Selecting a bundled workflow validates its global Forge skill, writes ignored
`.172x/active-workflow`, adds `.172x/` to local Git exclude when available, and optionally launches
the local `codex` executable. Project-owned workflows are authoring, listing, and inspection
material only in v0.1; `--workflow`, `$172x run`, and `$172x use` do not select or run them. The CLI
never installs or authenticates Codex.

### Codex CLI options

When launching a workflow, unknown root options are forwarded unchanged to the local Codex
executable before the 172X workflow prompt:

```bash
agents --model gpt-5.4 --ask-for-approval never --workflow dev-loop
```

Use only options supported by your installed `codex --help`.

## GitHub change-request guard

```text
agents github reviewers
agents github reviewer-status --reviewer LOGIN
agents github review PR_NUMBER --reviewer LOGIN --head HEAD_OID --report REPORT
agents github approve PR_NUMBER --reviewer LOGIN --head HEAD_OID --report REPORT
agents github review-threads PR_NUMBER
agents github resolve-thread PR_NUMBER THREAD_ID
agents github merge-policy
agents github gate PR_NUMBER
agents github merge PR_NUMBER
```

Reviewer actions are authorized by local repository configuration in `.git/172x/config.toml`; token
values never belong in that file:

```toml
[github.review]

[[github.review.reviewers]]
login = "172x-reviewer-bot"
token_env = "REVIEWER_GH_TOKEN"
```

Run `agents activate python` to create this file interactively. Its defaults are provider `github`,
base branch `main`, merge method `squash`, reviewer `172x-reviewer-bot`, and token environment
variable `REVIEWER_GH_TOKEN`. This mapping is required only for the guarded GitHub actions below.
The standalone PR Reviewer can
inspect a change and return a local recommendation without it. A local `APPROVED` result is not a
GitHub approval. For `dev-loop`, the mapping and exported credentials are required project setup;
the loop validates them before provider review and fails closed when the reviewer identity cannot
access the repository.

The reviewer list is the source of truth; there is no separate reviewer-count setting. Its length
determines the required reviewer count, and every configured reviewer must approve the exact current
pull-request head before `gate` or `merge` can proceed. Each `token_env` names an environment
variable containing that reviewer's token. `reviewer-status` verifies the token's GitHub login and
repository permission without printing the token. `review` publishes a non-approving report review;
`approve` submits and confirms an actual provider approval. Both commands re-check that the pull
request is open, non-draft, authored by a different account, and still at `--head HEAD_OID`.

`review-threads` is read-only. `resolve-thread`, `gate`, and `merge` require an active local context
and fail closed unless the pull request is open, non-draft, clean, targets `main`, has GitHub's
`APPROVED` decision, has no failing or pending reported checks, has no unresolved review threads,
and has approvals from every configured reviewer on the checked head. `merge` repeats that gate,
pins the reviewed head commit, and uses only the configured normal merge method; it never sends
`--admin` or `--auto` and never bypasses repository rules.

### Provider and merge policy

`agents providers` lists registered provider families and implemented capabilities without network
access. Source-control commands remain explicitly namespaced so authentication and provider
semantics are visible. The workflow itself uses provider-neutral change-request, review, and merge
contracts.

Projects select a source-control provider and an explicit merge method in `.git/172x/config.toml`:

```toml
[provider]
family = "source_control"
name = "github"

[merge]
base_branch = "main"
method = "rebase"
```

`agents github merge-policy` displays the configured method, live GitHub-allowed methods, the
provider default, and a PASS or BLOCKED compatibility result. `gate` and `merge` repeat this
compatibility check immediately before acting. Existing projects without local configuration retain
the v0.1 GitHub and profile defaults for compatibility. A legacy root `172x.toml`, if present, is
migrated by activation and remains a read-only fallback.
