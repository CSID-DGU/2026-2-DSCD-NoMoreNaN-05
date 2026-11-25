from config import DB_VERSION, MAP_THRESHOLD, PAIRS_PATH, REF_DSN
from files import save_json

from .remap import remap


def run(videos: list[dict], run_dir, input_path=None) -> list[dict]:
    results, audits, summary = remap(videos, REF_DSN, PAIRS_PATH, MAP_THRESHOLD, DB_VERSION, input_path)
    save_json(run_dir / "02_claims_with_db.json", results)
    save_json(run_dir / "02_product_mapping_audit.json", audits)
    save_json(run_dir / "02_product_mapping_summary.json", summary)
    return results
