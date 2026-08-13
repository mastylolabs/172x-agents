# Testing strategy

Choose evidence in proportion to risk and change scope.

- Map every acceptance criterion to a check, direct inspection, or explicit coverage limit.
- Prefer focused checks first, then the repository's required gate.
- Test meaningful success, failure, authorization, integration, and regression paths.
- Report commands and observed results exactly; a command that did not run is a coverage limit.
- A PASS means the applicable criteria have evidence, not merely that one test command passed.
