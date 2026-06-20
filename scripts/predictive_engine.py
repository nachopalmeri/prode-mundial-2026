#!/usr/bin/env python3
"""Dynamic probabilistic engine for the World Cup 2026 prode."""

from __future__ import annotations

import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from prode_core import (
    HTML_PATH,
    SOURCE_KEYS,
    get_source_weights,
    get_total_weight,
    Match,
    consensus_score,
    load_matches,
    parse_score,
    validate_matches,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
TEAM_STRENGTHS_PATH = DATA_DIR / "config" / "team_strengths.json"
WC_HISTORY_PATH = DATA_DIR / "config" / "wc_history.json"
H2H_PATH = DATA_DIR / "config" / "h2h_matches.json"
RUNTIME_PATH = DATA_DIR / "runtime" / "results.json"
OUTPUT_PATH = DATA_DIR / "model" / "latest_predictions.json"
BIAS_PATH = DATA_DIR / "model" / "source_bias.json"
DRAW_INFLATION_PATH = DATA_DIR / "model" / "draw_inflation.json"
MODEL_VERSION = "dynamic-prode-v2"

_DRAW_INFLATION_CACHE: float | None = None
_INJURY_CACHE: dict[str, Any] | None = None


def load_draw_inflation() -> float:
    global _DRAW_INFLATION_CACHE
    if _DRAW_INFLATION_CACHE is not None:
        return _DRAW_INFLATION_CACHE
    if DRAW_INFLATION_PATH.exists():
        try:
            data = json.loads(DRAW_INFLATION_PATH.read_text(encoding="utf-8"))
            base = float(data.get("base_inflation", 0.55))
            _DRAW_INFLATION_CACHE = base
            return base
        except (json.JSONDecodeError, ValueError, TypeError):
            pass
    _DRAW_INFLATION_CACHE = 0.55
    return 0.55


def dixon_coles_rho(home_mean: float, away_mean: float, rho: float = -0.13) -> dict[tuple[int, int], float]:
    """Dixon-Coles low-score correlation adjustment factors.

    Models the negative correlation between home and away goals in low-scoring
    matches. Returns a dict mapping (hg, ag) to their correction factor τ(x,y).

    τ(0,0) = 1 - λ·μ·ρ   (fewer scoreless draws than independent Poisson)
    τ(0,1) = 1 + λ·ρ     (more 0-1 than independent)
    τ(1,0) = 1 + μ·ρ     (more 1-0 than independent)
    τ(1,1) = 1 - ρ       (fewer 1-1 than independent)
    τ(x,y) = 1           (otherwise -- no correction for high scores)
    """
    rho = max(-0.40, min(-0.01, rho))
    factors: dict[tuple[int, int], float] = {}
    for x in range(9):
        for y in range(9):
            if x == 0 and y == 0:
                factors[(x, y)] = 1.0 - home_mean * away_mean * rho
            elif x == 0 and y == 1:
                factors[(x, y)] = 1.0 + home_mean * rho
            elif x == 1 and y == 0:
                factors[(x, y)] = 1.0 + away_mean * rho
            elif x == 1 and y == 1:
                factors[(x, y)] = 1.0 - rho
            else:
                factors[(x, y)] = 1.0
    return factors


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_bias() -> dict[str, dict]:
    return load_json(BIAS_PATH, {})


def load_wc_history() -> dict[str, Any]:
    return load_json(WC_HISTORY_PATH, {})


def compute_wc_history_score(team: str, wc_data: dict[str, Any]) -> float:
    entry = wc_data.get(team, {})
    titles = entry.get("titles", 0)
    appearances = entry.get("appearances", 0)
    best = entry.get("best_result", "Never qualified")

    score = 0.0
    score += titles * 0.15
    score += min(appearances, 15) * 0.02
    if best == "Champion":
        score += 0.05
    elif best in ("Runner-up",):
        score += 0.03
    elif best in ("Fourth place", "Semi-finals"):
        score += 0.02
    elif best in ("Quarter-finals",):
        score += 0.01
    return min(score, 1.0)


def load_h2h() -> dict[str, Any]:
    return load_json(H2H_PATH, {})


def load_injuries() -> dict[str, Any]:
    global _INJURY_CACHE
    if _INJURY_CACHE is not None:
        return _INJURY_CACHE
    path = DATA_DIR / "config" / "injuries.json"
    _INJURY_CACHE = load_json(path, {})
    return _INJURY_CACHE


def compute_h2h_score(team1: str, team2: str, h2h_data: dict[str, Any]) -> float:
    """Compute H2H advantage for team1 over team2.
    Returns +0.3 if team1 dominates, -0.3 if team2 dominates, 0 if even or unknown."""
    pair = f"{team1}__{team2}"
    pair_rev = f"{team2}__{team1}"
    entry = h2h_data.get(pair) or h2h_data.get(pair_rev)
    if not entry:
        return 0.0
    mp = entry.get("matches_played", 0)
    if mp == 0:
        return 0.0
    t1w = entry.get("team1_wins", 0)
    t2w = entry.get("team2_wins", 0)
    draws = entry.get("draws", 0)
    t1g = entry.get("team1_goals", 0)
    t2g = entry.get("team2_goals", 0)

    # Use goal difference as the primary signal
    total = t1w + draws + t2w
    if total == 0:
        return 0.0

    # Win rate advantage (capped)
    is_forward = pair in h2h_data
    if is_forward:
        win_rate = (t1w + 0.5 * draws) / total
    else:
        win_rate = (t2w + 0.5 * draws) / total

    # Goal differential per match
    if is_forward:
        gd_per_match = (t1g - t2g) / max(mp, 1)
    else:
        gd_per_match = (t2g - t1g) / max(mp, 1)

    # Combined score: win_rate (0-1) scaled + goal_diff contribution
    score = (win_rate - 0.5) * 0.4 + gd_per_match * 0.06
    return max(-0.3, min(0.3, score))


def dynamic_blend_ratio(results_count: int) -> float:
    """Return source blend ratio based on how many results are available.
    Early: trust the statistical model more.
    After ~20 results: trust sources more.
    """
    return max(0.35, min(0.75, 0.35 + results_count * 0.02))


def poisson_probability(mean_goals: float, goals: int) -> float:
    return math.exp(-mean_goals) * (mean_goals**goals) / math.factorial(goals)


def weighted_source_goals(match: Match) -> tuple[float, float]:
    sw = get_source_weights()
    tw = get_total_weight()
    home_goals = 0.0
    away_goals = 0.0
    for key, score in match.predictions.items():
        home, away = parse_score(score)
        weight = sw[key]
        home_goals += home * weight
        away_goals += away * weight
    return home_goals / tw, away_goals / tw


def weighted_outcomes(match: Match) -> dict[str, float]:
    sw = get_source_weights()
    tw = get_total_weight()
    totals = {"home": 0.0, "draw": 0.0, "away": 0.0}
    for key, score in match.predictions.items():
        home, away = parse_score(score)
        weight = sw[key]
        if home > away:
            totals["home"] += weight
        elif away > home:
            totals["away"] += weight
        else:
            totals["draw"] += weight
    return {key: value / tw for key, value in totals.items()}


def _form_to_float(form_val: Any) -> float:
    if isinstance(form_val, (int, float)):
        return float(form_val)
    if isinstance(form_val, list):
        if not form_val:
            return 0.0
        scores = []
        for m in form_val:
            r = m.get("r", "D")
            scores.append({"W": 1.0, "D": 0.5, "L": 0.0}.get(r, 0.5))
        return sum(scores) / len(scores)
    return 0.0


def team_prior(team: str, priors: dict[str, Any]) -> dict[str, float]:
    teams = priors.get("teams", {})
    if team not in teams:
        prior = {
            "elo": 1500.0,
            "fifa_rank": 48.0,
            "market_value_m": 150.0,
            "home_boost": 0.0,
            "attack": 1.0,
            "defense": 1.0,
            "form": 0.0,
            "style_tempo": 1.0,
            "injury_penalty": 0.0,
            "h2h_bonus": 0.0,
        }
    else:
        raw = teams[team]
        prior = {
            "elo": float(raw.get("elo", 1500)),
            "fifa_rank": float(raw.get("fifa_rank", 48)),
            "market_value_m": float(raw.get("market_value_m", 150)),
            "home_boost": float(raw.get("home_boost", 0.0)),
            "attack": float(raw.get("attack", 1.0)),
            "defense": float(raw.get("defense", 1.0)),
            "form": _form_to_float(raw.get("form", 0.0)),
            "style_tempo": float(raw.get("style_tempo", 1.0)),
            "injury_penalty": float(raw.get("injury_penalty", 0.0)),
            "h2h_bonus": float(raw.get("h2h_bonus", 0.0)),
        }
    # Apply injury + suspension penalty from live data
    injuries = load_injuries()
    if team in injuries:
        team_ij = injuries[team]
        out_n = len(team_ij.get("out", []))
        dbt_n = len(team_ij.get("doubtful", []))
        sus_n = len(team_ij.get("suspended", []))
        total = 0.15 * out_n + 0.05 * dbt_n + 0.15 * sus_n
        if total > 0:
            prior["injury_penalty"] += min(1.2, total)
    return prior


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


def correct_source_goals(match: Match, biases: dict[str, dict]) -> tuple[float, float]:
    """Apply bias correction per source before computing weighted goals."""
    sw = get_source_weights()
    tw = get_total_weight()
    home_goals = 0.0
    away_goals = 0.0
    for key, score in match.predictions.items():
        home, away = parse_score(score)
        weight = sw[key]
        b = biases.get(key, {})
        home_corrected = home - b.get("goal_bias_home", 0.0)
        away_corrected = away - b.get("goal_bias_away", 0.0)
        home_corrected = max(0, home_corrected)
        away_corrected = max(0, away_corrected)
        home_goals += home_corrected * weight
        away_goals += away_corrected * weight
    return home_goals / tw, away_goals / tw


def prior_adjusted_goals(match: Match, priors: dict[str, Any], motivation: dict[str, Any],
                         runtime: dict[str, Any], biases: dict[str, dict] | None = None,
                         wc_data: dict[str, Any] | None = None,
                         h2h_data: dict[str, Any] | None = None) -> tuple[float, float]:
    home = team_prior(match.home, priors)
    away = team_prior(match.away, priors)
    biases = load_bias() if biases is None else biases
    wc_data = load_wc_history() if wc_data is None else wc_data
    h2h_data = load_h2h() if h2h_data is None else h2h_data

    # Bias-corrected source goals
    source_home, source_away = correct_source_goals(match, biases)

    # Dynamic blend ratio based on results available
    results_count = len(runtime.get("results", {}))
    blend = dynamic_blend_ratio(results_count)

    elo_delta = (home["elo"] - away["elo"]) / 400.0
    market_delta = math.log((home["market_value_m"] + 40.0) / (away["market_value_m"] + 40.0))
    rank_delta = (away["fifa_rank"] - home["fifa_rank"]) / 48.0
    context_delta = home["home_boost"] - away["home_boost"] + home["form"] - away["form"] + home["h2h_bonus"] - away["h2h_bonus"]
    injury_delta = away["injury_penalty"] - home["injury_penalty"]
    wc_delta = compute_wc_history_score(match.home, wc_data) - compute_wc_history_score(match.away, wc_data)
    h2h_delta = compute_h2h_score(match.home, match.away, h2h_data)

    strength_delta = (0.30 * elo_delta + 0.12 * market_delta + 0.10 * rank_delta
                      + 0.13 * context_delta + 0.15 * injury_delta + 0.10 * wc_delta + 0.10 * h2h_delta)
    tempo_delta = float(motivation["home"]["tempo"]) + float(motivation["away"]["tempo"])
    tempo = max(0.78, min(1.25, (home["style_tempo"] + away["style_tempo"]) / 2.0 + tempo_delta))

    home_attack = max(0.45, home["attack"] + float(motivation["home"]["attack"]))
    away_attack = max(0.45, away["attack"] + float(motivation["away"]["attack"]))
    home_defense = max(0.55, home["defense"] + float(motivation["home"]["defense"]))
    away_defense = max(0.55, away["defense"] + float(motivation["away"]["defense"]))

    model_home = 1.32 * tempo * home_attack / max(0.72, away_defense) * math.exp(strength_delta * 0.34)
    model_away = 1.12 * tempo * away_attack / max(0.72, home_defense) * math.exp(-strength_delta * 0.34)

    blended_home = blend * source_home + (1 - blend) * model_home
    blended_away = blend * source_away + (1 - blend) * model_away

    return max(0.12, min(4.8, blended_home)), max(0.12, min(4.8, blended_away))


def score_matrix(home_mean: float, away_mean: float, match: Match, draw_inflation_base: float = 0.55) -> list[dict[str, Any]]:
    source_score = consensus_score(match.predictions).replace(" ", "")
    rows: list[dict[str, Any]] = []

    # Dixon-Coles ρ correction: fixed reference (0.55 = neutral draw base).
    # draw_inflation_base is now calibrated independently (0.30-2.00 range).
    dc_rho = max(-0.40, min(-0.01, -0.13))
    dc_factors = dixon_coles_rho(home_mean, away_mean, dc_rho)

    for home_goals in range(9):
        for away_goals in range(9):
            score = f"{home_goals}-{away_goals}"
            probability = poisson_probability(home_mean, home_goals) * poisson_probability(away_mean, away_goals)
            if score == source_score:
                probability *= 1.18
            elif score in match.predictions.values():
                probability *= 1.06
            # Dixon-Coles low-score correlation
            probability *= dc_factors.get((home_goals, away_goals), 1.0)
            rows.append({"score": score, "probability": probability})

    total = sum(row["probability"] for row in rows)
    return [
        {"score": row["score"], "probability": row["probability"] / total}
        for row in sorted(rows, key=lambda item: item["probability"], reverse=True)
    ]


def monte_carlo_simulation(home_mean: float, away_mean: float, n_simulations: int = 10000, dc_factors: dict[tuple[int, int], float] | None = None) -> dict[str, Any]:
    home_wins = 0
    draws = 0
    away_wins = 0
    total_home_goals = 0
    total_away_goals = 0
    over_2_5 = 0
    both_teams_score = 0
    score_counts: dict[tuple[int, int], int] = {}
    rng = random.Random()

    for _ in range(n_simulations):
        if dc_factors is not None:
            hg, ag = _dc_poisson_sample(home_mean, away_mean, dc_factors, rng)
        else:
            hg = 0
            p = 1.0
            while p > math.exp(-home_mean):
                p *= random.random()
                hg += 1
            hg = max(0, hg - 1)
            ag = 0
            p = 1.0
            while p > math.exp(-away_mean):
                p *= random.random()
                ag += 1
            ag = max(0, ag - 1)

        total_home_goals += hg
        total_away_goals += ag
        key = (hg, ag)
        score_counts[key] = score_counts.get(key, 0) + 1

        if hg > ag:
            home_wins += 1
        elif ag > hg:
            away_wins += 1
        else:
            draws += 1

        if hg + ag > 2:
            over_2_5 += 1
        if hg > 0 and ag > 0:
            both_teams_score += 1

    most_likely = sorted(
        [
            {"score": f"{h}-{a}", "probability": round(c / n_simulations * 100, 1)}
            for (h, a), c in score_counts.items()
        ],
        key=lambda x: x["probability"],
        reverse=True,
    )[:5]

    return {
        "n_simulations": n_simulations,
        "home_win_pct": round(home_wins / n_simulations * 100, 1),
        "draw_pct": round(draws / n_simulations * 100, 1),
        "away_win_pct": round(away_wins / n_simulations * 100, 1),
        "most_likely_scores": most_likely,
        "expected_goals": {
            "home": round(total_home_goals / n_simulations, 2),
            "away": round(total_away_goals / n_simulations, 2),
        },
        "over_under_2_5": round(over_2_5 / n_simulations * 100, 1),
        "both_teams_score": round(both_teams_score / n_simulations * 100, 1),
    }


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


def value_ranked_picks(
    matrix: list[dict[str, Any]],
    one_x_two: dict[str, float],
    pool_size: int = 13,
    default_consensus: float = 0.5,
) -> dict[str, Any]:
    """Rank score predictions by expected value for a prode pool of N people.
    
    V(pick) = [P(exacto) * 3 + P(ganador) * 1] * (1 - consensus * (1 - 1/pool_size))
    
    Returns best_value_pick, consensus_pick, and a differentiation strategy label.
    """
    pool_adjust = 1.0 / max(pool_size, 2)
    
    scored = []
    for item in matrix:
        score = item["score"]
        prob = item["probability"]
        hg, ag = parse_score(score)
        if hg > ag:
            winner_prob = prob + (one_x_two["home"] - prob)
        elif ag > hg:
            winner_prob = prob + (one_x_two["away"] - prob)
        else:
            winner_prob = prob + (one_x_two["draw"] - prob)
        
        expected_pts = prob * 3.0 + (winner_prob - prob) * 1.0
        consensus = default_consensus
        diff_factor = 1.0 - consensus * (1.0 - pool_adjust)
        value = expected_pts * max(diff_factor, 0.05)
        scored.append({"score": score, "prob": prob, "value": value})
    
    scored.sort(key=lambda x: x["value"], reverse=True)
    best_value = scored[0]["score"] if scored else "0-0"
    scored_by_prob = sorted(scored, key=lambda x: x["prob"], reverse=True)
    consensus_pick = scored_by_prob[0]["score"] if scored_by_prob else "0-0"
    
    # Determine strategy
    max_prob = scored_by_prob[0]["prob"] if scored_by_prob else 0
    value_diff = scored[0]["value"] - scored_by_prob[0]["value"] if scored and scored_by_prob else 0
    
    if max_prob > 0.72:
        strategy = "safe"
    elif max_prob > 0.60:
        strategy = "semi-value" if value_diff > 0.01 else "safe"
    else:
        strategy = "value"
    
    return {
        "best_value_pick": best_value,
        "consensus_pick": consensus_pick,
        "strategy": strategy,
        "value_diff": round(value_diff, 3),
        "top_value_scores": scored[:3] if scored else [],
    }


def build_match_prediction(
    match: Match,
    priors: dict[str, Any],
    runtime: dict[str, Any],
    standings: dict[str, dict[str, dict[str, int]]],
    biases: dict[str, dict] | None = None,
    wc_data: dict[str, Any] | None = None,
    h2h_data: dict[str, Any] | None = None,
    draw_inflation_base: float | None = None,
) -> dict[str, Any]:
    results = runtime.get("results", {})
    played_result = results.get(str(match.id))
    motivation = motivation_profile(match, standings)
    home_mean, away_mean = prior_adjusted_goals(match, priors, motivation, runtime, biases, wc_data, h2h_data)
    wc_data = load_wc_history() if wc_data is None else wc_data
    h2h_data = load_h2h() if h2h_data is None else h2h_data
    h2h_delta = compute_h2h_score(match.home, match.away, h2h_data)
    dib = draw_inflation_base if draw_inflation_base is not None else load_draw_inflation()
    matrix = score_matrix(home_mean, away_mean, match, dib)
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

    # Value optimization for prode pools
    value_info = value_ranked_picks(matrix, one_x_two, pool_size=13, default_consensus=0.5)

    return {
        "id": match.id,
        "group": match.group,
        "date": match.date,
        "time": match.time,
        "home": match.home,
        "away": match.away,
        "wc_history": {
            "home": wc_data.get(match.home, {"appearances": 0, "titles": 0, "best_result": "Unknown"}),
            "away": wc_data.get(match.away, {"appearances": 0, "titles": 0, "best_result": "Unknown"}),
        },
        "h2h_advantage": round(h2h_delta, 3),
        "best_pick": top_three[0]["score"],
        "best_value_pick": value_info["best_value_pick"],
        "strategy": value_info["strategy"],
        "value_diff": value_info["value_diff"],
        "consensus_pick": value_info["consensus_pick"],
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
        "monte_carlo": monte_carlo_simulation(home_mean, away_mean, 10000, dc_factors=dixon_coles_rho(home_mean, away_mean, max(-0.40, min(-0.01, -0.13)))),
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
    biases = load_bias()
    wc_data = load_wc_history()
    h2h_data = load_h2h()
    standings = calculate_standings(matches, runtime)
    dib = load_draw_inflation()
    predictions = [build_match_prediction(match, priors, runtime, standings, biases, wc_data, h2h_data, dib) for match in matches]
    knockout = generate_knockout_bracket(predictions, priors, wc_data, h2h_data)

    return {
        "metadata": {
            "model_version": MODEL_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "match_count": len(predictions),
            "knockout_match_count": len(knockout["knockout_predictions"]),
            "source_count": len(SOURCE_KEYS),
            "strategy": "dynamic_blend_bias_corrected_v2",
            "runtime_results_count": len(runtime.get("results", {})),
            "dynamic_context": "group_standings_and_round_motivation",
            "bias_correction": True,
            "draw_inflation": True,
            "draw_inflation_base": dib,
        },
        "standings": standings,
        "matches": predictions,
        **knockout,
    }


KNOCKOUT_MATCH_START = 73
TOTAL_GROUP_MATCHES = 72

R32_BRACKET = [
    (73, ("R", "A"), ("R", "B")),
    (74, ("W", "E"), ("3RD", ["A", "B", "C", "D", "F"])),
    (75, ("W", "F"), ("R", "C")),
    (76, ("W", "C"), ("R", "F")),
    (77, ("W", "I"), ("3RD", ["C", "D", "F", "G", "H"])),
    (78, ("R", "E"), ("R", "I")),
    (79, ("W", "A"), ("3RD", ["C", "E", "F", "H", "I"])),
    (80, ("W", "L"), ("3RD", ["E", "H", "I", "J", "K"])),
    (81, ("W", "D"), ("3RD", ["B", "E", "F", "I", "J"])),
    (82, ("W", "G"), ("3RD", ["A", "E", "H", "I", "J"])),
    (83, ("R", "K"), ("R", "L")),
    (84, ("W", "H"), ("R", "J")),
    (85, ("W", "B"), ("3RD", ["E", "F", "G", "I", "J"])),
    (86, ("W", "J"), ("R", "H")),
    (87, ("W", "K"), ("3RD", ["D", "E", "I", "J", "L"])),
    (88, ("R", "D"), ("R", "G")),
]

R16_PARENTS = [
    (89, 74, 77),
    (90, 73, 75),
    (91, 83, 84),
    (92, 81, 82),
    (93, 76, 78),
    (94, 79, 80),
    (95, 86, 88),
    (96, 85, 87),
]

QF_PARENTS = [
    (97, 89, 90),
    (98, 93, 94),
    (99, 91, 92),
    (100, 95, 96),
]

SF_PARENTS = [
    (101, 97, 98),
    (102, 99, 100),
]

FINAL_PARENTS = [
    (103, 101, 102),
]

THIRD_PLACE_PARENTS = [
    (104, 101, 102),
]


def _simulate_group_standings(predictions: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, float]]]:
    """Deterministic group standings using most likely outcome per match (for bracket propagation)."""
    groups: dict[str, dict[str, dict[str, float]]] = {}
    for p in predictions:
        g = p["group"]
        groups.setdefault(g, {})
        groups[g].setdefault(p["home"], {"played": 0, "points": 0, "gf": 0, "ga": 0, "gd": 0})
        groups[g].setdefault(p["away"], {"played": 0, "points": 0, "gf": 0, "ga": 0, "gd": 0})
        ox2 = p["one_x_two"]
        best_outcome = max(ox2, key=ox2.get)
        eh, ea = p["expected_goals"]["home"], p["expected_goals"]["away"]
        if best_outcome == "home":
            hg, ag = max(1, round(eh)), max(0, round(ea))
        elif best_outcome == "away":
            hg, ag = max(0, round(eh)), max(1, round(ea))
        else:
            hg = ag = max(1, round((eh + ea) / 2))
        groups[g][p["home"]]["played"] += 1
        groups[g][p["home"]]["gf"] += hg
        groups[g][p["home"]]["ga"] += ag
        groups[g][p["away"]]["played"] += 1
        groups[g][p["away"]]["gf"] += ag
        groups[g][p["away"]]["ga"] += hg
        if hg > ag:
            groups[g][p["home"]]["points"] += 3
        elif ag > hg:
            groups[g][p["away"]]["points"] += 3
        else:
            groups[g][p["home"]]["points"] += 1
            groups[g][p["away"]]["points"] += 1
        groups[g][p["home"]]["gd"] = groups[g][p["home"]]["gf"] - groups[g][p["home"]]["ga"]
        groups[g][p["away"]]["gd"] = groups[g][p["away"]]["gf"] - groups[g][p["away"]]["ga"]
    return groups


