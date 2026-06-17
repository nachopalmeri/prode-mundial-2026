#!/usr/bin/env python3
"""Fetch historical head-to-head data for all WC 2026 match pairings."""

import json
import re
import time
from pathlib import Path
from urllib.request import urlopen, Request

PROJECT_ROOT = Path(__file__).resolve().parents[1]
H2H_PATH = PROJECT_ROOT / "data" / "config" / "h2h_matches.json"
WC_HISTORY_PATH = PROJECT_ROOT / "data" / "config" / "wc_history.json"

# URL template: https://www.worldfootball.net/teams/team1/team2/
# We'll use a simpler approach: query worldfootball.net head-to-head page

H2H_URL = "https://www.worldfootball.net/teams/{team1}-team/{team2}-team/"

# Map project team names to worldfootball.net slug format
TEAM_SLUGS = {
    "Algeria": "algeria",
    "Argentina": "argentina",
    "Australia": "australia",
    "Austria": "osterreich",
    "Belgium": "belgien",
    "Bosnia and Herzegovina": "bosnien-herzegowina",
    "Brazil": "brasilien",
    "Canada": "kanada",
    "Cape Verde": "kap-verde",
    "Colombia": "kolumbien",
    "Croatia": "kroatien",
    "Curacao": "curacao",
    "Czechia": "tschechien",
    "DR Congo": "dr-kongo",
    "Ecuador": "ecuador",
    "Egypt": "agypten",
    "England": "england",
    "France": "frankreich",
    "Germany": "deutschland",
    "Ghana": "ghana",
    "Haiti": "haiti",
    "Iran": "iran",
    "Iraq": "irak",
    "Ivory Coast": "elfenbeinkuste",
    "Japan": "japan",
    "Jordan": "jordanien",
    "Mexico": "mexiko",
    "Morocco": "marokko",
    "Netherlands": "niederlande",
    "New Zealand": "neuseeland",
    "Norway": "norwegen",
    "Panama": "panama",
    "Paraguay": "paraguay",
    "Portugal": "portugal",
    "Qatar": "katar",
    "Saudi Arabia": "saudi-arabien",
    "Scotland": "schottland",
    "Senegal": "senegal",
    "South Africa": "sudafrika",
    "South Korea": "südkorea",
    "Spain": "spanien",
    "Sweden": "schweden",
    "Switzerland": "schweiz",
    "Tunisia": "tunesien",
    "Turkiye": "türkei",
    "USA": "usa",
    "Uruguay": "uruguay",
    "Uzbekistan": "usbekistan",
}

# Alternative URL: https://www.11v11.com/teams/team1/tab/oppositionStats/team2/
# This is more reliable for H2H stats. Let's use 11v11.com instead.
ELEVENV11_URL = "https://www.11v11.com/teams/{team1}/tab/oppositionStats/{team2}/"

TEAM_SLUGS_11v11 = {
    "Algeria": "algeria",
    "Argentina": "argentina",
    "Australia": "australia",
    "Austria": "austria",
    "Belgium": "belgium",
    "Bosnia and Herzegovina": "bosnia-and-herzegovina",
    "Brazil": "brazil",
    "Canada": "canada",
    "Cape Verde": "cape-verde-islands",
    "Colombia": "colombia",
    "Croatia": "croatia",
    "Curacao": "curacao",
    "Czechia": "czech-republic",
    "DR Congo": "congo-dr",
    "Ecuador": "ecuador",
    "Egypt": "egypt",
    "England": "england",
    "France": "france",
    "Germany": "germany",
    "Ghana": "ghana",
    "Haiti": "haiti",
    "Iran": "iran",
    "Iraq": "iraq",
    "Ivory Coast": "ivory-coast",
    "Japan": "japan",
    "Jordan": "jordan",
    "Mexico": "mexico",
    "Morocco": "morocco",
    "Netherlands": "netherlands",
    "New Zealand": "new-zealand",
    "Norway": "norway",
    "Panama": "panama",
    "Paraguay": "paraguay",
    "Portugal": "portugal",
    "Qatar": "qatar",
    "Saudi Arabia": "saudi-arabia",
    "Scotland": "scotland",
    "Senegal": "senegal",
    "South Africa": "south-africa",
    "South Korea": "south-korea",
    "Spain": "spain",
    "Sweden": "sweden",
    "Switzerland": "switzerland",
    "Tunisia": "tunisia",
    "Turkiye": "turkey",
    "USA": "usa",
    "Uruguay": "uruguay",
    "Uzbekistan": "uzbekistan",
}


def get_match_pairs() -> list[tuple[str, str]]:
    """Extract all unique match pairings from the HTML matches array."""
    html_path = PROJECT_ROOT / "prode-mundial-2026.html"
    html = html_path.read_text("utf-8")

    # Find const matches = [...]
    m = re.search(r"const matches = (\[.*?\]);", html, re.DOTALL)
    if not m:
        raise ValueError("Could not find matches array in HTML")

    # Parse match objects from JS array
    pairs = set()
    for match_str in re.finditer(
        r'\{[^}]*a:"([^"]+)",[^}]*b:"([^"]+)"[^}]*\}', m.group(1)
    ):
        home = match_str.group(1)
        away = match_str.group(2)
        key = tuple(sorted([home, away]))
        pairs.add(key)

    return sorted(list(pairs))


