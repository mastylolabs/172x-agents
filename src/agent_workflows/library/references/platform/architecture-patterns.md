# Architecture patterns

Use this reference when a backend or cross-discipline design requires a consequential architecture choice. Start from the smallest pattern that satisfies the confirmed constraints; a pattern is not a goal in itself.

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

## Ports and adapters

**Use when:** long-lived business rules need to remain independent of databases, web frameworks, queues, or third-party providers.

**Benefits:** focused tests and controlled infrastructure substitution.

**Watch-outs:** use small purposeful ports. Do not abstract every framework call or create interfaces before an alternate implementation exists.

## CQRS and projections

**Use when:** write-side invariants and read-side queries have genuinely different models or scale characteristics.

**Benefits:** read models can be tailored to important user journeys.

**Guardrails:** document source of truth, projection lag, rebuild strategy, data reconciliation, and behavior while projections are stale.

## Data ownership and migrations

Every pattern needs explicit ownership for schemas, API contracts, and personal data. Prefer backward-compatible changes, staged migrations, safe defaults, observable backfills, and rollback or forward-repair plans. A service boundary without data ownership is not a boundary.

## Practical anti-patterns

- Microservices without independent ownership and operational maturity.
- Shared databases across purportedly independent services.
- Async processing without idempotency, retries, or a failure queue.
- A distributed transaction disguised as a sequence of synchronous calls.
- A clean diagram with no ownership, failure, migration, or authorization story.
