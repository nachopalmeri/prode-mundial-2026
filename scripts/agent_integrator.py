#!/usr/bin/env python3
"""
Agente 6: Integrador — Compila datos de los 5 agentes y actualiza:
  - data/config/team_strengths.json
  - Ejecuta predictive_engine.py
  - Ejecuta update_dynamic_dashboard.py
Uso: python agent_integrator.py [timestamp]
"""

import json, sys, subprocess
from pathlib import Path

from prode_core import load_teams

BASE = Path(__file__).resolve().parent
RAW = BASE.parent / "data" / "raw"
CONFIG = BASE.parent / "data" / "config"
MODEL = BASE.parent / "data" / "model"
CONFIG.mkdir(parents=True, exist_ok=True)

TS = sys.argv[1] if len(sys.argv) > 1 else "latest"
DEFAULT_TEAM_FIELDS = {
    "elo": 1500,
    "fifa_rank": 48,
    "market_value_m": 120,
    "home_boost": 0.0,
    "attack": 1.0,
    "defense": 1.0,
    "form": 0.0,
    "style_tempo": 1.0,
    "injury_penalty": 0.0,
    "h2h_bonus": 0.0,
}

def load_raw(name):
    """Load latest raw data file for given agent"""
    files = sorted(RAW.glob(f"{name}_*.json"))
    if not files:
        print(f"  [integrator] No raw data for {name}")
        return None
    f = files[-1]
    return json.loads(f.read_text(encoding="utf-8"))


def merge_team_strengths():
    """Merge rankings + injuries + h2h into team_strengths.json"""
    rankings = load_raw("rankings")
    injuries = load_raw("injuries")
    h2h = load_raw("h2h")
    
    # Load existing
    existing_path = CONFIG / "team_strengths.json"
    if existing_path.exists():
        existing = json.loads(existing_path.read_text(encoding="utf-8"))
    else:
        existing = {"metadata": {"version": "web-search-agents", "teams": {}}, "teams": {}}
    
    fixture_teams = load_teams()
    teams = {
        name: {**DEFAULT_TEAM_FIELDS, **existing.get("teams", {}).get(name, {})}
        for name in fixture_teams
    }
    
    if rankings and "teams" in rankings:
        for name, data in rankings["teams"].items():
            if name not in teams:
                continue
            teams[name]["elo"] = data.get("elo", teams[name].get("elo", 1500))
            teams[name]["fifa_rank"] = data.get("fifa_rank", teams[name].get("fifa_rank", 50))
            teams[name]["market_value_m"] = data.get("market_value_m", teams[name].get("market_value_m", 100))
    
    if injuries and "teams" in injuries:
        for name, data in injuries["teams"].items():
            if name not in teams:
                continue
            teams[name]["injury_penalty"] = data.get("injury_penalty", teams[name].get("injury_penalty", 0.0))
    
    if h2h and "teams" in h2h:
        for name, data in h2h["teams"].items():
            if name not in teams:
                continue
            if isinstance(data, dict) and "h2h_bonus" in data:
                teams[name]["h2h_bonus"] = data["h2h_bonus"]
            if isinstance(data, dict) and "form" in data:
                teams[name]["form"] = data["form"]
    
    output = {
        "metadata": {
            "version": f"web-search-{TS}",
            "source": "Merged from web search agents",
            "fields": "elo/fifa_rank/market_value_m/injury_penalty/h2h_bonus/form/style_tempo/attack/defense",
            "last_updated": TS,
        },
        "teams": teams,
    }
    
    existing_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(f"  [integrator] team_strengths.json updated: {len(teams)} teams")
    return output


def run_predictive_engine():
    """Run predictive_engine.py to regenerate latest_predictions.json"""
    engine = BASE / "predictive_engine.py"
    if not engine.exists():
        print("  [integrator] predictive_engine.py not found, skipping")
        return False
    
    try:
        r = subprocess.run([sys.executable, str(engine)], capture_output=True, text=True, timeout=60)
        print(f"  [integrator] predictive_engine: {'OK' if r.returncode == 0 else 'FAIL'}")
        if r.stdout:
            print(f"    {r.stdout.strip()}")
        if r.returncode != 0:
            print(f"    {r.stderr[:200]}")
        return r.returncode == 0
    except Exception as e:
        print(f"  [integrator] predictive_engine error: {e}")
        return False


def update_dashboard():
    """Run update_dynamic_dashboard.py to inject predictions into HTML"""
    updater = BASE / "update_dynamic_dashboard.py"
    if not updater.exists():
        print("  [integrator] update_dynamic_dashboard.py not found, skipping")
        return False
    
    try:
        r = subprocess.run([sys.executable, str(updater)], capture_output=True, text=True, timeout=30)
        print(f"  [integrator] dashboard updater: {'OK' if r.returncode == 0 else 'FAIL'}")
        if r.stdout:
            print(f"    {r.stdout.strip()}")
        return r.returncode == 0
    except Exception as e:
        print(f"  [integrator] dashboard updater error: {e}")
        return False


def main():
    print("[integrator] Merging web search data...")
    merge_team_strengths()
    
    print("[integrator] Running predictive engine...")
    run_predictive_engine()
    
    print("[integrator] Updating dashboard...")
    update_dashboard()
    
    print("[integrator] Done.")


if __name__ == "__main__":
    main()
