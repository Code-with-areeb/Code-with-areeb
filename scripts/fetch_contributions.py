#!/usr/bin/env python3
"""Fetch public GitHub contribution counts and derive profile statistics."""

from __future__ import annotations

import datetime
import json
import os
import re
import sys

import requests
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from profile import USERNAME

URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join(HERE, "..", "data", "contributions.json")


def fetch_days() -> list[dict]:
    response = requests.get(
        URL,
        headers={"User-Agent": "profile-readme-bot/1.0"},
        timeout=30,
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    cells = soup.select("td.ContributionCalendar-day") or soup.select(
        "rect.ContributionCalendar-day"
    )
    if not cells:
        print("no calendar cells found; GitHub markup may have changed", file=sys.stderr)
        raise SystemExit(1)

    days: list[dict] = []
    for cell in cells:
        date = cell.get("data-date")
        if not date:
            continue
        cell_id = cell.get("id")
        tooltip = soup.find("tool-tip", attrs={"for": cell_id}) if cell_id else None
        text = tooltip.get_text(strip=True) if tooltip else (cell.get("aria-label") or "")
        if re.search(r"no contributions", text, re.I):
            count = 0
        else:
            match = re.search(r"(\d+)\s+contribution", text, re.I) or re.match(r"(\d+)", text)
            count = int(match.group(1)) if match else 0
        days.append({"date": date, "count": count, "level": int(cell.get("data-level") or 0)})

    days.sort(key=lambda item: item["date"])
    if not days:
        raise SystemExit("GitHub returned calendar cells without dates")
    return days


def compute_current_streak(days: list[dict]) -> tuple[int, str | None, str | None]:
    index = len(days) - 1
    if days[index]["count"] == 0:
        index -= 1
    streak = 0
    end_index = index
    while index >= 0 and days[index]["count"] > 0:
        streak += 1
        index -= 1
    start_index = index + 1
    if streak == 0:
        return 0, None, None
    return streak, days[start_index]["date"], days[end_index]["date"]


def compute_longest_streak(days: list[dict]) -> tuple[int, str | None, str | None]:
    longest = run = 0
    longest_start = longest_end = None
    run_start_index = None
    for index, day in enumerate(days):
        if day["count"] > 0:
            if run == 0:
                run_start_index = index
            run += 1
            if run > longest:
                longest = run
                longest_start = days[run_start_index]["date"]
                longest_end = day["date"]
        else:
            run = 0
    return longest, longest_start, longest_end


def build_data(days: list[dict]) -> dict:
    total = sum(day["count"] for day in days)
    active_days = sum(day["count"] > 0 for day in days)
    best = max(days, key=lambda day: day["count"])
    current_length, current_start, current_end = compute_current_streak(days)
    longest_length, longest_start, longest_end = compute_longest_streak(days)
    monthly: dict[str, int] = {}
    for day in days:
        month = day["date"][:7]
        monthly[month] = monthly.get(month, 0) + day["count"]

    return {
        "username": USERNAME,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active_days,
        "avg_per_active_day": round(total / active_days, 1) if active_days else 0,
        "current_streak": {"length": current_length, "start": current_start, "end": current_end},
        "longest_streak": {"length": longest_length, "start": longest_start, "end": longest_end},
        "best_day": {"date": best["date"], "count": best["count"]},
        "monthly": [{"month": month, "total": count} for month, count in sorted(monthly.items())],
        "days": days,
    }


def main() -> None:
    data = build_data(fetch_days())
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as output:
        json.dump(data, output, indent=2)
    print(
        f"wrote {OUT_PATH}: {data['total_contributions']} contributions, "
        f"current streak {data['current_streak']['length']}, "
        f"longest streak {data['longest_streak']['length']}"
    )


if __name__ == "__main__":
    main()
