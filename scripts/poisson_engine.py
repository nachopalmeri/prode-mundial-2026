#!/usr/bin/env python3
"""
Poisson + Dixon-Coles goal model engine (Oloraculo clone).
Implements EloModel, GoalModel (Poisson+Dixon-Coles), and FinalPredictionSelector.

Model Ladder:
  GoalModel (Priority 4) -> EloModel (Priority 2)
  FinalPredictionSelector blends with RankingBias when models diverge.
"""

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"
OUTPUT_PATH = PROJECT_ROOT / "data" / "runtime" / "engine_predictions.json"

DIXON_COLES_RHO = -0.03
MAX_GOALS = 10
EM_ITERATIONS = 8
SHRINK_PRIOR = 2.0
CLAMP_MIN = 0.45
CLAMP_MAX = 2.25

SOURCE_KEYS = ("c", "g", "f", "fs", "esp", "yh", "tips", "e", "cup", "pm")
SOURCE_WEIGHTS = {"c": 1.6, "cup": 1.79, "e": 1.95, "esp": 1.95,
                   "f": 1.65, "fs": 1.47, "g": 1.65, "pm": 1.95,
                   "tips": 1.95, "yh": 1.19}


def parse_html():
    html = HTML_PATH.read_text(encoding="utf-8")

    ts_match = re.search(r'const TEAM_STRENGTHS\s*=\s*(\{.*?\});', html, re.DOTALL)
    if not ts_match:
        raise SystemExit("TEAM_STRENGTHS not found in HTML")
    team_strengths = json.loads(ts_match.group(1))

    op_match = re.search(r'const OLORACULO_PREDS\s*=\s*(\{.*?\});', html, re.DOTALL)
    oloraculo_preds = {}
    if op_match:
        raw = op_match.group(1)
        raw_json = re.sub(r'(?<=[{,])\s*(\d+)\s*:', r'"\1":', raw)
        try:
            oloraculo_preds = {str(k): v for k, v in json.loads(raw_json).items()}
        except json.JSONDecodeError:
            oloraculo_preds = {}

    match_objects = re.findall(r'\{id:\d+,gr:"[A-Z]",[^}]+}', html)
    matches = []
    for mo in match_objects:
        m = {}
        for key, num_val, str_val in re.findall(r'(\w+):(?:(\d+)|"([^"]*)")', mo):
            m[key] = num_val or str_val
        matches.append(m)

    return team_strengths, matches, oloraculo_preds


def parse_score(s):
    parts = s.split("-")
    return int(parts[0].strip()), int(parts[1].strip())


