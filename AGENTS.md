# Repository instructions for 172X Agents

These instructions apply to the entire `mastylolabs/172x-agents` repository.

## Read first

Before implementation, read these files in order:

1. `README.md`
2. `docs/ARCHITECTURE.md`
3. `docs/CLI.md`
4. `docs/CODEX_INTEGRATION.md`

If documents disagree, use the narrowest v0.1 interpretation and report the conflict before expanding scope.

## Product definition

172X Agents is a Markdown-first library of composable agents and workflows with a typed,
capability-based provider integration layer. It has:

- a small independently installable CLI whose implementation is Python source but whose end-user
  release is a standalone platform executable;
- an optional product command group for the separate public `172x` CLI;
- global Codex skill installation and optional ignored local activation contexts;
- a repository-scoped Codex workflow skill;
- native Codex skills for direct workflow and specialist selection;
- a provider registry with source-control capability contracts and a guarded GitHub adapter;
- four bundled workflows: `dev`, `dev-loop`, `idea-to-product`, and `idea-to-build`.

The selected host is the runtime and coordinator. 172X Agents does not implement its own agent executor.

## Non-negotiable minimalism

Do not add any of the following in v0.1:

- workflow engine or state machine;
- SQLite or another database;
- event or artifact store;
- MCP server;
- async scheduler, task queue, or event bus;
- host abstraction hierarchy;
- policy engine or expression language;
- web application or API server;
- Docker, Kubernetes, or cloud infrastructure;
- plugin marketplace or package manager;
- telemetry or analytics;
- live GitHub mutation other than the narrowly scoped, explicitly opted-in branch/PR, review-thread, approval, and protected merge actions documented for `dev-loop`;
- an unrestricted provider runtime, background integration process, or empty provider adapter;
- Pipeline migration;
- unapproved package publishing or website deployment. The approved distribution boundary is
  manual PyPI compatibility publishing plus versioned GitHub Release standalone artifacts
  documented in `RELEASING.md`;
- license selection without owner direction.

Do not create empty provider adapters or speculative operations. Provider-neutral contracts are
allowed only when they are exercised by an implemented adapter or required by the current registry
and configuration behavior.

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

## Thin core and deep references

Agent Markdown is a concise operating contract. Keep role identity, routing, readiness, the numbered
role method, decisive rules, deliverable, evidence, handoff, calibration, and authority in the core.
Put reusable decision depth and large output shapes in references and assets.

Every agent's `Use when` section must contain these labels exactly once:

- `**Use this agent when:**` for positive routing;
- `**Do not use this agent when:**` for adjacent-role routing and rejection conditions.

Every agent must distinguish blocking inputs from safe labeled assumptions, use a numbered
role-specific procedure, state conditional decisions and escalation, name an exact deliverable or
asset, require evidence for material conclusions, include a useful good/counterexample calibration,
and provide a complete handoff envelope. The envelope names the receiver and requested action,
artifact and versions, acceptance-criteria status, evidence state and limits, assumptions,
unresolved decisions, residual risks, and actual human/external-action state.

References are activated conditionally. A core or reference that depends on library support must
use an explicit rooted path such as `references/quality/testing-strategy.md` or
`assets/quality/qa-report-template.md`; the validator and focused installer use those paths as the
dependency contract. A substantive reference should supply readiness, a staged method, selection
rules, normal/failure paths, anti-patterns, calibration, evidence, escalation, and related assets
where relevant. Do not copy a vendor manual or create overlapping guidance when an existing
reference can be strengthened.

Assets are reusable deliverable templates, not decorative examples. Separate facts, observations,
inference, assumptions, decisions, and unknowns when the output makes material conclusions, and
carry evidence, unresolved decisions, residual risk, and handoff state. Do not duplicate a large
asset inside agent cores or workflows. File length is not a quality gate; include only text that
changes routing, decisions, evidence, output quality, or authority.

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

Workflow transitions pass identified artifacts and the complete evidence/handoff state. Workflows
may point to canonical assets, but must not duplicate agent procedures. Preserve independent QA and
review, bounded feedback, and human gates. `dev-loop` remains experimental and fail-closed: the
current prompt-only coordinator does not yet guarantee exactly-once delegation or reliable bounded
completion.

## Evaluation fixtures

Versioned behavioral scenarios live under `src/agent_workflows/library/evaluations/v1/`. Every
canonical agent has one TOML fixture whose `agent_version` matches the core and covers exactly:

- normal success;
- incomplete or conflicting inputs;
- tempting scope expansion;
- insufficient evidence;
- boundary or authority challenge;
- handoff completeness.

Each case states expected, prohibited, evidence, and handoff behavior. The shared rubric and manual
protocol define scoring and critical failures. Deterministic validation proves schema, category,
version, path, and catalog integrity only; it does not prove model behavior. Do not add a model API,
evaluation service, simulated workflow host, or runtime.

