# Repository instructions for 172X Agents

These instructions apply to the entire `mastylolabs/172x-agents` repository.

## Read first

Before implementation, read these files in order:

1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/CLI.md`
4. `docs/CODEX_INTEGRATION.md`
5. `docs/WEBSITE.md`
6. `CODEX_BUILD_PROMPT.md`

If documents disagree, use the narrowest v0.1 interpretation and report the conflict before expanding scope.

## Product definition

172X Agents v0.1 is a Markdown-first library of composable agents and workflows with:

- a small independently installable Python CLI;
- an optional product command group for the separate public `172x` CLI;
- project-scoped Codex installation and a committed project profile;
- a repository-scoped Codex workflow skill;
- native Codex custom-agent definitions;
- four bundled workflows: `dev`, `dev-loop`, `idea-to-product`, and `idea-to-build`.

The selected host is the runtime and coordinator. 172X Agents does not implement its own agent executor.

## Non-negotiable minimalism

Do not add any of the following in v0.1:

- workflow engine or state machine;
- SQLite or another database;
- event or artifact store;
- MCP server;
- provider API client;
- async scheduler, task queue, or event bus;
- host abstraction hierarchy;
- policy engine or expression language;
- web application or API server;
- Docker, Kubernetes, or cloud infrastructure;
- plugin marketplace or package manager;
- telemetry or analytics;
- live GitHub mutation other than the narrowly scoped, explicitly opted-in branch/PR, review-thread, approval, and protected merge actions documented for `dev-loop`;
- a generic host abstraction or adapter hierarchy;
- Pipeline migration;
- package publishing or website deployment;
- license selection without owner direction.

Do not create placeholders, empty abstractions, feature flags, interfaces, database models, or configuration fields for those future ideas.

## First filesystem change

The first implementation change must be a comprehensive root `.gitignore`. It must cover:

- Python caches, virtual environments, test and coverage output;
- build and distribution artifacts;
- MkDocs output;
- editor and operating-system files;
- environment files, local credentials, and common secret formats;
- local 172X state under `.172x/`;
- temporary and generated files that should not be committed.

Do not ignore the canonical Markdown library, Codex templates, tests, documentation, or lockfile if one is intentionally adopted.

## Canonical content

Agent and workflow Markdown under `src/agent_workflows/library/` is authoritative.

Every agent file uses flat YAML-style frontmatter with only scalar values:

```markdown
---
id: qa
name: QA Agent
description: Verifies requested behavior and returns evidence-backed PASS or FAIL results.
version: 1
---
```

The body must contain:

- Domain
- Mission
- Use when
- Inputs
- Process
- Decision rules
- Deliverables
- Deliverable format
- Quality bar
- Evidence requirements
- Handoff contract
- Boundaries

Every workflow file uses the same scalar frontmatter and contains:

- Purpose
- Inputs
- Participating agents
- Flow
- Parallel work
- Feedback loops
- Human gates
- Completion criteria
- Failure and escalation behavior

The Python frontmatter reader supports only this deliberately small scalar subset. Do not add a general YAML parser or schema framework.

## Agent quality rules

Agent definitions must be operational and concise.

- Define observable deliverables.
- Require evidence for QA and review decisions.
- State what the agent must not do.
- Specify the receiving agent or human in each handoff.
- Avoid invented experience, fake metrics, exaggerated claims, and decorative personalities.
- Avoid duplicating general host behavior.
- Do not give implementation agents authority to approve their own work.
- Do not let an agent claim a GitHub approval, merge, release, deployment, or notification unless the corresponding external action actually occurred.

## Workflow quality rules

- Workflows compose agent roles; they do not duplicate complete agent prompts.
- Every transition describes the required output from the previous step.
- Independent steps may run in parallel when the host supports it.
- Human gates must stop and ask the user for a decision.
- The `dev` workflow allows at most three implementation feedback cycles before escalation.
- The workflow coordinator must not silently weaken acceptance criteria after a failure.
- A workflow change affects the next execution; do not pretend an already-running agent was retroactively reconfigured.

## CLI boundaries

Keep the Python application small and direct.

Allowed responsibilities:

- load and validate the bundled flat frontmatter;
- list and show agents and workflows;
- install Codex skills, references, custom agents, and one supported project profile;
- select an active workflow in `.172x/active-workflow`;
- optionally launch the local `codex` executable with an initial skill prompt;
- make the narrowly configured `dev-loop` branch/PR, review-thread, approval, and protected merge actions through the local `git` and `gh` executables;
- diagnose whether installed managed files match bundled content;
- expose the Agents Typer application through a `172x.commands` entry point.

Disallowed responsibilities:

- execute workflow steps;
- spawn agents itself;
- track run attempts or histories;
- interpret arbitrary workflow graphs;
- call model APIs;
- manage secrets;
- bypass GitHub protection, administrator requirements, or merge queues;
- provide a background daemon.

Use argument-list subprocess calls with `shell=False`. Never interpolate user input into a shell command.

## Host installation boundaries

The installer writes only documented managed paths:

- `.agents/skills/172x-agents/**`
- `.codex/agents/172x-*.toml`
- `172x.toml`
- `.172x/active-workflow` when a workflow is selected

It must:

- default to the current project;
- accept an explicit target path;
- support `--dry-run`;
- be idempotent;
- preserve unrelated files;
- create parent directories safely;
- refuse conflicting managed files unless `--force` is explicit;
- never write credentials;
- never install or authenticate Codex;
- never edit `.codex/config.toml`.

## Dependencies

Runtime dependencies are limited to Typer and its required transitive dependencies.

Use the Python standard library for:

- paths and file operations;
- package resources;
- frontmatter parsing;
- TOML string generation where practical;
- subprocess launching;
- plugin discovery through `importlib.metadata`.

Development dependencies may include pytest, Ruff, one type checker, MkDocs, and Material for MkDocs.

Do not add Pydantic, PyYAML, tomlkit, an MCP SDK, an ORM, a web framework, or an agent framework.

## Testing expectations

Test behavior at the smallest useful boundary:

- flat frontmatter loading and rejection of invalid content;
- unique agent and workflow IDs;
- every workflow references existing agents;
- required agent and workflow sections exist;
- Codex TOML output parses successfully;
- dry-run writes nothing;
- repeated installation is unchanged;
- unrelated project files survive installation;
- conflicts fail safely and `--force` affects only managed paths;
- active workflow selection validates the ID;
- Codex launch is tested with a mocked subprocess;
- missing Codex produces a helpful message;
- the standalone `agents` and `172x-agents` commands share one application;
- the Agents application mounts beneath a synthetic `172x agents` root;
- workflow completion, CLI help, and completion generation work;
- dev-loop GitHub gates reject missing opt-in, unresolved review threads, non-passing checks, non-approved reviews, and unsafe PR state;
- dev-loop merge uses only the checked PR head and never uses an administrator or auto-merge flag;
- `mkdocs build --strict` succeeds.

Do not create mock workflow hosts or simulated agent runtimes.

## Documentation rules

- Describe only behavior implemented in the repository.
- Do not represent `/workflow` as a native Codex command.
- Use `$172x-agents run <workflow>` for an existing Codex session.
- Clearly separate local review recommendations, GitHub command acceptance, merge-queue state, and an actual confirmed merge.
- Keep install instructions short.
- Preserve the distinction between the 172X product name, repository name, Python distribution name, and import package.

## Change discipline

- Prefer a Markdown change over Python when the behavior is guidance for an agent.
- Prefer a direct function over a class when no persistent object behavior is needed.
- Avoid one-file-per-concept architecture for tiny functions.
- Do not refactor unrelated files.
- Do not commit generated user-project installations.
- Do not add code solely because the previous future blueprint mentioned it.

If real tests demonstrate that prompt-based coordination is unreliable, document the observed failure before proposing deterministic runtime machinery.
