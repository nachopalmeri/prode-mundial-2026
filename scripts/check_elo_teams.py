#!/usr/bin/env python3
"""Check which teams without elo_updated have actually played matches."""
import json

preds = json.load(open("data/model/latest_predictions.json", "r", encoding="utf-8"))
matches = preds.get("matches", [])

missing = ["England", "Portugal", "Colombia", "Croatia", "Panama", "Uzbekistan", "DR Congo", "Ghana"]

print("Teams without elo_updated and their matches:")
for m in matches:
    if not m.get("played") or not m.get("played_result"):
        continue
    if m["home"] in missing or m["away"] in missing:
        print(f"  Match {m['id']}: {m['home']} vs {m['away']} -> {m['played_result']}")

print("\nTeams in missing but NOT in any played match:")
teams_in_played = set()
for m in matches:
    if m.get("played"):
        teams_in_played.add(m["home"])
        teams_in_played.add(m["away"])
for t in missing:
    if t not in teams_in_played:
        print(f"  {t} (no ha jugado todavia -> correcto que no tenga elo_updated)")
    else:
        print(f"  {t} (JUGO pero no tiene elo_updated -> INCONSISTENTE)")
