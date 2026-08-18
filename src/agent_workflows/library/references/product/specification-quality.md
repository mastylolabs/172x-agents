# Specification quality

Use this reference after discovery, relevant research or feasibility work, and required human
validation have produced stable product intent. Its purpose is to turn validated inputs into
traceable behavior and acceptance criteria, not to choose UI layout, architecture, or implementation.

## Required inputs and readiness

- Identified approved discovery, research, feasibility, policy, and human-decision artifacts.
- Actors, desired outcomes, scope, non-goals, constraints, and source-authority order.
- Existing product behavior and compatibility obligations when relevant.
- Known authorization, data, content, accessibility, privacy, and risk requirements.
- Unresolved questions, owners, human-gate state, and intended downstream receivers.

Conflicting approved policy, unknown actor or ownership, absent material success behavior, or a
claimed approval without evidence blocks the affected requirement. Non-material detail may remain
a labeled assumption only when downstream roles can proceed without changing visible behavior or
authority.

## Staged method

1. **Fix artifact identity and authority.** Record source versions, validation decision, scope,
   non-goals, and unresolved conflicts.
2. **Define stable IDs.** Assign each requirement, acceptance criterion, decision, and material
   unknown a unique stable ID. Preserve IDs across revisions; mark removed items rather than
   silently reusing them.
3. **Write requirement anatomy.** For each requirement, name actor, trigger or condition, observable
   behavior, outcome, priority source, relevant constraints, and source traceability.
4. **Select activated states.** Cover normal, loading, empty, validation, denied, failure, retry,
   partial, stale, recovery, cancellation, and terminal states only when the behavior can reach
   them. Mark not applicable deliberately.
5. **Define data and policy needs.** State product-visible data, ownership, authorization outcome,
   retention or disclosure behavior, content, and cross-discipline questions without prescribing
   implementation.
6. **Write acceptance criteria.** Link each criterion to requirement IDs and specify given context,
   observable action or event, outcome, and acceptable evidence boundary.
7. **Trace evidence and uncertainty.** Map requirements to approved inputs; separate facts,
   observations, inference, assumptions, decisions, and unknowns with
   `references/common/evidence-and-uncertainty.md`.
8. **Test downstream usability.** Ensure UX/UI can map every requirement to flows and states,
   architecture can map data/contract needs, and QA can verify criteria without inventing behavior.
   Complete `assets/product/product-specification-template.md` and the handoff envelope.

## Requirement and criterion rules

| Element | Required content | Reject when |
| --- | --- | --- |
| Requirement | Stable ID, actor, condition, behavior, outcome, priority authority, source | It is a feature label, solution choice, or unsupported policy |
| Acceptance criterion | Stable ID, linked requirement IDs, context, event, observable result, evidence | It uses vague adjectives or checks an implementation detail without a product reason |
| Non-goal | Excluded behavior and boundary consequence | It merely says “future work” without clarifying current scope |
| Assumption | Premise, evidence state, impact if false, validation owner | It silently supplies material policy or approval |
| Decision | Decision, authorized owner, artifact/date, affected IDs | Authority or decision state is unverified |
| Unknown | Missing answer, affected IDs, consequence, next owner | It is hidden inside ambiguous prose |

Use priority only when its source and meaning are supplied. Do not invent schedules, performance,
availability, coverage, adoption, or issue-count targets.

## State selection and traceability

For each requirement, ask whether the actor can encounter no data, invalid data, denied access,
dependency failure, interrupted progress, partial completion, stale state, retry, or irreversible
outcome. Include only reachable material states and state why excluded states are not applicable.

Traceability must remain bidirectional:

`source or decision -> REQ ID -> AC ID -> UX flow/state and data need -> architecture contract -> QA evidence`

A downstream design or architecture artifact may refine its own decisions but must not silently
change the originating requirement. A changed requirement produces a new specification version and
invalidates affected downstream evidence.

## Normal and failure paths

On the normal path, every material behavior has a stable ID, approved source, relevant state set,
observable criteria, and identical handoff to UX/UI and architecture. Unresolved non-blocking items
remain visible with owners.

If policy or authority conflicts, keep affected IDs blocked and send the smallest decision to the
human. If feasibility evidence cannot support a requested outcome, preserve the condition or route
scope reconsideration; do not disguise it as implementation detail. If design or architecture
reveals a product gap, revise the specification rather than letting downstream artifacts redefine
it. If an arbitrary metric lacks an approved outcome and measurement boundary, reject it.

## Common mistakes

- Writing a feature inventory instead of actor-and-outcome requirements.
- Giving criteria no stable IDs or source links.
- Covering only the happy path while hiding denial, failure, and recovery.
- Prescribing endpoints, schemas, framework components, or pixel layouts as product behavior.
- Using “fast,” “simple,” “intuitive,” “robust,” or “secure” without observable evidence.
- Treating feasibility conditions or research implications as approved decisions.
- Sending different product contracts to UX/UI and architecture.
- Claiming stakeholder approval without an identified decision artifact.

## Calibration

**Good:** “REQ-4 — An account owner can request an audit export without keeping the page open
(source: approved decision DEC-2). AC-7 — Given an accepted request, when the owner returns later,
the current status and terminal outcome are available. UX must define progress/recovery states;
architecture must define job identity, ownership, and status errors.”

**Counterexample:** “The export should be fast and use a queue with a polished progress screen.” It
mixes vague product intent, architecture, and visual implementation without source or evidence.

## Evidence expectations

Trace every requirement, priority, constraint, and criterion to an identified validated source or
authorized decision. Record artifact versions and exact source locations. Label assumptions and
unknowns with consequences and owners. Passing tests, existing code, market implications, or the
specialist's preference do not establish product approval.

## Escalation triggers

Escalate conflicting approved sources; missing actor, product policy, authorization outcome, or
data owner; unsupported fixed metric; feasibility condition requiring risk acceptance; scope change;
unverified approval; or any downstream request that would silently alter requirement IDs or
acceptance behavior.

## Related assets

- `assets/product/product-specification-template.md` for the complete identified specification.
- `assets/design/ux-ui-spec-template.md` for requirement-to-flow/state traceability.
- `assets/platform/architecture-template.md` for requirement-to-contract traceability.
- `assets/quality/design-architecture-matrix-template.md` for independent cross-artifact review.
