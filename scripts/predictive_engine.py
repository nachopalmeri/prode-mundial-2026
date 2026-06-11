#!/usr/bin/env python3
"""Dynamic probabilistic engine for the World Cup 2026 prode."""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prode_core import (
    HTML_PATH,
    SOURCE_KEYS,
    SOURCE_WEIGHTS,
    TOTAL_WEIGHT,
    Match,
    consensus_score,
    load_matches,
    parse_score,
    validate_matches,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEAM_STRENGTHS_PATH = PROJECT_ROOT / "data" / "config" / "team_strengths.json"
RUNTIME_PATH = PROJECT_ROOT / "data" / "runtime" / "results.json"
OUTPUT_PATH = PROJECT_ROOT / "data" / "model" / "latest_predictions.json"
MODEL_VERSION = "dynamic-prode-v1"


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def poisson_probability(mean_goals: float, goals: int) -> float:
    return math.exp(-mean_goals) * (mean_goals**goals) / math.factorial(goals)


def weighted_source_goals(match: Match) -> tuple[float, float]:
    home_goals = 0.0
    away_goals = 0.0
    for key, score in match.predictions.items():
        home, away = parse_score(score)
        weight = SOURCE_WEIGHTS[key]
        home_goals += home * weight
        away_goals += away * weight
    return home_goals / TOTAL_WEIGHT, away_goals / TOTAL_WEIGHT


def weighted_outcomes(match: Match) -> dict[str, float]:
    totals = {"home": 0.0, "draw": 0.0, "away": 0.0}
    for key, score in match.predictions.items():
        home, away = parse_score(score)
        weight = SOURCE_WEIGHTS[key]
        if home > away:
            totals["home"] += weight
        elif away > home:
            totals["away"] += weight
        else:
            totals["draw"] += weight
    return {key: value / TOTAL_WEIGHT for key, value in totals.items()}


def team_prior(team: str, priors: dict[str, Any]) -> dict[str, float]:
    teams = priors.get("teams", {})
    if team not in teams:
        return {
            "elo": 1500.0,
            "fifa_rank": 48.0,
            "market_value_m": 150.0,
            "home_boost": 0.0,
            "attack": 1.0,
            "defense": 1.0,
            "form": 0.0,
            "style_tempo": 1.0,
            "injury_penalty": 0.0,
        }
    return {key: float(value) for key, value in teams[team].items()}


def get_match_round(match_id: int) -> int:
    if match_id <= 24:
        return 1
    if match_id <= 48:
        return 2
    return 3


def empty_team_row() -> dict[str, int]:
    return {"played": 0, "points": 0, "gf": 0, "ga": 0, "gd": 0}


def calculate_standings(matches: list[Match], runtime: dict[str, Any]) -> dict[str, dict[str, dict[str, int]]]:
    results = runtime.get("results", {})
    standings: dict[str, dict[str, dict[str, int]]] = {}

    for match in matches:
        group = standings.setdefault(match.group, {})
        group.setdefault(match.home, empty_team_row())
        group.setdefault(match.away, empty_team_row())
        result = results.get(str(match.id))
        if not result:
            continue

        home_goals, away_goals = parse_score(result)
        home_row = group[match.home]
        away_row = group[match.away]
        home_row["played"] += 1
        away_row["played"] += 1
        home_row["gf"] += home_goals
        home_row["ga"] += away_goals
        away_row["gf"] += away_goals
        away_row["ga"] += home_goals
        if home_goals > away_goals:
            home_row["points"] += 3
        elif away_goals > home_goals:
            away_row["points"] += 3
        else:
            home_row["points"] += 1
            away_row["points"] += 1
        home_row["gd"] = home_row["gf"] - home_row["ga"]
        away_row["gd"] = away_row["gf"] - away_row["ga"]

    return standings


def motivation_profile(match: Match, standings: dict[str, dict[str, dict[str, int]]]) -> dict[str, Any]:
    group = standings.get(match.group, {})
    home = group.get(match.home, empty_team_row())
    away = group.get(match.away, empty_team_row())
    match_round = get_match_round(match.id)

    def side_factor(row: dict[str, int]) -> dict[str, float | str]:
        played = row["played"]
        points = row["points"]
        gd = row["gd"]
        if played == 0:
            return {"attack": 0.0, "defense": 0.0, "tempo": 0.0, "label": "base"}
        if match_round == 2:
            if points == 0:
                return {"attack": 0.06, "defense": -0.03, "tempo": 0.04, "label": "needs_response"}
            if points == 3:
                return {"attack": -0.02, "defense": 0.03, "tempo": -0.02, "label": "protects_position"}
            return {"attack": 0.02, "defense": 0.0, "tempo": 0.01, "label": "balanced"}
        if match_round == 3:
            if points >= 6:
                return {"attack": -0.09, "defense": 0.02, "tempo": -0.08, "label": "likely_rotation"}
            if points >= 4 and gd >= 1:
                return {"attack": -0.04, "defense": 0.04, "tempo": -0.04, "label": "draw_acceptable"}
            if points <= 1:
                return {"attack": 0.11, "defense": -0.06, "tempo": 0.08, "label": "must_win"}
            return {"attack": 0.05, "defense": -0.02, "tempo": 0.04, "label": "qualification_pressure"}
        return {"attack": 0.0, "defense": 0.0, "tempo": 0.0, "label": "base"}

    return {
        "round": match_round,
        "home": {"standing": home, **side_factor(home)},
        "away": {"standing": away, **side_factor(away)},
    }


def prior_adjusted_goals(match: Match, priors: dict[str, Any], motivation: dict[str, Any]) -> tuple[float, float]:
    home = team_prior(match.home, priors)
    away = team_prior(match.away, priors)
    source_home, source_away = weighted_source_goals(match)

    elo_delta = (home["elo"] - away["elo"]) / 400.0
    market_delta = math.log((home["market_value_m"] + 40.0) / (away["market_value_m"] + 40.0))
    rank_delta = (away["fifa_rank"] - home["fifa_rank"]) / 48.0
    context_delta = home["home_boost"] - away["home_boost"] + home["form"] - away["form"]
    injury_delta = away["injury_penalty"] - home["injury_penalty"]

    strength_delta = 0.34 * elo_delta + 0.14 * market_delta + 0.12 * rank_delta + 0.16 * context_delta + 0.18 * injury_delta
    tempo_delta = float(motivation["home"]["tempo"]) + float(motivation["away"]["tempo"])
    tempo = max(0.78, min(1.25, (home["style_tempo"] + away["style_tempo"]) / 2.0 + tempo_delta))

    home_attack = max(0.45, home["attack"] + float(motivation["home"]["attack"]))
    away_attack = max(0.45, away["attack"] + float(motivation["away"]["attack"]))
    home_defense = max(0.55, home["defense"] + float(motivation["home"]["defense"]))
    away_defense = max(0.55, away["defense"] + float(motivation["away"]["defense"]))

    model_home = 1.32 * tempo * home_attack / max(0.72, away_defense) * math.exp(strength_delta * 0.34)
    model_away = 1.12 * tempo * away_attack / max(0.72, home_defense) * math.exp(-strength_delta * 0.34)

    blended_home = 0.62 * source_home + 0.38 * model_home
    blended_away = 0.62 * source_away + 0.38 * model_away

    return max(0.12, min(4.8, blended_home)), max(0.12, min(4.8, blended_away))


def score_matrix(home_mean: float, away_mean: float, match: Match) -> list[dict[str, Any]]:
    source_score = consensus_score(match.predictions).replace(" ", "")
    rows: list[dict[str, Any]] = []
    for home_goals in range(7):
        for away_goals in range(7):
            score = f"{home_goals}-{away_goals}"
            probability = poisson_probability(home_mean, home_goals) * poisson_probability(away_mean, away_goals)
            if score == source_score:
                probability *= 1.18
            elif score in match.predictions.values():
                probability *= 1.06
            if home_goals == away_goals:
                probability *= 1.06
            rows.append({"score": score, "probability": probability})

    total = sum(row["probability"] for row in rows)
    return [
        {"score": row["score"], "probability": row["probability"] / total}
        for row in sorted(rows, key=lambda item: item["probability"], reverse=True)
    ]


def calculate_confidence(top_scores: list[dict[str, Any]], outcomes: dict[str, float]) -> str:
    top_mass = sum(item["probability"] for item in top_scores[:3])
    best_outcome = max(outcomes.values())
    if top_mass >= 0.28 or best_outcome >= 0.72:
        return "high"
    if top_mass >= 0.20 or best_outcome >= 0.56:
        return "medium"
    return "low"


def freeze_status(match_id: int, runtime: dict[str, Any]) -> dict[str, Any]:
    frozen = runtime.get("frozen_matches", {}).get(str(match_id))
    if not frozen:
        return {"frozen": False, "reason": "open_until_match_lock"}
    if isinstance(frozen, dict):
        return {"frozen": True, **frozen}
    return {"frozen": True, "reason": "manual_lock"}


def build_match_prediction(
    match: Match,
    priors: dict[str, Any],
    runtime: dict[str, Any],
    standings: dict[str, dict[str, dict[str, int]]],
) -> dict[str, Any]:
    results = runtime.get("results", {})
    played_result = results.get(str(match.id))
    motivation = motivation_profile(match, standings)
    home_mean, away_mean = prior_adjusted_goals(match, priors, motivation)
    matrix = score_matrix(home_mean, away_mean, match)
    top_three = [
        {
            "score": item["score"],
            "home_goals": int(item["score"].split("-")[0]),
            "away_goals": int(item["score"].split("-")[1]),
            "probability": round(item["probability"] * 100, 1),
        }
        for item in matrix[:3]
    ]

    one_x_two = {"home": 0.0, "draw": 0.0, "away": 0.0}
    for item in matrix:
        home_goals, away_goals = parse_score(item["score"])
        if home_goals > away_goals:
            one_x_two["home"] += item["probability"]
        elif away_goals > home_goals:
            one_x_two["away"] += item["probability"]
        else:
            one_x_two["draw"] += item["probability"]

    market_proxy = weighted_outcomes(match)
    blended_outcomes = {
        key: round((0.72 * one_x_two[key] + 0.28 * market_proxy[key]) * 100, 1)
        for key in one_x_two
    }

    return {
        "id": match.id,
        "group": match.group,
        "date": match.date,
        "time": match.time,
        "home": match.home,
        "away": match.away,
        "best_pick": top_three[0]["score"],
        "top_scores": top_three,
        "one_x_two": blended_outcomes,
        "expected_goals": {"home": round(home_mean, 2), "away": round(away_mean, 2)},
        "confidence": calculate_confidence(matrix[:3], market_proxy),
        "source_consensus": consensus_score(match.predictions).replace(" ", ""),
        "source_agreement": round(max(market_proxy.values()) * 100, 1),
        "freeze": freeze_status(match.id, runtime),
        "played": bool(played_result),
        "played_result": played_result,
        "motivation": {
            "round": motivation["round"],
            "home": motivation["home"]["label"],
            "away": motivation["away"]["label"],
        },
        "standings_snapshot": {
            "home": motivation["home"]["standing"],
            "away": motivation["away"]["standing"],
        },
        "movement": {"direction": "flat", "delta": 0.0},
        "signals": {
            "market_source_proxy": round(max(market_proxy.values()) * 100, 1),
            "model_version": MODEL_VERSION,
        },
    }


def build_predictions() -> dict[str, Any]:
    matches = load_matches(HTML_PATH)
    errors = validate_matches(matches)
    if errors:
        raise SystemExit("Invalid match data:\n- " + "\n- ".join(errors))

    priors = load_json(TEAM_STRENGTHS_PATH, {"teams": {}})
    runtime = load_json(RUNTIME_PATH, {"results": {}, "frozen_matches": {}, "news_adjustments": {}})
    standings = calculate_standings(matches, runtime)
    predictions = [build_match_prediction(match, priors, runtime, standings) for match in matches]

    return {
        "metadata": {
            "model_version": MODEL_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "match_count": len(predictions),
            "source_count": len(SOURCE_KEYS),
            "strategy": "dynamic_top3_market_rating_consensus",
            "runtime_results_count": len(runtime.get("results", {})),
            "dynamic_context": "group_standings_and_round_motivation",
        },
        "standings": standings,
        "matches": predictions,
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = build_predictions()
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH} with {len(output['matches'])} matches")


if __name__ == "__main__":
    main()
