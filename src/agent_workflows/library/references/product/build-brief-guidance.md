# Build brief guidance

Use this reference when one request, idea, repository, or set of named sources must become an
authoritative brief for design, architecture, implementation, QA, or a focused development loop.
Apply it proportionately: a small coding request needs a focused contract, while conflicting
multi-discipline sources need a fuller brief.

## Required inputs and readiness

- User request, intended outcome, and explicitly named source material.
- Repository instructions and current product or code context when supplied.
- Known users or actors, constraints, non-goals, risks, and required human gates.
- Existing requirements, decisions, policies, and acceptance evidence.
- The downstream use of the brief and the artifact versions being summarized.

Every named source must be readable or explicitly marked unavailable. A material conflict in
product behavior, policy, scope, compliance, cost, or risk blocks the affected criterion until an
authorized human resolves it. Missing non-material detail may proceed only as a labeled assumption
with impact and validation owner.

## Source authority and conflict rules

| Evidence type | How to use it | What it cannot establish alone |
| --- | --- | --- |
| Current explicit user direction | Treat as controlling within repository and policy boundaries | Facts about uninspected systems or external approval |
| Approved decision or specification | Preserve the identified version and decision scope | A later unstated change |
| Named source material | Extract exact supported facts and constraints | Precedence over a conflicting source without authority |
| Repository observation | Describe current behavior, interfaces, and conventions | Product intent or stakeholder approval |
| Supported inference | Link observations to a provisional conclusion | A requirement or fact without validation |
| Assumption | Expose a necessary premise, impact if false, and owner | Permission to cross a material gate |

When sources conflict, quote or precisely locate each position, describe the affected behavior and
downstream consequence, preserve compatible facts, and ask for the smallest decision. Never blend
incompatible claims into vague wording.

## Staged method

1. **Fix scope and artifact identity.** Record the requested outcome, brief type, named sources,
   repository state, intended receivers, and version or date.
2. **Build a source ledger.** For every material source, record authority, relevant locations,
   facts, constraints, decisions, conflicts, and unread or stale portions.
3. **Frame intent and users.** State the problem or requested change, actors, triggering context,
   desired observable outcome, and explicitly excluded outcomes without inventing research.
4. **Define scope boundaries.** Separate in scope, necessary enabling work, and non-goals. Preserve
   supplied constraints for product, compatibility, privacy, security, cost, delivery, and human
   authority.
5. **Map cross-discipline behavior.** Identify user flows and states, content and accessibility
   needs, data and interface responsibilities, authorization, failure/recovery, and evidence needs
   only where the requested outcome activates them.
6. **Write observable criteria.** Give each material criterion a stable ID and specify actor,
   condition, behavior, outcome, and acceptable evidence. Do not invent numeric targets.
7. **Classify uncertainty.** Separate facts, observations, inference, assumptions, decisions, and
   unknowns using `references/common/evidence-and-uncertainty.md`. Assign every material unknown an
   owner and consequence.
8. **Check downstream readiness.** Confirm receivers can act without redefining intent. Complete
   `assets/product/build-brief-template.md` and `references/common/handoff-envelope.md`.

## Brief selection rules

| Situation | Brief depth | Required emphasis |
| --- | --- | --- |
| Bounded implementation request | Focused | Current behavior, exact change, non-goals, criteria, repository gate, risks |
| New product or multi-discipline feature | Full | Users, flows, cross-discipline needs, decisions, traceability, human gates |
| Conflicting named sources | Partial pending decision | Conflict register, compatible scope, blocked criteria, smallest human decision |
| Existing behavior is the main evidence | Evidence-led | Current observations separated from intended product behavior |
| Irreversible or security-sensitive outcome | Decision-gated | Authority, recovery, data/authorization policy, residual risk owner |

Detail is earned by decision or delivery risk. Do not turn the brief into screen design, system
architecture, implementation tasks, or a general repository summary.

## Normal and failure paths

On the normal path, every supplied source is accounted for, scope and non-goals are explicit,
criteria trace to authority, uncertainty is visible, and all receivers get the same identified
brief.

If a source is unreadable, record the coverage limit and do not claim it was consulted. If sources
conflict materially, stop only the affected criteria and route a decision. If downstream roles
discover a gap, revise only the evidenced gap, issue a new artifact version, and invalidate stale
dependent evidence. If the requested output becomes design, architecture, or implementation, hand
off rather than absorbing that authority.

## Common mistakes

- Summarizing only the user's latest sentence while ignoring named sources.
- Treating current code or tests as unquestionable product intent.
- Hiding a conflict as a broad assumption such as “use sensible defaults.”
- Writing “fast,” “secure,” or “intuitive” without an observable outcome or supplied boundary.
- Including implementation choices that downstream architecture should decide.
- Omitting non-goals, failure states, human gates, or the evidence needed for acceptance.
- Revising the brief after review without changing its identity or notifying affected receivers.

## Calibration

**Good:** “AC-3 — Given an authenticated account owner with an export containing no records, when
they request export, the product produces the approved empty export and identifies completion. User
direction establishes ownership; `product-notes.md` section 4 establishes the empty outcome.
Whether work continues after navigation is unresolved and blocks only progress-state design.”

**Counterexample:** “Build a scalable export experience with a modern UI and suitable backend.” It
has no bounded actor, behavior, evidence, non-goal, or authority and pushes invention downstream.

## Evidence expectations

Name every source consulted and its artifact version or retrieval context. Trace each material fact,
constraint, decision, and criterion to user direction, a source location, or a labeled assumption.
Preserve contradiction and unread-source limits. Do not claim research, approval, repository
behavior, external state, or a completed gate that was not directly supplied or observed.

## Escalation triggers

Escalate material source conflicts; unknown actor, policy, scope, or success outcome; compliance or
risk acceptance; unsupported fixed metrics; unavailable named sources; irreversible behavior
without recovery authority; or a requested decision belonging to design, architecture,
implementation, QA, review, or the human.

## Related assets

- `assets/product/build-brief-template.md` for the canonical brief.
- `assets/product/product-specification-template.md` when validated discovery becomes a product
  specification rather than a build brief.
- `assets/design/ux-ui-spec-template.md` for downstream interaction definition.
- `assets/quality/design-architecture-matrix-template.md` for independent compatibility review.
