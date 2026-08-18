# Agent catalog

172X Agents are operational specialists. They do not claim invented experience, make unverified
promises, or replace human authority. Every agent defines a mission, positive and negative routing,
input readiness, a numbered role method, conditional decisions, a concrete deliverable, evidence,
calibration, a complete handoff, and boundaries.

## Choose and load a role

Start with both sides of the role's routing contract: **Use this agent when** identifies work it can
own, while **Do not use this agent when** identifies the adjacent specialist or human that should
receive it. A role may proceed with a labeled assumption only when the missing fact does not change
authority, acceptance criteria, irreversible behavior, or external state. Otherwise it stops and
requests the blocking input.

Agent files are deliberately thin cores. They keep the behavior needed on every run, then point
conditionally to deeper `references/` for reusable decision methods and to `assets/` for complete
deliverable templates. A reference is not mandatory context merely because it exists. Load it when
the core's activation condition or the task requires it; use an asset when the requested output
matches that template.

Material conclusions distinguish facts, observations, inference, assumptions, decisions, and
unknowns and cite the evidence and limits that support them. Every handoff names the receiver and
requested action, artifact and version, acceptance-criteria status, evidence state, assumptions,
unresolved decisions, residual risks, and the real human/external-action state. A calibration
good/counterexample helps keep the same evidence and boundary standard across hosts without adding
decorative persona text.

## Product

| Agent | Role |
| --- | --- |
| `brief-author` | Turns an idea, vision, and named source materials into one authoritative build brief. |
| `discovery-specialist` | Clarifies the problem, user, constraints, and assumptions. |
| `market-researcher` | Produces source-backed market context and alternatives. |
| `product-specification-specialist` | Defines scope, non-goals, and testable acceptance criteria. |

## Design

| Agent | Role |
| --- | --- |
| `ux-ui-designer` | Defines flows, interactions, screen/component and content requirements, responsive behavior, states, accessibility criteria, and design-system-compatible UI guidance; it does not invent a brand or visual system. |

## Platform

| Agent | Role |
| --- | --- |
| `principal-architect` | Defines system boundaries, ownership, contracts, trade-offs, diagrams, and decision records. |
| `principal-engineer` | Implements bounded, cross-cutting engineering work. |
| `backend-engineer` | Implements agreed backend behavior against stable contracts. |
| `frontend-engineer` | Implements accessible frontend behavior against stable UX and backend contracts. |
| `technical-feasibility` | Assesses constraints, dependencies, risks, and experiments. |

## Quality

| Agent | Role |
| --- | --- |
| `backend-reviewer` | Independently reviews backend contracts, reliability, and maintainability. |
| `design-architecture-reviewer` | Tests the Brief, UX/UI, and architecture together before implementation. |
| `frontend-reviewer` | Independently reviews frontend behavior, accessibility, and maintainability. |
| `pr-reviewer` | Synthesizes evidence into a local approval recommendation. |
| `principal-codebase-reviewer` | Reconstructs intended behavior, assesses an existing codebase against it, and recommends evidence-backed remediation. |
| `qa-engineer` | Independently verifies acceptance criteria with PASS or FAIL evidence. |

## Security

| Agent | Role |
| --- | --- |
| `security-reviewer` | Identifies evidence-backed security risks and mitigations. |

Browse the same catalog in the CLI:

```bash
agents domains
agents list
```

In an installed Codex project, each agent is also a direct native skill. Open `/skills`, select an entry such as **172X · Brief Author**, **172X · Principal Architect**, or **172X · QA Engineer**, and give that specialist the task directly.

## Evaluation and safe changes

Each canonical agent has a version-aligned TOML fixture under
`src/agent_workflows/library/evaluations/v1/cases/`. Its six cases cover normal success,
incomplete/conflicting inputs, tempting scope expansion, insufficient evidence, an authority
challenge, and handoff completeness. The shared rubric and execution protocol define expected and
prohibited behavior.

Repository validation deterministically checks the agent schema, section order, IDs, internal
paths, handoff recipients, fixture structure and coverage, package resources, and Forge catalog. It
does not run or grade a model. Evidence that an authoring change improved behavior requires repeated
before/after host runs with the same recorded cases, host/model/settings, loaded support, and
predeclared repeat count, followed by scoring every retained transcript with the same rubric.

When changing a role, preserve its ID and narrow authority, update the core and only genuinely
shared references/assets, increment the version for a material contract change, synchronize its
fixture version and six cases, run the full repository gate, and regenerate Forge through the
existing generator. Do not make a file-length or one favorable model run into a quality claim.
