# Testing strategy

Use this reference when independent QA must select evidence for changed behavior, a material risk,
or a workflow gate. Apply it proportionately: a documentation-only change and an authorization or
migration change need different evidence, but both need explicit criterion coverage.

## Required inputs

- The authoritative request and observable acceptance criteria.
- A uniquely identified implementation artifact, diff, revision, or change-request head.
- The implementation handoff, stable contracts, changed paths, and known risk areas.
- Repository instructions, existing test capabilities, required gate commands, and environment.
- Prior failures, relevant incidents, and explicit coverage constraints when supplied.

Conflicting expected behavior, an unidentified artifact, or inability to inspect the change blocks a
conclusive verdict. Missing non-material environment detail may be recorded while tests proceed; a
missing material check remains a coverage limit and cannot support PASS.

## Staged method

1. **Confirm the test object.** Record artifact identity, environment, applicable criteria, and
   whether the handoff evidence targets the same state.
2. **Map risks and criteria.** Identify changed user journeys, interfaces, authorization, data,
   asynchronous behavior, migrations, dependencies, failure recovery, and likely regression paths.
3. **Select discriminating evidence.** Choose the smallest check that can falsify each material
   claim, then add integration or boundary checks where focused checks cannot observe behavior.
4. **Inspect independently.** Read the relevant diff and contracts; do not treat the implementer's
   command report as independent execution.
5. **Run focused checks.** Exercise representative success, validation, denied, empty, failure,
   retry or recovery, compatibility, and regression paths activated by the change.
6. **Run required gates.** Use the repository's existing environment and every applicable selected
   gate. Do not install, remove, upgrade, or select tools merely to make a gate appear available.
7. **Resolve unstable results.** Preserve the first observation, investigate environment and state,
   and repeat only enough to characterize a suspected flake. Do not rerun until a failure disappears.
8. **Assign criterion status.** Mark each criterion satisfied, not satisfied, unverified, or not
   applicable with evidence and limits, then derive PASS or FAIL from the material statuses.
9. **Package the handoff.** Use the QA asset for commands, observations, reproductions, assumptions,
   unknowns, residual risks, receiver, and artifact state.

## Evidence selection rules

| Risk or claim | Prefer | Add when activated | Do not substitute |
| --- | --- | --- | --- |
| Pure function or local rule | Focused deterministic check with boundary and invalid inputs | Property or regression cases when the defect class warrants them | Code inspection alone |
| Public interface or consumer contract | Contract or integration check at both sides of the boundary | Compatibility case for existing consumers and error semantics | Producer-only unit test |
| Authorization or data isolation | Allowed and denied cases using representative identities and ownership | Cross-tenant, default-deny, logging, and error-disclosure paths | A happy-path authenticated request |
| Persistent data or migration | Representative forward migration and invariant check | Backfill, mixed-version, rollback or forward-repair, and failure recovery | Model-level unit tests |
| Asynchronous work | Enqueue, duplicate, retry, ordering, timeout, and terminal failure behavior | Replay, idempotency, recovery, and user-visible progress | One successful worker invocation |
| User interface behavior | User-visible state and interaction at the relevant rendered boundary | Keyboard, focus, responsive, assistive, browser, and API-failure paths required by the contract | Static markup or a screenshot alone |
| Performance or reliability | The approved measurement boundary, workload, environment, and threshold | Baseline and variance evidence when supplied requirements make them material | Invented industry targets |
| Repository integrity | Focused checks followed by every required gate | Build/package/install verification for changed distribution behavior | “Tests are green” without commands |

## Criterion matrix

| Criterion | Risk | Check or inspection | Environment and artifact | Status | Coverage limit |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

`Not applicable` needs an authoritative reason. A low-risk criterion still needs a direct inspection
or check; risk affects evidence depth, not whether evidence is required.

## Normal and failure paths

On the normal path, focused evidence establishes material behavior, required gates pass on the same
artifact, every criterion has a supported status, and residual risk is explicit.

On a defect path, return FAIL with the smallest reproduction, expected versus observed behavior,
affected criterion, artifact and environment, responsible engineer, and pass condition. On an
environment path, report attempted commands and exact blockers; FAIL remains the safe verdict when
material behavior is unverified. If the artifact changes, rerun every affected check. If a failure
is intermittent, report all observations and the conditions investigated rather than selecting the
passing run.

## Common mistakes

- Reusing implementation test output as independent QA evidence.
- Testing only the happy path or only the changed function when the contract crosses a boundary.
- Treating test count, coverage percentage, or screenshot volume as proof of behavior.
- Marking an unrun material path not applicable without an authoritative reason.
- Ignoring environment, fixture, locale, time, ordering, or external-dependency conditions.
- Retrying until green and discarding the initial failure.
- Claiming a scanner, browser, provider gate, or external system was exercised when it was not.
- Implementing the fix and then presenting the same role's rerun as independent verification.

## Calibration

**Good:** “AC-4 requires an owner-only write. On head `abc123`, the owner case succeeded and the
cross-owner case returned the contracted 403. The repository gate passed. The production identity
provider was not exercised, so that integration is a residual coverage limit rather than proof of
production behavior.”

**Counterexample:** “All 214 tests passed, so authorization and production integration are
correct.” Test quantity does not identify the exercised policy, artifact, environment, or missing
boundary.

## Evidence expectations

Record exact commands, environment, artifact identity, observed output, and relevant inspection
locations. Tie each verdict to the criterion matrix. Separate facts, observations, inferences,
assumptions, decisions, and unknowns with
`references/common/evidence-and-uncertainty.md`. Confidence and test presence are not evidence.

## Escalation triggers

Escalate when expected behavior conflicts; the artifact cannot be identified or changed during
verification; a required environment or gate is unavailable; a material criterion cannot be
observed safely; a flaky result cannot be characterized; a product or contract decision is needed;
or the requested evidence would require credentials or an external mutation outside authority.

## Related assets

- `assets/quality/qa-report-template.md` for the complete PASS or FAIL report.
- `assets/quality/review-report-template.md` when verification evidence becomes a review input.
- `references/common/handoff-envelope.md` for receiver and artifact state.
