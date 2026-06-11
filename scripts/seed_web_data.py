#!/usr/bin/env python3
"""
Manual: Inyecta datos reales obtenidos de websearch (Junio 2026)
Correr despues de websearch manual para actualizar seed data.
"""

import json
from datetime import datetime
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

TS = datetime.now().strftime("%Y%m%d_%H%M")

# --- FIFA Rankings (Sporting News / FIFA.com, June 11 2026) ---
FIFA_RANKINGS = {
    "France": 1, "Spain": 2, "Argentina": 3, "England": 4, "Portugal": 5,
    "Brazil": 6, "Netherlands": 7, "Morocco": 8, "Belgium": 9, "Germany": 10,
    "Croatia": 11, "Colombia": 13, "Senegal": 14, "Mexico": 15, "USA": 16,
    "Uruguay": 17, "Japan": 18, "Switzerland": 19, "Iran": 21, "Turkey": 22,
    "Ecuador": 23, "Austria": 24, "South Korea": 25, "Australia": 27,
    "Algeria": 28, "Egypt": 29, "Canada": 30, "Norway": 31,
    "Ivory Coast": 34, "Paraguay": 40, "Tunisia": 44, "DR Congo": 46,
    "Uzbekistan": 50, "Qatar": 57, "Iraq": 56, "Saudi Arabia": 61,
    "Jordan": 63, "Ghana": 73,
}

# --- Injuries (fwcschedule.com / sportingnews, June 2026) ---
INJURIES = {
    "Brazil": [
        {"player": "Rodrygo", "injury": "ACL + meniscus tear", "status": "out", "penalty": 0.40},
        {"player": "Eder Militao", "injury": "Hamstring tendon rupture", "status": "out", "penalty": 0.35},
        {"player": "Neymar", "injury": "Calf grade 2 tear", "status": "doubt", "penalty": 0.30},
        {"player": "Estevao", "injury": "Hamstring tear", "status": "doubt", "penalty": 0.25},
    ],
    "Netherlands": [
        {"player": "Xavi Simons", "injury": "ACL tear", "status": "out", "penalty": 0.30},
        {"player": "Frenkie de Jong", "injury": "Ankle", "status": "doubt", "penalty": 0.20},
    ],
    "France": [
        {"player": "Hugo Ekitike", "injury": "Achilles rupture", "status": "out", "penalty": 0.25},
        {"player": "Boubacar Kamara", "injury": "Knee", "status": "out", "penalty": 0.15},
        {"player": "Kylian Mbappe", "injury": "Muscle injury", "status": "monitoring", "penalty": 0.15},
    ],
    "Germany": [
        {"player": "Serge Gnabry", "injury": "Torn adductor", "status": "out", "penalty": 0.25},
        {"player": "Marc-Andre ter Stegen", "injury": "Hamstring", "status": "doubt", "penalty": 0.20},
        {"player": "Kai Havertz", "injury": "Knock", "status": "doubt", "penalty": 0.10},
    ],
    "England": [
        {"player": "Jack Grealish", "injury": "Foot surgery", "status": "out", "penalty": 0.20},
        {"player": "Jarrad Branthwaite", "injury": "Muscle", "status": "out", "penalty": 0.10},
    ],
    "USA": [
        {"player": "Patrick Agyemang", "injury": "Achilles rupture", "status": "out", "penalty": 0.20},
    ],
    "Mexico": [
        {"player": "Luis Malagon", "injury": "Achilles tear", "status": "out", "penalty": 0.25},
    ],
    "Spain": [
        {"player": "Lamine Yamal", "injury": "Hamstring", "status": "expected fit", "penalty": 0.05},
    ],
    "Argentina": [
        {"player": "Cristian Romero", "injury": "Knee ligament", "status": "doubt", "penalty": 0.20},
        {"player": "Leonardo Balerdi", "injury": "Thigh", "status": "out", "penalty": 0.15},
    ],
    "Egypt": [
        {"player": "Mohamed Salah", "injury": "Hamstring tear", "status": "likely fit", "penalty": 0.10},
    ],
    "Croatia": [
        {"player": "Josko Gvardiol", "injury": "Tibia fracture", "status": "uncertain", "penalty": 0.20},
    ],
    "Morocco": [
        {"player": "Achraf Hakimi", "injury": "Hamstring tear", "status": "doubt", "penalty": 0.20},
    ],
    "Austria": [
        {"player": "Christoph Baumgartner", "injury": "Thigh muscle", "status": "out", "penalty": 0.15},
    ],
}

