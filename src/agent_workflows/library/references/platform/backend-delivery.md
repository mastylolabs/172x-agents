# Backend delivery

Use this reference for backend implementation or specialist review when a change affects an
interface, authorization, persistent data, migration, asynchronous work, external dependency,
reliability behavior, or operational evidence. For a local pure-function change, activate only the
relevant checks.

## Required inputs

- Approved behavior and acceptance criteria.
- Stable architecture, interface, error, data-ownership, and authorization contracts.
- Current repository state, conventions, supported environments, and verification commands.
- Migration, compatibility, recovery, reliability, privacy, and security constraints when relevant.
- The current implementation artifact and QA evidence for review work.

Conflicting ownership or interface sources, undefined security-sensitive policy, an unidentified
artifact, or a missing irreversible-data decision blocks affected implementation or approval.
Repository conventions may guide a reversible internal detail only as a labeled assumption.

## Staged method

1. **Map the contract.** Identify actor, trigger, inputs, success output, error taxonomy,
   authorization, idempotency, ordering, compatibility, and consuming interfaces.
2. **Assign ownership.** Name the source of truth, invariant owner, transaction boundary, personal
   or sensitive data, retention, and permitted access paths.
3. **Design normal and denied paths.** Validate at the owning boundary, enforce authorization rather
   than relying on a client, keep error disclosure intentional, and define duplicate behavior.
4. **Plan data change.** Prefer backward-compatible schema and interface evolution. Define staged
   migration, mixed-version behavior, backfill observation, rollback or forward repair, and failure
   recovery when persistent state changes.
5. **Bound asynchronous and external work.** Define timeout, retry conditions, idempotency,
   ordering, cancellation, terminal failure, reconciliation, and user-visible state. Do not hide a
   workflow in an unobservable chain of calls.
6. **Make operations observable.** Record what detects an important failure, how related work is
   correlated, which data must not be logged, and who owns remediation. Use only requirements and
   repository-supported capabilities.
7. **Implement or review the smallest coherent path.** Cover activated success and failure behavior
   without changing shared contracts unilaterally.
8. **Verify and hand off.** Map criteria to focused and integration checks, report unrun boundaries,
   and transfer contract, data, recovery, evidence, and residual-risk state.

## Conditional selection rules

| Concern | Activate when | Required decision or evidence |
| --- | --- | --- |
| Interface errors | A caller can observe failure or retry behavior | Stable error categories, status or result semantics, retryability, and information disclosure |
| Authorization | Behavior reads, writes, lists, exports, or administers owned or sensitive data | Policy source, enforcement boundary, allowed and denied cases, and safe default |
| Idempotency | A write or message may be retried or duplicated | Key scope, duplicate result, storage duration when relevant, and concurrent behavior |
| Transactions and invariants | Multiple writes must remain consistent | Atomic boundary, partial-failure behavior, reconciliation, and source of truth |
| Migration or backfill | Schema, stored meaning, or required data changes | Compatibility window, progress observation, recovery, validation, and owner |
| Asynchronous work | Completion is deferred, retried, reordered, or rate limited | Ownership, state model, timeout, retry, terminal failure, cancellation, and replay policy |
| External dependency | Correctness depends on another service or provider | Timeout, unavailable or malformed response, rate limit, fallback, data exposure, and contract version |
| Observability | Failure would be hard to detect or diagnose | Correlation, safe logs, metric or trace evidence where supported, alert or investigation owner |

Do not invent latency, throughput, availability, retention, or coverage targets. If a requirement
needs one, record its measurement boundary and approved source.

## Normal and failure paths

On the normal path, the owning boundary validates input and authority, invariants hold, interfaces
return documented results, state changes are observable, and consumers can integrate without
guessing.

For each failure, state whether it is rejected, retried, compensated, reconciled, or surfaced; who
owns recovery; what the caller sees; and what evidence detects it. A retry must be bounded and safe.
A partial migration or dependency outage is a first-class state, not an exceptional footnote. If
the contract cannot define a safe outcome, stop for architecture, product, or human direction.

## Common mistakes

- Trusting client-side authorization or accepting an identifier without verifying ownership.
- Returning one generic error when callers need stable retry or recovery behavior.
- Adding retries without timeouts, idempotency, termination, or observability.
- Treating database schema as shared ownership across purported boundaries.
- Shipping a migration without mixed-version behavior, representative validation, or recovery.
- Logging credentials, tokens, full sensitive payloads, or errors that disclose protected state.
- Claiming reliability from a unit test that never crosses the relevant boundary.
- Choosing a queue, cache, store, framework, or service because it is familiar rather than required.

## Calibration

**Good:** “The write contract requires an owner-only operation and permits client retry. Enforce
ownership at the service boundary, use the supplied idempotency key for the operation scope, return
the existing denied error, and verify owner, cross-owner, duplicate, and concurrent cases. The
migration is additive and reversible before old readers are removed.”

**Counterexample:** “The UI hides the button, so the endpoint is authorized. Add three retries and
log the full request if the provider fails.” This moves policy to the client, creates duplicate risk,
and exposes data without evidence.

## Evidence expectations

Trace material claims to current contracts, producing and consuming code, schema or migration
artifacts, and executed checks. Record the exact artifact and environment. Distinguish direct
observation, inference, assumption, decision, and unknown using
`references/common/evidence-and-uncertainty.md`. A design claim is not implementation evidence; an
implementation check is not independent QA or review.

## Escalation triggers

Escalate when data or contract ownership conflicts; authorization policy is absent; compatibility
would break a stable consumer; a migration has no safe recovery; retries cannot be idempotent;
privacy or security impact is unresolved; a required dependency or environment cannot be observed;
or a requested change requires unapproved infrastructure, cost, or external authority.

## Related assets

- `assets/platform/architecture-template.md` for stable system and contract decisions.
- `assets/quality/qa-report-template.md` for backend verification.
- `assets/quality/review-report-template.md` for specialist findings.
- `references/quality/testing-strategy.md` for risk-based evidence selection.
- `references/quality/review-findings.md` for actionable finding lifecycle.
