# 172X Agents

Markdown-first, composable AI-agent workflows for Codex.

172X Agents gives Codex a focused library of specialist roles and workflow playbooks. The host runs the agents; 172X defines how they collaborate.

## Start small

```bash
curl -fsSL https://forge.172x.ai/install.sh | sh
agents install codex
agents --workflow dev
```

The `dev` workflow coordinates independent Principal Engineer, QA Engineer, and PR Reviewer roles,
then stops for a human merge decision.

The only supported profile today is Codex + Python + Git + GitHub on macOS. The canonical library is
host-neutral, but Claude, Gemini, Rust, other languages, Linux, and Windows are planned—not
selectable.

For a repository that deliberately opts in, `dev-loop` takes a task through branch creation,
engineering gates, pull-request creation, independent review, and a guarded merge path. It remains
experimental; see [experimental status](DEV_LOOP_VALIDATION.md) before using it.

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

[Get started](getting-started.md), browse the [agent catalog](agents.md), or read the
[architecture](ARCHITECTURE.md).
