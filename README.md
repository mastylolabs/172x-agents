# 172X Agents

Open-source, composable AI-agent workflows—from idea discovery and architecture to coding, QA, PR review, and release.

172X Agents is a Markdown-first workflow layer for coding-agent hosts. It provides focused agent
definitions, reusable workflow playbooks, a direct Codex integration, an independent `agents` CLI, and an
optional command group for the public `172x` CLI ecosystem.

The first release deliberately does not build another agent runtime. Codex runs native subagents, provides tools, and returns results to its coordinating session. 172X Agents tells the host which specialists to use, how work moves between them, where human decisions are required, and what a completed workflow must produce.

Repository: `mastylolabs/172x-agents`

Documentation site: `agents.172x.ai`

## Community and security

172X Agents is distributed under the [MIT License](LICENSE.md). See
[CONTRIBUTING.md](CONTRIBUTING.md) for development and pull-request guidance, follow the
[Code of Conduct](CODE_OF_CONDUCT.md) in community spaces, and report vulnerabilities privately
under the [Security Policy](SECURITY.md). Brand usage is described in [TRADEMARKS.md](TRADEMARKS.md).

The docs dependency intentionally stays on MkDocs 1.x for now: the current Material site uses the MkDocs 1.x theme/plugin model, while MkDocs 2.0 is not a compatible upgrade path. We validate the site with strict builds and will make a deliberate migration decision rather than silently accepting a breaking major release.

## Product principle

Start with instructions. Add machinery only after real usage proves that instructions are insufficient.

That means the first release uses:

- Markdown as the canonical source for agents and workflows;
- native Codex skills for direct workflow and specialist selection, plus a repository-scoped coordinator skill;
- native Codex custom agents and subagents;
- a small Python CLI for installation, discovery, workflow selection, and launching Codex;
- a plain-text active-workflow file when the CLI needs to pass a selection to a new session.

It does not use:

- a workflow engine or scheduler;
- SQLite or an event store;
- a bundled MCP server;
- runtime state machines;
- a policy language;
- direct model-provider APIs;
- a hosted service.

The original deterministic control-plane design is preserved separately as a future architecture option. It is not the v0.1 implementation plan.

## Flexible by design

172X Agents is not one fixed pipeline. A workflow selects only the agents needed for that job.

A developer can run a focused engineering workflow:

```text
Coding -> QA -> PR Review -> Human merge
   ^       |        |
   +-------+--------+
      structured feedback
```

A founder can run a broader idea-to-product workflow:

```text
Idea
  -> Discovery
  -> Market Research + Technical Feasibility
  -> Human validation
  -> Product Specification
  -> UX/UI Design + Backend Architecture
  -> Stable contracts and acceptance criteria
  -> Frontend + Backend Implementation
  -> QA
  -> Frontend + Backend + Security Review
  -> PR/Release recommendation
  -> Human approval
```

Users can add new agents, remove stages, or create smaller workflows without changing Python code.

For project-specific composition, select **172X · Workflow Composer** from Codex `/skills`. It proposes a workflow from the installed roles, waits for your approval, then writes project-owned Markdown under `.172x/workflows/`. Run `agents install codex python --force` afterward to generate that workflow as its own native `/skills` entry. This remains Markdown composition, not a 172X workflow runtime.

## Initial agent library

The first release ships only the roles required by the bundled workflows:

- Brief Author
- Discovery Specialist
- Market Researcher
- Technical Feasibility Specialist
- Product Specification Specialist
- UX/UI Designer
- Principal Architect
- Principal Engineer
- Frontend Engineer
- Backend Engineer
- QA Engineer
- Frontend Reviewer
- Backend Reviewer
- Security Reviewer
- PR Reviewer

These are operational roles, not novelty personalities. Each definition must specify its mission, inputs, process, deliverables, evidence requirements, handoff contract, and boundaries.

## Initial workflows

### `dev`

For an issue or coding request:

1. Coding implements the requested change.
2. QA runs the relevant tests and returns `PASS` or structured failure evidence.
3. Failed QA returns to Coding.
4. Passed QA moves to PR Review.
5. Requested review changes return to Coding.
6. An approved review produces a local approval recommendation and notifies the user.
7. The user decides whether to merge.
8. After three feedback cycles without approval, stop and escalate to the user.

