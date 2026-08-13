# Contributing to 172X Agents

Thank you for helping make 172X Agents more useful, reliable, and clear.

## Before you start

Open an issue before substantial work so maintainers and contributors can agree on the problem,
scope, and acceptance criteria. Keep proposed changes within the documented product boundaries:
172X is a Markdown-first library and project-scoped CLI, not an agent runtime, hosted service, or
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

## Development checks

Use Python 3.12+ and install the repository development dependencies with the project's existing
environment workflow. Before opening a pull request, run:

```bash
uv run ruff format src tests scripts
uv run pytest
uv run ruff check .
uv run mypy
uv run mkdocs build --strict
cd forge && npm run build
```

Run the checks relevant to your change as you work; the complete set above is the expected final
gate for a change that touches shared behavior or documentation.

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
