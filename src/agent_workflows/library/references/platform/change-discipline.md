# Change discipline

Use this reference for a cross-cutting implementation, a correction returned by QA or review, or
any change where scope, contract compatibility, recovery, or unrelated cleanup could be confused.
For a genuinely isolated edit with an obvious verification path, keep the same principles but do
not manufacture a large change plan.

## Required inputs

- The authoritative request or implementation brief and observable acceptance criteria.
- Repository instructions and the current working-tree or artifact state.
- Stable architecture, interface, data, UX, and policy contracts affected by the work.
- The repository's existing verification commands and environment.
- Prior QA or review findings, including their artifact version and lifecycle state.

Unknown user work, conflicting authoritative contracts, or a missing material acceptance criterion
blocks implementation that would overwrite or decide it. A reversible detail may proceed as a
labeled assumption only when it does not alter product behavior, public contracts, security,
dependencies, authority, or external state.

## Staged method

1. **Freeze authority and state.** Read instructions and named sources, identify the current diff or
   head, and distinguish existing user changes from the requested work.
2. **Build a change map.** Trace each criterion through current behavior, likely paths, stable
   contracts, affected consumers, focused checks, and recovery concerns. Record unknowns before
   editing.
3. **Choose the minimum coherent scope.** Include requested behavior and changes strictly necessary
   to make it correct, integrated, and testable. Separate discovered cleanup and speculative
   improvements.
4. **Sequence for reversibility.** Preserve compatibility first; stage data or interface changes
   when required; keep migrations, fallback, and rollback or forward-repair behavior explicit.
5. **Implement in repository style.** Reuse direct patterns, avoid an abstraction without present
   behavior to support it, and re-check scope after each material discovery.
6. **Verify from narrow to broad.** Run the smallest discriminating checks, then every applicable
   repository gate. Record exact commands, environment, results, and coverage limits.
7. **Reconcile feedback.** Address every required finding against the current artifact. Record the
   disposition of non-blocking findings and route questions or contract changes to their owner.
8. **Prepare the handoff.** Identify the artifact, map criteria to evidence, state contract and
   recovery effects, and preserve assumptions, unresolved decisions, residual risks, and actual
   external-action state.

## Change-map fields

| Criterion or finding | Current behavior and evidence | Planned path or contract | Verification | Recovery or compatibility concern |
| --- | --- | --- | --- | --- |
| | | | | |

This is a reasoning aid, not a required large artifact. For a small change, one concise row per
material criterion is enough.

## Scope selection rules

| Candidate change | Include now when | Otherwise |
| --- | --- | --- |
| Direct requested behavior | It implements an approved criterion | Clarify the criterion before editing |
| Enabling correction | The requested behavior cannot be correct, safe, or testable without it | Explain the dependency and seek direction if it changes a stable contract |
| Regression test | It demonstrates a material criterion or reproduced failure | Keep broader coverage work as a separate follow-up |
| Refactor | It is the smallest safe way to remove a proven obstacle or preserve behavior during the change | Defer it with evidence; do not make style preference a prerequisite |
| Dependency or configuration change | An approved requirement needs it and repository evidence supports compatibility | Escalate; do not upgrade or add tooling opportunistically |
| Discovered defect | It blocks the current criteria or creates immediate material risk in the touched path | Report it separately with owner and priority evidence |

The smallest diff is not automatically the safest diff. Prefer the smallest **coherent** change:
one that covers required success and failure behavior, compatibility, and verification without
unrelated redesign.

## Normal and failure paths

On the normal path, the current state is understood, each edit maps to a criterion or necessary
enabler, focused checks and the required gate pass, and independent QA receives a reproducible
handoff.

If a check fails, preserve its exact output and determine whether the implementation, test
environment, or criterion is responsible before changing code. If a required command cannot run,
report the coverage limit and do not declare the gate passed. If the artifact changes after a check,
invalidate affected evidence. If a correction would expand scope or change a stable contract, stop
for its owner rather than hiding it inside the fix.

## Common mistakes

- Editing before identifying user work, contracts, consumers, and verification paths.
- Treating “fewest changed lines” as permission to omit error, migration, or recovery behavior.
- Rewriting adjacent code because it is old, unfamiliar, or stylistically inconsistent.
- Adding an interface, feature flag, dependency, or configuration field for a hypothetical future.
- Running only a broad gate whose output cannot show which criterion was exercised.
- Repeatedly changing tests until they pass without explaining whether behavior or expectation was
  wrong.
- Silently ignoring a required finding, unresolved question, or failed command.
- Claiming a commit, push, change request, approval, merge, or deployment that did not occur.

## Calibration

**Good:** “AC-2 reaches the parser and CLI formatter. The coherent change is the parser correction,
one formatter compatibility branch, and two regression cases. The nearby configuration rewrite is
unrelated and remains a follow-up. Focused tests and the repository gate passed; recovery is a clean
revert because no persisted format changed.”

**Counterexample:** “While fixing AC-2 I modernized the configuration layer, upgraded the parser,
and renamed public methods because the old design was messy.” The extra work lacks a criterion,
increases compatibility risk, and obscures evidence for the requested behavior.

## Evidence expectations

For every material edit or no-change decision, name the criterion, finding, contract, or direct
repository evidence that justifies it. Record commands and observed results exactly. Separate code
inspection, executed behavior, inference, assumptions, and unknowns using
`references/common/evidence-and-uncertainty.md`. A passing implementation check is not independent
QA or approval.

## Escalation triggers

Escalate when user work cannot be isolated; authoritative inputs conflict; a public interface,
product behavior, data ownership, migration, security boundary, dependency policy, or external
state must change without approval; a required gate cannot run; feedback requires a product
decision; or the workflow feedback limit is reached.

## Related assets

- `assets/quality/qa-report-template.md` for the independent verification that follows.
- `assets/quality/review-report-template.md` for review findings returned against the artifact.
- `references/common/handoff-envelope.md` for the implementation handoff.
