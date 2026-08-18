# Feasibility experiments

Use this reference when a proposed outcome contains a material technical unknown that cannot be
resolved from current repository evidence or authoritative documentation. An experiment reduces a
specific decision uncertainty; it is not an early production implementation.

## Required inputs

- The discovery brief and requested outcome.
- Constraints for environment, compatibility, security, privacy, cost, delivery, and operations.
- Current system context, dependencies, representative inputs, and authoritative documentation.
- The decision owner, decision deadline when supplied, and what downstream scope depends on it.
- Permission and safe boundaries for any prototype, benchmark, or external access.

Conflicting product or policy constraints, unavailable representative evidence, missing authority
for a state-changing experiment, or an undefined decision blocks a conclusive verdict. Safe,
read-only inspection may proceed and must retain the unknown.

## Verdict taxonomy

| Verdict | Use when | Required statement |
| --- | --- | --- |
| `FEASIBLE` | Current evidence supports the outcome within every material supplied constraint | Evidence, conditions, remaining risk, and what was not tested |
| `CONDITIONALLY_FEASIBLE` | The outcome works only if named decisions, dependencies, limits, or mitigations hold | Each condition, owner, validation, and impact if false |
| `INFEASIBLE` | Reproducible evidence shows a material approved constraint cannot be met | Failed constraint, evidence, considered alternatives, and decision implication |
| `UNKNOWN` | Evidence cannot yet discriminate the material outcome | Missing evidence, bounded next experiment or decision, and cost of uncertainty |

“Likely feasible” is not a fifth verdict. Express uncertainty in conditions and evidence state.

## Staged method

1. **Frame the decision.** State the outcome, alternatives, material constraints, decision owner,
   and which fact would change the choice.
2. **Inventory evidence.** Inspect current code, supported versions, official documentation,
   representative data, prior experiments, and operational capabilities. Separate observation from
   assumption.
3. **Rank risks.** Consider correctness, compatibility, dependency viability, security and privacy,
   operability, performance only where sourced, delivery complexity, reversibility, and cost only
   where the user supplies a decision context.
4. **Select the smallest discriminating experiment.** Test one hypothesis at the closest relevant
   boundary with representative inputs and a predeclared decision threshold. Prefer read-only and
   disposable work.
5. **Bound the method.** State environment, versions, data, commands, safety constraints, time or
   cost bound if approved, and qualities the experiment cannot establish.
6. **Run only when authorized and possible.** Preserve raw observations, failed attempts, and
   environmental differences. Do not tune the method after seeing output without recording the
   change.
7. **Interpret proportionately.** Compare observation with the threshold; do not generalize a
   prototype to production reliability, scale, security, or maintainability.
8. **Assign verdict and handoff.** Use `assets/platform/feasibility-assessment-template.md`; state
   conditions, alternatives, evidence, unknowns, decisions, and residual risks for the human gate.

## Experiment selection rules

| Unknown | Useful bounded evidence | Does not prove |
| --- | --- | --- |
| Library or format compatibility | Target-version prototype with representative valid and invalid samples | Production integration, licensing, or long-term support |
| Interface viability | Contract spike against the documented producing and consuming boundary | Operational reliability or final architecture |
| Performance constraint | Representative workload at the approved measurement boundary with baseline and environment | Other workloads, production capacity, or an invented target |
| Migration viability | Disposable representative schema/data rehearsal with validation and recovery path | Production duration or zero operational risk |
| External dependency behavior | Authorized sandbox/read-only cases for success, timeout, rate limit, malformed response, and recovery | Provider availability guarantees or future behavior |
| Security assumption | Minimal threat path, control observation, and negative case in a safe environment | Absence of vulnerabilities outside the bounded surface |

Do not experiment to decide product policy. If two technically possible options differ mainly in
user value, legal policy, budget authority, or risk tolerance, give the human evidence and options.

## Normal and failure paths

On the normal path, the hypothesis and threshold are fixed, representative evidence is collected,
limitations remain visible, and the verdict narrows the downstream decision.

If the experiment cannot run, return UNKNOWN with the exact blocker and best existing evidence. If
the result is mixed, preserve conditions rather than averaging them into FEASIBLE. If a dependency
or environment differs from the target, report the applicability limit. If the experiment reveals
a new architecture or policy decision, stop rather than expanding the prototype.

## Common mistakes

- Building a broad prototype before naming the decision it serves.
- Selecting a preferred architecture and designing an experiment that can only confirm it.
- Treating documentation as target-environment observation.
- Changing data, production state, vendor accounts, or spend without explicit authority.
- Claiming production reliability, security, scale, or delivery schedule from a disposable spike.
- Hiding failed attempts or rerunning with new thresholds until the result appears favorable.
- Inventing performance, cost, availability, or delivery targets not supplied by approved inputs.
- Passing prototype code to implementation as production-ready.

## Calibration

**Good:** “Unknown: parser v4 support for the supplied legacy records. Hypothesis: it accepts all
required fields and rejects malformed length safely. Run the target version against the 12 supplied
representative samples in an isolated fixture. CONDITIONALLY_FEASIBLE if required fields round-trip
and malformed cases fail without partial output; this does not prove production throughput.”

**Counterexample:** “The quick demo parsed one file, so the integration is feasible, secure, and
will ship in two weeks.” One happy path cannot support those conclusions or schedule authority.

## Evidence expectations

Record the artifact, environment, versions, inputs, method, commands, raw observations, decision
threshold, limitations, and reasoning from observation to verdict. Cite official documentation only
when its applicable version or retrieval context matters; do not reproduce vendor guidance. Use
`references/common/evidence-and-uncertainty.md` for every material assumption and inference.

## Escalation triggers

Escalate when constraints conflict; representative data or target environment is unavailable;
testing requires credentials, spending, production mutation, sensitive data, or expanded authority;
the decision threshold is product or policy rather than technical; a dependency's license or
support state is material and unresolved; or no bounded experiment can reduce the uncertainty.

## Related assets

- `assets/platform/feasibility-assessment-template.md` for verdict, experiment, and handoff state.
- `assets/platform/architecture-decision-record-template.md` when approved feasibility leads to a
  consequential architecture choice.
- `references/platform/architecture-patterns.md` only when pattern viability is the tested unknown.
