"""Download only the listed KDCA health content, preserving response bytes."""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import quote, unquote
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
import requests

ROOT = Path(__file__).resolve().parent
ENDPOINT = 'http://api.kdca.go.kr/api/provide/healthInfo'
ERRORS = {
 '1': ('APPLICATION_ERROR', '어플리케이션 오류'),
 '2': ('DB_ERROR', '서버 데이터베이스 오류'),
 '3': ('NODATA_ERROR', '데이터 없음'),
 '4': ('HTTP_ERROR', 'HTTP 오류'),
 '5': ('SERVICETIMEOUT_ERROR', '서비스 연결 실패'),
 '10': ('INVALID_REQUEST_PARAMETER_ERROR', '콘텐츠 ID 등 요청 파라미터 오류'),
 '11': ('NO_MANDATORY_REQUEST_PARAMETERS_ERROR', '필수 파라미터 누락'),
 '12': ('NO_OPENAPI_SERVICE_ERROR', '서비스 없음 또는 폐기'),
 '20': ('SERVICE_ACCESS_DENIED_ERROR', '서비스 또는 해당 콘텐츠 접근 거부; 승인 상태 확인'),
 '21': ('TEMPORARILY_DISABLE_THE_SERVICEKEY_ERROR', '일시적으로 사용할 수 없는 서비스키'),
 '22': ('LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR', '요청 제한 초과'),
 '30': ('SERVICE_KEY_IS_NOT_REGISTERED_ERROR', '잘못되었거나 등록되지 않은 서비스키'),
 '31': ('DEADLINE_HAS_EXPIRED_ERROR', '활용 기간 만료'),
 '32': ('UNREGISTERED_IP_ERROR', '등록되지 않은 호출 IP'),
 '33': ('UNSIGNED_CALL_ERROR', '서명되지 않은 호출'),
 '99': ('UNKNOWN_ERROR', '기타 API 오류'),
}

def now():
    return datetime.now(timezone.utc).isoformat()

def redact(value, key):
    text = str(value)
    for secret in sorted({key, unquote(key), quote(key, safe=''), quote(unquote(key), safe='')}, key=len, reverse=True):
        if secret:
            text = text.replace(secret, '[REDACTED]')
    return re.sub(r'(?i)(TOKEN\s*[=:]\s*)[^\s&<>]+', r'\1[REDACTED]', text)

def safe_name(value):
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', value).rstrip(' .') or 'content'
    return name[:100]

def read_contents(path):
    items, seen = [], set()
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['content_id', 'content_name']:
            raise ValueError('contents.csv header must be content_id,content_name')
        for line, row in enumerate(reader, 2):
            identifier = (row.get('content_id') or '').strip()
            name = (row.get('content_name') or '').strip()
            if not re.fullmatch(r'[0-9]{1,10}', identifier) or not name or None in row:
                raise ValueError(f'Invalid contents.csv row {line}')
            identifier = str(int(identifier))
            if identifier == '0' or identifier in seen:
                raise ValueError(f'Invalid or duplicate content_id at row {line}')
            seen.add(identifier)
            items.append({'content_id': int(identifier), 'content_name': name})
    if not items:
        raise ValueError('contents.csv is empty')
    return items

def inspect_xml(body, identifier):
    """Parse for validation only; never reserialize the response file."""
    def local(node):
        return node.tag.rsplit('}', 1)[-1].upper()
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        # The official sample has adjacent HEAD and svc fragments. Support
        # those in memory only, preserving the downloaded bytes unchanged.
        match = re.match(br'\s*(?:\xef\xbb\xbf)?(?:<\?xml[^?]*\?>\s*)?(<HEAD\b)', body, re.I)
        if not match or not re.search(br'</HEAD>\s*<svc\b', body, re.I):
            return 'XML_PARSE_ERROR', 'XML 파싱 실패'
        try:
            root = ET.fromstring(b'<validation>' + body[match.start(1):] + b'</validation>')
        except ET.ParseError:
            return 'XML_PARSE_ERROR', 'XML 파싱 실패'
    head = next((node for node in root.iter() if local(node) == 'HEAD'), None)
    if head is not None:
        fields = {local(n): (n.text or '').strip() for n in head}
        code, message = fields.get('CODE', ''), fields.get('MESSAGE', '')
    else:
        fields = {local(n): (n.text or '').strip() for n in root.iter() if len(n) == 0}
        code = fields.get('RESULTCODE') or fields.get('RETURNREASONCODE') or fields.get('CODE', '')
        message = fields.get('RESULTMSG') or fields.get('RETURNAUTHMSG') or fields.get('MESSAGE', '')
    if head is None or code != 'S001':
        normalized = str(int(code)) if code.isdigit() else code
        error = ERRORS.get(normalized)
        if error:
            return error[0], error[1]
        for label, explanation in ERRORS.values():
            if label in message or label == code:
                return label, explanation
        return code or 'MISSING_RESULT_CODE', message or '정상 HEAD/CODE S001 확인 불가'
    services = [n for n in root.iter() if local(n) == 'SVC']
    if not services or not any((n.text or '').strip() for s in services for n in s.iter() if len(n) == 0):
        return 'NODATA_ERROR', '성공 코드가 있으나 콘텐츠 데이터가 없음'
    ids = [(n.text or '').strip() for s in services for n in s.iter() if local(n) in ('CNTNTS_SN', 'CNTNTSSN')]
    if not ids or any(value != str(identifier) for value in ids):
        return 'CONTENT_ID_MISMATCH', '응답 콘텐츠 ID 누락 또는 요청과 불일치'
    return None, None