The implementing agent must not review its own work.

### `dev-loop` (experimental)

For a repository with a committed `172x.toml` profile:

1. Brief turns the task into a focused implementation brief and acceptance criteria.
2. The coordinator normalizes any clean non-main branch through the same gated PR path, then creates a new task branch from updated `main`.
3. Coding implements, corrects, and passes the selected named Python gate tools before committing, pushing, and creating the GitHub change request.
4. Independent QA and PR Review classify findings as `MF`, `NH`, or `Q`, with at most two review-return trips.
5. After actual independent GitHub approval, all resolved review threads, and the live GitHub gate, the CLI requests the configured normal merge for the exact checked commit.

It never asks you for a PR number. It only reports completion once GitHub confirms the PR merged; merge-queue acceptance remains pending. It remains experimental while live validation establishes reliable exactly-once subagent handoffs; see [dev-loop validation](docs/DEV_LOOP_VALIDATION.md).

### `idea-to-product`

For turning an idea into an implementation-ready or production-ready result:

1. Discovery clarifies the problem, target user, constraints, and assumptions.
2. Market Research and Technical Feasibility run independently when useful.
3. A human decides whether the idea should proceed.
4. Product Specification defines scope and acceptance criteria.
5. UX/UI Design and Backend Architecture create compatible foundations.
6. Stable contracts and acceptance criteria are agreed before implementation.
7. Frontend and Backend Implementation run independently where possible.
8. QA verifies the integrated result.
9. Frontend, Backend, and Security Review evaluate the evidence.
10. PR Review synthesizes the final recommendation.
11. A human approves release, merge, or further work.

### `idea-to-build`

For a documented vision that will have UX/UI and backend work:

1. Brief reads the idea, vision, and named source materials into one authoritative build brief.
2. UX/UI Design and Backend Architecture work from that same brief in parallel.
3. Design and Architecture Review returns READY, REVISE, or BLOCKED with a gap register and contract matrix.
4. Brief reconciles bounded revisions; the user approves stable contracts before implementation.
5. Frontend and Backend Implementation proceed independently where possible, followed by QA, specialist review, PR Review, and a human decision.

## Intended command-line experience

The standalone installation exposes both a short command and a branded equivalent:

```text
agents ...
172x-agents ...
```

Install the project-scoped Codex integration:

```bash
agents install codex
```

Install only the 172X capabilities this project needs:

```bash
agents install codex python --only principal-architect --only principal-engineer
agents install codex python --only dev-loop
```

Each selected workflow installs its declared specialist roles. A selected specialist includes the
shared references and templates it needs, while the default command continues to install the complete
official library.

Or let the guided installer ask for the supported choices:

```bash
agents install
```

Today, the only selectable profile is Codex + Python + Git + GitHub on macOS. The installer asks for the
Python gate set, defaults to `mypy`, `ruff`, `radon`, and `pytest`, and adds selected tools through an existing
`uv` or Poetry project. It writes a reviewed, committed `172x.toml`; `agents capabilities` lists planned extension points without presenting them as
usable. Gate choices are known Python tool IDs, never arbitrary shell text. The installer and `agents doctor`
check the local host, Git repository and remote, GitHub authentication and repository permission, and selected gate
runner/tools before a run starts.

Explore the library:

```bash
agents list
agents workflows
agents show dev
agents capabilities
agents doctor
agents github gate 123
```

Select a workflow and start a new Codex session:

```bash
agents --workflow dev
```

Pass supported Codex CLI options straight through when launching:

```bash
agents --model gpt-5.4 --ask-for-approval never --workflow dev-loop
```

Select without launching Codex:

```bash
agents --workflow dev --no-launch
```

When the separate `172x-cli` package is installed in the same environment, the identical product
application is also available under the ecosystem command:

```bash
172x agents workflows
172x agents --workflow dev
```

Inside an existing Codex session, use the installed skill:

```text
$172x run dev
```

Switch workflows in the same session:

