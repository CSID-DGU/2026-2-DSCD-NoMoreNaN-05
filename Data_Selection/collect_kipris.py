"""Collect original KIPRIS patent/utility XML for the confirmed keyword."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time

import requests
from dotenv import load_dotenv
from collect_kipris_raw import ROOT, ENDPOINT, SPEC_URL, folder_name, inspect_response, request_page, now


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--word', required=True)
    parser.add_argument('--cache-db', action='store_true', help='Index saved raw XML into the local patent candidate cache')
    args = parser.parse_args()
    load_dotenv(ROOT / '.env')
    key = os.getenv('KIPRIS_API_KEY', '').strip()
    if not key:
        print('[KIPRIS] KIPRIS_API_KEY missing')
        return 1
    directory = ROOT / 'data/raw/kipris' / folder_name(args.word)
    directory.mkdir(parents=True, exist_ok=True)
    metadata = {'query': args.word, 'service': '특허·실용 공개·등록공보', 'endpoint': ENDPOINT,
                'official_specification': SPEC_URL, 'docs_count': 500,
                'docs_start_mode': 'start_index',
                'pagination_note': 'Live probe: docsStart=2 overlaps page 1 by 499 records; docsStart=501 yields the next distinct block.',
                'total_results': None, 'pages_collected': 0, 'records_observed': 0,
                'pages': [], 'collected_at': now(), 'status': 'running'}
    session = requests.Session()
    seen = set()
    try:
        page = 1
        while True:
            start = 1 + (page - 1) * 500
            path = directory / f'page_{page:03d}.xml'
            print(f'[KIPRIS] Request page {page} (docsStart={start})', flush=True)
            if path.exists():
                body = path.read_bytes()
            else:
                params = {'word': args.word, 'patent': 'true', 'utility': 'true', 'docsStart': start,
                          'docsCount': 500, 'lastvalue': '', 'accessKey': key}
                body = request_page(session, params, directory, page, 1)
            try:
                total, reported, ids = inspect_response(body)
            except RuntimeError:
                error_path = directory / f'error_page_{page:03d}_{int(time.time())}.xml'
                path.replace(error_path)
                raise
            if page == 1:
                print('[KIPRIS] API authentication OK', flush=True)
                metadata['total_results'] = total
                print(f'[KIPRIS] Total results: {total}', flush=True)
            if total != metadata['total_results'] or len(ids) != len(set(ids)) or seen.intersection(ids):
                raise RuntimeError('Total changed or overlapping records; raw responses preserved, stopped.')
            if not ids and len(seen) < total:
                raise RuntimeError('Empty response before total reached.')
            seen.update(ids)
            metadata['pages'].append({'page': page, 'docs_start': start, 'reported_start': reported,
                                      'records': len(ids), 'file': path.name, 'sha256': hashlib.sha256(body).hexdigest()})
            metadata.update(pages_collected=page, records_observed=len(seen))
            (directory/'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'[KIPRIS] Saved {path.name}', flush=True)
            if len(seen) == total:
                metadata['status'] = 'complete'
                metadata['pagination_verified'] = page > 1
                print('[KIPRIS] Collection complete', flush=True)
                break
            if len(seen) > total or len(ids) != 500:
                raise RuntimeError('Unexpected short page/count before total reached.')
            page += 1
            time.sleep(1)
    except Exception as exc:
        metadata['status'] = 'incomplete'
        message = str(exc).replace(key, '[REDACTED]') if isinstance(exc, RuntimeError) else type(exc).__name__
        print(f'[KIPRIS] Failed: {message}', flush=True)
        return 1
    finally:
        metadata['finished_at'] = now()
        (directory/'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
        session.close()
        if args.cache_db and metadata['pages']:
            from kipris_cache import import_directory
            count = import_directory(directory)
            print(f'[KIPRIS] Cached {count} patent candidates', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
