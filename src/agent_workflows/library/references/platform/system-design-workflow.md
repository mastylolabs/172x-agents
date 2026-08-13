# System design workflow

Use this reference for a material architecture decision. Keep it proportionate to the change.

## 1. Frame the problem

- Name the primary user journey and observable success criteria.
- State the one behavior that must not fail.
- Confirm latency, throughput, availability, cost, privacy, compliance, team, and delivery constraints.
- Identify existing code and conventions that must be preserved.

## 2. Define boundaries

- State what is in and out of scope.
- Name external dependencies and stable contracts.
- Assign ownership for data, schemas, and interfaces.

## 3. Draft the smallest design

- Start with a system-context Mermaid diagram.
- Identify runtime components and their responsibilities.
- Choose synchronous calls, queues, or events based on the required behavior—not fashion.

## 4. Make consequential choices explicit

Create an ADR for a data store, API style, consistency model, service boundary, eventing strategy, or other decision that would be expensive to reverse.

## 5. Stress critical paths

For each critical path, define failure mode, detection, mitigation, recovery, and user-visible behavior. Include timeouts, retries, rate limits, migration, backfill, and rollback when relevant.

## Review checklist

- One clear system boundary and explicit data ownership.
- Contracts cover authorization, idempotency, pagination or ordering where relevant, and failure behavior.
- Scaling assumptions name a likely bottleneck and next step.
- Observability covers the important path with logs, metrics, traces, or an explicit reason not to add them.
- The rollout has safe migration and recovery behavior.