To show that a prompt revision improves behavior, run the same selected cases before and after with
the same recorded host/model/settings and supporting material, choose the repeat count before the
runs, retain transcripts, score every run with the shared rubric, and report regressions and
critical failures. A repository test pass alone is not behavioral evidence.

## CLI boundaries

Keep the Python application small and direct.

Allowed responsibilities:

- load and validate the bundled flat frontmatter;
- list and show agents and workflows;
- install global Codex skills and references;
- refresh the user-level editable 172X Agents CLI and global Codex skills from a validated local checkout;
- record one supported local activation context, initialize local Git provider configuration, and diagnose its expected gates;
- select an active workflow in `.172x/active-workflow`;
- optionally launch the local `codex` executable with an initial skill prompt;
- resolve registered providers and their typed capabilities;
- make narrowly configured source-control branch/change-request, review-thread, approval, and
  protected merge actions through an implemented provider adapter;
- diagnose whether installed managed files match bundled content;
- create deterministic standalone release archives, manifests, and checksums without credentials
  or deployment side effects;
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

- `$CODEX_HOME/skills/172x-agents/**`
- `$CODEX_HOME/skills/172x-*/**`
- `.172x/contexts.toml`
- `.172x/active-workflow` when a workflow is selected

Full Codex installation includes canonical agent and workflow sources plus all bundled references
and assets. A focused agent installation includes only that direct skill, its canonical source, and
the transitive closure of explicit `references/` and `assets/` links. A focused workflow also
includes its canonical workflow source, participating specialist skills and sources, and their
transitive support. Keep selection deterministic and do not add a manifest or generic dependency
framework for this closure.

It must:

- install Forge capabilities once into the current user's Codex home;
- activate an explicit repository-relative local project path;
- support `--dry-run`;
- be idempotent;
- preserve unrelated files;
- create parent directories safely;
- refuse conflicting managed files unless `--force` is explicit;
- never write credentials;
- never install or authenticate Codex;
- never edit `.codex/config.toml`;
- never install, upgrade, remove, or select external development tools or package managers;
- when activating inside a Git repository, use only `.git/info/exclude` to keep `.172x/` local;
  never edit a committed `.gitignore`.

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
- required sections are unique and ordered;
- every role/workflow-like ID, internal reference/asset path, and handoff recipient resolves;
- every agent has one complete, version-aligned evaluation fixture;
- dry-run writes nothing;
- repeated global installation is unchanged;
- full installation includes all canonical workflow sources and support;
- focused installation contains only selected capabilities and transitive rooted-path support;
- every installed explicit reference/asset path remains closed;
- unrelated Codex-home and project files survive installation;
- conflicts fail safely and `--force` affects only managed paths;
- activation writes only ignored local state and never changes dependencies or package-manager files;
- active workflow selection validates the ID;
- Codex launch is tested with a mocked subprocess;
- missing Codex produces a helpful message;
- the standalone `agents` and `172x-agents` commands share one application;
- the Agents application mounts beneath a synthetic `172x agents` root;
- workflow completion, CLI help, and completion generation work;
- standalone release packaging preserves executable contents, emits checksums and a closed manifest,
  and the POSIX installer validates latest and pinned dry-run plus shell syntax behavior;
- dev-loop GitHub gates reject missing opt-in, unresolved review threads, non-passing checks, non-approved reviews, and unsafe PR state;
- dev-loop merge uses only the checked PR head and never uses an administrator or auto-merge flag;
- provider registry resolution, capability discovery, and source-control adapter contract tests;
- merge policy compatibility rejects a configured method that the live provider does not allow;
- Forge catalog generation covers every canonical agent/workflow and derives positive and negative
  routing separately from the labeled `Use when` section;
- `mkdocs build --strict` succeeds.

Do not create mock workflow hosts or simulated agent runtimes.

## Documentation rules

- Describe only behavior implemented in the repository.
- Do not represent `/workflow` as a native Codex command.
- Use a native `172X · …` skill from `/skills` for direct workflow or specialist selection. The optional catalog skill accepts `$172x run <workflow>`.
- Clearly separate local review recommendations, provider command acceptance, merge-queue state, and
  an actual confirmed merge.
- Keep install instructions short.
- Document GitHub Releases as the source of record; installers default to the latest stable release,
  support an explicit pinned version, and verify checksums before writing.
- Preserve the distinction between the 172X product name, repository name, Python distribution name, and import package.
- Do not publish or link `.private/` analysis or progress material.
- Regenerate `forge/src/data/catalog.generated.json` only through
  `scripts/generate_forge_catalog.py` or the existing Forge build command.

## Change discipline

- Prefer a Markdown change over Python when the behavior is guidance for an agent.
- Prefer a direct function over a class when no persistent object behavior is needed.
- Avoid one-file-per-concept architecture for tiny functions.
- Do not refactor unrelated files.
- Do not commit generated user-project installations.
- Do not add code solely because the previous future blueprint mentioned it.

If real tests demonstrate that prompt-based coordination is unreliable, document the observed failure before proposing deterministic runtime machinery.
