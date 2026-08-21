# Codex integration

Install Forge once for your Codex user profile:

```bash
agents install codex
```

The installer writes global, namespaced skills beneath the current Codex home (normally
`~/.codex/skills/172x-*`):

```text
~/.codex/skills/
├── 172x-agents/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   │   ├── agents/{domain}/<agent-id>.md
│   │   ├── workflows/<workflow-id>.md
│   │   └── {common,product,design,platform,quality,security}/*.md
│   └── assets/{product,design,platform,quality,security,workflows}/
├── 172x-dev/
├── 172x-dev-loop/
├── 172x-principal-architect/
└── 172x-<other bundled capability>/
```

A full install includes every direct agent/workflow skill, every canonical agent/workflow source,
and all bundled references and assets. The native skill remains small: when selected, it reads its
canonical source and then loads only the references or assets that the source activates for the
current task.

Use `--only` to keep the global catalog focused:

```bash
agents install codex --only principal-architect
agents install codex --only dev-loop
```

A focused agent install contains the coordinator, that one direct skill and canonical source, and
the transitive closure of explicit `references/` and `assets/` paths named by the source or its
supporting files. A focused workflow also includes its canonical workflow source plus every
participating specialist's direct skill, canonical source, and transitive support. It excludes
unselected workflows, specialists, and unrelated support. Path selection is deterministic and uses
the rooted links already validated in canonical Markdown; there is no separate dependency manifest.

The installer is idempotent, supports `--dry-run`, and refuses conflicting 172X-managed files
unless `--force` is explicit. It does not write project `.agents/` directories, project
`.codex/agents/` definitions, provider configuration, `.codex/config.toml`, credentials, or
package-manager files. Repeating the same selection reports managed files as unchanged, and
unrelated Codex-home or project files are preserved. Changing from a full or different focused
selection removes an unselected canonical file only when it still matches the bundled managed
bytes. A modified stale file is a conflict unless `--force` explicitly authorizes its removal;
unknown files are preserved.

To remove Forge's global skills without affecting other Codex skills:

```bash
agents uninstall codex
```

Use `agents uninstall codex --only principal-architect` for a direct capability, or add
`--dry-run` to inspect the exact namespaced directories first.

## Use a capability

In an existing Codex session, open `/skills` and select an entry such as **172X · Dev Loop**,
**172X · Brief Author**, or **172X · Principal Architect**. The optional **172X · Catalog** skill
also supports text selection:

```text
$172x run dev-loop
$172x use idea-to-build
```

Select and launch a bundled workflow from the terminal:

```bash
agents --workflow dev-loop
```

The selection is local ignored state at `.172x/active-workflow`; it is not a workflow run record.

## Activate a project context

Forge skills are language-neutral. If a project should have an expected gate contract, record it
locally after global installation:

```bash
agents activate rust
```

The command stores only the selected language and gate IDs in `.172x/contexts.toml`, which is
ignored by Git. It never installs Ruff, mypy, pytest, or any other external tool. Use
`agents doctor` to verify what is available in the project's existing environment.

For a monorepo, activate only the package paths you choose:

```bash
agents activate rust --path crates/api
```

For `dev-loop` provider review, run `agents activate python`. The command creates the local
`.git/172x/config.toml` and asks for the source-control selection, merge policy, and reviewer
identity. The resulting non-secret configuration has this shape:

```toml
[provider]
family = "source_control"
name = "github"

[merge]
base_branch = "main"
method = "squash"
```

The file lives inside Git metadata, is not visible to `git status`, and is never committed or pushed.
For GitHub, each `token_env` points to a separately exported secret under `[github.review]`. This is
one-time local setup for the guarded path. The standalone PR Reviewer does not need this mapping to
produce a local recommendation, and a local recommendation is not a provider approval. In
`dev-loop`, the provider adapter publishes the report and confirms approval for the exact reviewed
head before the coordinator invokes the provider gate and guarded merge operation.

## Generated files versus source Markdown

Canonical bundled content lives in `src/agent_workflows/library/` and is projected into the global
Codex skills at installation time. Make durable Forge changes in that canonical Markdown library,
then refresh the local CLI and global skills with:

```bash
agents refresh
```

172X intentionally does not assume or write a global Codex custom-agent TOML location until that
location is verified as supported by Codex.

Versioned evaluation fixtures also ship as Python package resources so repository validation can
verify coverage and core-version alignment. They are authoring and manual host-run specifications,
not installed model evaluations, run history, or a service. 172X does not call a model API or score
host behavior automatically.
