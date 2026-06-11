#!/usr/bin/env python3
"""Generate the final prode answer in strict chronological format."""

from __future__ import annotations

from prode_core import consensus_score, load_matches, validate_matches


def main() -> None:
    matches = load_matches()
    errors = validate_matches(matches)
    if errors:
        raise SystemExit("Invalid match data:\n- " + "\n- ".join(errors))

    lines: list[str] = []
    for index, match in enumerate(matches, start=1):
        score = consensus_score(match.predictions)
        home_goals, away_goals = score.replace(" ", "").split("-")
        lines.append(f"Partido {index}")
        lines.append(f"{match.home} {home_goals} - {away_goals} {match.away}")
        if index != len(matches):
            lines.append("")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
