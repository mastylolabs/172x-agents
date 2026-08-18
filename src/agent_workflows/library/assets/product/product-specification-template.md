# Product specification: <title>

## Result and identity

- Specification version or date:
- Approved outcome:
- Validation decision artifact:
- Intended receivers:
- Human-gate state:

## Validated source ledger

| Source and version/location | Authority and approval state | Supported requirements | Conflicts or limits |
| --- | --- | --- | --- |
| | | | |

## Context, actors, and goals

- Problem and target actors:
- Triggering context:
- Observable goals:

## Scope and non-goals

### In scope

-

### Non-goals

-

## Requirements

| Requirement ID | Actor and condition | Observable behavior and outcome | Priority source | Source trace | Status |
| --- | --- | --- | --- | --- | --- |
| REQ-1 | | | | | stable / blocked / unverified |

Preserve IDs across revisions. Do not silently reuse an ID for different behavior.

## User-visible behavior and states

| Requirement ID | Normal | Empty/loading | Validation/denied | Failure/retry/recovery | Content/data needs |
| --- | --- | --- | --- | --- | --- |
| REQ-1 | | | | | |

Include only reachable material states; record not applicable deliberately.

## Acceptance criteria

### AC-<number>: <observable result>

- Linked requirement IDs:
- Given actor/context/state:
- When event/action occurs:
- Then observable outcome:
- Acceptable evidence boundary:
- Status: satisfied / not satisfied / unverified / blocked

## Cross-discipline traceability

| Requirement and criterion IDs | UX flow/state and content need | Data/ownership/interface need | Architecture contract owner | QA evidence status |
| --- | --- | --- | --- | --- |
| REQ-1 / AC-1 | pending UX/UI definition | | pending architecture | unverified |

Downstream artifacts refine their own decisions but must not silently change product behavior.

## Evidence and uncertainty ledger

### Facts

- Validated product, policy, or source-backed fact:

### Observations

- Existing product or repository behavior directly inspected:

### Inferences

- Supported conclusion and reasoning link:

### Assumptions

- Premise, affected IDs, impact if false, validation owner:

### Decisions

- Decision, authorized owner, artifact/date, affected IDs:

### Unknowns

- Missing evidence or decision, affected IDs, consequence, next owner:

## Residual risks and open questions

| Risk or question | Affected IDs | Evidence state | Blocking? | Owner and next action |
| --- | --- | --- | --- | --- |
| | | | | |

## Handoff envelope

- Receiver and requested action:
- Specification and source-artifact versions:
- Acceptance-criteria status:
- Evidence state and coverage limits:
- Assumptions:
- Unresolved decisions and owner:
- Residual risks:
- Human-gate and external-action state:

Use the same identified specification and envelope for `ux-ui-designer` and
`principal-architect`.

## Calibration excerpt

**Good:** “REQ-4 and AC-7 trace to approved DEC-2. UX owns progress/recovery states; architecture
owns job identity, authorization, and status-error contracts. Neither downstream artifact may
change the requirement silently.”

**Bad:** “Use a queue and a polished progress component so export feels fast.”
