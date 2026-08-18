---
id: idea-to-product
name: Idea to Product Workflow
description: Discovery through evidence-backed review and human approval.
version: 2
---
## Purpose
Turn an idea into an implementation-ready or production-ready result while preserving human decisions.

## Inputs
The idea, intended user or current uncertainty, constraints, available repository context, desired
outcome, source authority, and known decisions or risks.

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
1. `discovery-specialist` produces an identified problem/validation brief with evidence,
   assumptions, questions, criteria, and risks.
2. `market-researcher` and `technical-feasibility` investigate the same discovery artifact and
   return separate evidence, conditions, unknowns, and decision implications.
3. Stop for human validation with all three artifacts: stop, revise, or proceed. Record only the
   decision that actually occurs.
4. After proceed, `product-specification-specialist` issues one versioned specification with stable
   requirement/criterion IDs and the complete evidence envelope.
5. `ux-ui-designer` and `principal-architect` independently consume that same specification, trace
   IDs through UX states/data needs and architecture contracts, and reconcile only shared contracts.
6. `frontend-engineer` and `backend-engineer` implement only after those identified contracts are
   stable and the applicable human gate has passed.
7. `qa-engineer` verifies the integrated artifact using `assets/quality/qa-report-template.md`.
8. `frontend-reviewer`, `backend-reviewer`, and `security-reviewer` independently evaluate the same
   QA-backed artifact.
9. `pr-reviewer` reconciles findings in `assets/quality/review-report-template.md`, provides a local
   recommendation, then stops for human approval.

## Parallel work
Market research and technical feasibility may run in parallel after discovery. UX/UI design and backend architecture may run in parallel before contract reconciliation. Frontend, backend, and security review may run in parallel after QA evidence exists.

## Feedback loops
QA failures and review changes return the artifact, finding evidence, affected criteria, pass
conditions, assumptions, decisions, and risks to the responsible implementation agent. Re-run
affected verification after changes; each QA, specialist-review, or PR-review return consumes one
implementation feedback cycle. After three cycles, stop and escalate to the human without silently
dropping or weakening criteria, findings, or roles.

## Human gates
The user must decide whether validated discovery should proceed. The user must approve release, merge, or further work after the final recommendation.

## Completion criteria
The workflow has human-approved scope; traceable specification, UX/UI, and architecture artifacts;
stable compatible contracts; current implementation, QA, and specialist-review evidence; a PR
Review recommendation; and an explicit human decision. Recommendations are not releases, merges,
or deployments.

## Failure and escalation
If research is inconclusive, contracts conflict, verification fails, or a required decision is missing, stop at the relevant human gate with evidence, alternatives, and open questions.