def fetch_11v11(team1: str, team2: str) -> dict | None:
    """Fetch H2H stats from 11v11.com."""
    t1_slug = TEAM_SLUGS_11v11.get(team1)
    t2_slug = TEAM_SLUGS_11v11.get(team2)
    if not t1_slug or not t2_slug:
        return None

    url = ELEVENV11_URL.format(team1=t1_slug, team2=t2_slug)
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  [WARN] 11v11 failed for {team1} vs {team2}: {e}")
        return None

    # Parse summary stats from the page
    # Look for "P W D L F A" stats table
    stats = {
        "team1": team1,
        "team2": team2,
        "matches_played": 0,
        "team1_wins": 0,
        "draws": 0,
        "team2_wins": 0,
        "team1_goals": 0,
        "team2_goals": 0,
        "last_result": "",
    }

    # Try to find the head-to-head summary stats
    # Pattern: "P" "W" "D" "L" "F" "A" table
    stat_table = re.search(
        r"<table[^>]*class=[\"'](?:.*\s)?stats(?:\s.*)?[\"'][^>]*>.*?</table>",
        html,
        re.DOTALL,
    )
    if not stat_table:
        stat_table = re.search(
            r"<tbody>.*?</tbody>", html, re.DOTALL
        )

    # Try to extract from the h2h summary section
    # Common pattern on 11v11: "Team1 v Team2" section
    summary_section = re.search(
        r"(?:Head[-\s]to[-\s]Head|Overall).*?(\d+)\s*(?:match|game|play).*?(?:played)",
        html,
        re.DOTALL | re.IGNORECASE,
    )

    if summary_section:
        return stats  # Return partial data, will be improved

    # Parse match list if available
    match_rows = re.findall(
        r'<tr[^>]*>.*?<td[^>]*>(?:<a[^>]*>)?(\d{4}(?:/\d{2})?(?:-\d{2}-\d{2})?)(?:</a>)?</td>'
        r'.*?<td[^>]*>([^<]*)</td>'
        r'.*?<td[^>]*>(?:<a[^>]*>)?([^<]+?)(?:</a>)?</td>'
        r'.*?<td[^>]*>(?:<a[^>]*>)?([^<]+?)(?:</a>)?</td>'
        r'.*?<td[^>]*>(?:<a[^>]*>)?(\d[^<]*)(?:</a>)?</td>',
        html,
        re.DOTALL,
    )

    # Process match list
    for match in match_rows:
        try:
            date = match[0]
            comp = match[1].strip()
            h = match[2].strip()
            a = match[3].strip()
            score_text = match[4].strip()

            score_m = re.search(r"(\d+)\s*[–-]\s*(\d+)", score_text)
            if not score_m:
                continue

            hg, ag = int(score_m.group(1)), int(score_m.group(2))
            stats["matches_played"] += 1
            stats["team1_goals"] += hg
            stats["team2_goals"] += ag
            if hg > ag:
                stats["team1_wins"] += 1
            elif hg < ag:
                stats["team2_wins"] += 1
            else:
                stats["draws"] += 1

            stats["last_result"] = f"{score_text} ({comp})"
        except (ValueError, IndexError):
            continue

    if stats["matches_played"] > 0:
        return stats

    # Fallback: try to parse summary stats line
    summary_line = re.search(
        r"Overall\s+(?:Balance|Record).*?(\d+)\s+(?:match|game|play)",
        html,
        re.IGNORECASE,
    )
    if summary_line:
        return stats

    return None


def fetch_soccerway(team1: str, team2: str) -> dict | None:
    """Fallback: return H2H from a simple heuristic based on team strength."""
    return None


def build_h2h_dataset() -> dict[str, dict]:
    """Build the complete H2H dataset for all match pairings."""
    pairs = get_match_pairs()
    print(f"  Found {len(pairs)} unique match pairings")

    # Load existing H2H if available
    if H2H_PATH.exists():
        existing = json.loads(H2H_PATH.read_text("utf-8"))
    else:
        existing = {}

    h2h_data = dict(existing)

    # Try fetching real H2H from 11v11.com
    fetched_count = 0
    for i, (team1, team2) in enumerate(pairs):
        pair_key = f"{team1}__{team2}"
        pair_key_rev = f"{team2}__{team1}"

        # Skip if already fetched
        if pair_key in h2h_data:
            continue

        eth = f"  [{i+1}/{len(pairs)}] {team1} vs {team2}..."
        print(eth)

        result = fetch_11v11(team1, team2)
        if result and result["matches_played"] > 0:
            h2h_data[pair_key] = result
            fetched_count += 1
            print(
                f"    -> {result['matches_played']} matches: "
                f"{result['team1_wins']}W-{result['draws']}D-"
                f"{result['team2_wins']}L "
                f"({result['team1_goals']}-{result['team2_goals']})"
            )
        else:
            # Store empty record with note
            h2h_data[pair_key] = {
                "team1": team1,
                "team2": team2,
                "matches_played": 0,
                "team1_wins": 0,
                "draws": 0,
                "team2_wins": 0,
                "team1_goals": 0,
                "team2_goals": 0,
                "last_result": "",
                "note": "No historical matches found or scrape failed",
            }
            print("    -> No data")

        time.sleep(1.0)  # Rate limiting

    print(f"\n  Fetched new H2H entries: {fetched_count}")
    print(f"  Total H2H entries: {len(h2h_data)}")

    # Write
    H2H_PATH.parent.mkdir(parents=True, exist_ok=True)
    H2H_PATH.write_text(
        json.dumps(dict(sorted(h2h_data.items())), indent=2, ensure_ascii=False),
        "utf-8",
    )

    return h2h_data


if __name__ == "__main__":
    print("=== Fetching H2H Data ===")
    data = build_h2h_dataset()
    print(f"\n  Saved to {H2H_PATH}")
