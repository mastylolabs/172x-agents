# Architecture

172X Agents is a Markdown-first library, not an agent runtime. Codex is the coordinator and executor; the Python package installs global canonical skills, records an optional local quality contract, selects a workflow, performs diagnostics, and provides narrow guarded GitHub helpers for `dev-loop`.

## Canonical content

```text
src/agent_workflows/library/
├── agents/{product,design,platform,quality,security}/*.md
├── workflows/*.md
├── references/{common,product,design,platform,quality,security}/*.md
├── assets/{product,design,platform,quality,security,workflows}/*.{md,mmd}
├── evaluations/v1/{README.md,rubric.md,cases/*.toml}
├── codex/SKILL.md
└── profiles/languages/python.toml
```

Bundled agent and workflow Markdown is authoritative. Forge installs the bundled coordinator and
direct skills once under the user's Codex home, namespaced as `172x-*`. Python validates the small
canonical contract, but does not parse arbitrary workflow graphs or execute steps. The global
installer does not write a guessed global custom-agent TOML location; Codex support for that exact
projection must be verified before it is added.

The direct skill catalog uses only domains with shipped roles: Product, Design, Platform, Quality,
and Security. Agent cores are thin operating contracts: they keep positive and negative routing,
readiness, a numbered specialist method, decisive rules, the deliverable, evidence, calibration,
handoff, and authority close to the role. Shared references provide deeper reusable methods and
selection guidance; assets provide reusable deliverable shapes. They are loaded only when the core
or task activates them, so specialist selection does not imply loading the whole library.

Explicit rooted paths such as `references/platform/change-discipline.md` and
`assets/quality/qa-report-template.md` are both readable links and the focused install dependency
contract. The installer follows those paths transitively, including links from one support file to
another. A full install includes all canonical agent and workflow sources, references, and assets.
A focused agent install includes its direct skill, canonical source, and only that transitive
support closure. A focused workflow additionally includes the selected canonical workflow source
and every participating specialist skill/source. This is a direct deterministic function, not a
manifest format or dependency framework.

Every agent has a scalar frontmatter header and the 12 ordered operational sections. Every workflow
describes its purpose, inputs, participants, flow, feedback loops, human gates, completion criteria,
and escalation behavior. Workflow transitions pass identified artifacts and complete handoff state
without copying specialist procedures. Forge derives both `use when` and `do not use when` from the
labeled canonical routing section; generated catalog JSON is not authored by hand.

## Evidence, handoffs, and evaluation

The common evidence guide separates facts, observations, inference, assumptions, decisions, and
unknowns and defines contradiction and confidence handling. Material conclusions must identify the
support and its limits. The common handoff envelope carries the receiver/requested action, artifact
identity and version, acceptance-criteria status, evidence state, assumptions, unresolved decisions,
residual risks, and actual human or external-action state. Templates preserve the same distinctions.

Versioned TOML cases cover normal success, incomplete/conflicting inputs, tempting scope expansion,
insufficient evidence, boundary/authority challenges, and handoff completeness for every agent.
Deterministic Python validation checks frontmatter, ordered unique sections, IDs, internal paths,
recipients, fixture schema/category/version coverage, and packaged resources. It does not claim that
a host model followed the prompt. The accompanying protocol requires repeated, recorded host runs
and rubric scoring to evaluate behavior; 172X adds no model API, evaluation service, or agent
runtime.

## Local activation and capabilities

`.172x/contexts.toml` is ignored local activation state shared by doctor, gates, and `dev-loop`:

```text
repository-relative path → language → expected gate IDs
```

The initial activatable language is Python. Other hosts, languages, providers, Linux, and Windows are listed as **planned** by `agents capabilities`; the loader rejects them rather than creating empty adapters or configuration fields.

Gates are selected tool IDs from the Python profile. Each maps to a safe argument-list command. Doctor may recognize an existing `uv` or Poetry runner to probe the selected tools, but 172X never installs tools, writes dependency files, or chooses a package manager. Repository-specific gate scripts and arbitrary command configuration are deliberately not part of this release.

## `dev-loop`

`dev-loop` is the experimental, guarded change-request workflow:

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

The current prompt-only coordinator does not yet guarantee exactly-once delegation or reliable
bounded completion. Its dispatch and retry rules are fail-closed guidance, not deterministic
runtime behavior. Provider and GitHub helpers remain separately guarded by the documented explicit
opt-in and live-state checks.

## Boundaries

172X does not add a workflow engine, database, scheduler, provider API client, generic host abstraction, plugin marketplace, hosted service, credentials, telemetry, or a background process. The local GitHub gate uses `gh` with argument lists and `shell=False`; it does not use administrator bypass or auto-merge.
