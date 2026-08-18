---
id: dev
name: Development Workflow
description: Coding, independent QA, and PR review with a human merge decision.
version: 2
---
## Purpose
Deliver a bounded coding request with independent verification and a local review recommendation.

## Inputs
The identified request, repository instructions, acceptance criteria, non-goals, relevant project
context, current artifact state, and unresolved decisions or risks.

## Participating agents
- `principal-engineer`
- `qa-engineer`
- `pr-reviewer`

## Flow
1. `principal-engineer` implements the bounded request and hands off the identified artifact,
   criteria status, checks and observations, assumptions, unresolved decisions, and residual risks.
2. `qa-engineer` independently evaluates that artifact and returns PASS or FAIL using
   `assets/quality/qa-report-template.md`.
3. On PASS, `pr-reviewer` evaluates the same artifact, diff, implementation handoff, and QA report,
   then records findings and its local verdict in `assets/quality/review-report-template.md`.
4. On APPROVED, provide the evidence envelope and local recommendation, then stop for the human
   merge decision.

## Parallel work
No stage is parallel by default because QA and review require the preceding handoff.

## Feedback loops
QA FAIL or PR review CHANGES_REQUESTED returns the current artifact, finding evidence, affected
criteria, pass conditions, assumptions, decisions, and risks to `principal-engineer`. Each return
consumes one feedback cycle. Refresh affected evidence after a change. After three cycles without
approval, stop and escalate; do not weaken acceptance criteria.

## Human gates
The user decides whether to merge after an APPROVED local recommendation. The workflow must stop after three feedback cycles for user direction.

## Completion criteria
All acceptance criteria have current-artifact evidence, QA returns PASS, PR Review returns
APPROVED with no unresolved finding, and the human receives the complete recommendation envelope.
No GitHub approval or merge occurs in this workflow.

## Failure and escalation
If checks cannot run, evidence is insufficient, or three feedback cycles are exhausted, report attempts, current failures, and options to the human. Do not claim completion.
