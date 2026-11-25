import os
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
DATA_DIR = BACKEND_DIR / "data"
RUNS_DIR = BACKEND_DIR / "runs"
PAIRS_PATH = DATA_DIR / "manufacturer_pairs.json"

MAP_THRESHOLD = 80
DB_VERSION = "2026-11-03T04:09:56.363154+00:00"
NLI_MODEL = "Huffon/klue-roberta-base-nli"
JOB_TTL_HOURS = 24
CACHE_STEP_DELAY_SEC = (5, 10, 15)
CORS_ORIGINS = [o.strip() for o in os.environ.get(
    "TRUEAD_CORS_ORIGINS",
    "http://210.94.179.19:9332,http://210.94.179.19:9321,http://localhost:5173").split(",") if o.strip()]
CACHE_DSN = os.environ.get("TRUEAD_CACHE_DSN", "host=127.0.0.1 port=15432 dbname=truead_cache user=truead_admin gssencmode=disable")
REF_DSN = os.environ.get("TRUEAD_REF_DSN", "host=127.0.0.1 port=15432 dbname=TrueAD_Evidence_Claim user=truead_admin gssencmode=disable options='-c search_path=claim_verification_enriched'")
