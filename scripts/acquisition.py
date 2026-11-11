#!/usr/bin/env python3
"""Acquire raw meteorological data from configured data sources."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))
from repository.repository import Repository


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Acquire raw meteorological data.")

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where raw data will be stored.",
    )

    parser.add_argument(
        "-s",
        "--start-date",
        type=str,
        required=True,
        help="Start date for data acquisition (YYYY-MM-DD).",
    )

    parser.add_argument(
        "-e",
        "--end-date",
        type=str,
        required=True,
        help="End date for data acquisition (YYYY-MM-DD).",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=Path("config/settings.yaml"),
        help="Path to the application configuration file.",
    )

    return parser.parse_args()


def main() -> int:
    """Execute the data acquisition process."""
    args = parse_arguments()

    try:
        if args.start_date and args.end_date and args.start_date > args.end_date:
            raise ValueError("Start date cannot be later than end date.")

        args.output_dir.mkdir(parents=True, exist_ok=True)

        print("Starting data acquisition...")
        print(f"Output directory: {args.output_dir}")

        # TODO: Initialize the data acquisition service.
        # TODO: Execute the acquisition process.

        repo = Repository(Path(args.output_dir) / "raw/aemet/")
        repo.save_raw(args.start_date + ".raw", "Datos de prueba " + args.start_date)

        print("Data acquisition completed successfully.")
        return 0

    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
