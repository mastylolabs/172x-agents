# Architecture: <title>

## Summary

What this system or change does and what good looks like.

## Goals and non-goals

- Goals:
- Non-goals:

## Constraints

- Performance and reliability:
- Cost and delivery:
- Privacy, security, or compliance:
- Existing conventions:

## Requirement-to-contract traceability

| Requirement and criterion IDs | UX/UI flow and state/data need | Owning component or boundary | Interface/data/authorization contract | Failure/recovery contract | Evidence/status |
| --- | --- | --- | --- | --- | --- |
| REQ-1 / AC-1 | | | | | stable / blocked / unverified |

Preserve product IDs and source-artifact versions. Architecture may refine contracts but must not
silently redefine product or UX/UI behavior.

## System context

Use `system-context-template.mmd` when boundaries benefit from a diagram.

## Components, ownership, and contracts

| Component | Responsibility | Owns | Interfaces |
| --- | --- | --- | --- |
| | | | |

## Data and state

Sources of truth, schema ownership, migrations, retention, and consistency behavior.

## Critical flows and failure behavior

Describe normal behavior, failure behavior, retries, idempotency, recovery, and user-visible states. Use `event-flow-template.mmd` for material asynchronous flows.

## Security and privacy

Trust boundaries, authorization, sensitive data, and mitigations.

## Rollout and rollback

Deployment, compatibility, migration or backfill, monitoring, and recovery plan.

## Decisions and open questions

Link an ADR for every consequential choice.
