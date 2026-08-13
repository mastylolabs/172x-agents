# CLI contract

`agents` and `172x-agents` expose the same small command group. The optional, separately installed root CLI may load it as `172x agents`.

The CLI installs and diagnoses integrations; Codex coordinates workflow steps. It does not run an agent runtime, track runs, call model APIs, or store credentials.

## Supported profile

```text
agents install
agents install codex [python] [--gate TOOL]... [--only CAPABILITY_ID]...
```

Bare `agents install` asks the same questions interactively. `agents install codex python` also asks which gate tools to install unless `--gate TOOL` is repeated explicitly. The default is all supported Python tools. The only selectable implementation is:

| Concern | Supported now | Planned, not selectable |
| --- | --- | --- |
| Host | Codex | Claude, Gemini |
| Language | Python | C++, Java, C#, Rust |
| SCM | Git | — |
| Git remote provider | GitHub | GitLab, Bitbucket |
| Platform | macOS | Linux, Windows |

`agents capabilities` prints this status from the program. It never presents a planned capability as installed.

### Focused installation

Use repeatable `--only` values to install one or more bundled agent or workflow IDs:

```bash
agents install codex python --only principal-architect
agents install codex python --only principal-architect --only principal-engineer
agents install codex python --only dev-loop
```

The selected capability receives the required shared references, assets, and generated Codex files. A
selected workflow also receives its documented participating roles. Focused installation is additive:
existing managed capabilities remain unless a separate explicit managed refresh replaces them. Omit
`--only` to install the complete official 172X library.

The installer writes canonical Codex files plus the committed `172x.toml` profile. It is idempotent, supports `--target`, `--dry-run`, and `--force`, preserves unrelated content, and plans all owned-file writes before writing any of them. A changed `172x.toml` is a managed-file conflict and requires explicit `--force`.

```toml
[host]
id = "codex"

[language]
id = "python"

[scm]
id = "git"

[provider]
id = "github"

[gate]
tools = ["mypy", "ruff", "radon", "pytest"]

[change_request]
kind = "pull_request"
base_branch = "main"
merge_method = "squash"
merge_current_branch = true
```

Python gate choices are fixed tool IDs from the bundled profile: `mypy`, `ruff`, `radon`, and `pytest`. They map to safe argument-list commands; arbitrary shell commands are not configuration. The installer adds selected tools to an existing `uv` or Poetry project's development dependencies, then checks them. For an existing Python repository, 172X prefers `uv run`, `poetry run`, or `hatch run` when its usual lock/configuration is present, otherwise it uses the existing environment.

## Diagnostics

```text
agents doctor [--target PATH]
```

`doctor` is read-only. It checks the installed Markdown library, Codex integration, active workflow selection, macOS, Codex, Git and the Git remote, GitHub CLI/authentication/repository permission, and selected gate runner/tools. It reports reviewer identity as `CHECK`: a logically independent reviewer agent is not automatically a distinct eligible GitHub account.

## Library and workflows

```text
agents list [--target PATH]
agents domains
agents workflows [--target PATH]
agents show WORKFLOW_ID [--target PATH]
agents --workflow WORKFLOW_ID [--target PATH] [--no-launch]
```

`list` and `domains` read the bundled catalog. `workflows` and `show` also include validated project-owned workflow Markdown from `.172x/workflows/` when `--target` is supplied. Selecting either a bundled or project-owned workflow validates the committed profile and current Codex installation, writes `.172x/active-workflow`, and optionally launches the local `codex` executable with the matching direct native skill. It never installs or authenticates Codex.

## Project-owned workflow composition

Open `/skills` and select **172X · Workflow Composer** to design a workflow from the installed roles. It proposes the role selection, handoffs, feedback limits, and human gates before writing one project-owned Markdown file:

```text
.172x/workflows/<workflow-id>.md
```

The Composer uses the same scalar frontmatter and required workflow sections as the bundled library. It does not create an executor, activate the workflow, or run it. After approving a new or revised workflow, run:

```bash
agents workflows --target .
agents install codex python --force
```

The refresh validates the workflow against existing agent IDs and generates a native `/skills` entry. Project workflows are source files owned by the project; only their generated skill projections are 172X-managed.

### Codex CLI options

When launching a workflow, unknown root options are forwarded unchanged to the local Codex executable before the 172X workflow prompt. This keeps the wrapper current as Codex adds options:

```bash
agents --model gpt-5.4 --ask-for-approval never --workflow dev-loop
```

Use only options supported by your installed `codex --help`. `--yolo` is not an option in the current Codex CLI; its closest explicit equivalent is `--dangerously-bypass-approvals-and-sandbox`, which intentionally remains conspicuous because it removes Codex approval and sandbox protection.

## GitHub change-request guard

`dev-loop` is experimental and starts from a task, never a pull-request number. Codex discovers or creates the GitHub pull request as part of the workflow. The language in the workflow is provider-neutral—*change request*, *review*, and *merge*—but the implemented adapter translates those terms to GitHub pull requests. See [validation status](DEV_LOOP_VALIDATION.md) for observed coordination limits.

```text
agents github review-threads PR_NUMBER
agents github resolve-thread PR_NUMBER THREAD_ID
agents github gate PR_NUMBER
agents github merge PR_NUMBER
```

The first command is read-only. The last two use the selected GitHub profile and fail closed unless the pull request is open, non-draft, clean, targets `main`, has GitHub's `APPROVED` decision, has reported all-passing checks, and has no unresolved review threads. `merge` repeats that gate, pins the reviewed head commit, and uses only the configured normal merge method; it never sends `--admin` or `--auto`. A merge-queue acceptance is pending until GitHub reports the merged state.

`resolve-thread` is a narrow GitHub write: it verifies that the thread belongs to the named pull request. The workflow allows it only after independent review has verified the exact fix.

## Managed paths

```text
.agents/skills/172x-agents/**
.agents/skills/172x-*/**
.codex/agents/172x-*.toml
.172x/workflows/*.md
.172x/active-workflow
172x.toml
```

The Workflow Composer writes only the documented project-owned workflow source path after user approval. The installer never writes Codex configuration, credentials, or arbitrary project files.
