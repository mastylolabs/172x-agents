# Review findings

Use this reference for an independent specialist or final review of a current artifact. It defines
how to turn observed risk into actionable findings and how to preserve finding lifecycle across a
feedback loop. It is not a quota, style guide, implementation plan, or external approval mechanism.

## Required inputs

- The authoritative request, acceptance criteria, and stable contracts.
- The exact artifact, diff, revision, or change-request head being reviewed.
- An implementation handoff and current QA evidence for the same artifact.
- Applicable specialist reviews and current provider-thread state when available and authorized.
- Repository instructions, review boundaries, and feedback-cycle state.

An unidentified or changed artifact, stale QA evidence, a missing material criterion, or unresolved
authority conflict blocks APPROVED. Review may still produce bounded observations, but must label
their evidence and artifact limits.

## Staged method

1. **Verify identity and independence.** Confirm the reviewer did not implement the work and record
   the artifact covered by every supplied evidence source.
2. **Check scope and criteria.** Compare the current diff to the request, non-goals, stable
   contracts, and acceptance criteria. Separate necessary enabling changes from unrelated work.
3. **Trace material paths.** Inspect the success, failure, authorization, data, integration,
   migration, recovery, accessibility, security, or maintainability paths activated by the change.
4. **Reconcile evidence.** Confirm QA and specialist evidence applies to the current artifact.
   Preserve conflicts and coverage limits instead of blending verdicts.
5. **Write findings.** For each supported issue, record classification, affected artifact or
   behavior, violated criterion or contract, observation or reproduction, impact, owner, bounded
   action, and pass condition.
6. **Resolve lifecycle state.** Track every finding through correction, accepted disposition, or
   evidence-backed answer. Reinspect the changed artifact and invalidate stale evidence.
7. **Derive the verdict.** Apply the role's verdict rules only after criterion and finding state is
   complete. State whether the result is local or an actual external action.
8. **Prepare the handoff.** Include artifact identity, criteria, evidence, assumptions, unresolved
   decisions, residual risks, receiver, requested action, and feedback-limit state.

## Finding anatomy

| Field | Required content |
| --- | --- |
| ID and classification | Stable finding ID plus MF, NH, Q, or the specialist's documented severity |
| Affected surface | Exact path, interface, user behavior, data flow, or contract |
| Violated authority | Acceptance criterion, architecture, policy, repository rule, or evidenced risk |
| Evidence | Direct observation, reproduction, current diff, or cited supplied evidence |
| Impact | Concrete failure mode and affected user, system, security boundary, or maintenance path |
| Owner and action | One responsible receiver and the smallest correction or answer needed |
| Pass condition | Observable evidence that would close the finding |
| Uncertainty | Assumption, unknown, confidence limit, or evidence still needed |

Do not create a finding merely to populate every field. If impact or violated authority cannot be
supported, keep the item as an evidence request or question.

## Classification rules

| Classification | Use when | Closure |
| --- | --- | --- |
| `MF` — Must Fix | Current evidence shows an unmet material criterion, broken stable contract, unsafe behavior, or material reliability or maintainability risk | Responsible engineer corrects it and affected QA/review evidence is current |
| `NH` — Nice to Have | The suggestion has evidenced value but current criteria and material safety do not require it | Implement, or record a decline reason that the independent reviewer accepts |
| `Q` — Question | A material conclusion needs an evidence-backed answer or authorized product/contract decision | Answer with evidence, or route to the human; it is not automatically a code change |
| Specialist severity | A specialist reference requires severity such as security impact | Preserve severity and translate unresolved blocking effect into the final MF/NH/Q lifecycle |

One issue should not be split to inflate count. Multiple symptoms with one root cause may share a
finding when owner and pass condition are the same. Separate issues when they require different
authority or verification.

## Verdict rules

- Return CHANGES_REQUESTED when an MF, unanswered material Q, stale required evidence, or unverified
  material criterion remains.
- Return APPROVED only when QA PASS applies to the current artifact, every material criterion has
  evidence, all findings are resolved, and residual risks are explicit.
- An NH decline is not silent dismissal; record the rationale and reviewer disposition.
- A local APPROVED verdict is a recommendation. It is not a provider approval, merge, release, or
  deployment.
- When a configured workflow authorizes a provider action, claim it only after the action actually
  succeeds and record its identifier and current artifact. Never resolve a thread without checking
  the addressed artifact.

## Normal and failure paths

On the normal path, the review covers the current artifact, findings are reproducible and scoped,
feedback returns to the correct owner, affected evidence is refreshed, and the final recommendation
has no hidden lifecycle state.

If evidence is stale or insufficient, withhold approval and request the smallest current check. If
a Q needs product or contract authority, stop at the human or owning role. If the artifact changes,
reinspect affected paths and provider threads. If the feedback limit is reached, preserve every
unresolved finding and escalate; never reclassify an issue merely to finish.

## Common mistakes

- “This feels wrong” without a violated contract, impact, or observation.
- Requiring a preferred pattern, framework, or broad cleanup unrelated to current criteria.
- Treating QA PASS as a substitute for independent diff review.
- Combining evidence from different heads or silently dropping a specialist concern.
- Classifying every suggestion MF or inventing a quota of issues.
- Giving the engineer an unbounded “refactor this area” action.
- Approving work the reviewer implemented or claiming unseen provider state.
- Treating a local recommendation or merge-queue acceptance as a confirmed merge.

## Calibration

**Good:** “MF-2 — On head `abc123`, `src/export.py:84` accepts an account ID without checking the
authenticated owner, contrary to AC-4. The supplied denied-user case returns success. Impact: a user
can export another account's data. Receiver: backend engineer. Pass condition: ownership is enforced
at the write boundary and current-head negative verification passes.”

**Counterexample:** “MF — The authorization code is messy; refactor it before approval.” This does
not identify a violated requirement, observed failure, bounded action, or pass condition.

## Evidence expectations

Reference the current diff or artifact, exact contract or criterion, and direct observation for
each finding. Use supplied QA or specialist evidence only when its artifact identity matches.
Separate observations from inference and unknowns using
`references/common/evidence-and-uncertainty.md`. Report provider-thread or approval state only when
actually inspected through an authorized capability.

## Escalation triggers

Escalate when artifact versions differ; criteria or contracts conflict; evidence cannot reproduce a
material concern; a Q requires product, policy, architecture, or human authority; the reviewer lacks
independence; an external action requires unavailable identity or authorization; or the workflow's
feedback limit is reached.

## Related assets

- `assets/quality/review-report-template.md` for the complete finding and verdict report.
- `assets/quality/qa-report-template.md` for required verification evidence.
- `references/common/handoff-envelope.md` for feedback and final recommendation transfer.
