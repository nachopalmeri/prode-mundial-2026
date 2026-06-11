# Dynamic Prode Engine Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a dynamic World Cup 2026 prediction engine that outputs top-3 scorelines per match with probabilities, recalculates pending matches, and feeds a premium visual dashboard.

**Architecture:** Keep the existing static HTML as the delivery surface, but move prediction logic into Python-generated JSON artifacts. The engine computes calibrated scoreline distributions from market/ratings/source consensus proxies, then the HTML consumes `data/model/latest_predictions.json` for top-3 outcomes and confidence visuals.

**Tech Stack:** Python standard library, static HTML/CSS/JS, GitHub Actions cron, JSON artifacts. No new external dependencies in this iteration.

---

## File Structure

- Create `scripts/predictive_engine.py`: probabilistic scoreline engine, source aggregation, Poisson matrix, top-3 picks, freeze metadata.
- Create `data/config/team_strengths.json`: editable team priors for Elo/FIFA/market/locality/style placeholders.
- Create `data/runtime/results.json`: current real results and freeze overrides, initially empty.
- Create `data/model/latest_predictions.json`: generated artifact consumed by UI.
- Create `scripts/update_dynamic_dashboard.py`: inject generated JSON and dashboard UI into HTML safely.
- Modify `scripts/prode_core.py`: expose match metadata and validation helpers used by engine.
- Modify `prode-mundial-2026.html`: add visual top-3 cards, probability bars, status metadata, and consume dynamic predictions.
- Modify `.github/workflows/auto-improve.yml`: run validation + prediction refresh on schedule and manual dispatch.
- Modify `scripts/validate_html.py`: assert dynamic artifact and top-3 UI wiring.

## Chunk 1: Prediction Data Model

### Task 1: Add team priors

**Files:**
- Create: `data/config/team_strengths.json`

- [ ] Add one object per team with `elo`, `fifa_rank`, `market_value_m`, `home_boost`, `attack`, `defense`, `form`, `style_tempo`, `injury_penalty`.
- [ ] Keep priors explicit and editable; use conservative defaults where real data is missing.
- [ ] Validate every team in the HTML has a prior.

### Task 2: Add runtime state

**Files:**
- Create: `data/runtime/results.json`

- [ ] Store `results`, `frozen_matches`, `last_updated`, and `notes`.
- [ ] Leave results empty initially.
- [ ] Use this file as the future GitHub Action input for played matches/news.

## Chunk 2: Prediction Engine

### Task 3: Implement top-3 score engine

**Files:**
- Create: `scripts/predictive_engine.py`
- Modify: `scripts/prode_core.py`

- [ ] Load matches from HTML.
- [ ] Load team priors and runtime state.
- [ ] Convert source scores into implied goals and 1X2 priors.
- [ ] Blend priors with weights: market/source consensus, Elo/FIFA, market value, locality, attack/defense, form, injuries.
- [ ] Generate a Poisson score matrix from 0-0 through 6-6.
- [ ] Recalibrate matrix toward source consensus and normalize to 100%.
- [ ] Emit top-3 scorelines, 1X2 probabilities, expected goals, confidence, movement placeholder, freeze status.

### Task 4: Generate latest predictions artifact

**Files:**
- Create: `data/model/latest_predictions.json`

- [ ] Run `python scripts/predictive_engine.py`.
- [ ] Verify 72 matches and 3 scorelines per match.
- [ ] Include metadata with generated timestamp and model version.

## Chunk 3: Visual Dashboard

### Task 5: Add dynamic top-3 UI

**Files:**
- Modify: `prode-mundial-2026.html`
- Create/Modify: `scripts/update_dynamic_dashboard.py`

- [ ] Add embedded `DYNAMIC_PREDICTIONS` JSON block.
- [ ] Add `renderDynamicTop3()` and call it from `init()`.
- [ ] Add a visual section with match cards, top-3 probabilities, confidence, freeze status, and source mix.
- [ ] Preserve existing comparison/final/prode tabs.

### Task 6: Make UI feel premium and usable

**Files:**
- Modify: `prode-mundial-2026.html`

- [ ] Use an editorial sports-betting visual direction: clean, high contrast, probability bars, clear current action.
- [ ] Make top-3 cards scannable on mobile.
- [ ] Avoid long explanations; show signals compactly.

## Chunk 4: Automation and Validation

### Task 7: Update automation

**Files:**
- Modify: `.github/workflows/auto-improve.yml`

- [ ] Run prediction engine.
- [ ] Inject dashboard JSON.
- [ ] Validate HTML.
- [ ] Commit generated artifacts only when changed.

### Task 8: Expand validation

**Files:**
- Modify: `scripts/validate_html.py`

- [ ] Validate latest predictions exists.
- [ ] Validate 72 matches, each with exactly 3 top scorelines.
- [ ] Validate probabilities are numeric and sorted descending.
- [ ] Validate UI has dynamic renderer.

## Validation Commands

- `python scripts\predictive_engine.py`
- `python scripts\update_dynamic_dashboard.py`
- `python scripts\validate_html.py`
- `python -m compileall scripts`
- `git diff --stat`

## Exit Criteria

- 72 matches have top-3 scoreline predictions with probabilities.
- HTML renders the new dynamic dashboard from generated JSON.
- GitHub Action can refresh artifacts without secrets.
- Existing prode output still works.
- Validation catches missing/sorted/coverage errors.
