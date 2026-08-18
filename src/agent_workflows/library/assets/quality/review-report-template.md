# Review report: <artifact or change>

## Result

`APPROVED` | `CHANGES_REQUESTED` | role-specific readiness verdict

State whether this is a local recommendation or an actual external action. Identify the artifact
path, version, diff, or reviewed head. Do not approve work you implemented.

## Review scope

- Reviewing role:
- Artifact identity:
- Request and acceptance criteria:
- QA or prior evidence received:
- Paths, interfaces, or risks examined:
- Explicit coverage limits:

## Acceptance-criteria status

| Criterion | Status (`satisfied`, `not satisfied`, `unverified`, `not applicable`) | Evidence | Finding IDs |
| --- | --- | --- | --- |
| | | | |

## Findings

### <severity or lifecycle label>-<number>: <concise title>

- Status or classification:
- Affected artifact, path, interface, or behavior:
- Violated criterion, contract, or repository rule:
- Direct evidence or reproduction:
- Impact and failure mode:
- Required owner:
- Bounded corrective action or answer needed:
- Pass condition:
- Confidence and evidence limit, if useful:

Repeat only for evidence-backed findings. Do not create a quota of findings.

## Non-blocking follow-ups

- Observation, benefit, owner, and why it does not block the current criteria:

## Evidence and uncertainty ledger

### Facts

- Authoritative requirements or source-backed facts:

### Observations

- Diff, behavior, or artifact details directly inspected:

### Inferences

- Conclusion, supporting observations, and reasoning link:

### Assumptions

- Premise, impact if false, and validation owner:

### Decisions

- Review-scoped classification or disposition and rationale:

### Unknowns

- Missing evidence, consequence, and next resolver:

## Residual risks

- Risk, supporting evidence, impact, and mitigation or monitoring owner:

## Handoff envelope

- Receiver and requested action:
- Artifact and version:
- Acceptance-criteria status:
- Evidence state and coverage limits:
- Assumptions:
- Unresolved decisions and owner:
- Residual risks:
- External-action state:

## Calibration excerpt

**Good:** “MF-1: The current update accepts an unowned account ID at `src/accounts.py:84`, contrary
to AC-4. Reproduction: the supplied denied-user case returns success on head `abc123`. Impact: one
user can modify another user's record. Receiver: `backend-engineer`. Pass condition: ownership is
enforced at the write boundary and the regression case passes. Verdict: CHANGES_REQUESTED.”

**Bad:** “The authorization code feels unsafe; consider refactoring it.”
