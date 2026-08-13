# Codex integration

`agents install codex python` installs a project-scoped coordinator skill, direct native skills for every workflow and specialist, and native custom agents from the canonical Markdown library. It also writes the reviewed, committed `172x.toml` project profile. It does not install Codex, authenticate it, edit `.codex/config.toml`, or write credentials.

For a focused project installation, repeat `--only` with canonical agent or workflow IDs. A selected
workflow includes its documented participating roles; a selected specialist includes its shared support
material:

```bash
agents install codex python --only principal-architect
agents install codex python --only dev-loop
```

When refreshing an installation created before the role-name update, run `agents install codex python --force`. The explicit force refresh replaces changed managed files and removes only the known old generated specialist files, so `/skills` shows the current role catalog without stale entries.

```text
.agents/skills/172x-agents/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── agents/{product,design,platform,quality,security}/*.md
│   ├── workflows/*.md
│   └── {product,platform,quality,security}/*.md
└── assets/
    └── {product,platform}/*.{md,mmd}

.agents/skills/172x-dev-loop/
├── SKILL.md
└── agents/openai.yaml

.agents/skills/172x-brief-author/
├── SKILL.md
└── agents/openai.yaml

.agents/skills/172x-workflow-composer/
├── SKILL.md
└── agents/openai.yaml

.codex/agents/172x-*.toml
172x.toml
```

## Using a workflow

Select and launch from the terminal:

```bash
agents --workflow dev-loop
```

Or, from an existing Codex session:

```text
$172x run dev-loop
```

## Direct Codex entry point

You can start Codex directly in an installed project:

```bash
codex --dangerously-bypass-approvals-and-sandbox
```

Open `/skills` and select a direct entry such as **172X · Dev Loop**, **172X · Brief Author**, or **172X · Principal Architect**. Codex owns that scroll-and-Return picker; selecting a workflow activates it for the current task, while selecting a specialist applies that specialist directly without starting a workflow.

The optional **172X · Catalog** skill remains available for text browsing with `$172x list`.

## Compose a project workflow

Select **172X · Workflow Composer** from `/skills` to draft a workflow from existing 172X roles. It first presents the intended agents, flow, feedback bounds, and human gates. On approval, it writes the project-owned Markdown source to `.172x/workflows/<workflow-id>.md`; it does not run or activate that workflow.

Validate and publish the new native picker entry with:

```bash
agents workflows --target .
agents install codex python --force
```

The refresh creates **172X · <Workflow Name>** from the project source. The generated files under `.agents/skills/` remain managed; the `.172x/workflows/` source remains project-owned and can be committed.

Each direct workflow skill reads the coordinator skill and selected workflow reference, then delegates bounded work to the appropriate native `172x-<role>` subagent. Each direct specialist skill reads and applies its own canonical agent reference without starting a workflow.

`dev-loop` uses `172x.toml` before it starts. It must honor the selected gate tool IDs and packaging convention, provider-neutral workflow language, GitHub pull-request implementation, and current branch policy. It gets its own pull-request number after creating the change request; it never requests one from the user.

Independent QA Engineer and PR Reviewer do not give Principal Engineer authority to approve its own work. Review labels are `MF`, `NH`, and `Q`; review returns are capped at two. After an actual independent GitHub approval, the coordinator may invoke only `agents github gate <number>` and `agents github merge <number>`—never raw `gh pr merge`, `--admin`, or `--auto`.

The Python CLI remains deterministic infrastructure, not a second coordinator. Its role is installation, profile parsing, diagnostics, active workflow selection, and the narrow fail-closed GitHub verification/merge calls.

## Generated files versus source Markdown

The files in `.codex/agents/` are Codex-native generated TOML. Read them when debugging an installation, but make durable changes in the canonical Markdown library (`src/agent_workflows/library/agents/<domain>/*.md`) and regenerate with `agents install codex python --force`. Hand-editing an installed generated file creates a managed-file conflict and is not a supported customization path.
