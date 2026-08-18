# Architecture patterns

Use this reference when a backend or cross-discipline design requires a consequential architecture choice. Start from the smallest pattern that satisfies the confirmed constraints; a pattern is not a goal in itself.

## Decision readiness

Require approved user journeys, existing system and ownership evidence, material non-functional
constraints, delivery and operating capability, stable consumers, and known migration or recovery
limits. If ownership, security policy, or a material product outcome conflicts, preserve the
conflict and stop the affected pattern decision. Do not use scale, reliability, or team assumptions
as facts without an identified source and measurement boundary.

## Selection order

1. Confirm user journeys, data sensitivity, expected load, reliability needs, team ownership, delivery window, and existing conventions.
2. Prefer a modular monolith and explicit module boundaries when a single team can ship the product.
3. Add asynchronous boundaries only for a proven long-running, integration, load-smoothing, or reliability need.
4. Split a service only when ownership, independent deployment, or scaling needs are durable and operationally supported.
5. Record the choice, alternatives, migration path, and measurable trigger for revisiting it.

## Modular monolith

**Use when:** one team owns related behavior, the domain is still evolving, and fast local development matters.

**Benefits:** one deployment path, simple debugging, transactions where appropriate, shared types, and low operational overhead.

**Guardrails:** define module ownership, keep internal APIs explicit, prevent direct cross-module data access, and avoid a global utility layer that erases boundaries.

## Layered application

**Use when:** the application is small to medium and its request, application, domain, and infrastructure concerns are stable and easy to separate.

**Benefits:** familiar navigation, clear dependency direction, and a straightforward place for cross-cutting concerns.

**Guardrails:** do not force every feature through a generic service layer. Keep domain logic out of controllers and persistence details out of business rules.

## Vertical slices

**Use when:** product work is organized around user capabilities rather than technical layers.

**Benefits:** each slice can own its route, application logic, data access, tests, and acceptance criteria; changes stay easier to review.

**Guardrails:** share only stable contracts and platform capabilities. Do not create a second monolith inside a shared services folder.

## Service boundaries

**Use when:** a bounded context has durable ownership, needs independent deployment or scaling, and the team can operate versioned contracts, tracing, alerts, retries, and partial failures.

**Benefits:** independent evolution and clearer ownership when those conditions are real.

**Watch-outs:** network failure, operational cost, distributed debugging, compatibility commitments, and data consistency become product concerns.

**Do not use because:** microservices appear more advanced, teams want different languages, or a single slow component exists without a real isolation need.

## Event-driven and asynchronous processing

**Use when:** work is long-running, external integrations are unreliable, producers and consumers need decoupling, or burst load must be smoothed.

**Benefits:** resilience, independent consumers, and an auditable sequence of work.

**Guardrails:** define message ownership, idempotency keys, ordering requirements, retry and dead-letter behavior, replay/backfill policy, observability, and user-visible eventual-consistency states.

## Pub/sub

**Use when:** one business event must inform multiple independent consumers, such as notifications, analytics, search indexing, or downstream integrations.

**Benefits:** producers remain unaware of consumers and new consumers can subscribe without changing the producer.

**Guardrails:** name events as past facts, establish ownership and schema evolution rules, and assume at-least-once delivery unless the platform proves otherwise. Do not use pub/sub for a command that needs one accountable handler.

## Queue-based background work

**Use when:** one owner must process a task asynchronously, retry it safely, or smooth burst load.

**Benefits:** explicit work ownership, bounded concurrency, and controllable retry behavior.

**Guardrails:** distinguish commands from events, define idempotency and visibility timeout behavior, provide a failure queue, and keep user-visible status accurate.

## Ports and adapters

**Use when:** long-lived business rules need to remain independent of databases, web frameworks, queues, or third-party providers.

**Benefits:** focused tests and controlled infrastructure substitution.

**Watch-outs:** use small purposeful ports. Do not abstract every framework call or create interfaces before an alternate implementation exists.

## CQRS and projections

**Use when:** write-side invariants and read-side queries have genuinely different models or scale characteristics.

**Benefits:** read models can be tailored to important user journeys.

**Guardrails:** document source of truth, projection lag, rebuild strategy, data reconciliation, and behavior while projections are stale.

## Event sourcing

**Use when:** the immutable history of domain decisions is itself essential and the team can operate event versioning, projections, replay, and reconciliation.

**Benefits:** rich auditability and reconstructable state for suitable domains.

**Watch-outs:** it is not a generic logging mechanism. Projection correctness, privacy deletion, schema evolution, and operational recovery become first-class concerns.

## Serverless and managed functions

**Use when:** workload is intermittent, event-triggered, operational simplicity matters, and execution constraints fit the request.

**Benefits:** low infrastructure management and natural scaling for bounded stateless work.

**Watch-outs:** cold starts, duration limits, local development, vendor coupling, and distributed observability. Keep durable state and workflows explicit rather than hidden in chained functions.

## Data ownership and migrations

Every pattern needs explicit ownership for schemas, API contracts, and personal data. Prefer backward-compatible changes, staged migrations, safe defaults, observable backfills, and rollback or forward-repair plans. A service boundary without data ownership is not a boundary.

## Pattern decision completeness

For a selected pattern, record the activated constraint, current evidence, rejected simpler option,
ownership, interfaces, data and consistency, authorization, critical failure path, operability,
migration and recovery, residual risks, and a measurable evidence-based revisit trigger. A pattern
name or diagram without these decisions is not an architecture.

Stress each critical path with: initiating actor; owned data; dependencies; timeout and partial
failure; retry or idempotency; detection; user-visible state; recovery owner; and evidence or
unknown. Use `references/platform/system-design-workflow.md` for the full method.

## Practical anti-patterns

- Microservices without independent ownership and operational maturity.
- Shared databases across purportedly independent services.
- Async processing without idempotency, retries, or a failure queue.
- Pub/sub used as an untraceable replacement for a direct command.
- Event sourcing adopted solely to appear sophisticated.
- A distributed transaction disguised as a sequence of synchronous calls.
- A clean diagram with no ownership, failure, migration, or authorization story.

## Failure and escalation

If the selected pattern cannot describe safe failure, recovery, migration, ownership, and
authorization within confirmed constraints, return to the smallest viable option or mark the
decision unresolved. Escalate when product behavior, data ownership, risk tolerance, cost,
operating capacity, or an irreversible migration needs human or contract-owner authority.

## Calibration

**Good:** “One team owns the evolving domain, current load fits the existing deployment, and no
independent scaling or release need is evidenced. Keep explicit modules in the monolith; add a queue
only for the approved long-running export, with idempotency, terminal failure, and progress state.”

**Counterexample:** “Use microservices and event sourcing because future scale may be large.” The
proposal has no durable ownership, workload, recovery, or operating evidence.

## Evidence expectations

Tie the pattern and each exception to current repository, contract, operational, or approved
constraint evidence. Label proposed choices, assumptions, and unknowns with
`references/common/evidence-and-uncertainty.md`. Do not claim production properties from a diagram
or an unrun experiment.

## Related assets

- `assets/platform/architecture-template.md` for the complete architecture.
- `assets/platform/architecture-decision-record-template.md` for consequential pattern choice.
- `assets/platform/system-context-template.mmd` and `assets/platform/event-flow-template.mmd` when a
  diagram materially clarifies boundaries or asynchronous failure.
