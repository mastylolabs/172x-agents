# Frontend delivery

Use this reference for frontend implementation or specialist review when a change affects user
flows, interactive states, accessibility, responsive behavior, content, browser behavior, API
integration, or evidenced performance. Apply only the activated paths; do not prescribe a
framework or visual system.

## Required inputs

- Approved product behavior, acceptance criteria, and UX/UI specification.
- Existing design system and repository component, content, and accessibility conventions.
- Stable API, data, authorization, error, loading, and recovery contracts.
- Supported viewport, browser, device, and assistive-technology requirements when authoritative.
- Current implementation artifact, test environment, and QA evidence for review work.

Conflicting UX and API contracts, missing material content or authorization behavior, an
unidentified artifact, or absent accessibility criteria for a new interaction blocks a ready
implementation or approval. Existing repository patterns may guide reversible details only when
their applicability is observed and labeled.

## Staged method

1. **Trace the journey.** Map actors, entry and exit points, tasks, content, data needs, navigation,
   focus movement, and success or recovery outcomes to criteria.
2. **Build the state matrix.** Identify initial, loading, progressive, empty, success, validation,
   denied, unavailable, partial, stale, retry, and terminal states that the contract activates.
3. **Bind stable interfaces.** Map each UI state to documented request, response, error,
   authorization, cancellation, and retry semantics. Escalate rather than parse undocumented
   strings or invent fallback policy.
4. **Apply existing UI language.** Reuse components, tokens, hierarchy, and content patterns. Add a
   new pattern only with authoritative design evidence; a delivery role does not create a brand.
5. **Specify or inspect interaction.** Cover keyboard order, focus placement and restoration,
   accessible names, instructions, errors, status changes, target size where required, motion, and
   alternative input behavior.
6. **Check responsive and resilience behavior.** Preserve task completion across approved
   viewports, content growth, localization, slow or failed APIs, repeated actions, and navigation.
7. **Measure only sourced performance.** If a requirement supplies a boundary and budget, inspect
   relevant loading, rendering, asset, and interaction evidence. Otherwise report observations
   without inventing a target.
8. **Verify and hand off.** Exercise activated states at the relevant rendered boundary, run
   repository gates, record browser or assistive coverage limits, and transfer artifact, contract,
   evidence, assumptions, and residual risk.

## State and evidence matrix

| User step | UI state | Trigger or API state | Content and action | Accessibility behavior | Evidence or limit |
| --- | --- | --- | --- | --- | --- |
| | | | | | |

## Conditional selection rules

| Concern | Activate when | Required decision or evidence |
| --- | --- | --- |
| Loading and cancellation | Work is not immediate or navigation can interrupt it | Progress semantics, duplicate prevention, cancellation, late-response behavior |
| Empty and partial data | A valid response may contain no or incomplete content | Meaning, next action, preserved context, and distinction from error |
| Validation and errors | Input or dependency failure is user-visible | Field and summary association, focus, retained input, safe copy, retry or recovery |
| Authorization | Availability or result depends on identity or ownership | Server-backed policy, denied state, information disclosure, and navigation |
| Keyboard and assistive use | The change adds or alters interaction or dynamic state | Operable sequence, focus, labels, announcements, and direct behavior evidence |
| Responsive behavior | Content or task spans approved viewport or device conditions | Hierarchy, reflow, overflow, target access, and completion across required sizes |
| Browser-specific behavior | The repository or requirement names supported browsers or APIs vary | Representative execution and explicit coverage limits |
| Performance | An approved user outcome and measurement boundary exist | Current artifact, environment, workload, observation, and sourced threshold |

## Normal and failure paths

On the normal path, the user can identify the task, operate it with supported input, understand
status, complete it, and recover or leave without losing unexpected state. UI and API contracts
agree, and evidence covers material states.

On failure, distinguish validation, denial, empty data, temporary unavailability, partial success,
and terminal failure. Preserve safe input and context, prevent duplicate destructive actions,
provide an authorized recovery, and avoid disclosing protected state. If the backend does not expose
the distinction required by UX, stop for contract reconciliation rather than simulate it in the
client.

## Common mistakes

- Implementing only the happy path shown in a static design.
- Treating semantic-looking markup or a screenshot as proof of keyboard or assistive behavior.
- Parsing error message text or duplicating authorization policy in the client.
- Inventing content, breakpoints, visual tokens, browser support, or performance budgets.
- Hiding an unavailable action without a specified denied or explanatory state.
- Disabling retry or submit without defining recovery and focus behavior.
- Replacing the design system or broad component API to deliver one bounded flow.
- Claiming cross-browser or accessibility completion for paths not exercised.

## Calibration

**Good:** “The timeout contract is recoverable. Preserve the query, show the approved inline error,
move focus only when the error needs immediate action, prevent duplicate requests during retry, and
verify keyboard, narrow viewport, success, timeout, and denied paths.”

**Counterexample:** “The desktop screenshot matches, so the flow is accessible. Unknown API errors
will use the empty state.” This confuses appearance with behavior and hides a contract failure.

## Evidence expectations

Tie each state and conclusion to approved UX/UI, product, API, design-system, code, or executed
behavior evidence. Identify the artifact, environment, viewport or browser where relevant, and
coverage limits. Use `references/common/evidence-and-uncertainty.md` to separate observations from
inference and assumptions. Do not claim a manual, browser, assistive, or visual check that did not
run.

## Escalation triggers

Escalate when UX and API states conflict; content, authorization, accessibility, or responsive
behavior is materially undefined; a stable interface would need unilateral change; supported
environment evidence is unavailable; design work would require a new brand or visual system; or
the requested behavior crosses product, architecture, security, or external authority.

## Related assets

- `assets/quality/qa-report-template.md` for behavior verification.
- `assets/quality/review-report-template.md` for frontend findings.
- `references/quality/testing-strategy.md` for rendered and integration evidence.
- `references/quality/review-findings.md` for finding lifecycle.
