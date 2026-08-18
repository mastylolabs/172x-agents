# 172X Agents

Markdown-first, composable AI-agent workflows for Codex.

172X Agents gives Codex a focused library of specialist roles and workflow playbooks. The host runs the agents; 172X defines how they collaborate.

## Start small

```bash
curl -fsSL https://forge.172x.ai/install.sh | sh
agents install codex
agents activate python
agents --workflow dev
```

Windows users can use the pinned PowerShell installer:

```powershell
irm https://forge.172x.ai/install.ps1 | iex
```

The `dev` workflow coordinates independent Principal Engineer, QA Engineer, and PR Reviewer roles,
then stops for a human merge decision.

Forge installation is global and language-neutral. Python is the only supported local activation
profile today; Claude, Gemini, Rust, other languages, Linux, and Windows are planned—not
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
- Global namespaced Codex skills
- Ignored local language and gate activation state
- Advisory `doctor` checks that never install external tools
- Independent `agents` and `172x-agents` commands
- Optional `172x agents` ecosystem integration
- No workflow server, database, or bundled MCP service

[Get started](getting-started.md), browse the [agent catalog](agents.md), or read the
[architecture](ARCHITECTURE.md).
