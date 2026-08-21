# Architecture

172X Agents is a Markdown-first library with a typed provider capability layer, not an agent
runtime. Codex is the coordinator and executor; the Python package installs global canonical
skills, records an optional local quality contract, selects a workflow, performs diagnostics, and
provides narrow guarded provider operations for `dev-loop`.

## Canonical content

```text
src/agent_workflows/library/
├── agents/{product,design,platform,quality,security}/*.md
├── workflows/*.md
├── references/{common,product,design,platform,quality,security}/*.md
├── assets/{product,design,platform,quality,security,workflows}/*.{md,mmd}
├── evaluations/v1/{README.md,rubric.md,cases/*.toml}
├── codex/SKILL.md
└── profiles/languages/{python,rust}.toml
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

## Provider capability layer

The registry separates provider discovery from provider behavior:

```text
ProviderRegistry
└── source_control:github
    ├── RepositoryOperations
    ├── ChangeRequestOperations
    ├── ReviewOperations
    ├── MergeOperations
    └── CapabilityDiscovery
```

Provider families are namespaced for future integrations such as models, notifications, artifacts,
secrets, and market data. Capability contracts are typed protocols; a concrete adapter implements
only the operations it actually supports. A large universal provider interface is deliberately not
used. The GitHub adapter is the first implemented source-control provider and wraps the existing
fail-closed `gh` operations. GitLab and Bitbucket can be added as adapters without changing the
workflow roles or provider-neutral handoffs.

The provider and merge policy are repository-local Git metadata initialized by `agents activate
python`, so activation never makes the working tree dirty:

```toml
[provider]
family = "source_control"
name = "github"

[merge]
base_branch = "main"
method = "squash"
```

The file lives at `.git/172x/config.toml` and is never committed or pushed. A legacy root
`172x.toml` remains a read-only compatibility fallback and is copied into local Git metadata during
activation.

The merge gate compares this policy with live provider capabilities and blocks a method mismatch.
Reviewer credentials remain provider-specific because login and token semantics differ by provider.

## Distribution boundary

GitHub Releases are the source of record for standalone executables. Each release contains
deterministic platform archives, per-archive SHA-256 files, an aggregate `SHA256SUMS`, a versioned
`manifest.json`, and the pinned installer scripts. The installer downloads directly from the
selected GitHub Release and verifies the checksum before writing an executable.

The build environment may use Python and PyInstaller, but those are release-build dependencies only.
The installed `agents` executable contains the CLI and packaged canonical library. Project language
gates remain a separate local activation concern and are never inferred from the installer runtime.

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

`agents refresh` is the local development synchronization path. It accepts only a checkout whose
`pyproject.toml` project name is `172x-agents`, refreshes the user-level editable CLI through the
existing `uv` executable, and then force-refreshes the managed Codex skills. It does not mutate the
checkout, project dependencies, external development tools, or credentials.

`.172x/contexts.toml` is ignored local activation state shared by doctor, gates, and `dev-loop`:

```text
repository-relative path → language → expected gate IDs
```

`agents activate python` also initializes `.git/172x/config.toml` with prompted provider, merge, and
reviewer defaults. Both locations are local to the checkout and do not appear in `git status`.

The activatable languages are Python and Rust. Other hosts, languages, concrete providers, Linux, and
Windows are listed as **planned** by `agents capabilities`; the loader rejects them rather than
creating empty adapters or pretending an integration works.

Gates are selected tool IDs from the language profile. Each maps to a safe argument-list command.
Python may recognize an existing `uv` or Poetry runner; Rust uses the existing `cargo` executable
directly. 172X never installs tools, writes dependency files, or chooses a package manager.
Repository-specific gate scripts and arbitrary command configuration are deliberately not part of
this release.

## `dev-loop`

`dev-loop` is the experimental, guarded change-request workflow:

```text
Task
  → Brief Author
  → clean-workspace normalization
  → new branch in the current checkout
  → Principal Engineer
  → selected engineering gate (repeat until pass)
  → commit / push / provider change request
  → independent QA Engineer and review
  → address MF / answer Q / explain any declined NH
  → independent approval (at most two review returns)
  → live provider gate
  → normal merge to main
```

The workflow calls the review unit a *change request* so providers can translate pull requests,
merge requests, or equivalent resources. The GitHub adapter currently operates on pull requests and
obtains their identifier from its own provider action rather than asking the user.

The guard verifies the selected provider's current approval, clean state, passing checks, resolved
threads, target branch, compatible merge policy, and checked head commit immediately before merge.
The provider-specific reviewer list remains the source of truth for independent identities; every
configured reviewer must approve the exact head using the token named by its `token_env` variable.
A repository with no reported provider checks is valid; its configured local engineering gate
remains the workflow evidence. 172X never creates, changes, weakens, or bypasses provider branch
rules. Codex never approves its own work.

There is no hidden run database. Safe recovery comes from visible artifacts: the branch, change request, brief, gate output, and review comments. A new Codex session inspects those artifacts and resumes only from verified state.

The current prompt-only coordinator does not yet guarantee exactly-once delegation or reliable
bounded completion. Its dispatch and retry rules are fail-closed guidance, not deterministic
runtime behavior. Provider adapters remain separately guarded by the documented explicit opt-in and
live-state checks.

## Boundaries

172X does not add a workflow engine, database, scheduler, generic host abstraction, plugin
marketplace, hosted service, credentials, telemetry, or a background process. Provider adapters use
explicit argument-list commands or provider clients only for documented capabilities; the GitHub
adapter uses `gh` with `shell=False` and does not use administrator bypass or auto-merge.