def sequential_monte_carlo(
    predictions: list[dict[str, Any]],
    n_simulations: int = 10000,
    seed: int = 42,
) -> dict[str, Any]:
    """Run n_simulations of full group stage, return qualification probabilities per team.
    
    For each simulation: for each match, sample Poisson(home_xG) vs Poisson(away_xG),
    compute standings (PTS/GD/GF), determine qualified teams.
    Aggregate across all simulations.
    """
    import random as _random
    rng = _random.Random(seed)
    # Group matches by group
    group_matches: dict[str, list[dict]] = {}
    for p in predictions:
        g = p["group"]
        group_matches.setdefault(g, [])
        group_matches[g].append(p)
    
    # {group: {team: {"winner": count, "runner_up": count, "third": count, "total": count}}}
    team_probs: dict[str, dict[str, dict[str, float]]] = {}
    all_teams: set[str] = set()
    
    for g, matches in group_matches.items():
        team_probs[g] = {}
        for m in matches:
            team_probs[g].setdefault(m["home"], {"winner": 0, "runner_up": 0, "third": 0, "total": 0})
            team_probs[g].setdefault(m["away"], {"winner": 0, "runner_up": 0, "third": 0, "total": 0})
            all_teams.add(m["home"])
            all_teams.add(m["away"])
    
    # Precompute Dixon-Coles rho for MC sampling
    mc_home_totals: dict[int, float] = {}
    mc_away_totals: dict[int, float] = {}
    mc_match_keys: dict[int, tuple[int, int]] = {}
    mc_dc_factors: dict[int, dict[tuple[int, int], float]] = {}

    for g, matches in group_matches.items():
        for m in matches:
            mid = m["id"]
            eh, ea = m["expected_goals"]["home"], m["expected_goals"]["away"]
            mc_home_totals[mid] = eh
            mc_away_totals[mid] = ea
            mc_match_keys[mid] = (eh, ea)
            dc_rho = max(-0.40, min(-0.01, -0.13 * (load_draw_inflation() / 0.55)))
            mc_dc_factors[mid] = dixon_coles_rho(eh, ea, dc_rho)

    for _ in range(n_simulations):
        for g, matches in group_matches.items():
            standings: dict[str, dict[str, float]] = {}
            for m in matches:
                h = m["home"]
                a = m["away"]
                standings.setdefault(h, {"points": 0, "gd": 0, "gf": 0})
                standings.setdefault(a, {"points": 0, "gd": 0, "gf": 0})
                mid = m["id"]
                eh, ea = mc_home_totals[mid], mc_away_totals[mid]
                dc_f = mc_dc_factors[mid]

                if m.get("played") and m.get("played_result"):
                    parts = m["played_result"].split("-")
                    if len(parts) == 2:
                        hg, ag = int(parts[0]), int(parts[1])
                    else:
                        hg, ag = _dc_poisson_sample(eh, ea, dc_f, rng)
                else:
                    hg, ag = _dc_poisson_sample(eh, ea, dc_f, rng)
                
                standings[h]["gf"] += hg
                standings[h]["gd"] += hg - ag
                standings[a]["gf"] += ag
                standings[a]["gd"] += ag - hg
                if hg > ag:
                    standings[h]["points"] += 3
                elif ag > hg:
                    standings[a]["points"] += 3
                else:
                    standings[h]["points"] += 1
                    standings[a]["points"] += 1
            
            # Sort by points, GD, GF
            sorted_teams = sorted(standings.items(), key=lambda x: (-x[1]["points"], -x[1]["gd"], -x[1]["gf"]))
            for idx, (team, _) in enumerate(sorted_teams):
                if idx == 0:
                    team_probs[g][team]["winner"] += 1
                elif idx == 1:
                    team_probs[g][team]["runner_up"] += 1
                elif idx == 2:
                    team_probs[g][team]["third"] += 1
                team_probs[g][team]["total"] += 1
    
    # Convert to percentages
    result: dict[str, dict[str, dict[str, float]]] = {}
    for g, teams in team_probs.items():
        result[g] = {}
        for team, counts in teams.items():
            n = counts["total"]
            result[g][team] = {
                "winner_pct": round(counts["winner"] / n * 100, 1),
                "runner_up_pct": round(counts["runner_up"] / n * 100, 1),
                "third_pct": round(counts["third"] / n * 100, 1),
                "qualify_pct": round((counts["winner"] + counts["runner_up"]) / n * 100, 1),
            }
    
    return result


