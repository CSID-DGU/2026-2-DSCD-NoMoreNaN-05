"""Save KIPRIS freeSearchInfo response bodies unchanged, one XML per page."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
import requests

ROOT = Path(__file__).resolve().parent
ENDPOINT = 'http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/freeSearchInfo'
MAX_DOCS_COUNT = 500
SPEC_URL = 'https://plus.kipris.or.kr/portal/popup/DBII_000000000000001/SC002/ADI_0000000000010162/apiDescriptionSearch.do'


def now():
    return datetime.now(timezone.utc).isoformat()


def folder_name(query):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', query).rstrip(' .')
    reserved = re.fullmatch(r'(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?', name, re.I)
    if not name or reserved:
        name = 'query_' + name
    if name != query or len(name) > 80:
        name = name[:80] + '_' + hashlib.sha256(query.encode()).hexdigest()[:10]
    return name


def inspect_response(body):
    """Read only pagination controls; never serialize or change the saved XML."""
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        raise RuntimeError('Response is not valid XML; original body remains saved.') from None
    def local(element):
        return element.tag.rsplit('}', 1)[-1].lower()
    def integer(tag):
        values = [(node.text or '').strip() for node in root.iter() if local(node) == tag.lower()]
        if not values or not values[0].isdigit():
            raise RuntimeError(f'Missing/invalid {tag}; cannot confirm pagination. Original XML remains saved.')
        return int(values[0])
    total = integer('TotalSearchCount')
    start = integer('SearchStartNumber')
    records = [node for node in root.iter() if local(node) == 'patentutilityinfo']
    ids = []
    for record in records:
        ids.append(next(((node.text or '').strip() for node in record.iter()
                         if local(node) == 'applicationnumber'), ''))
    if records and any(not identifier for identifier in ids):
        raise RuntimeError('Missing ApplicationNumber; cannot verify page overlap.')
    return total, start, ids


def request_page(session, params, directory, page, delay):
    for attempt in range(4):  # Initial request plus at most three retries.
        try:
            response = session.get(ENDPOINT, params=params, timeout=(15, 90))
        except (requests.Timeout, requests.ConnectionError):
            if attempt == 3:
                raise RuntimeError('Network/timeout failure after three retries.') from None
            print(f'[KIPRIS] Retrying page {page}: attempt {attempt + 1}/3')
            time.sleep(max(delay, 2 ** attempt))
            continue
        except requests.RequestException:
            raise RuntimeError('Request failed; request URL and credentials withheld.') from None
        if response.status_code == 429 or 500 <= response.status_code <= 599:
            (directory / f'page_{page:03d}_retry_{attempt:02d}.xml').write_bytes(response.content)
            if attempt == 3:
                raise RuntimeError(f'HTTP {response.status_code} after three retries.')
            retry_after = response.headers.get('Retry-After', '')
            wait = float(retry_after) if retry_after.isdigit() else 2 ** attempt
            time.sleep(max(delay, wait))
            continue
        (directory / f'page_{page:03d}.xml').write_bytes(response.content)
        if response.status_code != 200:
            raise RuntimeError(f'HTTP {response.status_code}; original body saved.')
        return response.content


def collect_query(query, key, output_root, count=500, delay=1.0, session=None):
    directory = output_root / folder_name(query)
    directory.mkdir(parents=True, exist_ok=True)
    if any(directory.glob('page_*.xml')):
        raise RuntimeError('Existing XML pages found; choose a new --output directory to preserve previous responses.')
    metadata = {'query': query, 'endpoint': ENDPOINT, 'official_specification': SPEC_URL,
                'docs_count': count, 'docs_start_mode': 'page_number', 'total_results': None,
                'pages_collected': 0, 'records_observed': 0, 'collected_at': now(),
                'status': 'running', 'pagination_verified': False, 'pages': []}
    owned = session is None
    session = session or requests.Session()
    seen = set()
    page = 1
    print(f'[KIPRIS] Query: {query}')
    try:
        while True:
            print(f'Collecting page {page}...')
            params = {'word': query, 'patent': 'true', 'utility': 'true', 'docsStart': page,
                      'docsCount': count, 'lastvalue': '', 'accessKey': key}
            body = request_page(session, params, directory, page, delay)
            total, reported_page, ids = inspect_response(body)
            if reported_page != page:
                raise RuntimeError('SearchStartNumber does not match requested page; stopped to avoid missing results.')
            if page == 1:
                metadata['total_results'] = total
                print(f'Total results: {total}')
            elif total != metadata['total_results']:
                raise RuntimeError('TotalSearchCount changed during collection; stopped to avoid inconsistent results.')
            if len(ids) > count or len(ids) != len(set(ids)) or seen.intersection(ids):
                raise RuntimeError('Duplicate/overlapping page or unexpected page size; pagination not confirmed.')
            if not ids and len(seen) < total:
                raise RuntimeError('Empty page before reported total; collection incomplete.')
            seen.update(ids)
            metadata['pages'].append({'page': page, 'docs_start': page, 'reported_page': reported_page,
                                      'records': len(ids), 'file': f'page_{page:03d}.xml',
                                      'sha256': hashlib.sha256(body).hexdigest()})
            metadata['pages_collected'] = page
            metadata['records_observed'] = len(seen)
            if len(seen) > total:
                raise RuntimeError('Observed record count exceeds reported total.')
            if len(seen) == total:
                metadata['status'] = 'complete'
                metadata['pagination_verified'] = page >= 2
                metadata['pagination_note'] = ('Distinct pages and reported page numbers verified.' if page >= 2
                                               else 'One page only; multi-page behavior not exercised.')
                break
            page += 1
            time.sleep(delay)
    except BaseException:
        metadata['status'] = 'incomplete'
        raise
    finally:
        metadata['finished_at'] = now()
        (directory / 'metadata.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
        if owned:
            session.close()
    print(f'Saved: {directory}')
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--queries', type=Path, default=ROOT / 'queries.txt')
    parser.add_argument('--output', type=Path, default=ROOT / 'data/raw/kipris')
    parser.add_argument('--docs-count', type=int, default=MAX_DOCS_COUNT)
    parser.add_argument('--delay', type=float, default=1.0)
    args = parser.parse_args()
    if not 1 <= args.docs_count <= MAX_DOCS_COUNT or args.delay < 0.1:
        parser.error('docs-count must be 1..500; delay must be at least 0.1 seconds.')
    load_dotenv(ROOT / '.env')
    key = os.getenv('KIPRIS_API_KEY', '').strip()
    if not key:
        print('[KIPRIS] KIPRIS_API_KEY is missing. Set it in the project root .env.')
        return 1
    try:
        queries = list(dict.fromkeys(line.strip() for line in args.queries.read_text(encoding='utf-8-sig').splitlines()
                                    if line.strip() and not line.lstrip().startswith('#')))
    except OSError:
        print('[KIPRIS] Cannot read queries.txt.')
        return 1
    failures = 0
    for query in queries:
        try:
            collect_query(query, key, args.output, args.docs_count, args.delay)
        except KeyboardInterrupt:
            print('[KIPRIS] Interrupted; saved original responses preserved.')
            return 130
        except Exception as exc:
            # Never print requests exceptions/URLs or raw API messages with credentials.
            message = str(exc).replace(key, '[REDACTED]') if isinstance(exc, RuntimeError) else type(exc).__name__
            print(f'[KIPRIS] Collection failed: {message}')
            failures += 1
        time.sleep(args.delay)
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
