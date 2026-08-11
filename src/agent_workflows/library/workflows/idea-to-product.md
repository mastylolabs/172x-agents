---
id: idea-to-product
name: Idea to Product Workflow
description: Discovery through evidence-backed review and human approval.
version: 1
---
## Purpose
Turn an idea into an implementation-ready or production-ready result while preserving human decisions.

## Inputs
The idea, intended user, constraints, available repository context, and desired outcome.

## Participating agents
- `discovery`
- `market-research`
- `technical-feasibility`
- `product-specification`
- `ux-ui-design`
- `backend-architecture`
- `frontend-implementation`
- `backend-implementation`
- `qa`
- `frontend-review`
- `backend-review`
- `security-review`
- `pr-review`

## Flow
1. `discovery` produces a bounded problem statement.
2. `market-research` and `technical-feasibility` investigate the discovery brief.
3. Stop for human validation: stop, revise, or proceed.
4. `product-specification` defines scope and acceptance criteria.
5. `ux-ui-design` and `backend-architecture` define compatible foundations and reconcile contracts.
6. `frontend-implementation` and `backend-implementation` implement only after contracts are stable.
7. `qa` verifies the integrated result.
8. `frontend-review`, `backend-review`, and `security-review` evaluate QA-backed work.
9. `pr-review` synthesizes a local recommendation, then stop for human approval.

## Parallel work
Market research and technical feasibility may run in parallel after discovery. UX/UI design and backend architecture may run in parallel before contract reconciliation. Frontend, backend, and security review may run in parallel after QA evidence exists.

## Feedback loops
QA failures and review changes return to the responsible implementation agent with evidence. Re-run affected verification after changes; do not silently drop criteria or roles.

## Human gates
The user must decide whether validated discovery should proceed. The user must approve release, merge, or further work after the final recommendation.

## Completion criteria
The workflow has a human-approved scope, stable compatible contracts, implementation and QA evidence, specialist review evidence, a PR Review recommendation, and an explicit human decision. Recommendations are not releases, merges, or deployments.

## Failure and escalation
If research is inconclusive, contracts conflict, verification fails, or a required decision is missing, stop at the relevant human gate with evidence, alternatives, and open questions.
