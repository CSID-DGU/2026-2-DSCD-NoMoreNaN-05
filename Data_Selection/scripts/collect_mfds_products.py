"""Collect all MFDS health functional food list and detail pages."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.collectors.mfds_products import collect


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="Resume a previously printed run ID")
    parser.add_argument("--page-size", type=int, default=100)
    args = parser.parse_args()
    try:
        manifest, processed = collect(args.run_id, args.page_size)
    except KeyboardInterrupt:
        print("Collection interrupted; saved pages can be resumed.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Collection failed: {exc}", file=sys.stderr)
        return 1
    print(f"Collection successful\nManifest: {manifest}\nProcessed: {processed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
