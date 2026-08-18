# Discovery methods

Use this reference when the intended user, problem, triggering context, desired outcome,
constraints, or validation decision is unclear enough that solution work would require material
invention. Discovery narrows the decision; it does not prove demand, choose a solution, or simulate
user research.

## Required inputs and readiness

- The user's idea, request, or observed problem and its source.
- Known actors, stakeholders, context, constraints, prior decisions, and available evidence.
- Existing product or repository observations when relevant.
- The downstream decision and the authority that will make it.
- Limits on research, access, time, sensitive data, and external actions.

Discovery may begin with incomplete information because exposing uncertainty is its purpose.
However, absent user access, research artifacts, or external tools must remain evidence gaps; do
not invent interviews, metrics, incidents, or stakeholder consensus.

## Staged method

1. **Frame the request.** Restate the initiating idea and identify what decision discovery must
   make possible. Separate the requested outcome from any proposed solution.
2. **Inventory evidence.** Record user direction, supplied research, repository observations,
   prior decisions, constraints, assumptions, conflicts, and missing sources.
3. **Map actor and context.** Identify who experiences the problem, their triggering situation,
   current path or workaround, affected outcome, and excluded audiences. Do not create personas
   unsupported by evidence.
4. **Select material questions.** Ask only questions whose answers change audience, scope,
   behavior, risk, validation, or the next handoff. State why each answer matters.
5. **Rank assumptions.** For each assumption, assess decision impact and current evidence. Convert
   high-impact weak assumptions into a validation question with an owner and safe method.
6. **Define the smallest useful outcome.** Separate core outcome, necessary constraints, non-goals,
   and optional solution ideas. Preserve alternatives without selecting one prematurely.
7. **Draft success evidence.** Describe observable user or operating outcomes and acceptable
   evidence boundaries. Do not invent targets, sample sizes, or schedules.
8. **Prepare the decision brief.** State the bounded problem, actors, context, desired outcome,
   evidence, assumptions, constraints, open questions, draft criteria, and next research or
   feasibility questions using `references/common/handoff-envelope.md`.

## Question selection rules

| Unknown | Ask or inspect | Route when unresolved |
| --- | --- | --- |
| Actor or affected context | Who encounters the problem, when, and with what current evidence? | Human or product owner |
| Problem versus proposed solution | What outcome fails today if the proposed feature is removed? | Human validation gate |
| Outcome | What observable change would make the work useful? | Human; research if evidence is needed |
| Product policy | Which behavior is permitted, required, or excluded? | Authorized human |
| Technical constraint | What existing system fact could prevent the outcome? | `technical-feasibility` |
| Market alternative | Which explicit comparison question affects proceeding? | `market-researcher` |
| Risk or irreversible choice | Who owns acceptance, and what recovery is required? | Human or owning specialist |

Prefer one high-impact question over a generic interview script. If the answer would not alter the
decision or handoff, omit it.

## Normal and failure paths

On the normal path, discovery converts ambiguity into a bounded problem and a short register of
evidence, assumptions, validation questions, constraints, and draft success criteria. Market and
technical investigation receive the same identified artifact.

If the user cannot answer a material question, retain alternatives and describe the consequence
rather than forcing closure. If research access is unavailable, propose the smallest authorized
validation and label the evidence limit. If evidence contradicts the initial framing, revise the
problem statement and preserve the contradiction. If the request is already clear and validated,
stop discovery and route to specification or the appropriate downstream role.

## Common mistakes

- Treating the requested feature as proof of the underlying problem.
- Generating decorative personas, journey maps, or interview quotes without evidence.
- Asking broad questions whose answers do not change a decision.
- Using “everyone” as the target user or “engagement” as an unbounded outcome.
- Turning an assumption into a fact because it seems plausible.
- Choosing architecture, UI, or vendor details during problem discovery.
- Declaring validation complete without a human decision or observed evidence.

## Calibration

**Good:** “Observed fact: support supplied six export incidents involving interrupted browser
sessions. Assumption A-2: users need work to continue after navigation; impact is high because it
changes UX and architecture. Validate with the supplied incident owner and current behavior before
specification. The export format itself is already approved.”

**Counterexample:** “Busy enterprise users need a delightful asynchronous dashboard.” This invents
an audience, emotional outcome, and solution without evidence.

## Evidence expectations

For every supplied fact, identify the user statement, artifact, repository path, or direct
observation. Label inference, assumptions, decisions, and unknowns with
`references/common/evidence-and-uncertainty.md`. Record questions asked and answers actually
received; never imply that interviews, analytics, experiments, approvals, or notifications occurred
when they did not.

## Escalation triggers

Escalate conflicting problem definitions, unknown product policy, material audience or scope
choice, missing risk owner, privacy-sensitive research, a validation step requiring unavailable
access or external mutation, invented fixed targets, or an unknown that only technical feasibility,
market research, or a human can resolve.

## Related assets

- `assets/product/build-brief-template.md` when discovery feeds a broader authoritative brief.
- `assets/product/product-specification-template.md` only after discovery and required human
  validation are approved.
- `references/product/market-research-evidence.md` for explicit external research questions.
- `references/platform/feasibility-experiments.md` for material technical unknowns.
