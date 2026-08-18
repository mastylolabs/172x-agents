# Security threat model and change-risk review: <change>

## Result

`APPROVED` | `CHANGES_REQUESTED`

- Reviewed artifact, diff, or head:
- Request and acceptance criteria:
- QA evidence version:
- Review scope and explicit exclusions:
- Verdict rationale and evidence limit:

This verdict is bounded to the reviewed artifact and evidence. It is not a security guarantee or an
external provider approval.

## Assets and data

| Asset or data | Sensitivity source | Owner | Required property | Retention or exposure concern |
| --- | --- | --- | --- | --- |
| | | | | |

## Actors, entry points, and trust boundaries

| Actor or dependency | Capability or trust level | Entry point/data flow | Boundary crossed | Evidence |
| --- | --- | --- | --- | --- |
| | | | | |

## Abuse cases and controls

### THREAT-<number>: <abuse case>

- Attacker or failure actor and preconditions:
- Asset and trust boundary:
- Abuse path:
- Existing preventive, detective, and recovery controls:
- Direct observation or reproduction:
- Exploitability and impact rationale:
- Classification: confirmed vulnerability | material risk | hardening opportunity | unknown
- Required mitigation and owner:
- Retest or pass condition:
- Residual risk:

Cover only activated authentication, authorization, validation, injection, secrets, dependency,
logging, privacy, availability, unsafe-default, and recovery paths.

## Evidence and uncertainty ledger

### Facts

- Authoritative policy, classification, contract, or requirement:

### Observations

- Code, data flow, configuration, dependency, command, or behavior directly inspected:

### Inferences

- Risk conclusion, supporting observations, and reasoning link:

### Assumptions

- Premise, impact if false, and validation owner:

### Decisions

- Review classification or mitigation disposition and rationale:

### Unknowns

- Unreviewed surface or missing evidence, consequence, and next resolver:

## Residual-risk register

| Risk | Evidence state | Impact | Accepted or proposed treatment | Authorized owner |
| --- | --- | --- | --- | --- |
| | | | | |

## Handoff envelope

- Receiver and requested action:
- Threat-model artifact and reviewed version:
- Acceptance-criteria status:
- Evidence state and coverage limits:
- Assumptions:
- Unresolved security, policy, or architecture decisions:
- Residual risks:
- External-action state:

## Calibration excerpt

**Good:** “CHANGES_REQUESTED. On head `abc123`, the import route accepts another account's record ID
without server-side ownership enforcement. The denied-user reproduction succeeds, crossing the
account trust boundary and exposing sensitive data. Receiver: backend engineer. Pass when ownership
is enforced at the write boundary and current-head negative QA passes. Other import formats were not
reviewed.”

**Bad:** “High risk: improve authorization. The scanner probably catches the rest.”
