# Handoff envelope

Use this reference whenever one specialist transfers work, a verdict, or a decision request to
another agent or a human. A handoff is complete only when the receiver can identify the artifact,
understand its acceptance and evidence state, and act without reconstructing hidden context.

## Required inputs

- The receiving agent or human and the action they are expected to take.
- The artifact being handed off, including its path, identifier, version, or reviewed head.
- Applicable acceptance criteria and current status for each material criterion.
- Evidence, assumptions, unresolved decisions, and residual risks.
- Any feedback-cycle or human-gate state that limits the next action.

Missing artifact identity, receiver, or material acceptance state blocks a ready handoff. Missing
non-material context may proceed only as a labeled assumption with an owner and consequence.

## Required envelope

1. **Receiver and requested action** — name one accountable next agent or the human decision owner.
2. **Artifact** — identify the deliverable and its current version, path, or change-request head.
3. **Acceptance-criteria status** — mark each criterion `satisfied`, `not satisfied`, `unverified`,
   or `not applicable`, with a short reason.
4. **Evidence state** — link or summarize the evidence supporting each material status and name
   coverage limits. Use `references/common/evidence-and-uncertainty.md` when labels are unclear.
5. **Assumptions** — state every premise used to proceed, its impact if false, and validation owner.
6. **Unresolved decisions** — name the decision, options when known, consequence of delay, and
   authorized decision owner.
7. **Residual risks** — describe remaining exposure, likelihood only when supported, impact, and
   mitigation or monitoring owner.
8. **External-action state** — distinguish a local recommendation from an actual provider approval,
   merge, release, deployment, or notification. Include external identifiers only for actions that
   actually occurred.

## Staged method

1. Confirm the receiver has authority for the requested next action.
2. Freeze or identify the artifact version. For code review, record the exact diff or head; for a
   document, record its path and revision or date.
3. Map every material acceptance criterion to status and evidence.
4. Move uncertainty into the explicit assumptions, unresolved decisions, and residual-risk fields.
5. Check that the next agent does not need to infer product intent, silently change a stable
   contract, or repeat evidence collection merely to discover what was done.
6. State the next action and the condition that permits it. Stop at a human gate or failed criterion.

## Routing rules

| Condition | Receiver | Handoff state |
| --- | --- | --- |
| Implementation is ready for independent verification | `qa-engineer` | Artifact identified; criteria and implementation checks attached; no self-approval claim |
| QA found a reproducible failure | Responsible implementation agent | `not satisfied` criterion, reproduction, affected artifact, and bounded fix request |
| QA passed and specialist review is required | Named reviewer | Current artifact, QA evidence, criteria matrix, coverage limits, and residual risks |
| Product, policy, scope, or authority decision is unresolved | Human | Options, evidence, consequence, and smallest decision needed; downstream work stops |
| Stable design and architecture are compatible | Implementation agents | Reviewed contract artifact plus explicit user gate state |
| Evidence is incomplete for a material verdict | Evidence owner or human | `unverified`, missing check, impact, and proposed next step; never a ready verdict |

One envelope may name multiple receivers only when each receives the same stable artifact and their
actions are independent. Otherwise create separate, scoped handoffs.

## Normal and failure paths

On the normal path, the sender provides a versioned artifact, criterion status, evidence, and risks;
the receiver accepts the artifact or returns a precise deficiency.

On a failure path, do not disguise missing evidence as an assumption. Return the handoff to its
owner when artifact identity or acceptance status is absent. Route a product or policy ambiguity to
the human. Route a contract conflict to the role that owns that contract. Record a feedback return
against the workflow's existing limit; do not weaken a criterion to make the handoff pass.

## Common mistakes

- “Done; please review” with no artifact version, criteria status, or evidence.
- Sending a fix request without reproduction, impact, or receiving owner.
- Naming every downstream role instead of one accountable next action.
- Hiding an unresolved product decision in implementation assumptions.
- Treating a local APPROVED recommendation as a GitHub approval or confirmed merge.
- Omitting residual risk because all automated checks passed.
- Asking the receiver to reconstruct commands or sources that the sender already used.

## Calibration

**Good:** “Receiver: `qa-engineer`; action: verify AC-1–AC-3. Artifact: working-tree diff for
`src/parser.py` at head `abc123`. AC-1/2 satisfied by focused tests; AC-3 unverified because the
fixture service was unavailable. Assumption: documented UTF-8 input contract remains authoritative
(owner: human if disputed). Open decisions: none. Residual risk: integration encoding behavior.
No external approval or deployment occurred.”

**Counterexample:** “Receiver: QA. Everything passes and is ready to ship.” The artifact, commands,
criteria, uncertainty, risks, and actual external-action state are all missing.

## Evidence expectations

The envelope should point to evidence, not duplicate every log. Preserve exact commands and
observations for failed or material checks. If evidence is stored only in the conversation, include
enough of it for the receiver to reproduce the conclusion. Never imply that an unavailable artifact
or external state was inspected.

## Escalation triggers

Escalate when no receiver has authority; sources disagree about ownership; the artifact changed
after evidence was collected; a material criterion is unverified; the requested next step crosses a
human gate; the workflow return limit is reached; or an external action requires credentials or
authorization not present in the handoff.

## Related assets

- `assets/quality/qa-report-template.md` for a PASS or FAIL handoff.
- `assets/quality/review-report-template.md` for specialist or final review handoffs.
