"""Run one complete live KIPRIS keyword collection without logging credentials."""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
from collect_kipris_raw import collect_query

if __name__ == '__main__':
    load_dotenv(ROOT / '.env')
    key = os.getenv('KIPRIS_API_KEY', '').strip()
    if not key:
        print('KIPRIS_API_KEY missing')
        raise SystemExit(1)
    try:
        result = collect_query('홍삼', key, ROOT / 'data/raw/kipris')
        print('Status:', result['status'])
        print('Pagination verified:', result['pagination_verified'])
    except Exception as exc:
        print('Live test failed:', str(exc).replace(key, '[REDACTED]') if isinstance(exc, RuntimeError) else type(exc).__name__)
        raise SystemExit(1)
