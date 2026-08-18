# QA evidence report: <artifact or change>

## Result

`PASS` | `FAIL`

State the artifact path, version, revision, or reviewed head. PASS requires evidence for every
applicable material acceptance criterion. An unrun material check is `unverified`, not PASS.

## Environment and scope

- Artifact identity:
- Environment and relevant versions:
- Requested scope:
- Explicit exclusions or coverage limits:

## Acceptance-criteria evidence

| Criterion | Status (`satisfied`, `not satisfied`, `unverified`, `not applicable`) | Evidence or observation | Coverage limit |
| --- | --- | --- | --- |
| | | | |

## Commands and direct observations

| Command or inspection | Observed result | Artifact or location |
| --- | --- | --- |
| | | |

## Evidence and uncertainty ledger

### Facts

- Authoritative requirements or source-backed facts:

### Observations

- Behavior directly exercised or artifacts directly inspected:

### Inferences

- Conclusion, supporting observations, and reasoning link:

### Assumptions

- Premise, impact if false, and validation owner:

### Decisions

- QA-scoped test or coverage decisions and rationale:

### Unknowns

- Missing evidence, consequence, and next resolver:

## Failures and bounded fix requests

| Failed criterion | Reproduction | Expected vs. observed | Receiving engineer | Pass condition |
| --- | --- | --- | --- | --- |
| | | | | |

## Residual risks

- Risk, evidence, impact, and mitigation or monitoring owner:

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

**Good:** “AC-2 — `not satisfied`. On head `abc123`, `uv run pytest
tests/test_access.py::test_denied -q` failed: a denied user received status 200 instead of the
specified 403. Receiver: `backend-engineer`. Pass condition: the denied path returns the contracted
error and the focused regression check passes.”

**Bad:** “Authorization seems broken. Please fix and rerun everything.”
