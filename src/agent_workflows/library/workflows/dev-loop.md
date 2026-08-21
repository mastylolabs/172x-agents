---
id: dev-loop
name: Experimental Development Loop
description: Experimental brief-to-branch development, independent review, and guarded merge to main.
version: 2
---
## Purpose
Exercise a task-to-merged-`main` loop under active human observation: establish a brief, normalize any existing clean non-main branch, create and develop a new branch, prove the active engineering gate, create and review a provider-neutral change request, then merge only after independent approval and the active provider gate. It is experimental until repeated live runs demonstrate that the host reliably honors the staged handoffs. The current prompt-only coordinator does not yet guarantee exactly-once delegation or reliable bounded completion.

## Inputs
The user's task, repository instructions, relevant project context, the matching local
`.172x/contexts.toml` activation entry, and the local Git metadata provider configuration. No change-request number is an input: the coordinator discovers or creates every change request needed by the loop.

## Provider review prerequisites
`dev-loop` is the guarded, end-to-end path, so it requires a selected source-control provider,
explicit merge policy, and provider-owned reviewer mapping before delegation. Run `agents activate
python` to create `.git/172x/config.toml` interactively. For the implemented GitHub adapter, it has
this shape:

```toml
[provider]
family = "source_control"
name = "github"

[merge]
base_branch = "main"
method = "squash"

[github.review]

[[github.review.reviewers]]
login = "172x-reviewer-bot"
token_env = "REVIEWER_GH_TOKEN"
```

Export each configured token in the environment used for the run; never put token values in the
repository or Git metadata. The reviewer list is authoritative—there is no separate reviewer-count setting, and
every listed identity must be able to access the repository and approve the exact pull-request
head. This is one-time project setup, not a per-run prompt. A missing mapping, unset token, login
mismatch, or inaccessible repository is a fail-closed blocker before provider review or merge.

The standalone `pr-reviewer` can still perform a local review without this mapping. Its local
`APPROVED` result is only a recommendation; `dev-loop` cannot publish an independent provider
review, submit provider approval, or pass its guarded merge gate until the mapping, credentials,
and selected provider capabilities are valid.

## Participating agents
- `brief-author`
- `principal-engineer`
- `qa-engineer`
- `pr-reviewer`

## Flow
1. Read the matching local `.172x/contexts.toml` activation entry and local Git metadata reviewer
configuration, then validate the active language, expected gate tools, and configured reviewer
credentials before any work. `brief-author` converts the task and supplied context into one
identified focused brief with source/evidence state, acceptance criteria, non-goals, assumptions,
unresolved decisions, risks, and the active engineering gate.
2. Normalize the workspace before changing it. Inspect the current branch and `git status --porcelain`. Treat the exact `.172x/active-workflow` file as 172X-generated local selection state, not user work: do not delete it and exclude only that exact path from the clean-tree decision. Any other changed or untracked path remains a blocker. If the branch is `main`, require the remaining tree to be clean and update it from its configured upstream. If it is any non-main branch, require the remaining tree to be clean, run the active engineering gate, push or create its change request as needed, and take that branch through the same independent QA, review, provider gate, and guarded merge steps before continuing. Do not restrict this handling to 172X-named branches. If `merge_current_branch = false`, stop for user direction instead.
3. From the updated `main`, create a new descriptive task branch and give the identical implementation brief and complete handoff envelope to `principal-engineer`.
4. `principal-engineer` implements the brief. It runs every tool selected in the active local context after each meaningful correction, using the repository's existing environment when applicable. 172X never installs, upgrades, removes, or selects those external tools. A gate failure returns its exact output to `principal-engineer` for correction; it may not declare the implementation ready without every selected command passing. Its handoff identifies the artifact, criteria status, evidence and limits, assumptions, unresolved decisions, and residual risks.
5. Once the engineering gate passes, `principal-engineer` commits the scoped change, pushes the branch, and creates an open change request targeting `main`. The change-request body contains the brief summary, acceptance criteria, engineering-gate evidence, and risks. The coordinator records its identifier from the configured provider rather than asking the user for it.
6. `qa-engineer` independently reruns the active engineering gate and evaluates the brief's acceptance criteria on the change-request head using `assets/quality/qa-report-template.md`. On PASS, `pr-reviewer` independently inspects that same head, diff, implementation handoff, QA report, and current provider review threads using `assets/quality/review-report-template.md`.
7. `pr-reviewer` publishes and labels every finding as `MF` (Must Fix), `NH` (Nice to Have), or `Q` (clarification needed). `MF` requires a correction. `NH` may be declined by `principal-engineer`, but the change request must contain the reason. `Q` requires an evidence-backed answer or user direction; it is not automatically a code-change request. No comment may be silently discarded.
8. On a return, `principal-engineer` addresses all `MF` findings, records any `NH` decision, answers each `Q`, reruns the active engineering gate, commits, and pushes the update. `qa-engineer` and `pr-reviewer` inspect the updated change request before the next verdict. There may be at most two review-return trips in total; do not weaken a finding to avoid escalation.
9. When QA passes and PR Review has no unresolved `MF`, `NH`, or `Q`, PR Review writes the versioned review report, publishes it through the selected provider adapter, and only then submits an actual independent provider approval for the exact current head. The provider-specific reviewer list is the source of truth; every listed reviewer must act with its own `token_env` credential. Resolve only review threads independently verified as addressed. A role-independent review subagent is not automatically a distinct provider identity, and no reviewer may approve its own implementation or claim an external action that did not occur. The current GitHub adapter exposes these actions as `agents github review` and `agents github approve`.
10. The coordinator invokes the selected provider's gate and guarded merge operation for the created change request. The current GitHub adapter exposes `agents github gate <created-pr-number>` and `agents github merge <created-pr-number>`; merge repeats the live policy-compatibility gate and requests the configured method only for the checked head. It does not create, change, weaken, or bypass repository branch rules.

## Parallel work
Briefing, workspace normalization, coding, the engineering gate, QA, review, and merge are sequential because each depends on the preceding evidence. Independent QA and PR Review remain separate roles even when they inspect the same PR head.

## Feedback loops
Engineering-gate failures return only their reproducible command output to `principal-engineer` until the gate passes or a real environment blocker is identified. QA FAIL, `MF`, unresolved `Q`, or a review request that needs a code change returns structured evidence to `principal-engineer`. Count review-return trips in the coordinating session; stop after two. An `NH` decline is permitted only with a recorded reason and independent reviewer acceptance.

## Human gates
The developer explicitly activates the current project locally before using the configured dev-loop
Git and provider actions. A clean generic non-main branch is handled only after the active context's
gate passes. The coordinator must still stop for user direction when the workspace is dirty, `main`
cannot be updated safely, a `Q` requires a product decision, an external command cannot run, or the
two-review-trip limit is reached.

## Completion criteria
The current branch has been normalized or explicitly deferred, the task brief has evidence-backed acceptance criteria, the new branch's active engineering gate passes, its change request is created and targets `main`, QA returns PASS, PR Review records no unresolved finding, an actual independent provider approval exists, all review threads are resolved, the live provider gate passes, and the provider confirms the change request is merged into `main`. A merge-queue acceptance is pending, not completion.

## Failure and escalation
Never commit unknown dirty work, bypass branch protection, use administrator merge, enable auto-merge, merge a different change-request head, or pretend a queued change request has merged. If the configured provider CLI is unavailable or unauthenticated, no eligible reviewer identity exists for the repository's rules, selected gate tools cannot run, the current branch cannot safely normalize, any gate fails, a Q needs the user, or review returns exceed two, report the branch, change request, commands, findings, and exact blocker to the user.
