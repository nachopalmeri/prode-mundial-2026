#!/usr/bin/env python3
"""Fetch or seed FIFA/Elo/market priors for the teams in the real fixture list."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover - GitHub Action installs requests
    requests = None

from prode_core import load_teams


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
CONFIG = PROJECT_ROOT / "data" / "config" / "team_strengths.json"
RAW.mkdir(parents=True, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (compatible; ProdeMundialBot/1.0)"


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


ALIASES = {
    "United States": "USA",
    "USA": "USA",
    "Korea Republic": "South Korea",
    "Türkiye": "Turkiye",
    "Turkey": "Turkiye",
    "Côte d'Ivoire": "Ivory Coast",
    "Cote d'Ivoire": "Ivory Coast",
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Curaçao": "Curacao",
    "Congo DR": "DR Congo",
}


def load_existing_priors() -> dict[str, Any]:
    if not CONFIG.exists():
        return {"teams": {}}
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def match_team(raw_name: str, teams: list[str]) -> str | None:
    alias = ALIASES.get(raw_name.strip())
    if alias in teams:
        return alias
    normalized = normalize_name(alias or raw_name)
    for team in teams:
        team_norm = normalize_name(team)
        if normalized == team_norm or normalized in team_norm or team_norm in normalized:
            return team
    return None


def fetch_fifa_rankings(teams: list[str]) -> tuple[str, dict[str, dict[str, Any]]]:
    if requests is None:
        return "requests_unavailable", {}

    urls = [
        "https://inside.fifa.com/fifa-world-ranking/men",
        "https://api.fifa.com/api/v3/ranking/men?page=1&limit=100",
    ]
    for url in urls:
        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json,text/html"}, timeout=15)
            if response.status_code != 200:
                continue
            data: Any
            try:
                data = response.json()
            except ValueError:
                data = {}
            entries = data.get("results") or data.get("data") or []
            found: dict[str, dict[str, Any]] = {}
            if isinstance(entries, list):
                for entry in entries:
                    name = str(entry.get("teamName") or entry.get("name") or entry.get("countryName") or "")
                    rank = entry.get("rank") or entry.get("position")
                    matched = match_team(name, teams)
                    if matched and rank:
                        found[matched] = {"fifa_rank": int(rank), "fifa_source": "live"}
            if found:
                return "live", found
        except Exception:
            continue
    return "seed", {}


def build_output(timestamp: str) -> dict[str, Any]:
    teams = load_teams()
    existing = load_existing_priors()
    fifa_status, fifa_live = fetch_fifa_rankings(teams)
    output_teams: dict[str, dict[str, Any]] = {}

    for team in teams:
        prior = existing.get("teams", {}).get(team, {})
        output_teams[team] = {
            "elo": prior.get("elo", 1500),
            "fifa_rank": fifa_live.get(team, {}).get("fifa_rank", prior.get("fifa_rank", 48)),
            "market_value_m": prior.get("market_value_m", 120),
            "fifa_source": fifa_live.get(team, {}).get("fifa_source", "seed"),
            "elo_source": "seed",
            "market_source": "seed",
            "last_updated": timestamp,
        }

    output = {
        "timestamp": timestamp,
        "status": fifa_status,
        "teams": output_teams,
        "team_count": len(output_teams),
        "note": "Live FIFA rank is used when available; Elo and market values fall back to editable priors.",
    }
    (RAW / f"rankings_{timestamp}.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Rankings saved: rankings_{timestamp}.json | teams={len(output_teams)} | fifa={fifa_status}")
    return output


def main() -> None:
    build_output(datetime.now().strftime("%Y%m%d_%H%M"))


if __name__ == "__main__":
    main()
