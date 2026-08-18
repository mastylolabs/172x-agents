# Architecture

172X Agents is a Markdown-first library, not an agent runtime. Codex is the coordinator and executor;
the CLI source is Python for maintainability, but end users receive a standalone platform executable
that installs canonical content without requiring Python.

## Canonical content

```text
src/agent_workflows/library/
├── agents/{product,design,platform,quality,security}/*.md
├── workflows/*.md
├── references/{product,platform,quality,security}/*.md
├── assets/{product,platform}/*.{md,mmd}
├── codex/SKILL.md
└── profiles/languages/python.toml
```

Bundled agent and workflow Markdown is authoritative. A project may additionally own canonical workflow Markdown at `.172x/workflows/`, authored through the Workflow Composer or directly in the same deliberately small format. The installer copies references into a project-scoped coordinator skill and generates one direct native skill for each bundled or validated project workflow; it generates native `.codex/agents/172x-*.toml` definitions for agent delegation. Python validates required sections and referenced role IDs, but does not parse arbitrary workflow graphs or execute steps.

The direct skill catalog uses only domains with shipped roles: Product, Design, Platform, Quality, and Security. Shared references are concise decision aids—not a hidden second prompt library; assets are copyable deliverable templates. For example, Principal Architect consults architecture patterns and decision guidance only for material design work, then uses an ADR or Mermaid template when it clarifies a real decision.

Every agent has a scalar frontmatter header and operational sections for mission, inputs, process, deliverables, evidence, handoff, and boundaries. Every workflow describes its purpose, inputs, participants, flow, feedback loops, human gates, completion criteria, and escalation behavior.

## Distribution boundary

GitHub Releases are the source of record for standalone executables. Each release contains
deterministic platform archives, per-archive SHA-256 files, an aggregate `SHA256SUMS`, a versioned
`manifest.json`, and the pinned installer scripts. The installer downloads directly from the
selected GitHub Release and verifies the checksum before writing an executable.

The build environment may use Python and PyInstaller, but those are release-build dependencies only.
The installed `agents` executable contains the CLI and packaged canonical library. Project language
gates remain a separate local activation concern and are never inferred from the installer runtime.

## Project profile and capabilities

`172x.toml` is the project-owned contract shared by installer, doctor, gates, and `dev-loop`:

```text
host → language → scm → provider → gate → change request
```

The initial supported combination is Codex / Python / Git / GitHub / macOS. Other hosts, languages, providers, Linux, and Windows are listed as **planned** by `agents capabilities`; the loader rejects them rather than creating empty adapters or configuration fields.

Gates are selected tool IDs from the Python profile. Each maps to a safe argument-list command. Python runner detection prefers a repository's `uv`, Poetry, or Hatch convention, so 172X does not invent a packaging command. Repository-specific gate scripts and arbitrary command configuration are deliberately not part of this release.

## `dev-loop`

`dev-loop` is the autonomous change-request workflow:

```text
Task
  → Brief Author
  → clean-workspace normalization
  → new branch in the current checkout
  → Principal Engineer
  → selected engineering gate (repeat until pass)
  → commit / push / GitHub pull request
  → independent QA Engineer and review
  → address MF / answer Q / explain any declined NH
  → independent approval (at most two review returns)
  → live GitHub gate
  → normal merge to main
```

The workflow calls the review unit a *change request* so later providers can translate it. The supported GitHub adapter operates on pull requests. It never receives a pull-request number from the user; it obtains that from its own GitHub action.

The guard verifies a current GitHub approval, clean state, every reported GitHub check passing, resolved threads, target branch, and checked head commit immediately before merge. A repository with no reported GitHub checks is valid; its configured local engineering gate remains the workflow evidence. 172X never creates, changes, weakens, or bypasses repository branch rules. Codex never approves its own work. If branch rules require a second eligible GitHub identity, the repository must already provide it; `doctor` reports this as a required check.

There is no hidden run database. Safe recovery comes from visible artifacts: the branch, change request, brief, gate output, and review comments. A new Codex session inspects those artifacts and resumes only from verified state.

## Boundaries

172X does not add a workflow engine, database, scheduler, provider API client, generic host abstraction,
hosted application, credentials, telemetry, or a background process. Versioned standalone release
artifacts are the only binary distribution surface; Forge's separate Cloudflare Pages catalog is
not an artifact mirror and the repository does not store deployment credentials or deploy as a side
effect of a normal build. The local GitHub
gate uses `gh` with argument lists and `shell=False`; it does not use administrator bypass or auto-merge.
