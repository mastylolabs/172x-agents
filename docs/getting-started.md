# Getting started

## Install the CLI

```bash
pipx install .
```

For repository development:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev,docs]"
```

## Prepare a project

From the GitHub repository that Codex will work on, run the guided installer:

```bash
agents install
```

Or accept the supported explicit profile:

```bash
agents install codex python
```

The installer asks which gate tools to add, defaulting to `mypy`, `ruff`, `radon`, and `pytest`; it adds the selected known tools through the repository's `uv` or Poetry project convention. For a preview that writes nothing, add `--dry-run`. Installation writes a committed `172x.toml` plus project-scoped Codex skills and custom agents. Today the supported profile is Codex + Python + Git + GitHub on macOS; use `agents capabilities` to see planned contribution targets.

Run a read-only readiness check before a workflow:

```bash
agents doctor
```

It reports missing executables, Git/GitHub prerequisites, profile gate tools, and the independent-reviewer identity requirement.

## Pick a workflow

For human-controlled development:

```bash
agents --workflow dev
```

For a documented idea that needs UX/UI and backend work:

```bash
agents --workflow idea-to-build
```

For the experimental autonomous coding cycle:

```bash
agents --workflow dev-loop
```

`dev-loop` takes your task, makes a Brief Author handoff, normalizes a clean current non-main branch when the profile permits it, creates a new task branch, runs the selected engineering gate, opens its own GitHub pull request, gets independent QA/review, addresses Must Fix findings, and merges only after the live GitHub gate passes. It does not ask for a pull-request number. It is experimental until repeated live runs demonstrate reliable stage handoffs; see [validation status](DEV_LOOP_VALIDATION.md).

The reviewer labels findings `MF` (Must Fix), `NH` (Nice to Have), or `Q` (clarification). Principal Engineer must fix MF; it may decline NH with an explanation in the pull request; Q needs an answer or user direction. The workflow stops after two review-return trips instead of spinning forever.

## Existing Codex session

In an already-open Codex session, open `/skills` and select a direct 172X entry such as **172X · Dev Loop**, **172X · Brief Author**, or **172X · Principal Architect**. The native picker scrolls and activates the selected workflow or specialist for the current task.

The optional catalog skill remains available for text browsing:

```text
$172x run dev-loop
```

Use `$172x use idea-to-build` to select the next workflow. `$172x list` shows the installed workflows and specialist-agent catalog. `/workflow` is not a native Codex command.

## Compose a project workflow

Select **172X · Workflow Composer** from `/skills` when the bundled workflows do not fit. It proposes a workflow using only installed roles and waits for approval before writing `.172x/workflows/<workflow-id>.md`. Then validate and add the native picker entry:

```bash
agents workflows --target .
agents install codex python --force
```
