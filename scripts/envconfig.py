#!/usr/bin/env python3
"""Acquire raw meteorological data from configured data sources."""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))
from envconfig.envconfig import EnvConfig


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print configuration variables.")

    parser.add_argument(
        "-f",
        "--envfile",
        type=Path,
        help="Path of the env config file.",
    )

    parser.add_argument(
        "-k",
        "--key",
        type=str,
        required=True,
        help="Key which will return its value",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    try:
        if args.envfile:
            config = EnvConfig(args.envfile)
        else:
            config = EnvConfig()

        print(f"{args.key}='{config.get(args.key)}'")
        return 0

    except (ValueError, OSError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