def _poisson_sample(lam: float, rng) -> int:
    """Sample from Poisson distribution using Knuth's algorithm."""
    if lam <= 0:
        return 0
    L = math.exp(-lam)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= rng.random()
    return k - 1


def _dc_poisson_sample(
    home_mean: float, away_mean: float,
    dc_factors: dict[tuple[int, int], float],
    rng,
) -> tuple[int, int]:
    """Sample from bivariate Poisson with Dixon-Coles correlation."""
    max_tau = max(dc_factors.values()) if dc_factors else 1.0
    for _attempt in range(50):
        hg = _poisson_sample(home_mean, rng)
        ag = _poisson_sample(away_mean, rng)
        tau = dc_factors.get((hg, ag), 1.0)
        if rng.random() < tau / max_tau:
            return hg, ag
    return _poisson_sample(home_mean, rng), _poisson_sample(away_mean, rng)


def _get_qualified_teams(
    sim_standings: dict[str, dict[str, dict[str, float]]],
) -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    groups: dict[str, dict[str, str]] = {}
    all_third: list[tuple[str, str, dict[str, float]]] = []
    for gn in sorted(sim_standings.keys()):
        st = sim_standings[gn]
        st_sorted = sorted(st.items(), key=lambda x: (-x[1]["points"], -x[1]["gd"], -x[1]["gf"]))
        groups[gn] = {"winner": st_sorted[0][0], "runner_up": st_sorted[1][0]}
        if len(st_sorted) > 2:
            all_third.append((gn, st_sorted[2][0], st_sorted[2][1]))
    all_third.sort(key=lambda x: (-x[2]["points"], -x[2]["gd"], -x[2]["gf"]))
    best_third: dict[str, str] = {item[0]: item[1] for item in all_third[:8]}
    return groups, best_third


