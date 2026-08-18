# 172X Agents

Markdown-first, composable AI-agent workflows for Codex.

172X Agents gives coding-agent hosts a focused library of specialists and workflow playbooks—from
idea discovery and architecture through implementation, QA, review, and a human decision. Codex is
the runtime and coordinator; 172X defines the roles, handoffs, evidence, and boundaries.

## Install

Install the latest stable standalone CLI; Python, `pip`, and `pipx` are not required:

```bash
curl -fsSL https://forge.172x.ai/install.sh | sh
```

On Windows, save and inspect the PowerShell installer before running it:

```powershell
irm https://forge.172x.ai/install.ps1 | iex
```

See the [distribution contract](docs/DISTRIBUTION.md) for release assets, checksum verification,
and pinned installation.

Install Forge capabilities once for Codex. This is personal, global installation; it does not
select a language or modify a project:

```bash
agents install codex
```

To install only the capabilities you want available in Codex:

```bash
agents install codex --only principal-architect --only principal-engineer
agents install codex --only dev-loop
```

The full library remains the default. A focused workflow includes its participating specialists;
a focused specialist includes its required shared material. Forge writes only its namespaced skills
under your Codex home and never edits `.codex/config.toml`.

Remove every global Forge skill later with:

```bash
agents uninstall codex
```

Use `--only CAPABILITY_ID` for one direct capability or `--dry-run` to inspect the removal plan.

Inside a project, optionally record the local quality contract that Forge should verify:

```bash
agents activate python
agents doctor
```

Activation asks for expected gate tools and stores them only in ignored `.172x/contexts.toml`.
172X Agents never installs, upgrades, removes, or selects external development tools or package
managers. In a monorepo, activate an explicit package path from the repository root:

```bash
agents activate python --path services/api
```

## What is supported today

The canonical Markdown library is designed to project into native host formats. The implemented
activation and diagnostic support is deliberately narrower:

| Concern | Supported now | Planned, not selectable |
| --- | --- | --- |
| Host | Codex | Claude, Gemini |
| Language | Python | Rust, C++, Java, C# |
| Source control | Git + GitHub | GitLab, Bitbucket |
| Platform | macOS | Linux, Windows |

`agents capabilities` reports the same distinction. 172X never presents a planned integration as
installed or working.

## Workflows, not another runtime

172X ships focused, operational roles such as Principal Architect, Principal Engineer, QA Engineer,
Security Reviewer, and Product Specification Specialist. It composes them into four workflows:

- `dev` — implementation, independent QA, review, and a human merge decision.
- `dev-loop` — an experimental opt-in loop that can create a branch and pull request, then use the
  guarded GitHub merge path only after independent approval and recorded checks pass.
- `idea-to-build` — turns documented vision into reviewed design, architecture, implementation, and
  verification.
- `idea-to-product` — adds discovery, research, feasibility, and product specification before the
  build path.

The project intentionally does not include a workflow engine, database, scheduler, provider API
client, hosted service, or bundled MCP server.

## Use with Codex

The installer creates global Codex skills. In an existing Codex session, open `/skills` and select
an entry such as **172X · Dev**, **172X · Principal Architect**, or **172X · QA Engineer**. The
optional catalog skill also supports text selection:

```text
$172x run dev
$172x use idea-to-build
```

`dev-loop` remains experimental. It has a concrete, fail-closed GitHub guard but requires further
live validation before it can be treated as fully autonomous. Read the
[experimental status](docs/DEV_LOOP_VALIDATION.md) before opting in.

## Documentation

- [Getting started](docs/getting-started.md)
- [Agent catalog](docs/agents.md)
- [Architecture](docs/ARCHITECTURE.md)
- [CLI contract](docs/CLI.md)
- [Codex integration](docs/CODEX_INTEGRATION.md)
- [Distribution](docs/DISTRIBUTION.md)
- [Experimental status](docs/DEV_LOOP_VALIDATION.md)

## Contributing and governance

172X Agents is distributed under the [MIT License](LICENSE.md). Read
[CONTRIBUTING.md](CONTRIBUTING.md), follow the [Code of Conduct](CODE_OF_CONDUCT.md), report
vulnerabilities through the private process in [SECURITY.md](SECURITY.md), and see
[TRADEMARKS.md](TRADEMARKS.md) for brand-use terms.

Maintainers use the manual, approval-gated [release procedure](RELEASING.md). GitHub Releases are
the primary distribution path; the optional PyPI workflow is manual and never runs on a pull
request or a merge to `main`.