```text
$172x use idea-to-product
```

`/workflow` is not documented as a native Codex command. A future 172X-owned interface may provide such a picker, but v0.1 uses the supported skill invocation model.

## What installation creates

In the target project:

```text
.agents/
  skills/
    172x-agents/
      SKILL.md
      agents/openai.yaml
      references/
        agents/{product,design,platform,quality,security}/*.md
        workflows/*.md
        platform/*.md
      assets/
        platform/*.{md,mmd}
    172x-dev/
      SKILL.md
      agents/openai.yaml
    172x-brief-author/
      SKILL.md
      agents/openai.yaml
    172x-<other-agent-or-workflow>/
      SKILL.md
      agents/openai.yaml

.codex/
  agents/
    172x-*.toml

172x.toml
```

It does not edit `.codex/config.toml` because v0.1 has no MCP server.

The profile is intentionally small:

```toml
[host]
id = "codex"

[language]
id = "python"

[scm]
id = "git"

[provider]
id = "github"

[gate]
tools = ["mypy", "ruff", "radon", "pytest"]

[change_request]
kind = "pull_request"
base_branch = "main"
merge_method = "squash"
merge_current_branch = true
```

Generated paths are owned by 172X Agents. Installation is project-scoped, idempotent, supports `--dry-run`, preserves unrelated files, and refuses to overwrite changed managed files unless the user explicitly passes `--force`.

## Editing agents: Markdown first

172X agents are authored in Markdown. The Codex `.toml` files are generated native-host projections, not the place to make durable edits.

For 172X maintainers, edit the canonical source:

```text
src/agent_workflows/library/agents/product/brief-author.md
```

Then reinstall with `--force` to regenerate the matching Codex definition:

```bash
agents install codex python --force
```

For an installation created before the role-name update, this explicit refresh also removes the known old generated specialist files so the `/skills` picker contains only current 172X roles.

For an installed project, treat `.codex/agents/172x-*.toml` as owned generated content. Do not edit it by hand: a future install will detect a conflict or replace it when `--force` is used. Project-specific Markdown overrides are a future addition, not behavior implemented today.

The model remains host-neutral:

```text
canonical 172X Markdown → Codex TOML today
                         → Claude Code Markdown when implemented
                         → Gemini CLI Markdown when implemented
```

This keeps the human-authored source readable while each host receives the native format it requires.

## CLI ecosystem

This repository does not own the root `172x` executable. It registers its product-owned Typer
application as `agents` in the standard Python entry-point group `172x.commands`.

The separate public `172x-cli` project may load that entry point alongside other independently
installed products:

```text
172x
  agents
  personalos  # independently installed
  pipeline    # private, independently installed
```

Agents remains fully usable through `agents` or `172x-agents` without installing `172x-cli`.
Pipeline, PersonalOS, and the root plugin host are not implemented in this repository.

## Documentation map

- [Architecture](docs/ARCHITECTURE.md)
- [CLI contract](docs/CLI.md)
- [Codex integration](docs/CODEX_INTEGRATION.md)
- [Agent catalog](docs/agents.md)
- [Website plan](docs/WEBSITE.md)
- [Getting started](docs/getting-started.md)
- [Codex build prompt](CODEX_BUILD_PROMPT.md)
- [Repository instructions](AGENTS.md)

## Scope test

Before adding code, ask:

1. Can the Codex skill express this behavior reliably?
2. Can a Markdown workflow make the handoff clear?
3. Is deterministic software required for safety or external side effects?
4. Has real usage demonstrated the failure?

If the first two answers are yes and the last two are no, keep it in Markdown.

## Later, only when justified

Potential future additions include:

- planned host adapters beyond Codex, language profiles beyond Python, Git remote providers beyond GitHub, and Linux/Windows adapters;
- a packaged Codex plugin;
- external MCP tools for GitHub, Linear, Slack, or shared memory;
- live PR review and notification actions with explicit credentials;
- durable workflow runs, audit trails, and resumability;
- deterministic gates for regulated or team environments;
- a richer 172X interactive workflow picker.

None of those belong in v0.1 unless the owner deliberately changes the scope.
