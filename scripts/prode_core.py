#!/usr/bin/env python3
"""Core utilities for the World Cup 2026 prode model."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


import json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = PROJECT_ROOT / "prode-mundial-2026.html"
WEIGHTS_PATH = PROJECT_ROOT / "data" / "model" / "weights_latest.json"

SOURCE_KEYS = ("c", "g", "f", "fs", "esp", "yh", "tips", "e", "cup", "pm")

_DEFAULT_WEIGHTS = {
    "c": 1.0,
    "g": 1.0,
    "f": 1.0,
    "fs": 0.8,
    "esp": 1.3,
    "yh": 0.8,
    "tips": 1.5,
    "e": 1.5,
    "cup": 1.4,
    "pm": 1.6,
}

def load_weights() -> dict[str, float]:
    if WEIGHTS_PATH.exists():
        try:
            data = json.loads(WEIGHTS_PATH.read_text(encoding="utf-8"))
            weights = data.get("weights", data)
            return {k: float(v) for k, v in weights.items() if k in SOURCE_KEYS}
        except (json.JSONDecodeError, KeyError, ValueError):
            pass
    return dict(_DEFAULT_WEIGHTS)

SOURCE_WEIGHTS = load_weights()
TOTAL_WEIGHT = sum(SOURCE_WEIGHTS.values())

def get_source_weights() -> dict[str, float]:
    global SOURCE_WEIGHTS, TOTAL_WEIGHT
    new = load_weights()
    if new != SOURCE_WEIGHTS:
        SOURCE_WEIGHTS = new
        TOTAL_WEIGHT = sum(SOURCE_WEIGHTS.values())
    return SOURCE_WEIGHTS

def get_total_weight() -> float:
    get_source_weights()
    return TOTAL_WEIGHT

SCORE_RE = re.compile(r"^\d+\s*-\s*\d+$")


@dataclass(frozen=True)
class Match:
    id: int
    group: str
    date: str
    time: str
    home: str
    away: str
    channel: str
    predictions: dict[str, str]


def parse_score(score: str) -> tuple[int, int]:
    left, right = score.split("-")
    return int(left.strip()), int(right.strip())


def outcome(score: str) -> str:
    left, right = parse_score(score)
    if left > right:
        return "A"
    if right > left:
        return "B"
    return "D"


def extract_raw_match_objects(html: str) -> list[str]:
    return re.findall(r"\{id:\d+,gr:\"[A-Z]\",[^\n]+\}", html)


def extract_key_values(raw_match: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for key, number_value, string_value in re.findall(r'(\w+):(?:(\d+)|"([^"]*)")', raw_match):
        pairs.append((key, number_value or string_value))
    return pairs


def parse_match(raw_match: str) -> Match:
    pairs = extract_key_values(raw_match)
    data = dict(pairs)
    predictions = {key: data[key] for key in SOURCE_KEYS}
    return Match(
        id=int(data["id"]),
        group=data["gr"],
        date=data["d"],
        time=data["h"],
        home=data["a"],
        away=data["b"],
        channel=data["ch"],
        predictions=predictions,
    )


def load_matches(html_path: Path = HTML_PATH) -> list[Match]:
    html = html_path.read_text(encoding="utf-8")
    return [parse_match(raw_match) for raw_match in extract_raw_match_objects(html)]


def load_teams(html_path: Path = HTML_PATH) -> list[str]:
    return sorted({team for match in load_matches(html_path) for team in (match.home, match.away)})


def consensus_score(predictions: dict[str, str]) -> str:
    sw = get_source_weights()
    tw = get_total_weight()
    score_weights: dict[str, float] = {}
    for key, score in predictions.items():
        score_weights[score] = score_weights.get(score, 0.0) + sw[key]

    best_score, best_weight = max(score_weights.items(), key=lambda item: item[1])
    if best_weight >= tw * 0.28:
        return best_score

    weighted_home = 0.0
    weighted_away = 0.0
    for key, score in predictions.items():
        home_goals, away_goals = parse_score(score)
        weighted_home += home_goals * sw[key]
        weighted_away += away_goals * sw[key]

    return f"{round(weighted_home / tw)} - {round(weighted_away / tw)}"


def validate_matches(matches: list[Match]) -> list[str]:
    errors: list[str] = []
    ids = [match.id for match in matches]
    if len(matches) != 72:
        errors.append(f"Expected 72 group-stage matches, found {len(matches)}")
    if ids != list(range(1, 73)):
        errors.append("Match IDs must be exactly 1..72 in chronological order")

    for match in matches:
        if not match.time or not re.match(r"^\d{2}:\d{2}$", match.time):
            errors.append(f"Match {match.id} has invalid time: {match.time!r}")
        missing = [key for key in SOURCE_KEYS if key not in match.predictions]
        if missing:
            errors.append(f"Match {match.id} missing sources: {', '.join(missing)}")
        for key, score in match.predictions.items():
            if not SCORE_RE.match(score):
                errors.append(f"Match {match.id} source {key} has invalid score: {score!r}")

    return errors
