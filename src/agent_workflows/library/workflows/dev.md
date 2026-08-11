---
id: dev
name: Development Workflow
description: Coding, independent QA, and PR review with a human merge decision.
version: 1
---
## Purpose
Deliver a bounded coding request with independent verification and a local review recommendation.

## Inputs
The user's request, repository instructions, acceptance criteria, and relevant project context.

## Participating agents
- `coding`
- `qa`
- `pr-review`

## Flow
1. `coding` implements the request and returns changed files, checks, results, and risks.
2. `qa` independently evaluates the acceptance criteria and returns PASS or FAIL with evidence.
3. On PASS, `pr-review` evaluates the request, diff context, and QA evidence.
4. On APPROVED, provide the local recommendation and stop for the human merge decision.

## Parallel work
No stage is parallel by default because QA and review require the preceding handoff.

## Feedback loops
QA FAIL or PR review CHANGES_REQUESTED returns structured evidence to `coding`. Each return consumes one feedback cycle. After three cycles without approval, stop and escalate; do not weaken acceptance criteria.

## Human gates
The user decides whether to merge after an APPROVED local recommendation. The workflow must stop after three feedback cycles for user direction.

## Completion criteria
All acceptance criteria have evidence, QA returns PASS, PR Review returns APPROVED, and the human has received the recommendation. No GitHub approval or merge occurs in this workflow.

## Failure and escalation
If checks cannot run, evidence is insufficient, or three feedback cycles are exhausted, report attempts, current failures, and options to the human. Do not claim completion.
