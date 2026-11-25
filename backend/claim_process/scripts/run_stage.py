import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import argparse

from claim_process.claim_extraction import extraction
from claim_process.claim_verification import (
    adapters,
    explanation,
    product_mapping,
    verdict_a,
    verdict_b,
)
from files import load_json, new_run_dir


def main():
    parser = argparse.ArgumentParser(description="파이프라인 단계 하나만 실행")
    parser.add_argument("stage", choices=["extraction", "mapping", "verdict_b", "verdict_a", "explanation"])
    parser.add_argument("--input", type=Path,
                        help="extraction: 영상 / mapping: 01 형식 / verdict_b·verdict_a: 02 형식 json")
    parser.add_argument("--b-result", type=Path, help="verdict_a: 03 형식 json")
    parser.add_argument("--url")
    parser.add_argument("--title")
    parser.add_argument("--run-dir", type=Path, help="explanation: 03·04 파일이 있는 run 폴더 (필수)")
    args = parser.parse_args()
    if args.stage == "explanation" and args.run_dir is None:
        parser.error("explanation에는 --run-dir가 필요함")
    if args.stage != "explanation" and args.input is None:
        parser.error(f"{args.stage}에는 --input이 필요함")

    if args.run_dir:
        run_dir = args.run_dir.resolve()
        run_dir.mkdir(parents=True, exist_ok=True)
    else:
        run_dir = new_run_dir()
    if args.stage == "extraction":
        extraction.run(args.input, run_dir, url=args.url, title=args.title)
    elif args.stage == "mapping":
        product_mapping.run(load_json(args.input), run_dir, input_path=args.input)
    elif args.stage == "verdict_b":
        verdict_b.run(load_json(args.input), run_dir)
    elif args.stage == "explanation":
        explanation.run(run_dir)
    else:
        verdict_a.run(load_json(args.input), adapters.b_records(load_json(args.b_result)), run_dir,
                      input_path=args.input, b_path=args.b_result)
    print(run_dir)


if __name__ == "__main__":
    main()
