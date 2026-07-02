"""CLI entrypoint that dispatches to one or more extractor modules.

Usage:
    python -m extract.run --all
    python -m extract.run --source open_meteo nager
    python -m extract.run --source open_meteo --dest LIS HND
"""

import argparse
import importlib

from extract.config import load_destinations

SOURCES = ["open_meteo", "nager", "opensky", "travelpayouts"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="Run every extractor")
    parser.add_argument("--source", nargs="+", choices=SOURCES, help="Run specific extractor(s)")
    parser.add_argument("--dest", nargs="+", help="Filter to specific IATA codes")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.all and not args.source:
        raise SystemExit("Specify --all or --source <name> [<name> ...]")

    sources = SOURCES if args.all else args.source
    destinations = load_destinations()
    if args.dest:
        wanted = {code.upper() for code in args.dest}
        destinations = [d for d in destinations if d.iata in wanted]
        if not destinations:
            raise SystemExit(f"No destinations match {sorted(wanted)}")

    for source in sources:
        module = importlib.import_module(f"extract.{source}")
        print(f"=== Running {source} for {len(destinations)} destination(s) ===")
        module.run(destinations=destinations)


if __name__ == "__main__":
    main()
