"""Collect the two documented MFDS operations with resumable raw pages."""
import hashlib
import json
import os
from pathlib import Path
import time
from datetime import datetime, timezone
from urllib.parse import unquote
import xml.etree.ElementTree as ET

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[2]
ENDPOINT = "https://apis.data.go.kr/1471000/HtfsInfoService03"
SOURCE = "https://www.data.go.kr/data/15056760/openapi.do"
OPERATIONS = ("getHtfsList01", "getHtfsItem01")
FIELDS = {"PRDUCT": "product_name", "ENTRPS": "company_name",
          "STTEMNT_NO": "manufacturing_report_number", "REGIST_DT": "registration_date",
          "DISTB_PD": "shelf_life", "SUNGSANG": "appearance", "SRV_USE": "intake_method",
          "PRSRV_PD": "storage_and_distribution_standard", "INTAKE_HINT1": "intake_precautions",
          "MAIN_FNCTN": "main_functionality", "BASE_STANDARD": "specification"}


def write_json(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def parse_page(content):
    try:
        data = json.loads(content)
    except (ValueError, UnicodeError):
        try:
            root = ET.fromstring(content)
            code = root.findtext(".//returnReasonCode") or root.findtext(".//resultCode")
        except ET.ParseError:
            code = "unknown"
        raise RuntimeError(f"Non-JSON API response (code: {code}); check API approval/key/quota.") from None
    data = data.get("response", data)
    code = str(data.get("header", {}).get("resultCode", "missing"))
    if code not in {"00", "0"}:
        raise RuntimeError(f"API error code: {code}; check API approval/key/quota.")
    body = data["body"]
    items = body.get("items") or []
    if isinstance(items, dict):
        items = items.get("item") or []
    if isinstance(items, dict):
        items = [items]
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise RuntimeError("Unexpected API item schema.")
    items = [row["item"] if set(row) == {"item"} and isinstance(row["item"], dict) else row for row in items]
    return body, items


def collect(run_id=None, page_size=100):
    load_dotenv(ROOT / ".env")
    key = unquote(os.getenv("DATA_GO_KR_API_KEY", "").strip())
    if not key:
        raise RuntimeError("Set DATA_GO_KR_API_KEY in .env.")
    if not 1 <= page_size <= 100:
        raise ValueError("page-size must be between 1 and 100 (collector safety limit).")
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    if any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in run_id):
        raise ValueError("Invalid run ID.")
    raw = ROOT / "data/raw/mfds_products" / run_id
    processed = ROOT / "data/processed/mfds_products" / run_id
    raw.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    manifest_path = raw / "manifest.json"
    manifest = {"run_id": run_id, "source_url": SOURCE, "endpoint": ENDPOINT,
                "requested_page_size": page_size, "status": "running", "operations": {}}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["requested_page_size"] != page_size:
            raise ValueError("Resume with the original page-size.")
    manifest["status"] = "running"
    write_json(manifest_path, manifest)
    print(f"Run ID: {run_id}", flush=True)
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"], respect_retry_after_header=True)))
    try:
        for operation in OPERATIONS:
            folder = raw / operation
            folder.mkdir(exist_ok=True)
            output = processed / f"{operation}.jsonl"
            temp = output.with_suffix(".jsonl.partial")
            page, count, expected = 1, 0, None
            fingerprints, ids = set(), set()
            duplicate_ids = 0
            with temp.open("w", encoding="utf-8") as stream:
                while True:
                    path = folder / f"page_{page:06d}.json"
                    if path.exists():
                        content = path.read_bytes()
                    else:
                        try:
                            response = session.get(f"{ENDPOINT}/{operation}", params={
                                "ServiceKey": key, "pageNo": page, "numOfRows": page_size, "type": "json"
                            }, timeout=(10, 60))
                        except requests.RequestException:
                            raise RuntimeError(f"Network failure at {operation} page {page}; resume with --run-id {run_id}.") from None
                        if response.status_code != 200:
                            raise RuntimeError(f"HTTP {response.status_code} at {operation} page {page}.")
                        content = response.content
                        parse_page(content)
                        pending = path.with_suffix(".json.tmp")
                        pending.write_bytes(content)
                        pending.replace(path)
                        time.sleep(0.15)
                    body, items = parse_page(content)
                    total = int(body["totalCount"])
                    if expected is None:
                        expected = total
                    if total != expected:
                        raise RuntimeError("totalCount changed; start a new run for consistency.")
                    if int(body["pageNo"]) != page:
                        raise RuntimeError("API returned the wrong page number.")
                    size = int(body["numOfRows"])
                    if size <= 0 or len(items) != min(size, max(0, total - count)):
                        raise RuntimeError("Incomplete or inconsistent page; collection is not complete.")
                    fingerprint = hashlib.sha256(json.dumps(items, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                    if items and fingerprint in fingerprints:
                        raise RuntimeError("Repeated API page detected.")
                    fingerprints.add(fingerprint)
                    for row in items:
                        identifier = row.get("STTEMNT_NO")
                        if identifier is not None:
                            duplicate_ids += identifier in ids
                            ids.add(identifier)
                        record = {name: row.get(field) for field, name in FIELDS.items()}
                        record.update({"original_fields": row, "source": {
                            "url": SOURCE, "endpoint": f"{ENDPOINT}/{operation}", "run_id": run_id,
                            "page": page, "raw_file": path.relative_to(ROOT).as_posix()}})
                        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                    count += len(items)
                    manifest["operations"][operation] = {
                        "status": "running", "total_count": total, "collected_count": count,
                        "pages": page, "effective_page_size": size, "duplicate_report_numbers": duplicate_ids}
                    write_json(manifest_path, manifest)
                    print(f"{operation}: page {page}, {count}/{total}", flush=True)
                    if count == total:
                        break
                    page += 1
            temp.replace(output)
            manifest["operations"][operation]["status"] = "complete"
            write_json(manifest_path, manifest)
        manifest["status"] = "complete"
        manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        write_json(manifest_path, manifest)
    except BaseException:
        manifest["status"] = "incomplete"
        write_json(manifest_path, manifest)
        raise
    finally:
        session.close()
    return manifest_path, processed
