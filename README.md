# Prode Mundial 2026

Multi-source AI prediction system for the 2026 FIFA World Cup. Aggregates 10 prediction sources using a weighted consensus + Poisson engine to generate probabilistic scoreline predictions for all 104 matches (72 group + 32 knockout). Includes Monte Carlo group simulation, prode value optimization, Elo post-match updates, and a static HTML dashboard deployed on Vercel.

## Features

- **10 prediction sources** — Cascade, ChatGPT, Gemini, Fansided, ESPN, Yahoo, 1960Tips, ELO Model, Cup26 AI, Polymarket
- **Poisson score matrix** — 7×7 probability matrix with dynamic draw inflation calibrated from real results
- **Monte Carlo group simulation** — 10,000 Poisson simulations per group for qualification probabilities (winner %, runner-up %, qualify %)
- **Value Pick Engine** — optimizes score picks for prode pools of N players (3 pts exacto, 1 pt ganador): `V = [P(exacto)*3 + P(ganador)*1] * (1 - consensus * (1 - 1/pool_size))`
- **Match motivation profiling** — contextual adjustments for must-win, draw-acceptable, qualification-pressure, and rotation scenarios
- **Source accuracy tracking** — per-source exact and winner accuracy with time decay and sample-factor confidence
- **Weight recalibration** — automatic weight adjustment based on historical accuracy, bias, and systematic draw under-prediction
- **Elo post-match updates** — `update_elo_from_result()` adjusts team strengths after each played match
- **Draw rate targeting** — dynamic base_inflation calibration via grid search that minimizes Brier score against real outcomes
- **CI auto-recalibration** — GitHub Actions pipeline runs prediction → dashboard update → recalibration daily
- **12-group knockout bracket** — automatic bracket propagation from group winners/runners-up + best third-placed teams

## Tech Stack

- **Frontend:** Static HTML + vanilla JS (no framework), Chart.js for dashboard charts
- **Backend/ML:** Python 3.12 + NumPy, Poisson statistics
- **Data:** JSON (team strengths, predictions, weights, draw inflation config)
- **Automation:** GitHub Actions (cron daily at 12:00 UTC)
- **Deploy:** Vercel (static export)

## Architecture

```
                    ┌──────────────────┐
                    │  sources/*.json  │  ← 10 AI/ML prediction files
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ predictive_engine │  ← Poisson matrix + MC + value picks
                    │   .py            │     + draw inflation + knockout bracket
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ update_dynamic_  │  ← embeds results, accuracy, standings
                    │ dashboard.py     │     into HTML + Elo updates
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │  recalibrate.py  │  ← weight adjustment + draw calibration
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │ prode-mundial-   │  ← static HTML deployed to Vercel
                    │ 2026.html        │
                    └──────────────────┘
```

Pipeline model: each run is stateless — scripts read JSON configs, produce JSON + embed into HTML, commit and push. No live backend.

## Project Structure

```
├── data/
│   ├── config/
│   │   ├── team_strengths.json    # Team priors (Elo, FIFA rank, form, injuries)
│   │   ├── wc_history.json        # Historical WC performance data
│   │   ├── h2h_matches.json       # Head-to-head records
│   │   └── matches.json           # 2026 WC match schedule with sources
│   ├── model/
│   │   ├── latest_predictions.json # Current model output (104 matches + KO bracket)
│   │   ├── weights_latest.json    # Per-source weights + accuracy report
│   │   ├── source_bias.json       # Goal bias correction per source
│   │   └── draw_inflation.json    # Calibrated draw inflation base
│   └── runtime/
│       ├── results.json           # Live match results from ESPN
│       └── results_order.json     # Chronological order for time decay
├── scripts/
│   ├── predictive_engine.py       # Core: score matrix, MC, value picks, KO bracket
│   ├── prode_core.py              # Shared types, loaders, consensus scoring
│   ├── sports_source.py           # Elo model, team priors, form, WC history
│   ├── update_dynamic_dashboard.py # Dashboard HTML injection + Elo updates
│   ├── recalibrate.py             # Weight adjustment + draw inflation calibration
│   ├── fetch_results.py           # Fetch live scores from ESPN (optional)
│   └── enter_results.py          # Manual result entry interface
├── prode-mundial-2026.html        # Main dashboard (single-file static HTML)
├── .github/workflows/
│   ├── daily_update.yml           # Scheduled daily pipeline
│   └── manual_update.yml          # Manual trigger (workflow_dispatch)
├── vercel.json                    # Vercel static deploy config
└── requirements.txt               # Python dependencies
```

## Setup

1. Clone the repo
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run the prediction engine: `python scripts/predictive_engine.py`
4. Update the dashboard: `python scripts/update_dynamic_dashboard.py`
5. Recalibrate weights (after results): `python scripts/recalibrate.py`

