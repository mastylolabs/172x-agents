# UX/UI definition of done

Use this reference when approved product requirements must become implementation-ready user flows,
interaction requirements, screen or component responsibilities, responsive behavior, content,
states, accessibility criteria, and design-system-compatible UI guidance. It defines behavior and
handoff readiness; it does not authorize a new brand, visual system, backend policy, or production
implementation.

## Required inputs and readiness

- Identified approved specification or brief with stable requirement and criterion IDs.
- Actors, tasks, scope, non-goals, content policy, authorization outcomes, and user constraints.
- Existing product behavior and authoritative brand or design-system material when available.
- Supported devices, viewports, input methods, language/content, and accessibility requirements
  only when supplied or established by authoritative project material.
- Known data, API, error, loading, authorization, persistence, and recovery contracts.
- Assumptions, unresolved decisions, artifact versions, and intended review/handoff path.

Conflicting product policy, absent material content, unknown authorization behavior, unstable data
or API semantics, or a request for an unsupported brand system blocks the affected design state.
Unspecified reversible layout detail may remain a labeled assumption only when existing
design-system evidence supports it and it cannot change product behavior or accessibility.

## Staged method

1. **Fix authority and traceability.** Record specification version, requirement/criterion IDs,
   current design-system sources, constraints, decisions, assumptions, and blocked items.
2. **Map user flows.** For each actor and goal, define entry, ordered actions and decisions,
   navigation, exit, interruption, success, and recovery. Link every step to requirement IDs.
3. **Assign screen/component responsibilities.** Define information hierarchy, controls, displayed
   data, validation ownership, component states, reuse rationale, and where a new pattern is
   genuinely required. Avoid framework prescriptions.
4. **Build the state matrix.** Cover activated initial, loading, empty, success, validation, denied,
   unavailable, error, partial, stale, retry, interrupted, recovery, and terminal states. Define
   state transitions and preserved user input.
5. **Specify content.** Provide labels, instructions, status, errors, confirmation, destructive
   warnings, empty states, and dynamic announcements or identify the authoritative content owner.
   Do not use placeholder copy for a material decision.
6. **Define responsive behavior.** Describe priority, reflow, wrapping, truncation, overflow,
   touch/keyboard implications, content growth, and state continuity across approved conditions.
   Do not invent breakpoints when the design system already owns them.
7. **Define accessibility criteria.** Specify semantic relationships, names, instructions, keyboard
   sequence, focus entry/restoration, errors, status communication, target/contrast needs when
   authoritative, motion alternatives, and non-visual equivalents for activated behavior.
8. **Map data and contracts.** For each state, identify data fields, source and ownership needs,
   authorization result, request/response/error semantics, freshness, persistence, cancellation,
   retry, progress, and recovery questions. Reconcile decisions with `principal-architect`.
9. **Package and check readiness.** Complete `assets/design/ux-ui-spec-template.md`, separate
   evidence states, and verify `assets/quality/design-architecture-matrix-template.md` can trace
   every material requirement through UX states/data needs to architecture contracts.

## Selection rules

| Situation | Required treatment | Escalate when |
| --- | --- | --- |
| Existing component/pattern satisfies behavior | Reuse it and cite the authoritative source | Its states or accessibility conflict with approved requirements |
| No authoritative visual or brand system exists | Provide neutral structural and behavioral guidance | A new brand, logo, typography, color, or visual language is requested |
| Backend contract is stable | Map UI states to exact success/error/authorization behavior | UX needs a semantic or state the contract does not provide |
| Backend contract is unresolved | Define the user need and mark contract state blocked | Product or architecture authority must choose behavior |
| Content is material but missing | Name content purpose, state, owner, and decision needed | Placeholder copy would alter consent, safety, authorization, or recovery |
| Responsive requirement is unsourced | Preserve existing system behavior and label coverage | New device support or breakpoint policy changes scope |
| Accessibility behavior is not observable in supplied artifact | Define testable behavior and evidence needed | A compliance claim or policy choice needs human authority |

Use a flow diagram, wireframe, component inventory, or prose only when it makes a decision clearer.
Visual polish without behavioral or evidentiary value is not completion.

## Normal and failure paths

On the normal path, stable requirement IDs trace through every material flow, state, content rule,
responsive condition, accessibility criterion, and data need; architecture reconciles the same
contract; frontend receives an identified implementation-ready artifact.

If product behavior conflicts, return the affected IDs to the specification owner. If an API or
data need is unstable, preserve the user need and reconcile with architecture rather than inventing
a response. If authoritative brand material is absent, stay design-system-compatible or neutral and
route the visual decision. If a screenshot or mockup cannot prove focus, keyboard, responsive,
dynamic, or failure behavior, record those areas as unverified. Any revised source artifact
invalidates affected traceability rows.

## Common mistakes

- Treating a happy-path flow or polished screenshot as a complete specification.
- Inventing a logo, palette, type scale, component library, breakpoint, or brand voice.
- Copying a framework's component API into generic interaction requirements.
- Omitting loading, denied, error, retry, interrupted, or recovery behavior.
- Using placeholder text where content changes consent, safety, or task success.
- Claiming accessibility from visual appearance or a checklist without observable criteria.
- Duplicating authorization or validation policy in the client design.
- Leaving data fields, errors, persistence, and ownership for engineers to guess.

## Calibration

**Good:** “REQ-4 / AC-7, export status: show queued, active, completed, and terminal-failure states;
preserve status after navigation; announce state changes; restore focus after retry; existing status
component DS-12 supplies hierarchy and tokens. Architecture must provide owned job ID, progress
semantics, denied/not-found distinction, and retry contract. Breakpoints remain the existing system's.”

**Counterexample:** “Create a modern blue dashboard with a spinner and accessible components.” It
has no requirement trace, state behavior, content, data contract, evidence, or brand authority.

## Evidence expectations

Trace each material design requirement to specification IDs, authoritative product/brand/design-
system sources, or a labeled assumption. Distinguish visible mockup observations from unproven
interaction, responsive, accessibility, and contract behavior. Record artifact versions, exact
source locations, coverage limits, and unresolved evidence. Do not claim user testing, compliance,
design approval, or architecture agreement unless it occurred.

## Escalation triggers

Escalate product-scope or policy changes; missing authorization or destructive-action behavior;
unsupported brand/visual-system work; material content without an owner; inaccessible or conflicting
design-system authority; new platform support; API/data contract conflict; accessibility commitment
or compliance claim requiring authority; or a requirement that cannot trace across product, UX/UI,
and architecture artifacts.

## Related assets

- `assets/design/ux-ui-spec-template.md` for the complete UX/UI artifact.
- `assets/product/product-specification-template.md` for source requirement and criterion IDs.
- `assets/platform/architecture-template.md` for reconciled data and interface contracts.
- `assets/quality/design-architecture-matrix-template.md` for independent readiness review.
