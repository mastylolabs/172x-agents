# Design-to-architecture contract matrix: <change or product>

## Result

`READY` | `REVISE` | `BLOCKED`

- Matrix artifact and version:
- Build brief/specification version:
- UX/UI artifact version:
- Architecture artifact version:
- Review scope:
- Verdict rationale:

READY is an independent readiness recommendation. It is not human build approval.

## Flow-to-contract matrix

| Requirement/criterion IDs and user step | UX/UI behavior and states | Content/accessibility | Data and ownership | Interface and authorization | Failure/recovery | Evidence and status | Owner or decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | |

Use `satisfied`, `not satisfied`, `unverified`, or `not applicable` for each material row. Add rows
for normal, denied, empty, loading, failure, retry, partial, migration, or asynchronous behavior only
when the approved flow activates them.

## Gap register

### GAP-<number>: <concise conflict or omission>

- Classification: `REVISE` | `BLOCKED` | non-blocking
- Conflicting or missing artifacts and exact locations:
- Affected criterion or user step:
- Direct evidence:
- Delivery impact:
- Receiving agent or human:
- Required correction or decision:
- Pass condition:
- Evidence limit:

## Evidence and uncertainty ledger

### Facts

- Authoritative brief, specification, policy, or source-backed facts:

### Observations

- Artifact details directly inspected:

### Inferences

- Compatibility conclusion, supporting observations, and reasoning link:

### Assumptions

- Premise, impact if false, and validation owner:

### Decisions

- Review classifications or dispositions and rationale:

### Unknowns

- Missing evidence, consequence, and next resolver:

## Residual risks and follow-ups

| Risk or follow-up | Evidence | Blocking? | Mitigation or next action | Owner |
| --- | --- | --- | --- | --- |
| | | | | |

## Handoff envelope

- Receiver and requested action:
- Matrix and source-artifact versions:
- Acceptance-criteria status:
- Evidence state and coverage limits:
- Assumptions:
- Unresolved decisions and owner:
- Residual risks:
- Human-gate and external-action state:

## Calibration excerpt

**Good:** “REVISE. At export step 3, UX requires resumable progress, while architecture section 4
defines one synchronous response and no progress state. AC-5 is not satisfied. Receivers:
`ux-ui-designer` and `principal-architect`; pass when both artifacts define one compatible progress,
timeout, and recovery contract. No human build approval occurred.”

**Bad:** “Design and architecture feel misaligned. Use a queue and try again.”
