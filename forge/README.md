# 172X Forge

The static Forge catalog for `forge.172x.ai`.

Forge is generated from the canonical agent and workflow Markdown in the parent repository. It is a
discovery and installation surface, not a second prompt library or workflow runtime.

## Run locally

```bash
npm install
npm run dev
```

Open `http://127.0.0.1:4173`.

`npm run dev` and `npm run build` first run the canonical catalog generator. The generated JSON is
intentionally ignored because it is a build artifact:

```bash
uv run python scripts/generate_forge_catalog.py
```

## Build

```bash
npm run build
```

The app uses React, TypeScript, Tailwind CSS, and static client-side search. It has no accounts,
database, API, telemetry, or hosted agent execution.
