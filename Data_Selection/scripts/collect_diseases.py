"""Collect HIRA disease names and codes; raw XML and normalized JSONL are stored separately."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.collectors.diseases import DEFAULT_PREFIXES, collect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="Resume a previously printed run ID")
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--prefixes", default=DEFAULT_PREFIXES, help="Code prefixes (default: 0-9 and A-Z)")
    parser.add_argument("--sick-types", default="1,2", help="Comma-separated: 1 (3-level), 2 (4-level)")
    parser.add_argument("--med-types", default="1,2", help="Comma-separated: 1 (western), 2 (traditional)")
    args = parser.parse_args()
    try:
        manifest, output = collect(args.run_id, args.page_size, args.prefixes, args.sick_types, args.med_types)
    except KeyboardInterrupt:
        print("Collection interrupted; saved XML pages can be resumed.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Collection failed: {exc}", file=sys.stderr)
        return 1
    print(f"Collection successful\nManifest: {manifest}\nProcessed: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
