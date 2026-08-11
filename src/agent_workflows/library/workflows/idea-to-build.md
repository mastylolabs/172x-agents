---
id: idea-to-build
name: Idea to Build Workflow
description: Turns a documented vision into reviewed UX and architecture, implementation, QA, and a human decision.
version: 1
---
## Purpose
Build a product from an idea, vision, and named source materials without allowing UX/UI, backend architecture, or implementation to drift from one another.

## Inputs
The idea, vision, explicitly named documentation or repository paths, desired outcome, constraints, and any existing product or technical context.

## Participating agents
- `brief`
- `ux-ui-design`
- `backend-architecture`
- `design-architecture-review`
- `frontend-implementation`
- `backend-implementation`
- `coding`
- `qa`
- `frontend-review`
- `backend-review`
- `security-review`
- `pr-review`

## Flow
1. `brief` reads all supplied materials and produces an authoritative build brief.
2. `ux-ui-design` and `backend-architecture` work independently from the same brief.
3. `design-architecture-review` returns READY, REVISE, or BLOCKED with a cross-discipline contract matrix.
4. REVISE returns to `brief`, which reconciles only the documented gaps and issues a revised brief. BLOCKED stops for a human decision.
5. When the review is READY, stop for the human build gate with the brief, designs, architecture, and contract matrix.
6. `frontend-implementation` and `backend-implementation` implement in parallel against stable contracts. Use `coding` only for explicitly assigned cross-cutting work.
7. `qa` verifies the integrated result against the brief and acceptance criteria.
8. `frontend-review`, `backend-review`, and `security-review` independently review QA-backed work.
9. `pr-review` synthesizes the evidence and provides a local recommendation. Stop for the human merge, release, or further-work decision.

## Parallel work
UX/UI design and backend architecture may run in parallel after the Brief. Frontend and backend implementation may run in parallel only after READY review and the human build gate. Frontend, backend, and security review may run in parallel after QA evidence exists.

## Feedback loops
The Brief/Design and Architecture Review loop allows at most two REVISE rounds. A third unresolved review outcome escalates to the human. QA FAIL, specialist review changes, or PR review changes return evidence to the responsible implementation agent; each return consumes one implementation feedback cycle. After three implementation feedback cycles without approval, stop and escalate without weakening criteria.

## Human gates
The user decides any BLOCKED design or architecture question. The user must explicitly approve the reviewed brief and stable contracts before implementation. The user decides merge, release, or further work after PR Review; no external action occurs automatically.

## Completion criteria
All named source materials are accounted for; a reviewed brief and stable contract matrix exist; the human has approved proceeding to build; implementation, QA, and specialist review evidence address the acceptance criteria; PR Review has issued a local recommendation; and the user has received it.

## Failure and escalation
If inputs are missing, source materials conflict, the review loop reaches its limit, contracts are unstable, checks cannot run, or implementation feedback reaches its limit, stop with the evidence, current artifacts, unresolved decisions, and options requiring user direction.
