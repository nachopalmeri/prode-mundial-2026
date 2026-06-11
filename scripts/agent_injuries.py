#!/usr/bin/env python3
"""Build injury adjustment data for the real fixture teams."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from prode_core import load_teams


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

SEED_INJURIES = {
    "France": [{"player": "Mike Maignan", "injury": "thigh", "status": "doubt", "penalty": 0.12}],
    "Netherlands": [{"player": "Frenkie de Jong", "injury": "ankle", "status": "doubt", "penalty": 0.12}],
    "Brazil": [{"player": "Neymar Jr.", "injury": "availability", "status": "doubt", "penalty": 0.10}],
}


def build_output(timestamp: str) -> dict:
    teams = load_teams()
    output_teams = {}
    for team in teams:
        injuries = SEED_INJURIES.get(team, [])
        output_teams[team] = {
            "injuries": injuries,
            "injury_penalty": round(sum(float(item.get("penalty", 0.0)) for item in injuries), 3),
            "source": "seed" if injuries else "neutral",
        }

    output = {
        "timestamp": timestamp,
        "status": "seed",
        "teams": output_teams,
        "team_count": len(output_teams),
        "total_flagged": sum(1 for item in output_teams.values() if item["injuries"]),
        "note": "Neutral by default. Replace with confirmed lineup/injury feed before lock.",
    }
    (RAW / f"injuries_{timestamp}.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Injuries saved: injuries_{timestamp}.json | teams={len(output_teams)}")
    return output


def main() -> None:
    build_output(datetime.now().strftime("%Y%m%d_%H%M"))


if __name__ == "__main__":
    main()
