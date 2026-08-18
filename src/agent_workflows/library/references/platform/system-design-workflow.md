# System design workflow

Use this reference for a material architecture decision, new or changed system boundary, or
cross-discipline contract that engineers cannot safely infer. Keep the artifact proportionate; do
not require distributed-system ceremony for a local reversible change.

## Required inputs and readiness

- Approved product behavior, acceptance criteria, non-goals, and important user journeys.
- Current repository structure, ownership, interfaces, data, deployment, and operating evidence.
- UX/UI data and state needs plus stable consumers and dependencies.
- Approved security, privacy, compliance, delivery, cost, and non-functional constraints.
- Migration, compatibility, recovery, and human decision boundaries.

Conflicting product behavior, data or interface ownership, security policy, or irreversible change
blocks a stable design. Missing non-material detail may remain a labeled assumption with impact and
owner; never invent a performance, availability, scale, or cost target.

## Staged method

### 1. Frame the problem

- Name the primary user journey and observable success criteria.
- State the one behavior that must not fail.
- Derive only applicable latency, throughput, availability, durability, privacy, compliance, cost,
  team, and delivery needs from approved user and operating outcomes.
- Identify existing code and conventions that must be preserved.

### 2. Derive non-functional requirements

| User or operating outcome | Quality attribute | Measurement boundary and evidence | Required behavior | Unknown or owner |
| --- | --- | --- | --- | --- |
| | | | | |

Turn “fast,” “reliable,” or “secure” into an observable boundary only when an authoritative input
supports it. Otherwise state the missing decision or bounded experiment.

### 3. Define boundaries

- State what is in and out of scope.
- Name external dependencies and stable contracts.
- Assign ownership for data, schemas, and interfaces.
- Identify trust boundaries, authoritative policy, and who operates each runtime component.

### 4. Draft the smallest design

- Start with a system-context Mermaid diagram.
- Identify runtime components and their responsibilities.
- Choose synchronous calls, queues, or events based on the required behavior—not fashion.
- Use `references/platform/architecture-patterns.md` only for a consequential pattern choice.

### 5. Complete contracts

For each interface, define actor and authorization; request and validation; success and stable error
semantics; ownership and source of truth; ordering, pagination, consistency, idempotency, timeout,
retry, and version compatibility when relevant; sensitive-data handling; and consumer-visible
recovery. A field list is not a complete contract.

### 6. Make consequential choices explicit

Create an ADR for a data store, API style, consistency model, service boundary, eventing strategy, or other decision that would be expensive to reverse.

### 7. Stress critical paths

For each critical path, define failure mode, detection, mitigation, recovery, and user-visible behavior. Include timeouts, retries, rate limits, migration, backfill, and rollback when relevant.

| Critical path | Failure or overload | Detection | Safe response | User-visible state | Recovery and owner | Evidence or unknown |
| --- | --- | --- | --- | --- | --- | --- |
| | | | | | | |

### 8. Plan evolution and handoff

Define compatibility window, rollout sequence, migration or backfill, observation, rollback or
forward repair, decision triggers, residual risks, and implementation acceptance criteria. Use
`references/common/handoff-envelope.md` for the reviewed architecture transfer.

## Review checklist

- One clear system boundary and explicit data ownership.
- Every material requirement and non-functional constraint traces to a design decision or open
  owner.
- Contracts cover authorization, errors, idempotency, pagination or ordering where relevant, and
  failure behavior.
- Scaling assumptions name a likely bottleneck and next step.
- Observability covers the important path with logs, metrics, traces, or an explicit reason not to add them.
- The rollout has safe migration and recovery behavior.
- Consequential choices record alternatives, rationale, reversibility, and revisit evidence.

## Normal and failure paths

On the normal path, existing boundaries are preserved where sufficient, every material journey
traces through explicit ownership and contracts, critical failures have observable recovery, and
implementation can proceed without inventing behavior.

If a path cannot define its source of truth, authorized actor, failure state, or recovery owner,
keep it open and block dependent implementation. If a non-functional need lacks a measurement
boundary, route it to the human or a bounded feasibility experiment. If the design grows beyond
evidenced constraints, return to the smallest option.

## Common mistakes

- Starting from a preferred diagram or technology before current-state inspection.
- Copying generic performance or availability targets into the design.
- Naming services without durable ownership or owned data.
- Describing only successful calls and leaving errors, retries, partial failure, and recovery to
  implementation.
- Declaring observability without a failure it must detect or an owner who acts.
- Treating an ADR as a decision log after the irreversible choice already happened.

## Calibration

**Good:** “The user may close the export page while work continues. The export module owns job
state; enqueue is idempotent by request key; progress may lag; timeout becomes a retryable state;
terminal failure preserves the request for a user retry; operations can correlate request and job
without logging export contents.”

**Counterexample:** “Use a worker and queue for scalability.” This omits the approved outcome,
ownership, contract, failure, observability, migration, and evidence.

## Evidence and escalation

Ground current-state and compatibility claims in code, documentation, operations evidence, or
approved constraints. Label inference, assumptions, decisions, and unknowns with
`references/common/evidence-and-uncertainty.md`. Escalate conflicting ownership, product policy,
security requirements, irreversible data choices, unsupported non-functional targets, unavailable
operating capability, or residual risk needing human acceptance.

## Related assets

- `assets/platform/architecture-template.md` for substantial architecture work.
- `assets/platform/architecture-decision-record-template.md` for consequential choices.
- `assets/platform/system-context-template.mmd`, `assets/platform/container-template.mmd`, and
  `assets/platform/event-flow-template.mmd` for useful boundary or flow diagrams.
- `assets/quality/design-architecture-matrix-template.md` for independent readiness review.
