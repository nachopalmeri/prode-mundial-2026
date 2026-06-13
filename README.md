# Prode Mundial 2026

Multi-source AI prediction system for the 2026 FIFA World Cup. Aggregates 10 prediction sources (Cascade, ChatGPT, Gemini, Fansided, ESPN, Yahoo, 1960Tips, ELO Model, Cup26 AI, Polymarket) using a weighted consensus + Poisson engine to generate probabilistic scoreline predictions for all 72 group-stage matches.

## Features

- 10 AI prediction sources with weighted consensus
- Poisson-based dynamic probabilistic engine
- Team strength priors (Elo, FIFA Rank, Market Value, Form)
- Match motivation profiling (must-win, rotation, etc.)
- Top-3 scoreline predictions with confidence levels
- Source accuracy tracking and weight recalibration
- Auto-updating every 6 hours via GitHub Actions
- Deployed to Vercel

## Tech Stack

- **Frontend:** Static HTML + Chart.js
- **Backend/ML:** Python 3.12 + NumPy
- **Data:** JSON (team strengths, predictions, weights)
- **Automation:** GitHub Actions (cron every 6h)
- **Deploy:** Vercel

## Project Structure

```
├── data/
│   ├── config/team_strengths.json    # Team priors
│   ├── model/                        # Generated predictions
│   ├── raw/                          # Scraped source data
│   └── runtime/results.json          # Match results
├── scripts/                          # Python automation
│   ├── predictive_engine.py          # Core prediction engine
│   ├── prode_core.py                 # Core utilities
│   ├── agent_*.py                    # Multi-agent system
│   └── run_orchestrator.py          # Workflow coordinator
├── prode-mundial-2026.html           # Main dashboard
├── .github/workflows/auto-improve.yml
└── vercel.json
```

## Setup

1. Clone the repo
2. Install Python dependencies: `pip install -r requirements.txt`
3. Run the prediction engine: `python scripts/predictive_engine.py`
4. Or run the full orchestrator: `python scripts/run_orchestrator.py`

## Prediction Sources

| Source | Key | Weight |
|---|---|---|
| Cascade | c | 1.0 |
| ChatGPT | g | 1.0 |
| Gemini | f | 1.0 |
| Fansided | fs | 0.8 |
| ESPN | esp | 1.3 |
| Yahoo | yh | 0.8 |
| 1960Tips | tips | 1.5 |
| ELO Model | e | 1.5 |
| Cup26 AI | cup | 1.4 |
| Polymarket | pm | 1.6 |

## Automation

The system runs every 6 hours via GitHub Actions:
1. Fetch latest predictions from all sources
2. Run the weighted consensus + Poisson engine
3. Validate output
4. Update HTML dashboard
5. Deploy to Vercel
