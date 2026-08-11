---
id: dev-loop
name: Experimental Development Loop
description: Experimental brief-to-branch development, independent review, and protected merge to main.
version: 1
---
## Purpose
Exercise a task-to-merged-`main` loop under active human observation: establish a brief, normalize any existing clean non-main branch, create and develop a new branch, prove the active engineering gate, create and review a provider-neutral change request, then merge only after independent approval and the active provider gate. It is experimental until repeated live runs demonstrate that the host reliably honors the staged handoffs.

## Inputs
The user's task, repository instructions, relevant project context, and committed `172x.toml`. No change-request number is an input: the coordinator discovers or creates every change request needed by the loop.

## Participating agents
- `brief`
- `coding`
- `qa`
- `pr-review`

## Flow
1. Read `172x.toml` and validate the active host, language, SCM, provider, gate tools, and change-request policy before any work. `brief` converts the task and supplied context into a focused implementation brief with acceptance criteria, non-goals, risks, and the active engineering gate.
2. Normalize the workspace before changing it. Inspect the current branch and `git status --porcelain`. Treat the exact `.172x/active-workflow` file as 172X-generated local selection state, not user work: do not delete it and exclude only that exact path from the clean-tree decision. Any other changed or untracked path remains a blocker. If the branch is `main`, require the remaining tree to be clean and update it from its configured upstream. If it is any non-main branch, require the remaining tree to be clean, run the active engineering gate, push or create its change request as needed, and take that branch through the same independent QA, review, provider gate, and protected merge steps before continuing. Do not restrict this handling to 172X-named branches. If `merge_current_branch = false`, stop for user direction instead.
3. From the updated `main`, create a new descriptive task branch and give the implementation brief to `coding`.
4. `coding` implements the brief. It runs every tool selected in `[gate].tools` after each meaningful correction, using the repository's detected Python runner when applicable (`uv`, Poetry, Hatch, or the existing environment). A gate failure returns its exact output to `coding` for correction; it may not declare the implementation ready without every selected command passing.
5. Once the engineering gate passes, `coding` commits the scoped change, pushes the branch, and creates an open change request targeting `main`. The change-request body contains the brief summary, acceptance criteria, engineering-gate evidence, and risks. The coordinator records its identifier from the configured provider rather than asking the user for it.
6. `qa` independently reruns the active engineering gate and evaluates the brief's acceptance criteria on the change-request head. On PASS, `pr-review` independently inspects the diff, QA evidence, and current provider review threads.
7. `pr-review` publishes and labels every finding as `MF` (Must Fix), `NH` (Nice to Have), or `Q` (clarification needed). `MF` requires a correction. `NH` may be declined by `coding`, but the change request must contain the reason. `Q` requires an evidence-backed answer or user direction; it is not automatically a code-change request. No comment may be silently discarded.
8. On a return, `coding` addresses all `MF` findings, records any `NH` decision, answers each `Q`, reruns the active engineering gate, commits, and pushes the update. `qa` and `pr-review` inspect the updated change request before the next verdict. There may be at most two review-return trips in total; do not weaken a finding to avoid escalation.
9. When QA passes and PR Review has no unresolved `MF`, `NH`, or `Q`, PR Review submits an actual independent provider approval and resolves only review threads it has independently verified as addressed. A role-independent review subagent is not automatically a distinct provider identity: if branch rules require another eligible account, use the repository's already-configured reviewer bot or credential. It must not approve its own implementation or claim an external action that did not occur.
10. The coordinator invokes the configured provider gate and protected merge command for the created change request. The currently supported GitHub provider commands are `agents github gate <created-pr-number>` and `agents github merge <created-pr-number>`; merge repeats the live gate and requests a normal merge only for the checked head.

## Parallel work
Briefing, workspace normalization, coding, the engineering gate, QA, review, and merge are sequential because each depends on the preceding evidence. Independent QA and PR Review remain separate roles even when they inspect the same PR head.

## Feedback loops
Engineering-gate failures return only their reproducible command output to `coding` until the gate passes or a real environment blocker is identified. QA FAIL, `MF`, unresolved `Q`, or a review request that needs a code change returns structured evidence to `coding`. Count review-return trips in the coordinating session; stop after two. An `NH` decline is permitted only with a recorded reason and independent reviewer acceptance.

## Human gates
Committing `172x.toml` is the repository owner's explicit authorization for the configured dev-loop Git/GitHub actions. `merge_current_branch` defaults to `true`, so a clean generic non-main branch is handled autonomously. Set it to `false` when the owner wants the coordinator to stop and ask before normalizing the current branch. The coordinator must still stop for user direction when the workspace is dirty, `main` cannot be updated safely, a `Q` requires a product decision, an external command cannot run, or the two-review-trip limit is reached.

## Completion criteria
The current branch has been normalized or explicitly deferred, the task brief has evidence-backed acceptance criteria, the new branch's active engineering gate passes, its change request is created and targets `main`, QA returns PASS, PR Review records no unresolved finding, an actual independent provider approval exists, all review threads are resolved, the live provider gate passes, and the provider confirms the change request is merged into `main`. A merge-queue acceptance is pending, not completion.

## Failure and escalation
Never commit unknown dirty work, bypass branch protection, use administrator merge, enable auto-merge, merge a different change-request head, or pretend a queued change request has merged. If the configured provider CLI is unavailable or unauthenticated, no eligible reviewer identity exists for the repository's rules, selected gate tools cannot run, the current branch cannot safely normalize, any gate fails, a Q needs the user, or review returns exceed two, report the branch, change request, commands, findings, and exact blocker to the user.
