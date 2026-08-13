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
- `discovery-specialist`
- `market-researcher`
- `technical-feasibility`
- `product-specification-specialist`
- `ux-ui-designer`
- `principal-architect`
- `frontend-engineer`
- `backend-engineer`
- `qa-engineer`
- `frontend-reviewer`
- `backend-reviewer`
- `security-reviewer`
- `pr-reviewer`

## Flow
1. `discovery-specialist` produces a bounded problem statement.
2. `market-researcher` and `technical-feasibility` investigate the discovery brief.
3. Stop for human validation: stop, revise, or proceed.
4. `product-specification-specialist` defines scope and acceptance criteria.
5. `ux-ui-designer` and `principal-architect` define compatible foundations and reconcile contracts.
6. `frontend-engineer` and `backend-engineer` implement only after contracts are stable.
7. `qa-engineer` verifies the integrated result.
8. `frontend-reviewer`, `backend-reviewer`, and `security-reviewer` evaluate QA-backed work.
9. `pr-reviewer` synthesizes a local recommendation, then stop for human approval.

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
