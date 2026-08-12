# Agent catalog

172X Agents are operational specialists. They do not claim invented experience, make unverified promises, or replace human authority. Every agent defines a mission, decision rules, concrete deliverable format, quality bar, evidence requirements, handoff, and boundaries.

## Product

| Agent | Role |
| --- | --- |
| `brief` | Turns an idea, vision, and named source materials into one authoritative build brief. |
| `discovery` | Clarifies the problem, user, constraints, and assumptions. |
| `market-research` | Produces source-backed market context and alternatives. |
| `product-specification` | Defines scope, non-goals, and testable acceptance criteria. |

## Design

| Agent | Role |
| --- | --- |
| `ux-ui-design` | Defines flows, states, accessibility requirements, and frontend-facing interface needs. |

## Platform

| Agent | Role |
| --- | --- |
| `backend-architecture` | Defines backend responsibilities, interfaces, data, failure behavior, and risk. |
| `backend-implementation` | Implements agreed backend behavior against stable contracts. |
| `coding` | Implements bounded, cross-cutting engineering work. |
| `frontend-implementation` | Implements accessible frontend behavior against stable UX and backend contracts. |
| `technical-feasibility` | Assesses constraints, dependencies, risks, and experiments. |

## Quality

| Agent | Role |
| --- | --- |
| `backend-review` | Independently reviews backend contracts, reliability, and maintainability. |
| `design-architecture-review` | Tests the Brief, UX/UI, and backend architecture together before implementation. |
| `frontend-review` | Independently reviews frontend behavior, accessibility, and maintainability. |
| `pr-review` | Synthesizes evidence into a local approval recommendation. |
| `qa` | Independently verifies acceptance criteria with PASS or FAIL evidence. |

## Security

| Agent | Role |
| --- | --- |
| `security-review` | Identifies evidence-backed security risks and mitigations. |

Browse the same catalog in the CLI:

```bash
agents domains
agents list
```

In an installed Codex project, each agent is also a direct native skill. Open `/skills`, select an entry such as **172X · Brief** or **172X · QA**, and give that specialist the task directly.
