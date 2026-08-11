# Codex integration

`agents install codex python` installs a project-scoped Codex skill and native custom agents from the canonical Markdown library. It also writes the reviewed, committed `172x.toml` project profile. It does not install Codex, authenticate it, edit `.codex/config.toml`, or write credentials.

```text
.agents/skills/172x-agents/
├── SKILL.md
├── agents/openai.yaml
└── references/{agents,workflows}/*.md

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

Open `/skills` and select **172X**. Then use the catalog front door:

```text
$172x list
```

It lists the installed workflows and specialist agents. Agents are native Codex subagents, not separate user-facing skills, so Codex does not render them as a nested `/skills` tree. Start a workflow with:

```text
$172x run dev-loop
```

The skill reads the selected workflow and its named agent references. It delegates bounded work to the appropriate native `172x-<role>` subagent and preserves the handoff contracts in the Markdown source.

`dev-loop` uses `172x.toml` before it starts. It must honor the selected gate tool IDs and packaging convention, provider-neutral workflow language, GitHub pull-request implementation, and current branch policy. It gets its own pull-request number after creating the change request; it never requests one from the user.

Independent QA and PR Review do not give Coding authority to approve its own work. Review labels are `MF`, `NH`, and `Q`; review returns are capped at two. After an actual independent GitHub approval, the coordinator may invoke only `agents github gate <number>` and `agents github merge <number>`—never raw `gh pr merge`, `--admin`, or `--auto`.

The Python CLI remains deterministic infrastructure, not a second coordinator. Its role is installation, profile parsing, diagnostics, active workflow selection, and the narrow fail-closed GitHub verification/merge calls.

## Generated files versus source Markdown

The files in `.codex/agents/` are Codex-native generated TOML. Read them when debugging an installation, but make durable changes in the canonical Markdown library (`src/agent_workflows/library/agents/*.md`) and regenerate with `agents install codex python --force`. Hand-editing an installed generated file creates a managed-file conflict and is not a supported customization path.