# --- Polymarket Win Probabilities (from polymarketworldcup.com, June 11 2026) ---
POLYMARKET_MATCHES = {
    1: {"home_pct": 0.74, "draw_pct": 0.16, "away_pct": 0.10},  # USA vs Iran
    2: {"home_pct": 0.82, "draw_pct": 0.12, "away_pct": 0.06},  # England vs Panama
    3: {"home_pct": 0.78, "draw_pct": 0.14, "away_pct": 0.08},  # USA vs Panama
    4: {"home_pct": 0.71, "draw_pct": 0.19, "away_pct": 0.10},  # England vs Iran
    5: {"home_pct": 0.52, "draw_pct": 0.20, "away_pct": 0.28},  # USA vs England (KEY)
    # Spain vs Croatia: Spain 64%, Draw 21%, Croatia 15%
    # Brazil vs Switzerland: Brazil 64%, Draw 22%, Swiss 14%
    # France vs Senegal: France 72%, Draw 17%, Senegal 11%
    # Argentina vs Colombia: Argentina 55%, Draw 24%, Colombia 21%
    # Portugal vs South Korea: Portugal 66%, Draw 21%, Korea 13%
}

# Write rankings
rankings_out = {
    "timestamp": TS, "status": "manual-websearch", "source": "sportingnews.com + inside.fifa.com",
    "fifa_source": "manual-websearch", "elo_source": "manual-websearch",
    "teams": {}, "team_count": len(FIFA_RANKINGS),
}
TEAMS_ALL = list(FIFA_RANKINGS.keys())
# Seed ELO from GFR data
ELO_RATINGS = {
    "Spain": 1877, "Argentina": 1873, "France": 1870, "England": 1834,
    "Brazil": 1760, "Portugal": 1760, "Netherlands": 1756, "Morocco": 1737,
    "Belgium": 1731, "Germany": 1724, "Croatia": 1717, "Colombia": 1701,
    "USA": 1682, "Mexico": 1676, "Uruguay": 1673, "Japan": 1650,
    "Switzerland": 1655, "Senegal": 1648, "Iran": 1617, "South Korea": 1599,
    "Ecuador": 1592, "Austria": 1586, "Turkey": 1583, "Australia": 1574,
    "Canada": 1559, "Norway": 1533, "Egypt": 1521, "Algeria": 1516,
    "Paraguay": 1502, "Tunisia": 1497, "Ivory Coast": 1490,
    "Costa Rica": 1464, "Uzbekistan": 1462,
}

for name in TEAMS_ALL:
    ranks_out = rankings_out["teams"]
    ranks_out[name] = {
        "fifa_rank": FIFA_RANKINGS[name],
        "fifa_source": "manual-websearch",
        "elo": ELO_RATINGS.get(name, 1500),
        "elo_source": "manual-websearch",
        "market_value_m": 200,  # placeholder, not from websearch
        "last_updated": TS,
    }

fp = RAW / f"rankings_{TS}.json"
fp.write_text(json.dumps(rankings_out, indent=2, ensure_ascii=False))
print(f"Written: {fp.name} ({len(TEAMS_ALL)} teams)")

# Write injuries
injuries_out = {
    "timestamp": TS, "status": "manual-websearch",
    "source": "fwcschedule.com + sportingnews.com",
    "teams": {}, "team_count": len(INJURIES), "total_injured": 0,
}
inj_count = 0
for team, injs in INJURIES.items():
    total_p = sum(i["penalty"] for i in injs)
    injuries_out["teams"][team] = {"injuries": injs, "injury_penalty": total_p}
    inj_count += len(injs)
injuries_out["total_injured"] = inj_count

fp = RAW / f"injuries_{TS}.json"
fp.write_text(json.dumps(injuries_out, indent=2, ensure_ascii=False))
print(f"Written: {fp.name} ({inj_count} injuries across {len(INJURIES)} teams)")

# Write polymarket
pm_out = {
    "timestamp": TS, "status": "manual-websearch",
    "source": "polymarketworldcup.com",
    "matches_matched": len(POLYMARKET_MATCHES),
    "predictions": {},
}
for mid, odds in POLYMARKET_MATCHES.items():
    hp, dp, ap = odds["home_pct"], odds["draw_pct"], odds["away_pct"]
    if hp > dp and hp > ap:
        goals = max(1, round(hp / 20))
        pm_out["predictions"][str(mid)] = {"score": f"{goals}-0", "home_prob": hp*100, "away_prob": ap*100}
    elif ap > hp:
        goals = max(1, round(ap / 20))
        pm_out["predictions"][str(mid)] = {"score": f"0-{goals}", "home_prob": hp*100, "away_prob": ap*100}
    else:
        pm_out["predictions"][str(mid)] = {"score": "1-1", "home_prob": hp*100, "away_prob": ap*100}

fp = RAW / f"polymarket_{TS}.json"
fp.write_text(json.dumps(pm_out, indent=2, ensure_ascii=False))
print(f"Written: {fp.name} ({len(POLYMARKET_MATCHES)} matches)")

print("\nDone. Run agent_integrator.py to apply to team_strengths.json")
