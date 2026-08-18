# Evidence and uncertainty

Use this reference whenever a material conclusion, requirement, test verdict, review finding, or
recommendation could affect downstream work. Apply it most rigorously to research, feasibility,
QA, security, and review decisions. It does not replace role-specific evidence rules.

## Required inputs

- The claim or decision being evaluated.
- The authoritative request, acceptance criteria, and applicable contracts.
- Available sources or observable artifacts, including their identity and current version.
- The environment and commands used for direct checks.
- Known coverage limits, conflicts, and unavailable evidence.

If the authoritative criterion or artifact identity is missing, do not issue a conclusive verdict.
Proceed only with clearly labeled exploration when the result cannot be mistaken for approval or
completion.

## Evidence labels

| Label | Meaning | Minimum record |
| --- | --- | --- |
| Fact | Supplied authoritative direction or a claim directly supported by an identified source | Source, location, and relevant version or date |
| Observation | Something directly inspected or produced in the current work | Artifact or command, environment, and observed result |
| Inference | A conclusion drawn from facts or observations | Supporting evidence and the reasoning link |
| Assumption | A provisional premise used to continue | Why it is needed, impact if false, and validation owner |
| Decision | A selected option within the role's authority | Decision owner, alternatives considered, and rationale |
| Unknown | A material question the available evidence cannot answer | Missing evidence, consequence, and next resolver |

Confidence is a description of evidence quality, not evidence itself. Use `high`, `medium`, or
`low` only when it helps the receiver interpret an inference, and explain what would change it.

## Staged method

1. **Frame the claim.** Write one falsifiable or observable statement and identify the criterion or
   contract it affects.
2. **Choose the strongest available evidence.** Prefer authoritative user direction, current
   repository artifacts, reproducible behavior, and primary sources over summaries or memory.
3. **Record provenance.** Name the file and location, command and environment, artifact version or
   change-request head, or external source and retrieval date.
4. **Separate observation from interpretation.** State what was seen before stating what it means.
5. **Test conflict and absence.** Look for contrary evidence and distinguish “not observed” from
   “proved absent.”
6. **Label the conclusion.** Mark facts, observations, inferences, assumptions, decisions, and
   unknowns explicitly when they coexist in one artifact.
7. **Expose the limit.** Record omitted paths, commands that could not run, stale sources, or
   environmental differences. Route any material unresolved decision to its owner.

## Selection rules

| Situation | Evidence to prefer | Failure behavior |
| --- | --- | --- |
| Repository behavior | Reproducible command output plus exact code, test, or configuration location | Report the unrun check or inaccessible path as a coverage limit |
| User-visible acceptance criterion | Direct exercise of the behavior at the relevant boundary | Do not substitute implementation inspection when behavior could differ |
| Interface or architecture claim | Current contract and both producing and consuming paths | Mark compatibility unknown if only one side was inspected |
| External or time-sensitive claim | Current primary source with retrieval date and applicable version or geography | Do not reuse an undated secondary summary as current fact |
| QA or review verdict | Criterion-by-criterion evidence on the identified artifact version | Withhold PASS or APPROVED when a material criterion is unverified |
| Negative claim such as “no risk” | Bounded search or test scope plus explicit limitations | Never generalize a bounded check into a guarantee |

When sources conflict, preserve both observations, assess their authority and freshness, and name
the decision owner. User direction can resolve product intent; it cannot retroactively change what
a test or source showed.

## Normal and failure paths

On the normal path, evidence is current, reproducible, tied to a criterion, and sufficient for the
role's bounded conclusion. The handoff names the evidence and any residual risk.

On a failure path, keep the most specific supported result. A failed command is an observation, not
proof of root cause. An unavailable command is a coverage limit, not a pass. Conflicting sources
produce an unresolved decision, not a blended fact. If evidence is too weak for the requested
verdict, return the strongest provisional finding and the smallest next check or decision needed.

## Common mistakes

- Treating a plausible explanation, remembered convention, or confidence statement as evidence.
- Reporting only a command name instead of its inputs, environment, and observed result.
- Citing a passing aggregate gate without mapping material criteria to checks.
- Treating test presence, code style, or a happy path as proof of complete behavior.
- Omitting contrary observations or silently resolving source conflicts.
- Claiming research, scans, approvals, merges, deployments, or notifications that did not occur.
- Inventing a numeric target not supplied by an approved requirement.

## Calibration

**Good:** “Observation: `uv run pytest tests/test_widget.py -q` passed 8 tests on change head
`abc123`. Inspection at `src/widget.py:42` confirms the error is mapped to the documented empty
state. Coverage limit: the browser-specific recovery path was not exercised. Inference: criterion
AC-3 is supported for the Python boundary, but cross-browser behavior remains unknown.”

**Counterexample:** “AC-3 should pass; the implementation looks standard and I am highly
confident.” This names neither an observation nor a source and hides the untested boundary.

## Escalation triggers

Escalate when authoritative sources conflict; the artifact or version under review is unclear; a
material criterion cannot be observed; required external evidence is unavailable; an assumption
would change scope, authority, security, cost, or compatibility; or the requested conclusion would
require a guarantee beyond the checks performed.

## Related assets

- `assets/quality/qa-report-template.md` for criterion-level verification evidence.
- `assets/quality/review-report-template.md` for evidence-backed findings and verdicts.
- `references/common/handoff-envelope.md` for transferring evidence state without losing limits.
