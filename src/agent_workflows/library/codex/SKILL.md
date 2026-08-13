---
name: 172x
description: Browse and run 172X workflows with specialist Codex agents for discovery, architecture, implementation, QA, review, and human approval.
---

# 172X Agents

Use this catalog skill for an explicit request such as `$172x list`, `$172x run dev`, `$172x use idea-to-product`, or `$172x show workflow dev`. For the fastest native selection, use `/skills` and choose a dedicated `172X · …` workflow or specialist skill instead.

## Commands

- `list`: Read the installed references and show two compact catalogs: workflows (ID, name, description) and agents (ID, name, description). Do not delegate work.
- `list workflows` or `list agents`: Show only the named catalog. Do not delegate work.
- `show workflow <id>`: Summarize the workflow stages, participating agents, feedback limits, human gates, and completion criteria without starting it.
- `show agent <id>`: Summarize that agent's mission, use-when guidance, deliverables, handoff recipient, and boundaries without delegating it.
- `run <workflow>`: Find the reference with the matching workflow ID under `references/workflows/` (including `custom/`) and read it completely. If a task or idea is missing, ask for it before delegation.
- `use <workflow>`: Confirm the selected workflow for the next run. Do not change work already delegated.

Treat `list` as the catalog home. Its final line must say: `Run a workflow with: $172x run <workflow-id>`. Do not present agent IDs as commands a user should invoke directly; they are specialist subagents selected by a workflow coordinator.

If no workflow is named explicitly, the project-root `.172x/active-workflow` is advisory only. Use it only when it contains a known ID; otherwise ask the user to choose.

## Coordination rules

1. Read the complete selected workflow before delegating. Read the complete relevant role definition under `references/agents/` before constructing a specialist task.
2. Preserve the original request, repository instructions, constraints, and acceptance criteria in each relevant handoff.
3. Delegate bounded work to the matching 172X custom agent. Keep implementation, QA, and review independent; an implementation agent must not approve its own work.
4. Dispatch exactly one active delegation for each logical role and workflow stage. Before delegating the same role again, confirm its prior handoff is complete and name the evidence requiring a revision. Never create duplicate agent calls merely because a prior call is still running or a wait returned no result.
5. Run independent workflow branches in parallel only when their upstream inputs are stable. Wait for required handoffs before dependent work.
5. Require the following handoff shape from every specialist:

   ```markdown
   ## Result
   <deliverable or verdict>

   ## Evidence
   - <files, commands, observations, sources, or artifacts>

   ## Acceptance criteria
   - [x] <satisfied criterion>
   - [ ] <unsatisfied criterion and reason>

   ## Risks and open questions
   - <remaining uncertainty>

   ## Recommended next step
   <receiving agent or human action>
   ```

6. Count feedback cycles only in this coordinating session. For `dev`, a QA or PR Review return to Coding consumes one cycle; stop after three without approval and ask the user what to do. For `dev-loop`, count only QA/Review returns after a PR exists; stop after two review-return trips without weakening a finding.
7. Stop at every workflow human gate and wait for a decision. Never silently omit a required stage or weaken acceptance criteria after failure.
8. Describe recommendations as recommendations. Never invent tests, research, GitHub actions, notifications, approvals, merges, releases, deployments, durable state, or a 172X MCP tool.
9. If a session boundary interrupts work, explain that continuity and feedback counting cannot be guaranteed; use project artifacts and user direction to resume.

## Workflow-specific reminders

For `dev`, Principal Engineer hands off to QA Engineer, QA Engineer returns PASS or reproducible FAIL evidence, and PR Reviewer returns APPROVED or CHANGES_REQUESTED. APPROVED is only a local recommendation; the user decides whether to merge.

For `dev-loop`, read its workflow and committed `172x.toml` completely before acting. Do not ask for a change-request number. Dispatch exactly one `brief-author` agent first, including the user task, repository observations, and active gate. Wait for its complete structured handoff, summarize the accepted brief in the coordinator response, and only then inspect or normalize the branch. Do not dispatch a second `brief-author` agent unless a documented review return requires a revised brief. Treat exactly `.172x/active-workflow` as generated local selection state and exclude it from a clean-tree decision; do not delete it. Any other uncommitted or untracked path remains a blocker. Handle any clean non-main branch through its own active gate, change request, independent review, and merge before creating the task branch when `[change_request].merge_current_branch` permits it. Do not commit a dirty workspace. Create the task branch from updated main in the current repository checkout; Principal Engineer owns the implementation, selected gate, scoped commit, push, and change-request creation. Run the named `[gate].tools` from the active language profile, using the repository's detected Python runner (`uv`, Poetry, Hatch, or existing environment) when applicable.

For the dev-loop change request, QA Engineer and PR Reviewer remain independent. PR Reviewer labels every finding `MF`, `NH`, or `Q`; Principal Engineer must fix MF, may decline NH with a recorded reason, and must answer Q or ask the user when it needs a product decision. PR Reviewer publishes findings through the active provider and may resolve a review thread only after independently verifying the exact fix. After all findings are resolved, it submits an actual independent provider approval. With the supported GitHub provider, obtain the PR number from GitHub, run `agents github gate <pr-number>`, and run `agents github merge <pr-number>`. Do not use raw `gh pr merge`, `--admin`, `--auto`, or any bypass. The merge command rechecks the live GitHub gate and pins the checked head commit. Report completion only when GitHub confirms MERGED; a merge queue is pending, not completed.

For `idea-to-product`, perform discovery before research branches, stop for human validation after research and feasibility, stabilize UX/backend contracts before implementation, run QA before specialist reviews, and stop for human approval after PR Review synthesis.

For `idea-to-build`, the Brief Author reads all named source materials before UX/UI Design and Principal Architecture run in parallel. The Design and Architecture Reviewer returns READY, REVISE, or BLOCKED; the human must approve READY artifacts before implementation begins.
