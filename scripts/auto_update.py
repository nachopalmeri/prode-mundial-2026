#!/usr/bin/env python3
"""
Auto-update real scores + DraftKings odds from ESPN via sports-skills.
Injects into HTML: EMBEDDED_REAL_SCORES, DK_PREDS.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sports_skills import football

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"
RUNTIME_DIR = PROJECT_ROOT / "data" / "runtime"

WC_START = "2026-06-11"

TEAM_NAMES = {
    "Bosnia-Herzegovina": "Bosnia and Herzegovina",
    "Korea Republic": "South Korea",
    "IR Iran": "Iran",
    "DR Congo": "DR Congo",
    "Congo DR": "DR Congo",
    "Côte d'Ivoire": "Ivory Coast",
    "Türkiye": "Turkiye",
    "Curaçao": "Curacao",
    "United States": "USA",
}


def normalize_team(name: str) -> str:
    return TEAM_NAMES.get(name, name)


def parse_matches(html: str) -> list[dict]:
    m = re.search(r"const matches = (\[.*?\]);", html, re.DOTALL)
    if not m:
        print("  ERROR: could not find matches array")
        sys.exit(1)
    raw = m.group(1)
    raw = re.sub(r"([{,]\s*)(\w+)(\s*:)", r'\1"\2"\3', raw)
    return json.loads(raw)


def american_to_prob(american: int) -> float:
    if american > 0:
        return 100.0 / (american + 100)
    return abs(american) / (abs(american) + 100.0)


def odds_to_scoreline(home_odd: int, draw_odd: int, away_odd: int) -> str:
    raw = {
        "home": american_to_prob(home_odd),
        "draw": american_to_prob(draw_odd),
        "away": american_to_prob(away_odd),
    }
    total = sum(raw.values())
    fair = {k: v / total for k, v in raw.items()}
    hp, dp, ap = fair["home"], fair["draw"], fair["away"]
    if hp >= dp and hp >= ap:
        if hp > 0.55:
            return "2-0"
        if hp > 0.45:
            return "2-1"
        return "1-0"
    if dp >= hp and dp >= ap:
        return "1-1"
    if ap > 0.55:
        return "0-2"
    if ap > 0.45:
        return "1-2"
    return "0-1"


def daterange(start_str: str, end_str: str):
    start = datetime.strptime(start_str, "%Y-%m-%d").date()
    end = datetime.strptime(end_str, "%Y-%m-%d").date()
    for i in range((end - start).days + 1):
        yield (start + timedelta(days=i)).isoformat()


def main() -> None:
    print("=== Auto Update: Real Scores + DraftKings ===")

    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    html = HTML_PATH.read_text(encoding="utf-8")
    matches = parse_matches(html)

    team_to_id: dict[tuple[str, str], int] = {}
    for m in matches:
        team_to_id[(m["a"].lower(), m["b"].lower())] = m["id"]

    print(f"  Loaded {len(matches)} matches from HTML")

    results: dict[str, str] = {}
    dk_preds: dict[str, str] = {}
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    for date_str in daterange(WC_START, today_str):
        if date_str > today_str:
            break
        print(f"  Fetching {date_str} ...")
        try:
            schedule = football.get_daily_schedule(date=date_str)
        except Exception as e:
            print(f"    SKIP: {e}")
            continue

        events = schedule.get("data", {}).get("events", [])
        if not events:
            print(f"    No events")
            continue

        for ev in events:
            if ev.get("competition", {}).get("name") != "FIFA World Cup":
                continue

            competitors = ev.get("competitors", [])
            if len(competitors) < 2:
                continue

            home = normalize_team(competitors[0]["team"]["name"])
            away = normalize_team(competitors[1]["team"]["name"])

            match_id = team_to_id.get((home.lower(), away.lower()))
            if match_id is None:
                match_id = team_to_id.get((away.lower(), home.lower()))
            if match_id is None:
                print(f"    WARN: no match for {home} vs {away}")
                continue

            mid = str(match_id)
            status = ev.get("status", "")

            if status == "closed":
                scores = ev.get("scores", {})
                hs = scores.get("home")
                as_ = scores.get("away")
                if hs is not None and as_ is not None:
                    score = f"{int(hs)}-{int(as_)}"
                    results[mid] = score
                    print(f"    Match {mid}: {home} {score} {away}")

            odds = ev.get("odds")
            ml = (odds or {}).get("moneyline")
            if ml and all(k in ml for k in ("home", "draw", "away")):
                try:
                    ho = int(ml["home"])
                    dr = int(ml["draw"])
                    ao = int(ml["away"])
                    scoreline = odds_to_scoreline(ho, dr, ao)
                    dk_preds[mid] = scoreline
                    print(f"    Match {mid}: DK {scoreline} ({ho}/{dr}/{ao})")
                except (ValueError, TypeError):
                    pass

    print(f"\n  Real scores: {len(results)}")
    print(f"  DK predictions: {len(dk_preds)}")

    # --- Update REAL_SCORES ---
    if results:
        existing: dict[str, str] = {}
        rm = re.search(r"const EMBEDDED_REAL_SCORES = (\{[^}]+\});", html)
        if rm:
            existing = json.loads(rm.group(1))
        existing.update(results)
        new_scores = json.dumps(existing, ensure_ascii=False)
        html = re.sub(
            r"/\* BEGIN_REAL_SCORES \*/.*?/\* END_REAL_SCORES \*/",
            f"/* BEGIN_REAL_SCORES */\nconst EMBEDDED_REAL_SCORES = {new_scores};\n/* END_REAL_SCORES */",
            html,
            flags=re.DOTALL,
        )
        print(f"  Updated REAL_SCORES ({len(existing)} total)")

    # --- Update DK_PREDS ---
    if dk_preds:
        dk_json = json.dumps(dict(sorted(dk_preds.items(), key=lambda x: int(x[0]))), ensure_ascii=False)
        if "/* BEGIN_DK_PREDS */" in html:
            html = re.sub(
                r"/\* BEGIN_DK_PREDS \*/.*?/\* END_DK_PREDS \*/",
                f"/* BEGIN_DK_PREDS */\nconst DK_PREDS = {dk_json};\n/* END_DK_PREDS */",
                html,
                flags=re.DOTALL,
            )
        else:
            print("  WARN: DK_PREDS markers not found in HTML")
        print(f"  Updated DK_PREDS ({len(dk_preds)} matches)")

    HTML_PATH.write_text(html, encoding="utf-8")
    print(f"\n  Saved {HTML_PATH.name}")

    # Also write results.json for other scripts
    if results:
        rp = RUNTIME_DIR / "results.json"
        rp.write_text(json.dumps({"results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  Saved results.json ({len(results)} entries)")


if __name__ == "__main__":
    main()
