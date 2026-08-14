# Experimental status: `dev-loop`

`dev-loop` is experimental. It is a Codex-coordinated Markdown workflow, not a deterministic workflow engine.

## Observed limitation — 2026-08-12

An internal GitHub playground run passed environment diagnostics and successfully completed these
steps:

- created the feature branch, `feature/add-greet`;
- implemented and committed the greeting task;
- pushed the branch and opened a GitHub pull request.

The host then dispatched `brief` twice and later dispatched `qa` twice, followed by repeated waits
without a completed handoff. This is direct evidence that the current prompt-only coordinator does
not yet guarantee exactly-once delegation or reliable bounded completion.

The run was stopped before treating QA or review evidence as trustworthy. No merge occurred. The
visible recovery artifacts—the branch, commit, and pull request—remained available for inspection.

## Current rule

Do not claim that `dev-loop` is fully autonomous until repeated live tests show that it can:

1. dispatch every dependent role exactly once;
2. receive and preserve each required handoff;
3. enforce the two-review-return limit; and
4. safely resume or escalate after interruption.

172X records this failure rather than adding a workflow engine prematurely. The next investigation is whether supported Codex subagent controls can provide dependable stage completion; if not, the owner must decide whether deterministic coordination machinery is justified.
