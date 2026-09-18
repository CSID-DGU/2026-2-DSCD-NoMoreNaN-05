"""Collect YouTube health-functional-food ad candidate URLs and metadata; never downloads video files."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.collectors.youtube_candidate_collector import collect, CANDIDATES_PATH, ROOT, CANDIDATE_URLS_PATH


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-results", type=int, required=True, help="Maximum final unique candidate count")
    parser.add_argument("--max-pages-per-keyword", type=int, default=1,
                        help="Search pages per keyword (default: 1; raises YouTube API quota use)")
    args = parser.parse_args()
    try:
        manifest = collect(args.max_results, args.max_pages_per_keyword)
    except KeyboardInterrupt:
        print("Collection interrupted; raw responses remain saved.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Collection failed: {exc}", file=sys.stderr)
        return 1
    print("Collection completed")
    print(f"Total API results: {manifest['total_api_results']}")
    print(f"Unique videos: {manifest['final_unique_videos']}")
    print(f"Saved:\n{CANDIDATES_PATH.relative_to(ROOT)}\n{CANDIDATE_URLS_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
