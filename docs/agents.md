# Agent catalog

172X Agents are operational specialists. They do not claim invented experience, make unverified promises, or replace human authority. Every agent defines a mission, decision rules, concrete deliverable format, quality bar, evidence requirements, handoff, and boundaries.

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
| `ux-ui-designer` | Defines flows, states, accessibility requirements, and frontend-facing interface needs. |

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
