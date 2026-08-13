# Technology decision guide

Use this guide after confirmed constraints, not as a substitute for them.

## APIs

- **REST:** default for resource-oriented, cacheable, well-tooled interfaces.
- **GraphQL:** use when multiple clients need flexible composition and the team can govern schemas and query cost.
- **Events:** use to announce facts to independent consumers; define schemas and delivery behavior.
- **Commands over a queue:** use for owned asynchronous work with retry and backpressure needs.

## Data storage

- **Relational database:** default for transactional data, relationships, and strong integrity constraints.
- **Document storage:** fit for genuinely variable documents with simple access patterns.
- **Search index:** use for full-text or ranking; do not make it the transactional source of truth.
- **Cache:** add only with a key strategy, invalidation or TTL, stale-data tolerance, and observability.

## Reliability defaults

- Set timeouts and bound retries.
- Use idempotency for retried writes and messages.
- Use a dead-letter or explicit failure path for background work.
- Correlate logs and trace important cross-process paths.
- Measure latency, traffic, errors, and saturation when operating a service.

## Decision test

Record the problem, options, trade-offs, choice, migration or rollback, and measurable trigger for revisiting the choice.
