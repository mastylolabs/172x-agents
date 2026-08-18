# Agent-quality evaluations v1

This directory defines repository-native behavioral scenarios for the canonical 172X agents. The
fixtures support repeatable comparison of prompt revisions; they are not an agent runtime, model
API client, automated evaluator, or claim that a model behaved correctly.

## What is deterministic

`agent_workflows.library.validate_library()` performs only repository checks:

- one fixture exists for every canonical agent and no unknown agent has a fixture;
- the fixture and canonical agent versions agree;
- every fixture contains exactly the six required case categories;
- required scalar fields and non-empty behavior lists are present;
- case and agent identifiers are unique and paths are packaged resources;
- canonical section, relationship, and internal-path validation still passes.

These checks prove fixture structure and discoverability. They do not execute a host, judge an
answer, calculate a behavioral pass rate, or prove that enriched instructions improve outcomes.

Run the deterministic lane with:

```bash
uv run pytest -q tests/test_library.py tests/test_evaluations.py
```

## Fixture schema

Each `cases/<agent-id>.toml` file contains:

```toml
schema_version = 1
agent_id = "<canonical-agent-id>"
agent_version = 1

[[cases]]
id = "<globally-unique-case-id>"
category = "<required-category>"
title = "<short diagnostic label>"
scenario = "<self-contained task and supplied evidence>"
expected_behaviors = ["<observable behavior>"]
prohibited_behaviors = ["<observable failure>"]
evidence_expectations = ["<evidence the answer must use or request>"]
handoff_expectations = ["<required receiver, artifact, state, or risk>"]
```

The six categories are:

1. `normal-success`
2. `incomplete-or-conflicting-inputs`
3. `tempting-scope-expansion`
4. `insufficient-evidence`
5. `boundary-or-authority-challenge`
6. `handoff-completeness`

Keep a scenario self-contained and diagnostic. Expected and prohibited behaviors should describe
observable response properties, not preferred prose. Do not require a provider action, credential,
or destructive mutation to evaluate a case.

## Repeated host-run protocol

Behavioral execution is deliberately manual and non-deterministic:

1. Identify the candidate agent definition by repository revision and record every conditional
   reference or asset loaded. Use the same host, model, reasoning setting, tool availability, and
   system instructions for candidates being compared.
2. Start a clean host session for one scenario. Supply the canonical agent and only the references
   conditionally activated by that agent, followed by the scenario exactly as written. Do not add
   hints from the expected or prohibited lists.
3. Run each candidate on each scenario at least three times. If resource limits require fewer runs,
   report the missing repetitions as a coverage limit rather than treating the case as passed.
4. Preserve each response verbatim with run ID, timestamp, candidate revision, host/model version,
   settings, loaded references/assets, tool availability, and any actual commands or external
   actions. A local recommendation is not an external approval or action.
5. Have an evaluator who did not author the response score each run with `rubric.md`. Record a short
   evidence excerpt for every non-full score and every critical failure. If independent evaluation
   is unavailable, label the author-scored result as a limitation.
6. Compare run-level results by case and rubric dimension. Look for stable improvement, variance,
   and regressions rather than hiding them in one aggregate number.
7. Adopt a prompt revision only through human judgment backed by the recorded runs. A revision with
   a new authority, unsupported-action, or invented-evidence failure is a regression even if other
   dimensions improve.

Use inert repositories, fixtures, or read-only context. If a scenario mentions a commit, approval,
merge, release, deployment, notification, or external source, the response should reason from the
supplied state and must not perform or claim that action.

## Comparison record

For each evaluation batch, record outside this packaged directory:

- objective and candidate revisions;
- cases and run counts attempted;
- host/model/settings and loaded supporting material;
- raw responses or durable locations;
- per-run rubric scores and evidence;
- critical failures and variance;
- coverage limits;
- human adoption decision and rationale.

Evaluation results are observations about named runs, not permanent properties of an agent or
model. A workflow change affects future executions only.

## Authoring checks

When modifying a fixture, verify that the scenario still tests its declared category, the expected
behavior stays inside the canonical role, and the handoff expectation uses the full envelope from
`references/common/handoff-envelope.md`. Use `references/common/evidence-and-uncertainty.md` to
distinguish evidence from confidence or inference.
