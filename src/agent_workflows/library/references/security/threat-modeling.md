# Threat modeling and change-risk review

Use this reference when a change creates or alters a trust boundary, authentication or authorization,
sensitive data, untrusted input, secret, dependency, external integration, privileged operation,
logging exposure, or material availability path. For a bounded review, model only the changed and
directly affected surface; do not claim whole-system security.

## Required inputs

- Authoritative request, acceptance criteria, policy, data classification, and risk constraints.
- Identified implementation artifact and matching QA evidence.
- Current architecture, data flows, actors, identities, entry points, trust boundaries, and owners.
- Authentication, authorization, validation, secret, dependency, logging, and recovery behavior.
- Prior threat models, known incidents, scanner or dependency evidence only when actually available.

Unknown data sensitivity, authorization ownership, artifact identity, or material trust-boundary
behavior blocks APPROVED. Safe review may proceed to identify evidence gaps, but an absent policy is
not permission to invent one.

## Staged method

1. **Confirm scope and artifact.** Record changed paths, criteria, QA head, exclusions, and whether
   the reviewer is independent.
2. **Inventory assets and data.** Identify confidentiality, integrity, availability, privacy,
   retention, deletion, and ownership needs from authoritative sources.
3. **Map actors and flows.** Record identities, capabilities, entry points, dependencies, trust
   transitions, storage, logs, and privileged actions. Use a diagram only when it clarifies a real
   boundary.
4. **Enumerate plausible abuse and failure paths.** Ask how an actor could impersonate, exceed
   authority, inject or confuse input, expose secrets or data, exploit a dependency, evade
   detection, create unsafe defaults, or exhaust an important resource.
5. **Inspect controls.** Distinguish preventive, detective, and recovery controls; verify that policy
   is enforced at the owning boundary and failures default safely.
6. **Test evidence.** Use current code, configuration, dependency records, direct negative cases,
   and authorized tool output. A configured scanner is not a completed scan.
7. **Classify findings.** Base priority on supported exploitability, prerequisites, affected asset,
   impact, detectability, and recovery—not generic severity language. Separate confirmed
   vulnerability, material risk, hardening opportunity, and unknown.
8. **Specify treatment.** Name bounded mitigation, responsible owner, retest condition, residual
   risk, and any product, architecture, or human decision.
9. **Issue verdict and handoff.** Use `assets/security/threat-model-template.md`; return APPROVED only
   when no material security criterion or required finding remains unresolved.

## Conditional review matrix

| Concern | Activate when | Evidence and decision required |
| --- | --- | --- |
| Authentication | Identity establishment, session, credential, token, or recovery changes | Trusted issuer, lifecycle, failure, replay, revocation, and safe logging |
| Authorization | Access depends on role, ownership, tenant, state, or privileged action | Policy source, server/owner boundary enforcement, allowed and denied cases, safe default |
| Input and injection | Untrusted data reaches parsing, commands, queries, templates, files, or URLs | Canonicalization, bounds, validation boundary, output handling, failure and negative cases |
| Sensitive data/privacy | Personal, regulated, confidential, or credential data is collected, stored, moved, or logged | Classification, minimization, purpose, access, retention/deletion, encryption context, disclosure limits |
| Secrets | Keys, tokens, credentials, signing, or configuration are touched | Source, access boundary, rotation/revocation, error and logging behavior; never expose values |
| Dependencies/supply chain | Package, image, service, plugin, or build input changes | Provenance, applicable version, support/advisory evidence, privileges, isolation, update and recovery owner |
| Logging/observability | Security events or sensitive context may be recorded | Detection need, correlation, access, retention, redaction, alert/investigation owner |
| Availability/abuse | Expensive, repeatable, asynchronous, or shared-resource work is exposed | Bounds, quotas only when approved, cancellation, backpressure, idempotency, detection, recovery |
| Unsafe defaults | Missing configuration, first-run, fallback, or error state changes behavior | Deny/safe behavior, explicit opt-in, operator visibility, and recovery |

## Normal and failure paths

On the normal path, assets and policy have owners, every relevant trust transition has an evidenced
control, negative cases exercise material abuse paths, findings have current-artifact evidence, and
residual risk is visible to the authorized owner.

If policy or data class conflicts, stop for the human or owning role. If a tool cannot run, report
the attempted command and coverage limit; do not claim zero findings. If evidence shows a plausible
high-impact path but exploitability is incomplete, preserve it as a material risk or unknown with a
bounded next check. If the artifact changes, retest affected controls.

## Common mistakes

- Producing a generic checklist unrelated to changed assets and flows.
- Trusting client-side controls for server-owned authorization.
- Reporting severity without actor, precondition, path, asset, and impact.
- Treating validation, escaping, encryption, or authentication as one universal control.
- Logging full sensitive payloads to improve debugging.
- Claiming a scan ran because configuration exists, or a clean scan proves absence of risk.
- Inventing compliance, vulnerability counts, risk acceptance, or a security guarantee.
- Implementing the fix and then approving the same work as an independent reviewer.

## Calibration

**Good:** “On head `abc123`, the import route accepts a record ID without verifying account
ownership at the service boundary. The cross-owner case succeeds, exposing sensitive data. Required
mitigation: enforce owner policy at the write boundary; pass when current-head denied QA succeeds.
Other import formats were not reviewed.”

**Counterexample:** “Authorization looks weak. Run a scanner and make it secure.” This lacks an
asset, trust boundary, evidence, impact, owner, mitigation, and pass condition.

## Evidence expectations

Tie every material conclusion to the current diff, exact path or data flow, authoritative policy,
configuration, dependency record, executed check, or direct observation. Record artifact,
environment, and tool limitations. Use `references/common/evidence-and-uncertainty.md` to separate
observation, inference, assumption, decision, and unknown. Never expose secret values in evidence.

## Escalation triggers

Escalate conflicting policy or data classification; absent authorization ownership; suspected
active compromise; material vulnerability needing coordinated disclosure; unavailable evidence for
a high-impact path; dependency or credential actions requiring external authority; unresolved
privacy, legal, architecture, or risk-acceptance decisions; or lack of reviewer independence.

## Related assets

- `assets/security/threat-model-template.md` for the complete threat and change-risk report.
- `assets/quality/review-report-template.md` for final review synthesis.
- `references/quality/testing-strategy.md` for negative and boundary evidence.
- `references/quality/review-findings.md` for finding lifecycle.