def _resolve_third_place_opponent(
    allowed_groups: list[str],
    best_third: dict[str, str],
    assigned: set[str],
) -> str | None:
    candidates = [(g, best_third[g]) for g in allowed_groups if g in best_third and g not in assigned]
    if candidates:
        assigned.add(candidates[0][0])
        return candidates[0][1]
    remaining = [g for g in best_third if g not in assigned]
    if remaining:
        assigned.add(remaining[0])
        return best_third[remaining[0]]
    return None


def _get_bracket_team(
    spec: tuple[str, str],
    groups: dict[str, dict[str, str]],
    best_third: dict[str, str],
    assigned_third: set[str],
) -> str | None:
    spec_type, spec_val = spec
    if spec_type == "W":
        return groups.get(spec_val, {}).get("winner")
    if spec_type == "R":
        return groups.get(spec_val, {}).get("runner_up")
    if spec_type == "3RD":
        return _resolve_third_place_opponent(spec_val, best_third, assigned_third)
    return None


def _get_knockout_round_name(match_id: int) -> str:
    if match_id <= 88:
        return "R32"
    if match_id <= 96:
        return "R16"
    if match_id <= 100:
        return "QF"
    if match_id <= 102:
        return "SF"
    if match_id == 103:
        return "F"
    return "3P"


