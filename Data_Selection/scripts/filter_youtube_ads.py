"""Run conservative YouTube rule filtering and optional LLM ad classification."""

import argparse
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from src.collectors.youtube_ad_filter import (
    CANDIDATES_PATH, CLASSIFICATIONS_PATH, CONFIRMED_URLS_PATH, ROOT, RULE_OUTPUT_PATH, classify_candidates,
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=CANDIDATES_PATH, help="Candidate metadata CSV")
    parser.add_argument("--rules-only", action="store_true", help="Write only the conservative rule-filter result")
    parser.add_argument("--model", default=None, help="OpenAI model; defaults to OPENAI_MODEL or gpt-5-mini")
    parser.add_argument("--minimum-confidence", type=float, default=0.85, help="Confidence required for ad_urls.csv")
    parser.add_argument("--limit", type=int, help="Maximum new LLM classifications; useful for a small pilot")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")
    load_dotenv(ROOT / ".env")
    model = args.model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
    try:
        result = classify_candidates(input_path=args.input, rules_only=args.rules_only, model=model,
                                     minimum_confidence=args.minimum_confidence, limit=args.limit)
    except Exception as exc:
        print(f"Filtering failed: {exc}", file=sys.stderr)
        return 1
    print("Filtering completed")
    for key, value in result.items():
        print(f"{key}: {value}")
    print(f"Saved:\n{RULE_OUTPUT_PATH.relative_to(ROOT)}")
    if not args.rules_only:
        print(f"{CLASSIFICATIONS_PATH.relative_to(ROOT)}\n{CONFIRMED_URLS_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
