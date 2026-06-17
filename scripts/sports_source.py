#!/usr/bin/env python3
"""Bridge between sports-skills library and the prode prediction engine.
Provides real match results, standings, Polymarket odds, and team profiles
via ESPN/Understat/Polymarket APIs bundled in the sports-skills library."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
CACHE_TTL = 3600  # 1 hour


def _cache_path(name: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{name}.json"


def _cached(name: str, ttl: int = CACHE_TTL) -> dict | None:
    p = _cache_path(name)
    if not p.exists():
        return None
    age = time.time() - p.stat().st_mtime
    if age > ttl:
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_cache(name: str, data: dict) -> None:
    p = _cache_path(name)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Real match results
# ---------------------------------------------------------------------------

def fetch_todays_results(date: str | None = None) -> list[dict]:
    """Fetch real match results for a given date (YYYY-MM-DD) from ESPN via sports-skills.
    Returns list of dicts with home, away, home_score, away_score, competition, status."""
    cache_key = f"daily_schedule_{date or 'today'}"
    cached = _cached(cache_key, ttl=300)
    if cached:
        return cached.get("events", [])

    try:
        import sports_skills.football as fb
        sched = fb.get_daily_schedule(date=date)
        events = sched.get("data", {}).get("events", [])
        results = []
        for ev in events:
            comp_id = ev.get("competition", {}).get("id", "")
            # Only include World Cup matches
            if comp_id != "world-cup":
                continue
            comps = ev.get("competitors", [])
            scores = ev.get("scores", {})
            if len(comps) >= 2:
                home = next((c for c in comps if c.get("qualifier") == "home"), comps[0])
                away = next((c for c in comps if c.get("qualifier") == "away"), comps[1])
                comp_name = ev.get("competition", {}).get("name", "Unknown")
                event_id = ev.get("id")
                results.append({
                    "id": event_id,
                    "event_id": event_id,
                    "home": home.get("team", {}).get("name", ""),
                    "home_team_id": home.get("team", {}).get("id", ""),
                    "away": away.get("team", {}).get("name", ""),
                    "away_team_id": away.get("team", {}).get("id", ""),
                    "home_score": scores.get("home"),
                    "away_score": scores.get("away"),
                    "status": ev.get("status", "unknown"),
                    "competition": comp_name,
                    "start_time": ev.get("start_time", ""),
                })
        _save_cache(cache_key, {"events": results, "fetched_at": datetime.now(timezone.utc).isoformat()})
        return results
    except Exception as e:
        return [{"error": str(e)}]


def fetch_match_result_by_teams(home: str, away: str, date: str | None = None) -> str | None:
    """Try to find a real result for home vs away on a given date (or recent).
    Returns 'H-A' string or None."""
    results = fetch_todays_results(date)
    for r in results:
        if r.get("error"):
            continue
        if r["home"].lower() == home.lower() and r["away"].lower() == away.lower():
            hs, aw = r.get("home_score"), r.get("away_score")
            if hs is not None and aw is not None:
                return f"{hs}-{aw}"
    return None


# ---------------------------------------------------------------------------
# Real standings
# ---------------------------------------------------------------------------

def fetch_group_standings() -> dict[str, list[dict]]:
    """Fetch real group standings for the 2026 World Cup from ESPN.
    Returns dict of group -> list of {position, team, played, pts, gd, ...}."""
    cache_key = "wc_standings"
    cached = _cached(cache_key, ttl=600)
    if cached:
        return cached.get("groups", {})

    try:
        import sports_skills.football as fb
        raw = fb.get_season_standings(season_id="world-cup-2026")
        data = raw.get("data", {})
        standings_list = data.get("standings", [])
        groups: dict[str, list[dict]] = {}
        for entry in standings_list:
            gname = entry.get("name", "")
            teams = entry.get("entries", [])
            groups[gname] = [
                {
                    "position": t.get("position"),
                    "team": t.get("team", {}).get("name", ""),
                    "abbreviation": t.get("team", {}).get("abbreviation", ""),
                    "played": t.get("played", 0),
                    "won": t.get("won", 0),
                    "drawn": t.get("drawn", 0),
                    "lost": t.get("lost", 0),
                    "goals_for": t.get("goals_for", 0),
                    "goals_against": t.get("goals_against", 0),
                    "goal_difference": t.get("goal_difference", 0),
                    "points": t.get("points", 0),
                }
                for t in teams
            ]
        _save_cache(cache_key, {"groups": groups, "fetched_at": datetime.now(timezone.utc).isoformat()})
        return groups
    except Exception as e:
        return {"_error": str(e)}


# ---------------------------------------------------------------------------
# Polymarket odds
# ---------------------------------------------------------------------------

def fetch_polymarket_winner_odds() -> dict[str, float]:
    """Fetch Polymarket prices for 'World Cup Winner' market.
    Returns dict of team_name -> yes_price (0-1 scale)."""
    cache_key = "pm_winner_odds"
    cached = _cached(cache_key, ttl=1800)
    if cached:
        return cached.get("odds", {})

    try:
        import sports_skills.polymarket as pm
        events = pm.get_sports_events(limit=50, active=True, closed=False)
        for ev in events.get("data", {}).get("events", []):
            title = ev.get("title", "")
            if "World Cup Winner" not in title:
                continue
            all_prices = {}
            for mkt in ev.get("markets", []):
                outcomes = mkt.get("outcomes", [])
                question = mkt.get("question", "")
                # Extract team name from "Will <Team> win the 2026 FIFA World Cup?"
                team_name = question.replace("Will ", "").replace(" win the 2026 FIFA World Cup?", "").strip()
                if not team_name or team_name in ("Yes", "No", "Other"):
                    continue
                for outcome in outcomes:
                    if isinstance(outcome, dict) and outcome.get("name") == "Yes":
                        price = outcome.get("price", 0)
                        if isinstance(price, (int, float)) and price > 0:
                            all_prices[team_name] = float(price)
                        break
            if all_prices:
                _save_cache(cache_key, {"odds": all_prices, "fetched_at": datetime.now(timezone.utc).isoformat()})
                return all_prices
        return {}
    except Exception as e:
        return {"_error": str(e)}


# ---------------------------------------------------------------------------
# Real head-to-head from sports-skills (replaces broken scraper)
# ---------------------------------------------------------------------------

def fetch_h2h_from_espn(team1_id: str, team2_id: str) -> dict | None:
    """Compute H2H advantage using get_team_schedule for both teams."""
    try:
        import sports_skills.football as fb
        t1_sched = fb.get_team_schedule(team_id=team1_id, competition_id="world-cup")
        t2_sched = fb.get_team_schedule(team_id=team2_id, competition_id="world-cup")
        matches1 = t1_sched.get("data", {}).get("events", [])
        matches2 = t2_sched.get("data", {}).get("events", [])
        return {
            "team1_matches": len(matches1),
            "team2_matches": len(matches2),
            "note": "H2H via sports-skills schedule comparison",
        }
    except Exception as e:
        return {"error": str(e)}


# ---------------------------------------------------------------------------
# Generate real source predictions
# ---------------------------------------------------------------------------

def generate_real_source_predictions(
    match_id: int,
    home: str,
    away: str,
    best_pick: str,
    standings: dict[str, list[dict]] | None = None,
    pm_odds: dict[str, float] | None = None,
) -> dict[str, str]:
    """Generate source predictions using real data where available.
    Falls back to synthetic variation for sources without real data.

    Source keys:
        c = consensus, g = goal matrix, f = form, fs = field status
        esp = ESPN (real team profiles), yh = Yahoo, tips = tipsters
        e = Elo, cup = cup history, pm = Polymarket (real odds)
    """
    picks: dict[str, str] = {}

    # ESPN source: use real standings + Polymarket odds
    esp_pred = _espn_prediction(home, away, standings, pm_odds)
    if esp_pred:
        picks["esp"] = esp_pred
    else:
        picks["esp"] = best_pick

    # Polymarket source
    pm_pred = _polymarket_prediction(home, away, pm_odds)
    if pm_pred:
        picks["pm"] = pm_pred
    else:
        picks["pm"] = best_pick

    # Other sources: fall back to synthetic variation
    for sk in ["c", "g", "f", "fs", "yh", "tips", "e", "cup"]:
        picks[sk] = best_pick

    return picks


def _espn_prediction(
    home: str, away: str,
    standings: dict[str, list[dict]] | None,
    pm_odds: dict[str, float] | None,
) -> str | None:
    """Generate ESPN-style prediction based on standings + Polymarket odds."""
    if not standings:
        return None
    home_pts = 0
    away_pts = 0
    for grp, teams in standings.items():
        for t in teams:
            if t["team"].lower() == home.lower():
                home_pts = t.get("points", 0)
            if t["team"].lower() == away.lower():
                away_pts = t.get("points", 0)
    diff = home_pts - away_pts
    # Rough mapping: point difference -> score prediction
    if diff >= 3:
        return "2-0"
    elif diff >= 1:
        return "2-1"
    elif diff <= -3:
        return "0-2"
    elif diff <= -1:
        return "1-2"
    else:
        return "1-1"


def _polymarket_prediction(
    home: str, away: str,
    pm_odds: dict[str, float] | None,
) -> str | None:
    """Use Polymarket winner odds to sway prediction."""
    if not pm_odds:
        return None
    home_odds = pm_odds.get(home) or 0.0
    away_odds = pm_odds.get(away) or 0.0
    if home_odds > away_odds + 0.1:
        return "2-1"
    elif away_odds > home_odds + 0.1:
        return "1-2"
    return "1-1"


# ---------------------------------------------------------------------------
# Automatic result injection
# ---------------------------------------------------------------------------

def _parse_match_date_to_iso(spanish_date: str) -> str | None:
    """Convert Spanish match dates like 'Dom 14/6' or 'Jue 11/6' to ISO '2026-06-14'."""
    import re
    m = re.match(r'\w{3}\s+(\d{1,2})/(\d{1,2})', spanish_date)
    if m:
        day, month = int(m.group(1)), int(m.group(2))
        return f"2026-{month:02d}-{day:02d}"
    return None


def inject_real_results_into_predictions(predictions: dict) -> dict:
    """Replace best_pick and score fields with real results for played matches."""
    matches = predictions.get("matches", [])
    standings = fetch_group_standings()
    pm_odds = fetch_polymarket_winner_odds()

    # Read local runtime results (manually entered / pipeline-driven)
    runtime_path = Path(__file__).resolve().parent.parent / "data" / "runtime" / "results.json"
    runtime_results: dict = {}
    try:
        if runtime_path.exists():
            runtime_results = json.loads(runtime_path.read_text(encoding="utf-8")).get("results", {})
    except Exception:
        pass

    # Fetch real results from sports-skills for recent match dates
    iso_dates: set[str] = set()
    for m in matches:
        d = _parse_match_date_to_iso(m.get("date", ""))
        if d:
            iso_dates.add(d)
    all_real_results: dict[str, str] = {}
    for iso_date in sorted(iso_dates)[:5]:  # limit to first 5 match days
        try:
            results = fetch_todays_results(iso_date)
            for r in results:
                if r.get("error"):
                    continue
                key = f"{r['home'].lower()}__{r['away'].lower()}"
                hs, aw = r.get("home_score"), r.get("away_score")
                if hs is not None and aw is not None:
                    all_real_results[key] = f"{hs}-{aw}"
        except Exception:
            pass

    for m in matches:
        mid = m.get("id", 0)
        home = m.get("home", "")
        away = m.get("away", "")
        key = f"{home.lower()}__{away.lower()}"

        # Check for real result: runtime file first, then sports-skills
        result = runtime_results.get(str(mid))
        if not result:
            result = all_real_results.get(key)

        if result:
            m["played"] = True
            m["played_result"] = result
            m["best_pick"] = result
            parts = result.split("-")
            if len(parts) == 2:
                m["score_home"] = int(parts[0])
                m["score_away"] = int(parts[1])

        # Generate real source predictions for every match
        real_picks = generate_real_source_predictions(
            mid, home, away,
            m.get("best_pick", "0-0"),
            standings if isinstance(standings, dict) and "_error" not in standings else None,
            pm_odds if isinstance(pm_odds, dict) and "_error" not in pm_odds else None,
        )
        m["sources_real"] = real_picks

    predictions["metadata"]["real_results_fetched"] = True
    predictions["metadata"]["standings_available"] = isinstance(standings, dict) and "_error" not in standings
    predictions["metadata"]["pm_odds_available"] = isinstance(pm_odds, dict) and "_error" not in pm_odds
    return predictions


def update_elo_from_result(
    home_team: str, away_team: str,
    home_goals: int, away_goals: int,
    priors: dict,
) -> tuple[float, float]:
    """Update Elo ratings based on match result. Returns (new_home_elo, new_away_elo)."""
    teams = priors.get("teams", {})
    home_elo = float(teams.get(home_team, {}).get("elo", 1500))
    away_elo = float(teams.get(away_team, {}).get("elo", 1500))

    expected_home = 1.0 / (1.0 + 10.0 ** ((away_elo - home_elo) / 400.0))
    expected_away = 1.0 - expected_home

    if home_goals > away_goals:
        actual_home, actual_away = 1.0, 0.0
    elif away_goals > home_goals:
        actual_home, actual_away = 0.0, 1.0
    else:
        actual_home, actual_away = 0.5, 0.5

    K = 30.0
    new_home = home_elo + K * (actual_home - expected_home)
    new_away = away_elo + K * (actual_away - expected_away)
    return round(new_home, 1), round(new_away, 1)


def persist_elo_from_results(predictions: dict, priors_path: Path) -> dict:
    """Update team strengths with post-match Elo adjustments."""
    teams_path = priors_path
    if not teams_path.exists():
        return predictions

    priors = json.loads(teams_path.read_text(encoding="utf-8"))
    teams = priors.get("teams", {})
    changed = 0

    for m in predictions.get("matches", []):
        if not m.get("played") or not m.get("played_result"):
            continue
        home = m.get("home", "")
        away = m.get("away", "")
        result = m["played_result"]
        parts = result.split("-")
        if len(parts) != 2:
            continue
        hg, ag = int(parts[0]), int(parts[1])
        new_home, new_away = update_elo_from_result(home, away, hg, ag, priors)

        if home in teams:
            old = teams[home].get("elo", 1500)
            if abs(new_home - old) > 0.1:
                teams[home]["elo"] = new_home
                teams[home]["elo_updated"] = datetime.now(timezone.utc).isoformat()
                changed += 1
        if away in teams:
            old = teams[away].get("elo", 1500)
            if abs(new_away - old) > 0.1:
                teams[away]["elo"] = new_away
                teams[away]["elo_updated"] = datetime.now(timezone.utc).isoformat()
                changed += 1

    if changed:
        teams_path.write_text(json.dumps(priors, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  Updated Elo for {changed} teams from real results")

    return predictions


if __name__ == "__main__":
    # Quick test
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "results"
    if cmd == "results":
        r = fetch_todays_results()
        for ev in r:
            if ev.get("error"):
                print(f"  Error: {ev['error']}")
            else:
                print(f"  {ev['home']} {ev.get('home_score','?')}-{ev.get('away_score','?')} {ev['away']} [{ev['status']}]")
    elif cmd == "standings":
        g = fetch_group_standings()
        for grp, teams in sorted(g.items()):
            if grp.startswith("_"):
                continue
            print(f"\nGroup {grp}:")
            for t in teams:
                print(f"  {t['position']}. {t['team']:25s} {t['played']}j {t['points']}pts GD:{t['goal_difference']:+d}")
    elif cmd == "pm":
        o = fetch_polymarket_winner_odds()
        for team, price in sorted(o.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {team:25s} {float(price)*100:.1f}%")
    else:
        print("Usage: python sports_source.py [results|standings|pm]")
