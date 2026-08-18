# Technology decision guide

Use this guide only after confirmed constraints show that a technology choice is consequential.
Prefer the repository's supported choice when it satisfies the need. Do not create a comparison for
a reversible local detail.

## Required inputs

- The problem and approved user or operating outcome.
- Current repository technologies, team ownership, deployment, and support evidence.
- Required interfaces, data properties, security/privacy, compatibility, migration, and recovery.
- Approved non-functional measurement boundaries and cost or delivery constraints when applicable.
- Candidate support/version evidence and the authorized decision owner.

If the desired outcome, owner, target environment, or irreversible constraint is unknown, keep the
choice open or use a bounded feasibility experiment. Familiarity and popularity are not evidence.

## Staged decision method

1. State the decision, owner, deadline when supplied, and consequence of deferral.
2. Record constraints and the simplest existing option.
3. Compare only viable candidates on the same activated dimensions.
4. Validate the highest-risk unknown with official documentation or a bounded target-environment
   experiment; use `references/platform/feasibility-experiments.md` when appropriate.
5. Select or defer, then record rationale, rejected alternatives, migration, recovery, residual
   risks, and evidence-based revisit trigger.

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

These are checks, not universal mandates. Apply them only to an activated service or dependency and
derive targets from approved requirements.

## Comparison dimensions

| Dimension | Question | Evidence |
| --- | --- | --- |
| Functional fit | Does it meet the required contract without hidden product compromise? | Target-version behavior or authoritative documentation |
| Compatibility | Can current consumers, data, and environments migrate safely? | Current code, representative experiment, and migration plan |
| Security/privacy | What data and trust boundaries change, and who owns controls? | Policy, threat model, dependency and configuration evidence |
| Reliability/operations | How do timeout, failure, recovery, observation, and support work? | Supported runtime and operating capability |
| Reversibility | What is locked in, and how can the choice be replaced or rolled back? | Interface boundary, data format, exit and recovery plan |
| Delivery/cost | What approved constraint materially differs between options? | Supplied team, schedule, or cost evidence; no invented estimates |

## Decision completeness

Record the problem, options, trade-offs, choice, migration or rollback, and measurable trigger for revisiting the choice.

Also record applicable versions, evidence sources or retrieval dates, data and interface ownership,
failure behavior, security consequences, operating owner, assumptions, unknowns, and residual risk.
Use `assets/platform/architecture-decision-record-template.md`; do not reproduce vendor
documentation.

## Normal and failure paths

On the normal path, the existing option is assessed first, candidates share one constraint set, a
material unknown is tested, and the chosen option has an owned migration and recovery path.

If evidence is stale, candidates require different product outcomes, a safe exit is absent, or the
team cannot operate the choice, return UNKNOWN or choose the simpler supported option where
authority permits. Do not conceal uncertainty inside optimistic implementation assumptions.

## Common mistakes

- Comparing feature lists without a decision or shared dimensions.
- Selecting a provider or framework from popularity, novelty, or invented future scale.
- Ignoring version, license, support, migration, data exit, or operational ownership.
- Treating a small prototype as proof of production reliability, security, or cost.
- Creating a generic abstraction solely to keep every candidate possible.

## Calibration

**Good:** “The current relational store meets transactional ownership and query needs. Search is a
separate indexed projection only because the approved ranking journey needs it; the relational data
remains source of truth, projection lag is visible, and rebuild and rollback are defined.”

**Counterexample:** “Adopt a document database because the schema may change someday.” No current
constraint, ownership, migration, or recovery evidence supports the choice.

## Evidence and escalation

Tie fit and trade-off claims to current repository evidence, applicable official documentation, or
target-version experiments. Record retrieval date when external support state is material. Escalate
unresolved product trade-offs, vendor spend, license or privacy risk, irreversible data migration,
unsupported runtime needs, or a decision that exceeds architecture authority.

## Related assets

- `assets/platform/architecture-decision-record-template.md` for the decision.
- `assets/platform/feasibility-assessment-template.md` for unresolved candidate viability.
- `references/platform/architecture-patterns.md` when the choice changes system structure.
