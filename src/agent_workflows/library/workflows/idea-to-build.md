---
id: idea-to-build
name: Idea to Build Workflow
description: Turns a documented vision into reviewed UX and architecture, implementation, QA, and a human decision.
version: 2
---
## Purpose
Build a product from an idea, vision, and named source materials without allowing UX/UI, backend architecture, or implementation to drift from one another.

## Inputs
The idea, vision, explicitly named documentation or repository paths, desired outcome, constraints,
current product/technical context, source authority, and known decisions or risks.

## Participating agents
- `brief-author`
- `ux-ui-designer`
- `principal-architect`
- `design-architecture-reviewer`
- `frontend-engineer`
- `backend-engineer`
- `principal-engineer`
- `qa-engineer`
- `frontend-reviewer`
- `backend-reviewer`
- `security-reviewer`
- `pr-reviewer`

## Flow
1. `brief-author` accounts for every supplied source and produces one versioned brief with criteria,
   evidence state, assumptions, unresolved decisions, and residual risks.
2. `ux-ui-designer` and `principal-architect` work independently from the same identified brief and
   trace its requirement/criterion IDs through UX states/data needs and architecture contracts.
3. `design-architecture-reviewer` returns READY, REVISE, or BLOCKED in
   `assets/quality/design-architecture-matrix-template.md` for the identified source artifacts.
4. REVISE returns finding evidence and pass conditions to `brief-author` and the affected UX/UI or
   architecture owner; revised artifacts receive new identities before review. BLOCKED stops for the
   smallest human decision.
5. When review is READY, stop for the human build gate with the brief, UX/UI specification,
   architecture, matrix, criteria/evidence status, assumptions, decisions, and residual risks.
6. After that gate, `frontend-engineer` and `backend-engineer` implement in parallel against the
   stable contracts. Use `principal-engineer` only for explicitly assigned cross-cutting work.
7. `qa-engineer` verifies the integrated artifact and returns
   `assets/quality/qa-report-template.md` against the brief and criteria.
8. `frontend-reviewer`, `backend-reviewer`, and `security-reviewer` independently review the same
   QA-backed artifact and preserve their separate findings and risk authority.
9. `pr-reviewer` reconciles current evidence in `assets/quality/review-report-template.md` and
   provides a local recommendation. Stop for the human merge, release, or further-work decision.

## Parallel work
UX/UI design and backend architecture may run in parallel after the Brief. Frontend and backend implementation may run in parallel only after READY review and the human build gate. Frontend, backend, and security review may run in parallel after QA evidence exists.

## Feedback loops
The Brief/Design and Architecture Review loop allows at most two REVISE rounds. A third unresolved
outcome escalates to the human. QA FAIL, specialist-review changes, or PR-review changes return the
artifact, evidence, affected criteria, and pass conditions to the responsible owner; revised work
invalidates affected evidence. Each implementation return consumes one of at most three feedback
cycles. Stop at the limit without weakening criteria.

## Human gates
The user decides any BLOCKED design or architecture question. The user must explicitly approve the reviewed brief and stable contracts before implementation. The user decides merge, release, or further work after PR Review; no external action occurs automatically.

## Completion criteria
All named sources are accounted for; the identified brief, UX/UI, architecture, and matrix are
traceable and compatible; the human approved the build gate; current-artifact implementation, QA,
and specialist evidence address the criteria; PR Review issued a local recommendation; and the user
received the complete evidence envelope.

## Failure and escalation
If inputs are missing, source materials conflict, the review loop reaches its limit, contracts are unstable, checks cannot run, or implementation feedback reaches its limit, stop with the evidence, current artifacts, unresolved decisions, and options requiring user direction.
