# UX/UI specification: <title>

## Result and identity

- UX/UI artifact version or date:
- Product specification/brief version:
- Existing design-system and brand sources:
- Scope and supported conditions:
- Review and human-gate state:

## Requirement traceability

| Requirement and criterion IDs | Actor/task | Flow and step IDs | Screen/component responsibilities | Status |
| --- | --- | --- | --- | --- |
| REQ-1 / AC-1 | | FLOW-1 / STEP-1 | | stable / blocked / unverified |

## User flows

### FLOW-<number>: <actor goal>

- Entry and preconditions:
- Ordered steps and decisions with requirement IDs:
- Navigation, interruption, and preserved state:
- Success exit:
- Failure and recovery exits:
- Evidence or unresolved questions:

## Screen and component requirements

| Screen/component ID | Purpose and information hierarchy | Controls/content | Reused design-system source | New pattern justification |
| --- | --- | --- | --- | --- |
| UI-1 | | | | |

Do not invent a new brand, logo, visual language, token system, or framework component API.

## State, content, accessibility, and data contract

| REQ/AC and UI IDs | State/trigger | Visible content and action | Keyboard/focus/status behavior | Responsive behavior | Data/API/authorization need | Evidence/status |
| --- | --- | --- | --- | --- | --- | --- |
| | normal / loading / empty / validation / denied / error / retry / recovery / terminal | | | | | |

Record state transitions, preserved input, cancellation, stale/partial behavior, and not-applicable
states when material.

## Responsive and content requirements

- Existing breakpoints or conditions and authoritative source:
- Reflow, ordering, wrapping, overflow, truncation, and content-growth behavior:
- Touch, keyboard, pointer, viewport, orientation, and interrupted-state continuity:
- Labels, instructions, help, status, errors, confirmations, destructive warnings, and content owner:

## Accessibility criteria

| Criterion ID | Semantic/name/instruction need | Keyboard and focus | Error/status communication | Visual/motion/non-visual equivalent | Required evidence |
| --- | --- | --- | --- | --- | --- |
| UXA-1 | | | | | |

## Architecture reconciliation

| Requirement/state IDs | Data and ownership | Interface and authorization | Failure/retry/recovery | Architecture decision/status | Owner |
| --- | --- | --- | --- | --- | --- |
| | | | | stable / blocked / unverified | |

## Evidence and uncertainty ledger

### Facts

- Approved product, policy, brand, or design-system fact and source:

### Observations

- Existing artifact, component, or product behavior directly inspected:

### Inferences

- Design conclusion, supporting observation, and reasoning:

### Assumptions

- Premise, affected requirement/state, impact if false, validation owner:

### Decisions

- UX/UI decision, authority, rationale, and affected IDs:

### Unknowns

- Missing product/content/brand/contract/evidence, affected IDs, consequence, owner:

## Residual risks and follow-ups

| Risk or follow-up | Evidence | Affected IDs | Blocking? | Mitigation or next action | Owner |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Handoff envelope

- Receiver and requested action:
- UX/UI and source-artifact versions:
- Acceptance-criteria and traceability status:
- Evidence state and coverage limits:
- Assumptions:
- Unresolved decisions and owner:
- Residual risks:
- Human-gate and external-action state:

## Calibration excerpt

**Good:** “REQ-4 / AC-7 maps to FLOW-2 and queued, active, completed, denied, and terminal-failure
states. Existing component DS-12 supplies visual hierarchy; architecture must resolve job ownership
and status errors. Keyboard, focus restoration, status announcement, and narrow-layout behavior are
explicit.”

**Bad:** “Use a modern blue dashboard, spinner, and accessible components.”
