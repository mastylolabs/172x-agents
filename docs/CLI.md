# CLI contract

`agents` and `172x-agents` expose the same small command group. The optional, separately
installed root CLI may load it as `172x agents`.

The CLI installs and diagnoses integrations; Codex coordinates workflow steps. It does not run an
agent runtime, call model APIs, manage credentials, install package dependencies, or provision
external development tools.

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
agents activate [python] [--path RELATIVE_PATH] [--gate TOOL]... [--dry-run] [--force]
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

The only activatable language today is Python. Rust, TypeScript, and other languages are planned
and are rejected rather than appearing to work.

## Diagnostics

```text
agents doctor [--target PATH]
```

`doctor` is read-only. It validates the bundled library, global Forge skills, Codex availability,
local activation, selected gate availability, and relevant Git/GitHub prerequisites. It reports
missing gates with evidence and guidance; it does not install anything.

## Library and workflows

```text
agents list
agents domains
agents capabilities
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
agents github review-threads PR_NUMBER
agents github resolve-thread PR_NUMBER THREAD_ID
agents github gate PR_NUMBER
agents github merge PR_NUMBER
```

The first command is read-only. The latter commands require an active local context and fail
closed unless the pull request is open, non-draft, clean, targets `main`, has GitHub's
`APPROVED` decision, has no failing or pending reported checks, and has no unresolved review
threads. `merge` repeats that gate, pins the reviewed head commit, and uses only the configured
normal merge method; it never sends `--admin` or `--auto` and never bypasses repository rules.
