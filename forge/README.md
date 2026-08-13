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
python ../scripts/generate_forge_catalog.py
```

## Build

```bash
npm run build
```

The app uses React, TypeScript, Tailwind CSS, and static client-side search. It has no accounts,
database, API, telemetry, or hosted agent execution.

## Cloudflare Pages

Forge is ready to deploy as a static Cloudflare Pages project. Configure the connected repository
with these settings:

| Setting | Value |
| --- | --- |
| Production branch | `main` |
| Root directory | `forge` |
| Build command | `npm ci && npm run build` |
| Build output directory | `dist` |
| Node.js version | `22` |
| Python version | `3.12` or later |

The build generates the catalog directly from the canonical Markdown library with standard Python;
it does not require `uv`. Once connected, Cloudflare Pages can publish commits to `main` and create
preview deployments for pull requests. No Forge deployment, custom domain, or DNS change is made by
this repository configuration.