def source_implied_strength_delta(
    home: str, away: str, matches: list[dict[str, Any]]
) -> float:
    """Compute strength delta from source consensus across all group matches
    involving these teams. Positive = home is stronger according to sources.
    """
    home_source_goals = 0.0
    home_source_against = 0.0
    home_count = 0
    away_source_goals = 0.0
    away_source_against = 0.0
    away_count = 0

    for mp in matches:
        if mp["home"] == home:
            home_source_goals += mp["expected_goals"]["home"]
            home_source_against += mp["expected_goals"]["away"]
            home_count += 1
        elif mp["away"] == home:
            home_source_goals += mp["expected_goals"]["away"]
            home_source_against += mp["expected_goals"]["home"]
            home_count += 1
        if mp["home"] == away:
            away_source_goals += mp["expected_goals"]["home"]
            away_source_against += mp["expected_goals"]["away"]
            away_count += 1
        elif mp["away"] == away:
            away_source_goals += mp["expected_goals"]["away"]
            away_source_against += mp["expected_goals"]["home"]
            away_count += 1

    if home_count == 0 or away_count == 0:
        return 0.0

    home_gf_avg = home_source_goals / home_count
    home_ga_avg = home_source_against / home_count
    away_gf_avg = away_source_goals / away_count
    away_ga_avg = away_source_against / away_count

    return (home_gf_avg - home_ga_avg) - (away_gf_avg - away_ga_avg)


