#!/usr/bin/env python3
"""Build recent-form and H2H adjustment data for fixture teams."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from prode_core import load_teams


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

SEED_FORM = {
    "Argentina": {"form": ["W", "W", "W"], "h2h_bonus": 0.06},
    "Spain": {"form": ["W", "W", "D"], "h2h_bonus": 0.04},
    "France": {"form": ["W", "D", "W"], "h2h_bonus": 0.03},
    "Brazil": {"form": ["W", "W", "L"], "h2h_bonus": 0.02},
    "Morocco": {"form": ["W", "D", "W"], "h2h_bonus": 0.04},
    "Japan": {"form": ["W", "W", "L"], "h2h_bonus": 0.02},
}


def form_value(results: list[str]) -> float:
    score = sum(1 for item in results if item == "W") - sum(1 for item in results if item == "L")
    return max(-0.35, min(0.35, score * 0.08))


def build_output(timestamp: str) -> dict:
    teams = load_teams()
    output_teams = {}
    for team in teams:
        seed = SEED_FORM.get(team, {"form": [], "h2h_bonus": 0.0})
        output_teams[team] = {
            "form_results": seed["form"],
            "form": form_value(seed["form"]),
            "h2h_bonus": seed["h2h_bonus"],
            "source": "seed" if seed["form"] else "neutral",
        }

    output = {
        "timestamp": timestamp,
        "status": "seed",
        "teams": output_teams,
        "team_count": len(output_teams),
        "note": "Neutral by default. Use confirmed recent-form feed when available.",
    }
    (RAW / f"h2h_{timestamp}.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"H2H/form saved: h2h_{timestamp}.json | teams={len(output_teams)}")
    return output


def main() -> None:
    build_output(datetime.now().strftime("%Y%m%d_%H%M"))


if __name__ == "__main__":
    main()
