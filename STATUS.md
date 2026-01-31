# Scraps n' Bids — Project Status

## Project Overview

Scraps n' Bids is a single-page auction demo built for the PDD-Toolhouse-rtrvr-ElevenLabs hackathon. It simulates a live auction of 6 hardcoded unfinished meals with synthesized bidding, countdown timers, and winner announcements. The app is pure client-side (HTML/CSS/vanilla JS, zero dependencies) deployed as a single `index.html` on Vercel static hosting. The DOM uses stable IDs so it can be parsed by rtrvr.ai agents.

## Current State: Config-Only

The repository contains architecture definitions, PDD configuration, and deployment config — but **no generated application code**. The `index.html` that would contain the entire application has never been committed.

### What exists

- `architecture.json` — full module definitions for all 9 components
- `.pddrc` — PDD context configuration (9 contexts, all outputting to `index.html`)
- `vercel.json` — static deployment config (no build step, serves from root)
- `README.md` — project documentation
- `PROMPT_GENERATION_SUMMARY.md` — PDD generation log
- `architecture_diagram.html` — interactive dependency visualization
- `pdd_cost.csv` — cost tracking for PDD API calls
- `.github/workflows/pdd-secrets-dispatch.yml` — secrets encryption workflow

### What is missing

- **`index.html`** — the entire application (HTML structure, embedded CSS, embedded JS modules)

## The 404 Bug (GitHub Issue #3)

**Issue:** [Bug: Production deployment returns 404 — missing index.html](https://github.com/potable-anarchy/scraps-n-bids/issues/3)

The Vercel deployment is live but returns a 404 because there is no `index.html` in the repository. The `vercel.json` is configured correctly for static hosting — the only fix is to generate and commit the application code.

**Root cause:** `pdd generate` created the prompt files and config, but `pdd sync` was either never run or its output was never committed.

## PDD Cloud Credits Unavailable

The PDD cloud service credits ran out during development. To continue generating code from the prompts, PDD needs to be installed and run locally. The prompt files exist in the `prompts/` directory (gitignored) and need to be synced one module at a time in dependency order.

## The 9 Modules (Sync Order)

All modules output to a single `index.html`. They must be synced in this order to respect dependencies:

| Step | Module | Prompt File | Dependencies |
|------|--------|-------------|--------------|
| 1 | HTML Structure | `html_structure_HTML.prompt` | None |
| 2 | CSS Styles | `css_styles_CSS.prompt` | None |
| 3 | Meal Data | `meal_data_JavaScript.prompt` | None |
| 4 | Utility Helpers | `utility_helpers_JavaScript.prompt` | None |
| 5 | Auction State | `auction_state_JavaScript.prompt` | meal_data |
| 6 | Timer Module | `timer_module_JavaScript.prompt` | utility_helpers |
| 7 | Bidding Engine | `bidding_engine_JavaScript.prompt` | utility_helpers, auction_state |
| 8 | DOM Render | `dom_render_JavaScript.prompt` | utility_helpers, auction_state |
| 9 | Auction Lifecycle | `auction_lifecycle_JavaScript.prompt` | all 6 JS modules above |

Steps 1–4 have no dependencies and could theoretically be synced in parallel. Steps 5–8 depend on earlier modules. Step 9 depends on everything.

### Dependency Graph

```
html_structure ──────────────────────────────────┐
css_styles ──────────────────────────────────────┤
meal_data ──────────┬────────────────────────────┤
utility_helpers ──┬─┤────────────────────────────┤
                  │ └─→ auction_state ──┬────────┤
                  ├───→ timer_module ───┤────────┤
                  ├───→ bidding_engine ─┤────────┤
                  └───→ dom_render ─────┘────────┤
                                                 └─→ auction_lifecycle → index.html
```

## Next Steps

1. **Install PDD locally** — cloud credits are exhausted, so the CLI must run against a local or self-hosted LLM
2. **Generate/verify prompt files** — ensure all 9 `.prompt` files exist in `prompts/`
3. **Sync modules in order** — run `pdd sync` for each module following the dependency order above
4. **Verify `index.html`** — open locally in a browser, confirm auctions run end-to-end
5. **Commit `index.html`** — add the generated file to git
6. **Redeploy to Vercel** — push to main to trigger auto-deploy, or run `vercel --prod`
7. **Close issue #3** — verify production URL no longer returns 404

## Key Files Reference

| File | Purpose |
|------|---------|
| `.pddrc` | PDD module contexts — maps prompt file patterns to output paths |
| `architecture.json` | Full module specs (inputs, outputs, dependencies, constraints) |
| `vercel.json` | Vercel static deploy config (no build, serves root directory) |
| `pdd_cost.csv` | API cost tracking for PDD generate/sync calls |
| `prompts/` | Directory containing `.prompt` files (gitignored) |