def poisson_prob(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def dixon_coles_tau(h, a, lam_h, lam_a, rho):
    if h == 0 and a == 0:
        return 1.0 - lam_h * lam_a * rho
    if h == 0 and a == 1:
        return 1.0 + lam_h * rho
    if h == 1 and a == 0:
        return 1.0 + lam_a * rho
    if h == 1 and a == 1:
        return 1.0 - rho
    return 1.0


def build_score_matrix(lam_home, lam_away):
    matrix = {}
    total = 0.0
    for h in range(MAX_GOALS + 1):
        for a in range(MAX_GOALS + 1):
            p_h = poisson_prob(h, lam_home)
            p_a = poisson_prob(a, lam_away)
            tau = dixon_coles_tau(h, a, lam_home, lam_away, DIXON_COLES_RHO)
            p = p_h * p_a * tau
            key = f"{h}-{a}"
            matrix[key] = p
            total += p
    if total > 0:
        for k in matrix:
            matrix[k] /= total
    return matrix


def extract_outcomes(matrix):
    hw = dw = aw = 0.0
    for score, p in matrix.items():
        hg, ag = parse_score(score)
        if hg > ag:
            hw += p
        elif ag > hg:
            aw += p
        else:
            dw += p
    return {"home": hw, "draw": dw, "away": aw}


def best_scoreline(matrix):
    return max(matrix.items(), key=lambda x: x[1])[0]


def outcome_label(probs):
    return max((k for k in ("home", "draw", "away")), key=probs.get)


def compute_consensus_scores(matches):
    consensus = {}
    for m in matches:
        mid = int(m["id"])
        h_total = a_total = w_total = 0.0
        for key in SOURCE_KEYS:
            val = m.get(key)
            if not val or "-" not in val:
                continue
            try:
                hg, ag = parse_score(val)
                w = SOURCE_WEIGHTS.get(key, 1.0)
                h_total += hg * w
                a_total += ag * w
                w_total += w
            except (ValueError, IndexError):
                pass
        if w_total > 0:
            consensus[mid] = (h_total / w_total, a_total / w_total)
        else:
            consensus[mid] = (1.0, 1.0)
    return consensus


def elo_expectation(a, b):
    return 1.0 / (1.0 + 10.0 ** ((b - a) / 400.0))


def compute_elo_model(team_strengths, matches):
    predictions = {}
    for m in matches:
        mid = int(m["id"])
        home = m["a"]
        away = m["b"]

        h_data = team_strengths.get(home, {})
        a_data = team_strengths.get(away, {})
        h_elo = h_data.get("elo", 1500)
        a_elo = a_data.get("elo", 1500)

        gap = h_elo - a_elo
        exp_h = elo_expectation(h_elo, a_elo)

        draw_prob = 0.30 * math.exp(-abs(gap) / 550.0) + 0.08
        draw_prob = max(0.08, min(0.34, draw_prob))

        home_win = exp_h * (1.0 - draw_prob)
        away_win = (1.0 - exp_h) * (1.0 - draw_prob)

        home_boost = h_data.get("home_boost", 0)
        is_neutral = (home_boost <= 0)
        base_xg = 2.6
        h_xg = base_xg * (h_elo / 1900) / (a_elo / 1900)
        a_xg = base_xg / (h_elo / 1900) * (a_elo / 1900)

        if not is_neutral:
            h_xg *= 1.08

        h_xg = max(0.3, min(4.5, h_xg))
        a_xg = max(0.2, min(3.5, a_xg))

        matrix = build_score_matrix(h_xg, a_xg)
        outcomes = extract_outcomes(matrix)

        predictions[mid] = {
            "home": round(outcomes["home"], 4),
            "draw": round(outcomes["draw"], 4),
            "away": round(outcomes["away"], 4),
            "scoreline": best_scoreline(matrix),
        }

    return predictions


def fit_goal_model(team_strengths, matches, consensus):
    attack = {}
    defense = {}
    for team, data in team_strengths.items():
        attack[team] = data.get("attack", 1.0)
        defense[team] = data.get("defense", 1.0)

    total_goals = 0.0
    for hg, ag in consensus.values():
        total_goals += hg + ag
    n_matches = len(consensus)
    avg_match_goals = total_goals / n_matches if n_matches > 0 else 2.6
    avg_goals_per_team = avg_match_goals / 2.0

    team_matches = defaultdict(list)
    for m in matches:
        mid = int(m["id"])
        home = m["a"]
        away = m["b"]
        hg, ag = consensus.get(mid, (1.0, 1.0))
        team_matches[home].append({"opponent": away, "gf": hg, "ga": ag, "is_home": True})
        team_matches[away].append({"opponent": home, "gf": ag, "ga": hg, "is_home": False})

    for iteration in range(EM_ITERATIONS):
        new_attack = {}
        new_defense = {}

        for team in sorted(attack.keys()):
            mt = team_matches.get(team, [])
            if not mt:
                new_attack[team] = attack[team]
                new_defense[team] = defense[team]
                continue

            total_gf = sum(mm["gf"] for mm in mt)
            total_ga = sum(mm["ga"] for mm in mt)

            opp_def_sum = sum(defense.get(mm["opponent"], 1.0) for mm in mt)
            opp_att_sum = sum(attack.get(mm["opponent"], 1.0) for mm in mt)

            n = len(mt)
            shrink_gf = SHRINK_PRIOR * avg_goals_per_team
            shrink_ga = SHRINK_PRIOR * avg_goals_per_team

            num_att = total_gf + shrink_gf
            den_att = avg_goals_per_team * opp_def_sum + shrink_gf
            new_attack[team] = num_att / den_att if den_att > 0 else 1.0

            num_def = total_ga + shrink_ga
            den_def = avg_goals_per_team * opp_att_sum + shrink_ga
            new_defense[team] = num_def / den_def if den_def > 0 else 1.0

        mean_att = sum(new_attack.values()) / len(new_attack)
        if mean_att > 0:
            for t in new_attack:
                new_attack[t] /= mean_att

        for t in new_attack:
            new_attack[t] = max(CLAMP_MIN, min(CLAMP_MAX, new_attack[t]))
            new_defense[t] = max(CLAMP_MIN, min(CLAMP_MAX, new_defense[t]))

        attack, defense = new_attack, new_defense

    return attack, defense, avg_goals_per_team


def compute_goal_model(attack, defense, avg_goals_per_team, matches, team_strengths):
    predictions = {}
    for m in matches:
        mid = int(m["id"])
        home = m["a"]
        away = m["b"]

        home_att = attack.get(home, 1.0)
        home_def = defense.get(home, 1.0)
        away_att = attack.get(away, 1.0)
        away_def = defense.get(away, 1.0)

        lam_h = avg_goals_per_team * home_att * away_def
        lam_a = avg_goals_per_team * away_att * home_def

        home_boost = team_strengths.get(home, {}).get("home_boost", 0)
        is_neutral = (home_boost <= 0)
        if not is_neutral:
            lam_h *= 1.08

        lam_h = max(0.1, lam_h)
        lam_a = max(0.1, lam_a)

        matrix = build_score_matrix(lam_h, lam_a)
        outcomes = extract_outcomes(matrix)

        predictions[mid] = {
            "home": round(outcomes["home"], 4),
            "draw": round(outcomes["draw"], 4),
            "away": round(outcomes["away"], 4),
            "scoreline": best_scoreline(matrix),
        }

    return predictions


def source_outcome_consensus(matches):
    outcomes = {}
    for m in matches:
        mid = int(m["id"])
        hw = dw = aw = 0.0
        for key in SOURCE_KEYS:
            val = m.get(key)
            if not val or "-" not in val:
                continue
            try:
                hg, ag = parse_score(val)
                w = SOURCE_WEIGHTS.get(key, 1.0)
                if hg > ag:
                    hw += w
                elif ag > hg:
                    aw += w
                else:
                    dw += w
            except (ValueError, IndexError):
                pass
        outcomes[mid] = outcome_label({"home": hw, "draw": dw, "away": aw})
    return outcomes


def final_prediction_selector(elo_preds, poisson_preds, matches, source_consensus_outcomes):
    engine = {}
    for m in matches:
        mid = int(m["id"])
        poiss = poisson_preds.get(mid)
        elo = elo_preds.get(mid)
        if mid in source_consensus_outcomes:
            src_out = source_consensus_outcomes[mid]
        else:
            mid_s = str(mid)
            if mid_s in source_consensus_outcomes:
                src_out = source_consensus_outcomes[mid_s]
            else:
                src_out = None

        if poiss and elo:
            poiss_out = outcome_label(poiss)
            elo_out = outcome_label(elo)
            if src_out and elo_out == src_out and poiss_out != src_out:
                for k in ("home", "draw", "away"):
                    poiss[k] = poiss[k] * 0.85 + elo.get(k, 0) * 0.15
                total = sum(poiss[k] for k in ("home", "draw", "away"))
                if total > 0:
                    for k in ("home", "draw", "away"):
                        poiss[k] = round(poiss[k] / total, 4)
            engine[mid] = poiss
        elif poiss:
            engine[mid] = poiss
        elif elo:
            engine[mid] = elo
        else:
            engine[mid] = {"home": 0.4, "draw": 0.2, "away": 0.4, "scoreline": "1-1"}

        s = engine[mid]["scoreline"]
        hg, ag = parse_score(s)
        engine[mid]["scoreline"] = f"{hg}-{ag}"

    return engine


def main():
    team_strengths, matches, oloraculo_ref = parse_html()
    n_matches = len(matches)
    print(f"[poisson_engine] Loaded {len(team_strengths)} teams, {n_matches} matches")

    consensus = compute_consensus_scores(matches)
    print(f"[poisson_engine] Computed consensus scores for {len(consensus)} matches")

    elo_preds = compute_elo_model(team_strengths, matches)
    print(f"[poisson_engine] EloModel: {len(elo_preds)} predictions")

    attack, defense, avg_goals = fit_goal_model(team_strengths, matches, consensus)
    print(f"[poisson_engine] GoalModel EM: {EM_ITERATIONS} iterations, avg_goals_per_team={avg_goals:.3f}")

    poisson_preds = compute_goal_model(attack, defense, avg_goals, matches, team_strengths)
    print(f"[poisson_engine] GoalModel: {len(poisson_preds)} predictions")

    src_outcomes = source_outcome_consensus(matches)
    engine_preds = final_prediction_selector(elo_preds, poisson_preds, matches, src_outcomes)

    elo_clean = {str(k): v for k, v in elo_preds.items()}
    poisson_clean = {str(k): v for k, v in poisson_preds.items()}
    engine_clean = {str(k): v for k, v in engine_preds.items()}

    output = {
        "engine": engine_clean,
        "elo": elo_clean,
        "poisson": poisson_clean,
        "metadata": {
            "model_version": "oloraculo-p1",
            "engine": "poisson_dixon_coles_v1",
            "match_count": n_matches,
            "em_iterations": EM_ITERATIONS,
            "dixon_coles_rho": DIXON_COLES_RHO,
            "avg_goals_per_team": round(avg_goals, 4),
            "strategy": "priority_ladder_goalModel_first",
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    print(f"[poisson_engine] Wrote {OUTPUT_PATH}")

    elo_hw = sum(1 for p in elo_preds.values() if p["home"] > p["draw"] and p["home"] > p["away"])
    elo_aw = sum(1 for p in elo_preds.values() if p["away"] > p["draw"] and p["away"] > p["home"])
    elo_d = n_matches - elo_hw - elo_aw
    print(f"[poisson_engine] Elo   | H:{elo_hw:2d} D:{elo_d:2d} A:{elo_aw:2d}")

    ps_hw = sum(1 for p in poisson_preds.values() if p["home"] > p["draw"] and p["home"] > p["away"])
    ps_aw = sum(1 for p in poisson_preds.values() if p["away"] > p["draw"] and p["away"] > p["home"])
    ps_d = n_matches - ps_hw - ps_aw
    print(f"[poisson_engine] Poisson| H:{ps_hw:2d} D:{ps_d:2d} A:{ps_aw:2d}")

    en_hw = sum(1 for p in engine_preds.values() if p["home"] > p["draw"] and p["home"] > p["away"])
    en_aw = sum(1 for p in engine_preds.values() if p["away"] > p["draw"] and p["away"] > p["home"])
    en_d = n_matches - en_hw - en_aw
    print(f"[poisson_engine] Engine | H:{en_hw:2d} D:{en_d:2d} A:{en_aw:2d}")


if __name__ == "__main__":
    main()
