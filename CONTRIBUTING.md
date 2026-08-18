# Contributing to 172X Agents

Thank you for helping make 172X Agents more useful, reliable, and clear.

## Before you start

Open an issue before substantial work so maintainers and contributors can agree on the problem,
scope, and acceptance criteria. Keep proposed changes within the documented product boundaries:
172X is a Markdown-first library and global-skill CLI, not an agent runtime, hosted service, or
package marketplace.

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md). Report security vulnerabilities privately
as described in [SECURITY.md](SECURITY.md), not through a public issue.

## Where changes belong

- Agent and workflow behavior belongs in canonical Markdown under
  `src/agent_workflows/library/`.
- Small installation, validation, and discovery behavior belongs in the Python CLI only when
  Markdown guidance cannot provide it.
- Forge catalog content is generated from canonical Markdown. Do not edit
  `forge/src/data/catalog.generated.json`.

Agent definitions must use the supported scalar frontmatter and include every required operational
section. Workflow definitions must reference existing agent IDs and retain clear human gates,
evidence requirements, and bounded feedback loops.

## Authoring agents safely

Use a thin core with deep, conditional support. Keep routing, input readiness, the numbered
role-specific method, decisive if/then rules, the deliverable, evidence requirements, calibration,
the complete handoff envelope, and authority boundaries in the agent file. Put reusable methods in
`references/` and reusable output shapes in `assets/`; do not duplicate either across agents.

When adding or changing an agent:

1. Preserve an existing ID and name. For a new role, first show that an adjacent role cannot own the
   work without broadening its authority.
2. Use the exact `**Use this agent when:**` and `**Do not use this agent when:**` labels. Route
   rejected work to a named adjacent agent or human.
3. Separate blocking inputs from safe, explicitly labeled assumptions. Require escalation when an
   assumption would change authority, acceptance criteria, irreversible behavior, or external
   state.
4. Keep all 12 required sections, once each and in repository order. Use explicit rooted paths such
   as `references/quality/testing-strategy.md` and `assets/quality/qa-report-template.md` for
   conditional support; those paths define focused-install dependencies.
5. Require evidence for every material conclusion. Distinguish facts, observations, inference,
   assumptions, decisions, and unknowns where those states can be confused.
6. Name the receiving agent or human, artifact and version, acceptance-criteria status, evidence
   state, assumptions, unresolved decisions, residual risks, requested action, and actual external-
   action state in the handoff.
7. Include a small good/counterexample calibration that changes decisions or output quality. Do not
   add decorative personality, invented memory or experience, fake metrics, or unsupported
   approval/deployment claims.
8. Increment the scalar agent `version` for a material contract change and update the matching
   `evaluations/v1/cases/<agent-id>.toml` `agent_version`. Keep all six scenario categories complete.
9. Run deterministic validation and regenerate Forge only through
   `scripts/generate_forge_catalog.py` or `npm run catalog`.

The shared rubric and manual protocol live in `src/agent_workflows/library/evaluations/v1/`.
Repository tests verify structure, paths, versions, fixture coverage, and catalog projection; they
do not execute or score a model. To claim a behavioral improvement, select cases before testing,
record the host/model/settings and loaded support, choose the repeat count in advance, retain every
transcript, score all runs with the same rubric, and report both regressions and critical failures.
Do not compare a favorable run with an unrecorded baseline.

## Development checks

Use Python 3.12+. The complete local gate mirrors `.github/workflows/ci.yml`:

```bash
uv sync --all-extras --frozen
uv run ruff format --check src tests scripts
uv run ruff check .
uv run mypy
uv run pytest
uv run mkdocs build --strict
(cd forge && npm ci && npm run build)
uv build

package_venv="$(mktemp -d)/venv"
uv venv --python 3.12 "$package_venv"
uv pip install --python "$package_venv/bin/python" dist/*.whl
"$package_venv/bin/agents" --help
"$package_venv/bin/172x-agents" --help
```

Run focused checks while working, but do not describe an omitted final command as a pass. Generated
Forge catalog data must come from `npm run catalog` or `npm run build`, never a manual JSON edit.

## Pull requests

Keep pull requests small and explain:

1. the problem and intended outcome;
2. the files and behavior changed;
3. the checks run and their results;
4. any canonical agent or workflow content changed; and
5. documentation or compatibility implications.

Do not commit generated project installations, credentials, private customer material, or build
output. Contributors retain ownership of their contributions while granting the project the rights
needed to distribute them under the repository's [MIT License](LICENSE.md).
