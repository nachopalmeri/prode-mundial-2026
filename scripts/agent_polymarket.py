#!/usr/bin/env python3
"""Fetch public Polymarket markets and map them to the real fixture list when possible."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None

from prode_core import load_matches


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW = PROJECT_ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
USER_AGENT = "Mozilla/5.0 (compatible; ProdeMundialBot/1.0)"


def fetch_markets() -> tuple[str, list[dict[str, Any]]]:
    if requests is None:
        return "requests_unavailable", []
    endpoints = [
        "https://gamma-api.polymarket.com/markets?closed=false&limit=500",
        "https://gamma-api.polymarket.com/events?closed=false&limit=200",
    ]
    markets: list[dict[str, Any]] = []
    for url in endpoints:
        try:
            response = requests.get(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}, timeout=20)
            if response.status_code != 200:
                continue
            data = response.json()
            items = data if isinstance(data, list) else data.get("data", [])
            if isinstance(items, list):
                markets.extend(item for item in items if isinstance(item, dict))
        except Exception:
            continue
    return ("live" if markets else "unavailable"), markets


def text_for_market(market: dict[str, Any]) -> str:
    return " ".join(
        str(market.get(key, ""))
        for key in ("question", "title", "slug", "description")
    ).lower()


def build_output(timestamp: str) -> dict[str, Any]:
    matches = load_matches()
    status, markets = fetch_markets()
    predictions: dict[str, Any] = {}

    for match in matches:
        home = match.home.lower()
        away = match.away.lower()
        for market in markets:
            text = text_for_market(market)
            if home in text and away in text:
                predictions[str(match.id)] = {
                    "market_title": market.get("question") or market.get("title") or market.get("slug", ""),
                    "source": "polymarket",
                    "raw_id": market.get("id") or market.get("conditionId"),
                }
                break

    output = {
        "timestamp": timestamp,
        "status": status,
        "markets_found": len(markets),
        "matches_matched": len(predictions),
        "predictions": predictions,
        "note": "Matched markets are metadata only until reliable 1X2 odds are parsed.",
    }
    (RAW / f"polymarket_{timestamp}.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Polymarket saved: polymarket_{timestamp}.json | markets={len(markets)} | matched={len(predictions)}")
    return output


def main() -> None:
    build_output(datetime.now().strftime("%Y%m%d_%H%M"))


if __name__ == "__main__":
    main()