def fetch(session, item, key, delay, read_timeout):
    response = None
    for attempt in range(4):
        try:
            response = session.get(ENDPOINT, params={'TOKEN': unquote(key), 'cntntsSn': item['content_id']},
                                   timeout=(15, read_timeout), allow_redirects=False)
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt < 3:
                print(f'[KDCA] 재시도 {attempt+1}/3: {type(exc).__name__}', flush=True)
                time.sleep(max(delay, 2**attempt))
                continue
            return None, {'error_code': 'TIMEOUT' if isinstance(exc, requests.Timeout) else 'CONNECTION_ERROR',
                          'error_message': '최대 3회 재시도 후 연결 실패'}
        except requests.RequestException:
            return None, {'error_code': 'REQUEST_ERROR', 'error_message': '요청 실패; 인증키 보호를 위해 URL 생략'}
        if response.status_code == 429 or 500 <= response.status_code < 600:
            if attempt < 3:
                print(f'[KDCA] 재시도 {attempt+1}/3: HTTP {response.status_code}', flush=True)
                time.sleep(max(delay, 2**attempt))
                continue
        break
    info = {'http_status': response.status_code, 'content_type': redact(response.headers.get('Content-Type', ''), key)}
    if response.status_code != 200:
        info.update(error_code='LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR' if response.status_code == 429 else 'HTTP_ERROR',
                    error_message=f'HTTP {response.status_code}')
        return None, info
    media = info['content_type'].split(';', 1)[0].strip().lower()
    if media not in ('text/xml', 'application/xml') and not media.endswith('+xml'):
        info.update(error_code='UNEXPECTED_CONTENT_TYPE', error_message='XML Content-Type이 아님')
        return None, info
    code, message = inspect_xml(response.content, item['content_id'])
    if code:
        info.update(error_code=redact(code, key), error_message=redact(message, key))
        return None, info
    return response.content, info

def collect(items, key, output, delay=0.4, read_timeout=120, session=None):
    output.mkdir(parents=True, exist_ok=True)
    metadata = {'service': '국가건강정보포털(건강정보 관련) 정보', 'service_id': 'KDCA-HEALTH-HealthInfo',
                'endpoint': ENDPOINT, 'total_requested': len(items), 'success_count': 0,
                'failed_count': 0, 'collected_at': now(), 'status': 'running', 'items': []}
    owned = session is None
    session = session or requests.Session()
    def save_metadata():
        path = output/'metadata.json'
        temporary = output/'metadata.json.tmp'
        temporary.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
        temporary.replace(path)
    try:
        for index, item in enumerate(items):
            print(f"[KDCA] {item['content_name']} ({item['content_id']}) 요청 중...", flush=True)
            if key:
                body, info = fetch(session, item, key, delay, read_timeout)
            else:
                body, info = None, {'error_code': 'MISSING_API_KEY', 'error_message': '.env의 KDCA_API_KEY가 비어 있음; 호출하지 않음'}
            result = {**item, **info, 'checked_at': now()}
            if body is not None:
                filename = f"{item['content_id']}_{safe_name(item['content_name'])}.xml"
                path = output/filename
                # Retain an earlier successful response if a fresh response changes.
                if path.exists() and path.read_bytes() != body:
                    history = output/'history'
                    history.mkdir(exist_ok=True)
                    old = path.read_bytes()
                    (history/(path.stem+'_'+hashlib.sha256(old).hexdigest()+'.xml')).write_bytes(old)
                temporary = path.with_suffix('.xml.tmp')
                temporary.write_bytes(body)
                temporary.replace(path)
                result.update(status='success', file=filename, sha256=hashlib.sha256(body).hexdigest(), bytes=len(body))
                metadata['success_count'] += 1
                print(f'[KDCA] 저장 완료: {path}', flush=True)
            else:
                result['status'] = 'failed'
                metadata['failed_count'] += 1
                with (output/'errors.jsonl').open('a', encoding='utf-8') as stream:
                    stream.write(json.dumps(result, ensure_ascii=False)+'\n')
                print(f"[KDCA] 오류: {info['error_code']} - {info['error_message']}", flush=True)
            metadata['items'].append(result)
            save_metadata()
            if key and index+1 < len(items):
                time.sleep(delay)
        metadata['status'] = 'complete' if not metadata['failed_count'] else 'completed_with_errors'
    finally:
        metadata['finished_at'] = now()
        save_metadata()
        if owned:
            session.close()
    print(f"[KDCA] Collection complete\nSuccess: {metadata['success_count']}\nFailed: {metadata['failed_count']}")
    return metadata

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contents', type=Path, default=ROOT/'contents.csv')
    parser.add_argument('--output', type=Path, default=ROOT/'data/raw/kdca')
    parser.add_argument('--delay', type=float, default=0.4)
    parser.add_argument('--read-timeout', type=float, default=120)
    args = parser.parse_args()
    if not 0.3 <= args.delay <= 0.5 or args.read_timeout <= 0:
        parser.error('delay must be 0.3..0.5 seconds; read-timeout must be positive')
    load_dotenv(ROOT/'.env')
    key = os.getenv('KDCA_API_KEY', '').strip()
    try:
        items = read_contents(args.contents)
        result = collect(items, key, args.output, args.delay, args.read_timeout)
    except (OSError, ValueError):
        print('[KDCA] 파일 읽기/쓰기 또는 CSV 검증 실패; 파일과 컬럼 형식을 확인하세요.')
        return 1
    except KeyboardInterrupt:
        print('[KDCA] 중단됨; 저장된 XML과 metadata 보존')
        return 130
    return int(result['failed_count'] > 0)

if __name__ == '__main__':
    raise SystemExit(main())
