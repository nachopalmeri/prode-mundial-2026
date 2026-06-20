#!/usr/bin/env python3
"""Run ELO persistence to populate applied_elo_match_ids and reconcile history."""
import sys, json
sys.path.insert(0, "scripts")
from pathlib import Path
from sports_source import persist_elo_from_results
from datetime import datetime, timezone

TEAM_STRENGTHS_PATH = Path("data/config/team_strengths.json")
PREDICTIONS_PATH = Path("data/model/latest_predictions.json")

predictions = json.loads(PREDICTIONS_PATH.read_text(encoding="utf-8"))

# Read current state BEFORE running
before = json.loads(TEAM_STRENGTHS_PATH.read_text(encoding="utf-8"))
before_ids = before.get("applied_elo_match_ids", [])
before_elos = {t: before["teams"][t].get("elo", 0) for t in before.get("teams", {})}

print(f"Applied match IDs BEFORE: {len(before_ids)}")
print(f"Teams registered: {len(before.get('teams', {}))}")

# Run persistence
persist_elo_from_results(predictions, TEAM_STRENGTHS_PATH)

# Check what changed
after = json.loads(TEAM_STRENGTHS_PATH.read_text(encoding="utf-8"))
after_ids = after.get("applied_elo_match_ids", [])
after_elos = {t: after["teams"][t].get("elo", 0) for t in after.get("teams", {})}

changes = []
for t in before_elos:
    if abs(before_elos[t] - after_elos[t]) > 0.1:
        changes.append((t, before_elos[t], after_elos[t]))

print(f"\nApplied match IDs AFTER: {len(after_ids)}")
print(f"Match IDs: {sorted(after_ids)}")

if changes:
    print(f"\nCAMBIOS detectados en {len(changes)} equipos (ERA ESPERADO si no se habia ejecutado antes):")
    for name, old, new in changes:
        print(f"  {name}: {old:.0f} -> {new:.0f} (delta={new-old:.1f})")
else:
    print(f"\nNO hay cambios en Elo - idempotencia verificada")
    print("(Los valores Elo ya estaban correctos y no se duplicaron)")
