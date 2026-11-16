#!/usr/bin/env python3
import argparse
import calendar
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import requests

from datacollector.aemet_opendata import AemetOpenDataClient
from envconfig.envconfig import EnvConfig
from repository.repository import Repository

FIRST_MONTH = (1980, 1)
SAFETY_DAYS = 7  # a month is stored only when its last day is at least this old


def next_month(year: int, month: int) -> tuple[int, int]:
    return (year + 1, 1) if month == 12 else (year, month + 1)


def latest_final_month(today: date) -> tuple[int, int]:
    """Latest month whose last day is at least SAFETY_DAYS days old."""
    year, month = today.year, today.month
    while True:
        year, month = (year - 1, 12) if month == 1 else (year, month - 1)
        last_day = date(year, month, calendar.monthrange(year, month)[1])
        if last_day + timedelta(days=SAFETY_DAYS) <= today:
            return year, month


def oldest_missing_month(repository: Repository, station_id: str, last: tuple[int, int]):
    """First month from FIRST_MONTH up to `last` with no stored file, or None."""
    current = FIRST_MONTH
    while current <= last:
        if not repository.exists(station_id, *current):
            return current
        current = next_month(*current)
    return None


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Download one month of AEMET daily values of a station into a folder.")

    parser.add_argument(
        "-p",
        "--path",
        required=True,
        help="folder where the raw json data is stored (e.g. data/aemet)",
    )
    parser.add_argument(
        "-m",
        "--month",
        nargs="?",
        help="month in YYYY-MM format (default: the oldest month without data since 1980-01)",
    )
    args = parser.parse_args(argv)

    args.year = args.mon = None
    if args.month:
        try:
            d = datetime.strptime(args.month, "%Y-%m")
        except ValueError:
            parser.error("month must be in YYYY-MM format")
        args.year, args.mon = d.year, d.month

    try:
        env = EnvConfig()
        args.api_key = env.get("AEMET_API_KEY")
        args.station_id = env.get("WEATHER_STATION_ID")
    except ValueError as error:
        parser.error(str(error))
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    repository = Repository(args.path)
    last_final = latest_final_month(date.today())

    if args.year:
        target = (args.year, args.mon)
        if target > last_final:
            sys.exit(f"{args.month} is not final yet (latest final month: {last_final[0]}-{last_final[1]:02d}).")
        if repository.exists(args.station_id, *target):
            print(f"{args.station_id} {args.month}: already stored, nothing to do.")
            return 0
    else:
        target = oldest_missing_month(repository, args.station_id, last_final)
        if target is None:
            print(
                f"{args.station_id}: all months from 1980-01 to {last_final[0]}-{last_final[1]:02d} are already stored."
            )
            return 0

    year, month = target
    client = AemetOpenDataClient(args.api_key)
    try:
        records = client.fetch_month(args.station_id, year, month)
    except (requests.RequestException, RuntimeError) as error:
        sys.exit(f"{args.station_id} {year}-{month:02d}: download failed ({error}). Nothing was saved.")

    text = json.dumps(records, ensure_ascii=False, indent=2)
    path = repository.save_raw(args.station_id, year, month, text)
    print(f"{args.station_id} {year}-{month:02d}: saved {len(records)} records to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