The pipeline runs automatically via GitHub Actions daily at 12:00 UTC.

## Prediction Sources

| Source | Key | Description |
|---|---|---|
| Cascade | c | Multi-step reasoning AI |
| ChatGPT | g | GPT-4o predictions |
| Gemini | f | Gemini 2.5 Pro |
| Fansided | fs | Sports media picks |
| ESPN | esp | ESPN FC predictions |
| Yahoo | yh | Yahoo Sports |
| 1960Tips | tips | Football tipster site |
| ELO Model | e | Statistical Elo-based model |
| Cup26 AI | cup | Custom tournament AI |
| Polymarket | pm | Prediction market odds |

Current weights are adjusted automatically by `recalibrate.py` based on historical accuracy per source.

## How It Works

### Prediction Engine (`predictive_engine.py`)

1. **Source consensus** — 10 sources each predict a scoreline per match. Weighted average gives xG for each team.
2. **Prior adjustment** — blends source predictions with Elo, FIFA rank, market value, form, injuries, WC history, H2H and motivation context.
3. **Score matrix** — 7×7 Poisson probability matrix with dynamic draw inflation (calibrated via grid search on real results, minimizing Brier score).
4. **1X2 blend** — matrix probabilities blended 72/28 with source-weighted market proxy outcomes.
5. **Monte Carlo** — 10,000 Poisson samples per match for O/U 2.5, BTTS, and most-likely scores.
6. **Value picks** — ranks score predictions by expected value for a prode pool: `V = [P(exacto)*3 + P(ganador)*1] * (1 - consensus * (1 - 1/pool_size))`. Classifies into safe/semi-value/value strategies.
7. **Knockout bracket** — propagates group winners/runners-up + best third-placed teams through R32 → R16 → QF → SF → F, with per-match Poisson win probabilities.

### Sequential Monte Carlo

`sequential_monte_carlo()` runs 10,000 full group-stage simulations. Each simulation:
- Samples Poisson goals for every group match
- Computes PTS/GD/GF standings
- Determines top-2 per group + best 4 third-placed teams
- Aggregates qualification probabilities per team

Output: `knockout_probs` with `winner_pct`, `runner_up_pct`, `third_pct`, `qualify_pct` per team.

### Draw Rate Targeting

`calibrate_draw_inflation()` in `recalibrate.py`:
- Reads latest predictions + real results
- Computes Brier score for draw probability predictions under different `base_inflation` candidates (0.30–1.00)
- Picks the value that minimizes Brier
- Smooths with learning rate based on sample count
- Persists to `data/model/draw_inflation.json`

### Elo Post-Match Updates

`sports_source.py` implements:
- `update_elo_from_result()` — adjusts Elo ratings based on match result and expected outcome
- `persist_elo_from_results()` — batch applies all played results to `team_strengths.json`
- K-factor of 32, home-field advantage, goal-margin weighting

### Weight Recalibration

`recalibrate.py` adjusts per-source weights based on:
- Exact accuracy (30%) + winner accuracy (70%) → confidence index
- Time decay (recent results weighted higher)
- Sample factor (full confidence at 5+ samples)
- Goal bias penalty (over/under-estimate per source)
- Draw under-prediction penalty

## Dashboard Tabs

The single-file HTML dashboard (`prode-mundial-2026.html`) includes:

| Tab | Description |
|---|---|
| Dinámico | All 104 matches with consensus picks, confidence, xG, Monte Carlo stats, played/pending badges, date+source filters |
| Comparativa | Side-by-side source comparison per match |
| Dashboard | Chart.js visualizations of win rates, distributions, accuracy trends |
| Final | Full 104-match table with all predictions |
| Prode | Pool pick comparison across participants |
| Noticias | Injury news and squad updates |
| Resultados | Real match results with model evaluation |
| Accuracy | Per-source accuracy table with exact/winner percentages, bias bars |
| Eliminatorias | Bracket view: R32 → R16 → QF → SF → F with winner confidence |
| **Estrategia** | Value-ranked picks per match grouped by strategy (safe/semi-value/value), with configurable pool size slider |
| **Grupos** | 12 group standing tables with Monte Carlo qualification % overlay |

## Automation

The CI pipeline runs daily at 12:00 UTC:

```yaml
1. python predictive_engine.py       # Generate predictions
2. python update_dynamic_dashboard.py # Embed results + Elo + accuracy
3. python recalibrate.py             # Adjust weights + calibrate draw inflation
4. git commit && git push            # Deploy trigger for Vercel
```

Trigger manually via GitHub Actions → `workflow_dispatch`.

## Deployment

Static HTML deployed on Vercel. Push to `main` triggers automatic deployment via `vercel.json` configuration. No build step required — Vercel serves the static files directly.

## License

MIT
