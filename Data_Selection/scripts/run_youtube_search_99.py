"""Run/resume the reviewed 99-product manifest using the normal API budgets."""
from collections import Counter
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import collect_youtube_ads as collector


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "docs/youtube_search_99_manifest.json")
    parser.add_argument("--summary", type=Path, default=ROOT / "docs/youtube_search_99_summary.json")
    parser.add_argument("--report", type=Path, default=ROOT / "state/search_99_report.json")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    ids = [str(product["id"]) for product in manifest["products"]]
    code = collector.main([
        "search", "--ids", *ids, "--max-api-calls", "200",
        "--report", str(args.report),
    ])
    products = collector.load_products(ROOT / "products_for_search.json", selected_ids=ids)
    state = collector.State(ROOT / "state")
    try:
        completed, pending = [], []
        for product in products:
            done = state.complete(f"search-v{collector.POLICY_VERSION}:" + collector.fingerprint(product))
            (completed if done else pending).append(product["id"])
        pairs = [json.loads(row[0]) for row in state.db.execute("SELECT value FROM assessments")]
        pairs = [row for row in pairs if str(row["id"]) in ids
                 and row.get("logic_version") == collector.POLICY_VERSION]
        counts = {status: sum(row["status"] == status for row in pairs)
                  for status in ("confirmed", "needs_review", "rejected")}
        accepted = [row for row in pairs if row["status"] != "rejected"]
        summary = dict(
            requested_products=len(products), completed_products=len(completed),
            pending_products=len(pending), completed_ids=completed, pending_ids=pending,
            counts=counts, accepted_product_video_pairs=len(accepted),
            unique_accepted_videos=len({row["video_id"] for row in accepted}),
            products_with_candidates=len({row["id"] for row in accepted}),
            exit_code=code,
            per_product=[dict(id=p["id"], product_name=p["product_name"],
                              completed=p["id"] in completed,
                              counts=dict(Counter(row["status"] for row in pairs if row["id"] == p["id"])))
                         for p in products],
        )
        destination = args.summary
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: value for key, value in summary.items()
                          if key not in {"per_product", "completed_ids", "pending_ids"}}))
    finally:
        state.db.close()
    return code


if __name__ == "__main__":
    raise SystemExit(main())
