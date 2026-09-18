"""Collect HIRA disease names and codes from the documented XML API."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import time
from urllib.parse import unquote
import xml.etree.ElementTree as ET

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[2]
ENDPOINT = "https://apis.data.go.kr/B551182/diseaseInfoService1/getDissNameCodeList1"
SOURCE = "https://www.data.go.kr/data/15119055/openapi.do"
DEFAULT_PREFIXES = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SICK_TYPES = {"1": "three_level", "2": "four_level"}
MED_TYPES = {"1": "western", "2": "korean_traditional"}


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    for attempt in range(5):
        try:
            temporary.replace(path)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.25 * (attempt + 1))


def parse_xml(content):
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        raise RuntimeError("Disease API returned malformed XML.") from None
    code = root.findtext(".//resultCode")
    message = root.findtext(".//resultMsg") or "unknown API error"
    if code not in {"00", "0"}:
        raise RuntimeError(f"Disease API error code: {code or 'unknown'} ({message}).")
    body = root.find(".//body")
    if body is None:
        raise RuntimeError("Disease API response has no body.")
    try:
        page = int(body.findtext("pageNo"))
        total = int(body.findtext("totalCount"))
        page_size = int(body.findtext("numOfRows"))
    except (TypeError, ValueError):
        raise RuntimeError("Disease API response has invalid pagination fields.") from None
    rows = [{child.tag: child.text or "" for child in item} for item in body.findall("./items/item")]
    return page, total, page_size, rows


def parse_values(value, allowed, name):
    values = tuple(part.strip() for part in value.split(",") if part.strip())
    if not values or any(part not in allowed for part in values):
        raise ValueError(f"{name} must use only: {', '.join(allowed)}")
    return values


def collect(run_id=None, page_size=100, prefixes=DEFAULT_PREFIXES, sick_types="1,2", med_types="1,2"):
    load_dotenv(ROOT / ".env")
    key = unquote(os.getenv("HIRA_DISEASE_API_KEY", "").strip())
    if not key:
        raise RuntimeError("Set HIRA_DISEASE_API_KEY in .env.")
    if not 1 <= page_size <= 100:
        raise ValueError("page-size must be between 1 and 100.")
    prefixes = "".join(dict.fromkeys(prefixes.upper()))
    if not prefixes or any(char not in DEFAULT_PREFIXES for char in prefixes):
        raise ValueError("prefixes may contain only 0-9 and A-Z.")
    sick_types = parse_values(sick_types, SICK_TYPES, "sick-types")
    med_types = parse_values(med_types, MED_TYPES, "med-types")
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ValueError("Invalid run ID.")
    raw_dir = ROOT / "data" / "raw" / "diseases" / run_id
    processed_dir = ROOT / "data" / "processed" / "diseases" / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = raw_dir / "manifest.json"
    manifest = {"run_id": run_id, "status": "running", "source_url": SOURCE, "endpoint": ENDPOINT,
                "operation": "getDissNameCodeList1", "disease_type": "SICK_CD", "prefixes": prefixes,
                "sick_types": list(sick_types), "med_types": list(med_types), "page_size": page_size, "queries": {}}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        fixed = {"prefixes": prefixes, "sick_types": list(sick_types), "med_types": list(med_types), "page_size": page_size}
        if any(manifest.get(name) != value for name, value in fixed.items()):
            raise ValueError("Resume with the original prefixes, types and page-size.")
    atomic_json(manifest_path, manifest)
    output = processed_dir / "disease_codes.jsonl"
    partial = output.with_suffix(".jsonl.partial")
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=Retry(
        total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"], respect_retry_after_header=True)))
    query_total = len(prefixes) * len(sick_types) * len(med_types)
    query_index, collected = 0, 0
    try:
        with partial.open("w", encoding="utf-8") as stream:
            for sick_type in sick_types:
                for med_type in med_types:
                    for prefix in prefixes:
                        query_index += 1
                        query_id = f"sick_{sick_type}_med_{med_type}_prefix_{prefix}"
                        query_dir = raw_dir / query_id
                        query_dir.mkdir(exist_ok=True)
                        page, expected, query_count = 1, None, 0
                        while True:
                            raw_path = query_dir / f"page_{page:06d}.xml"
                            if raw_path.exists():
                                content = raw_path.read_bytes()
                            else:
                                try:
                                    response = session.get(ENDPOINT, params={
                                        "serviceKey": key, "numOfRows": page_size, "pageNo": page,
                                        "sickType": sick_type, "medTp": med_type,
                                        "diseaseType": "SICK_CD", "searchText": prefix,
                                    }, timeout=(10, 60))
                                except requests.RequestException:
                                    raise RuntimeError(f"Network failure at {query_id} page {page}; resume with --run-id {run_id}.") from None
                                if response.status_code != 200:
                                    raise RuntimeError(f"HTTP {response.status_code} at {query_id} page {page}.")
                                content = response.content
                                parse_xml(content)
                                temporary = raw_path.with_suffix(".xml.tmp")
                                temporary.write_bytes(content)
                                temporary.replace(raw_path)
                                time.sleep(0.08)
                            returned_page, total, effective_size, rows = parse_xml(content)
                            if returned_page != page:
                                raise RuntimeError(f"Wrong page returned for {query_id}.")
                            if expected is None:
                                expected = total
                            if total != expected:
                                raise RuntimeError(f"totalCount changed for {query_id}; start a new run.")
                            if effective_size <= 0 or len(rows) != min(effective_size, max(0, total - query_count)):
                                raise RuntimeError(f"Incomplete page for {query_id}.")
                            for row in rows:
                                record = {"disease_name": row.get("sickNm", ""), "disease_code": row.get("sickCd", ""),
                                          "disease_name_en": row.get("sickEngNm", ""), "sick_type": sick_type,
                                          "sick_type_label": SICK_TYPES[sick_type], "medicine_type": med_type,
                                          "medicine_type_label": MED_TYPES[med_type], "original_fields": row,
                                          "source": {"url": SOURCE, "endpoint": ENDPOINT, "run_id": run_id,
                                                     "query_id": query_id, "page": page,
                                                     "raw_file": raw_path.relative_to(ROOT).as_posix()}}
                                stream.write(json.dumps(record, ensure_ascii=False) + "\n")
                            query_count += len(rows)
                            collected += len(rows)
                            manifest["queries"][query_id] = {"status": "running", "total_count": total,
                                "collected_count": query_count, "pages": page, "search_text": prefix}
                            atomic_json(manifest_path, manifest)
                            if query_count == total:
                                break
                            page += 1
                        manifest["queries"][query_id]["status"] = "complete"
                        atomic_json(manifest_path, manifest)
                        print(f"[{query_index}/{query_total}] {query_id}: {query_count}/{expected}", flush=True)
        partial.replace(output)
        manifest["status"] = "complete"
        manifest["collected_count"] = collected
        manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
        atomic_json(manifest_path, manifest)
    except BaseException:
        manifest["status"] = "incomplete"
        manifest["collected_count"] = collected
        atomic_json(manifest_path, manifest)
        raise
    finally:
        session.close()
    return manifest_path, output
