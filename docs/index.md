# 172X Agents

Open-source, composable AI-agent workflows—from idea discovery and architecture to coding, QA, PR review, and release.

172X Agents gives Codex a focused library of specialist roles and workflow playbooks. The host runs the agents; 172X defines how they collaborate.

## Start small

```bash
agents install codex python
agents --workflow dev
```

The `dev` workflow coordinates independent Principal Engineer, QA Engineer, and PR Reviewer roles and stops for a human merge decision.

For a repository that deliberately opts in, `dev-loop` takes a task from brief through branch creation, engineering gates, PR creation, independent review, and a protected merge to `main`.

## Build from a documented vision

The `idea-to-build` workflow turns your idea, vision, and named documentation into a reviewed build brief, compatible UX/UI and backend architecture, stable contracts, implementation, QA, and independent review.

## Go from idea to product

The `idea-to-product` workflow composes discovery, research, feasibility, product specification, UX/UI, architecture, implementation, QA, specialist review, and human approval.

Use the complete workflow or create a smaller Markdown workflow containing only the roles you need.

## Lightweight architecture

- Markdown agents and workflows
- Native Codex custom agents and skills
- Committed Codex/Python/Git/GitHub project profile
- Repository-scoped workflow skill
- Independent `agents` and `172x-agents` commands
- Optional `172x agents` ecosystem integration
- No workflow server, database, or bundled MCP service

[Get started](getting-started.md), browse the [agent catalog](agents.md), or read the [architecture](ARCHITECTURE.md).
