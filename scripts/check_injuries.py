#!/usr/bin/env python3
"""Test injury penalties in actual team_prior."""
import sys, json
sys.path.insert(0, 'scripts')
from predictive_engine import load_injuries, team_prior, TEAM_STRENGTHS_PATH

injuries = load_injuries()
print("Injuries loaded: %d teams" % len(injuries))

priors = json.loads(TEAM_STRENGTHS_PATH.read_text(encoding="utf-8"))

# First, check what the base injury_penalty is for each team (from the file)
print("\nBase injury_penalty from team_strengths:")
for team in sorted(priors.get("teams", {})):
    base = priors["teams"][team].get("injury_penalty", 0)
    if base > 0.001:
        print("  %s: base=%.2f" % (team, base))

# Now check what team_prior computes (with live injuries applied)
print("\nEffective injury_penalty AFTER live injuries:")
for team in sorted(priors.get("teams", {})):
    prior = team_prior(team, priors)
    if prior["injury_penalty"] > 0.001:
        base = priors["teams"][team].get("injury_penalty", 0)
        delta = prior["injury_penalty"] - base
        print("  %s: base=%.2f effective=%.2f delta=%.2f" % (team, base, prior["injury_penalty"], delta))