def knockout_match_prediction(
    match_id: int,
    home: str,
    away: str,
    priors: dict[str, Any],
    matches: list[dict[str, Any]] | None = None,
    wc_data: dict[str, Any] | None = None,
    h2h_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    h = team_prior(home, priors)
    a = team_prior(away, priors)
    wc_data = load_wc_history() if wc_data is None else wc_data
    h2h_data = load_h2h() if h2h_data is None else h2h_data
    ed = (h["elo"] - a["elo"]) / 400.0
    md = math.log((h["market_value_m"] + 40.0) / (a["market_value_m"] + 40.0))
    rd = (a["fifa_rank"] - h["fifa_rank"]) / 48.0
    cd = h["home_boost"] - a["home_boost"] + h["form"] - a["form"] + h["h2h_bonus"] - a["h2h_bonus"]
    nd = a["injury_penalty"] - h["injury_penalty"]
    wcd = compute_wc_history_score(home, wc_data) - compute_wc_history_score(away, wc_data)
    h2hd = compute_h2h_score(home, away, h2h_data)

    # Add source-implied strength delta from group stage
    source_delta = source_implied_strength_delta(home, away, matches or [])

    sd = 0.33 * ed + 0.12 * md + 0.10 * rd + 0.16 * cd + 0.15 * nd + 0.14 * wcd + 0.0 * h2hd + 0.06 * source_delta
    tempo = max(0.78, min(1.25, (h["style_tempo"] + a["style_tempo"]) / 2.0))
    ha = max(0.45, h["attack"])
    aa = max(0.45, a["attack"])
    hd = max(0.55, h["defense"])
    ad = max(0.55, a["defense"])
    hm = max(0.12, min(4.8, 1.32 * tempo * ha / max(0.72, ad) * math.exp(sd * 0.34)))
    am = max(0.12, min(4.8, 1.12 * tempo * aa / max(0.72, hd) * math.exp(-sd * 0.34)))
    dc_rho = max(-0.40, min(-0.01, -0.13))
    dc_factors = dixon_coles_rho(hm, am, dc_rho)
    hw = dw = aw = 0.0
    bp, bp_prob = "", 0.0
    for hg in range(15):
        for ag in range(15):
            p = poisson_probability(hm, hg) * poisson_probability(am, ag)
            p *= dc_factors.get((hg, ag), 1.0)
            if hg > ag:
                hw += p
            elif ag > hg:
                aw += p
            else:
                dw += p
            if hg < 9 and ag < 9 and p > bp_prob:
                bp_prob = p
                bp = f"{hg}-{ag}"
    dc_ratio = min(hw, aw) / max(hw, aw, 0.01)
    etp = min(dw * (1.0 + 0.3 * dc_ratio) * 1.5, 0.48)
    pp = etp * 0.7
    pw = home if hw >= aw else away
    pl = away if pw == home else home
    pc = (max(hw, aw) - min(hw, aw)) * 100
    rn = _get_knockout_round_name(match_id)
    return {
        "id": match_id,
        "round": rn,
        "home": home,
        "away": away,
        "wc_history": {
            "home": wc_data.get(home, {"appearances": 0, "titles": 0, "best_result": "Unknown"}),
            "away": wc_data.get(away, {"appearances": 0, "titles": 0, "best_result": "Unknown"}),
        },
        "h2h_advantage": round(h2hd, 3),
        "predicted_winner": pw,
        "predicted_loser": pl,
        "winner_confidence": round(pc, 1),
        "best_pick": bp,
        "expected_goals": {"home": round(hm, 2), "away": round(am, 2)},
        "win_probabilities": {
            "home": round(hw * 100, 1),
            "draw": round(dw * 100, 1),
            "away": round(aw * 100, 1),
        },
        "extra_time_probability": round(etp * 100, 1),
        "penalties_probability": round(pp * 100, 1),
        "source_strength_delta": round(source_delta, 3),
    }


def _resolve_bracket_match(
    mid: int,
    parent1_id: int,
    parent2_id: int,
    round_matches: dict[int, dict[str, Any]],
) -> tuple[str, str]:
    p1 = round_matches.get(parent1_id, {})
    p2 = round_matches.get(parent2_id, {})
    return p1.get("predicted_winner", "TBD"), p2.get("predicted_winner", "TBD")


def _resolve_bracket_losers(
    mid: int,
    parent1_id: int,
    parent2_id: int,
    round_matches: dict[int, dict[str, Any]],
) -> tuple[str, str]:
    p1 = round_matches.get(parent1_id, {})
    p2 = round_matches.get(parent2_id, {})
    return p1.get("predicted_loser", "TBD"), p2.get("predicted_loser", "TBD")


def generate_knockout_bracket(
    predictions: list[dict[str, Any]],
    priors: dict[str, Any],
    wc_data: dict[str, Any] | None = None,
    h2h_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sim_standings = _simulate_group_standings(predictions)
    groups, best_third = _get_qualified_teams(sim_standings)
    assigned_third: set[str] = set()
    r32_matches: dict[int, dict[str, Any]] = {}
    for mid, home_spec, away_spec in R32_BRACKET:
        ht = _get_bracket_team(home_spec, groups, best_third, assigned_third)
        at = _get_bracket_team(away_spec, groups, best_third, assigned_third)
        if ht and at:
            r32_matches[mid] = knockout_match_prediction(mid, ht, at, priors, predictions, wc_data, h2h_data)

    def propagate_round(parents: list[tuple[int, int, int]], prev: dict[int, dict[str, Any]]) -> dict[int, dict[str, Any]]:
        result: dict[int, dict[str, Any]] = {}
        for mid, p1, p2 in parents:
            ht, at = _resolve_bracket_match(mid, p1, p2, prev)
            if ht != "TBD" and at != "TBD":
                result[mid] = knockout_match_prediction(mid, ht, at, priors, predictions, wc_data, h2h_data)
        return result

    r16_matches = propagate_round(R16_PARENTS, r32_matches)
    qf_matches = propagate_round(QF_PARENTS, r16_matches)
    sf_matches = propagate_round(SF_PARENTS, qf_matches)
    final_matches = propagate_round(FINAL_PARENTS, sf_matches)

    third_place: dict[int, dict[str, Any]] = {}
    for mid, p1, p2 in THIRD_PLACE_PARENTS:
        ht, at = _resolve_bracket_losers(mid, p1, p2, sf_matches)
        if ht != "TBD" and at != "TBD":
            third_place[mid] = knockout_match_prediction(mid, ht, at, priors, predictions, wc_data, h2h_data)

    all_knockout = []
    for d in (r32_matches, r16_matches, qf_matches, sf_matches, final_matches, third_place):
        all_knockout.extend(sorted(d.values(), key=lambda x: x["id"]))

    # Run Monte Carlo for group qualification probabilities
    mc_probs = sequential_monte_carlo(predictions, n_simulations=10000)

    return {
        "knockout_predictions": all_knockout,
        "knockout_probs": mc_probs,
        "knockout_standings": {
            "groups": {gn: {"winner": v["winner"], "runner_up": v["runner_up"]} for gn, v in groups.items()},
            "best_third_place": dict(list(best_third.items())[:8]),
        },
        "rounds": {
            "R32": {"start_id": 73, "end_id": 88, "count": 16},
            "R16": {"start_id": 89, "end_id": 96, "count": 8},
            "QF": {"start_id": 97, "end_id": 100, "count": 4},
            "SF": {"start_id": 101, "end_id": 102, "count": 2},
            "F": {"start_id": 103, "end_id": 103, "count": 1},
            "3P": {"start_id": 104, "end_id": 104, "count": 1},
        },
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    output = build_predictions()
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ko = len(output.get("knockout_predictions", []))
    total = len(output["matches"]) + ko
    print(f"Wrote {OUTPUT_PATH} with {len(output['matches'])} group + {ko} knockout = {total} total matches")


if __name__ == "__main__":
    main()
