"""Collect YouTube health-functional-food ad candidates without downloading videos."""

import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import time

import requests
import yaml
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


ROOT = Path(__file__).resolve().parents[2]
API_URL = "https://www.googleapis.com/youtube/v3"
KEYWORDS_PATH = ROOT / "configs" / "youtube_search_keywords.yaml"
RAW_ROOT = ROOT / "data" / "raw" / "youtube_search"
CANDIDATES_PATH = ROOT / "data" / "processed" / "youtube_ad_candidates.csv"
URLS_PATH = ROOT / "data" / "input" / "ad_urls.csv"
CANDIDATE_FIELDS = [
    "video_id", "source_url", "title", "description", "channel_id", "channel_title",
    "published_at", "duration", "view_count", "search_keywords", "search_categories", "collected_at",
]
URL_FIELDS = ["source_url", "platform", "video_id"]


def utc_now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def load_keywords(path=None):
    path = path or KEYWORDS_PATH
    try:
        content = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RuntimeError(f"Keyword configuration not found: {path}") from None
    if not isinstance(content, dict) or not content:
        raise RuntimeError("Keyword configuration must be a non-empty category-to-keyword mapping.")
    entries = []
    for category, keywords in content.items():
        if not isinstance(category, str) or not isinstance(keywords, list):
            raise RuntimeError("Each category must contain a list of keywords.")
        for keyword in keywords:
            if not isinstance(keyword, str) or not keyword.strip():
                raise RuntimeError("Every keyword must be a non-empty string.")
            entries.append((category, keyword.strip()))
    if not entries:
        raise RuntimeError("Keyword configuration contains no keywords.")
    return entries


def load_existing_candidates(path=None):
    path = path or CANDIDATES_PATH
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or "video_id" not in reader.fieldnames:
            raise RuntimeError(f"Existing candidate CSV has no video_id column: {path}")
        candidates = {}
        for row in reader:
            video_id = (row.get("video_id") or "").strip()
            if not video_id:
                continue
            candidates[video_id] = {field: row.get(field, "") for field in CANDIDATE_FIELDS}
    return candidates


def pipe_values(value):
    return [item for item in value.split("|") if item]


def add_search_context(row, keyword, category):
    keywords = pipe_values(row.get("search_keywords", ""))
    categories = pipe_values(row.get("search_categories", ""))
    if keyword not in keywords:
        keywords.append(keyword)
    if category not in categories:
        categories.append(category)
    row["search_keywords"] = "|".join(keywords)
    row["search_categories"] = "|".join(categories)


def candidate_scoring_inputs(row):
    """Return the permitted future scoring inputs without assigning an ad label or score."""
    return {field: row.get(field, "") for field in (
        "search_keywords", "title", "description", "channel_title",
    )}


def safe_keyword_name(keyword):
    normalized = re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", keyword).strip("_")
    return normalized[:80] or "keyword"


def require_api_key():
    load_dotenv(ROOT / ".env")
    key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY is missing. Add it to .env after enabling YouTube Data API v3.")
    return key


class YouTubeClient:
    def __init__(self, api_key, session=None):
        self.api_key = api_key
        self.session = session or requests.Session()
        if session is None:
            self.session.mount("https://", HTTPAdapter(max_retries=Retry(
                total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"], respect_retry_after_header=True)))

    def get(self, resource, params):
        try:
            response = self.session.get(f"{API_URL}/{resource}", params={**params, "key": self.api_key}, timeout=(10, 45))
        except requests.RequestException:
            raise RuntimeError(f"YouTube API network failure while requesting {resource}.") from None
        if response.status_code != 200:
            try:
                reason = response.json().get("error", {}).get("message", "Unknown API error")
            except ValueError:
                reason = "Unknown API error"
            raise RuntimeError(f"YouTube API {resource} failed (HTTP {response.status_code}): {reason}")
        try:
            return response.json()
        except ValueError:
            raise RuntimeError(f"YouTube API {resource} returned invalid JSON.") from None

    def close(self):
        self.session.close()


def collect(max_results, max_pages_per_keyword=1, run_id=None, client=None, sleep_seconds=0.1):
    if max_results < 1:
        raise ValueError("max-results must be at least 1.")
    if max_pages_per_keyword < 1:
        raise ValueError("max-pages-per-keyword must be at least 1.")
    keywords = load_keywords()
    candidates = load_existing_candidates()
    existing_count = len(candidates)
    run_id = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ValueError("Invalid run ID.")
    raw_dir = RAW_ROOT / run_id
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = raw_dir / "manifest.json"
    manifest = {
        "run_id": run_id, "started_at": utc_now(), "status": "running",
        "max_results": max_results, "max_pages_per_keyword": max_pages_per_keyword,
        "keyword_count": len(keywords), "existing_candidates": existing_count,
        "total_api_results": 0, "new_unique_videos": 0, "metadata_unavailable": [], "requests": [],
        "filtering": "none; all type=video search results remain candidates",
    }
    atomic_json(manifest_path, manifest)
    owned_client = client is None
    client = client or YouTubeClient(require_api_key())
    discovered = {}
    total_api_results = 0
    try:
        for index, (category, keyword) in enumerate(keywords, start=1):
            if len(candidates) + len(discovered) >= max_results:
                break
            print(f"[{index}/{len(keywords)}] {keyword}", flush=True)
            page_token = None
            for page in range(1, max_pages_per_keyword + 1):
                if len(candidates) + len(discovered) >= max_results:
                    break
                result = client.get("search", {
                    "part": "snippet", "q": keyword, "type": "video", "maxResults": 50,
                    **({"pageToken": page_token} if page_token else {}),
                })
                raw_path = raw_dir / f"{index:03d}_{safe_keyword_name(keyword)}_page_{page:03d}.json"
                atomic_json(raw_path, result)
                manifest["requests"].append({"kind": "search", "keyword": keyword, "category": category,
                                             "page": page, "raw_file": raw_path.relative_to(ROOT).as_posix()})
                items = result.get("items", [])
                if not isinstance(items, list):
                    raise RuntimeError("YouTube search API returned an unexpected items schema.")
                total_api_results += len(items)
                for item in items:
                    identifier = item.get("id", {}) if isinstance(item, dict) else {}
                    video_id = identifier.get("videoId") if isinstance(identifier, dict) else None
                    if not isinstance(video_id, str) or not video_id:
                        continue
                    if video_id in candidates:
                        add_search_context(candidates[video_id], keyword, category)
                        continue
                    record = discovered.setdefault(video_id, {
                        "video_id": video_id, "source_url": f"https://www.youtube.com/watch?v={video_id}",
                        "title": "", "description": "", "channel_id": "", "channel_title": "",
                        "published_at": "", "duration": "", "view_count": "", "search_keywords": "",
                        "search_categories": "", "collected_at": utc_now(), "_search_snippet": item.get("snippet", {}),
                    })
                    add_search_context(record, keyword, category)
                print(f"Collected: {len(items)}\nUnique videos: {len(candidates) + len(discovered)}", flush=True)
                page_token = result.get("nextPageToken")
                if not page_token:
                    break
                time.sleep(sleep_seconds)
        ids = list(discovered)
        for offset in range(0, len(ids), 50):
            batch = ids[offset:offset + 50]
            result = client.get("videos", {"part": "snippet,contentDetails,statistics", "id": ",".join(batch), "maxResults": 50})
            batch_number = offset // 50 + 1
            raw_path = raw_dir / f"metadata_batch_{batch_number:03d}.json"
            atomic_json(raw_path, result)
            manifest["requests"].append({"kind": "videos", "video_ids": batch,
                                         "raw_file": raw_path.relative_to(ROOT).as_posix()})
            returned = {}
            for item in result.get("items", []):
                if isinstance(item, dict) and isinstance(item.get("id"), str):
                    returned[item["id"]] = item
            for video_id in batch:
                row = discovered[video_id]
                item = returned.get(video_id)
                snippet = item.get("snippet", {}) if item else row.pop("_search_snippet", {})
                row["title"] = snippet.get("title", "") or ""
                row["description"] = snippet.get("description", "") or ""
                row["channel_id"] = snippet.get("channelId", "") or ""
                row["channel_title"] = snippet.get("channelTitle", "") or ""
                row["published_at"] = snippet.get("publishedAt", "") or ""
                if item:
                    row["duration"] = item.get("contentDetails", {}).get("duration", "") or ""
                    row["view_count"] = item.get("statistics", {}).get("viewCount", "") or ""
                else:
                    manifest["metadata_unavailable"].append(video_id)
                row.pop("_search_snippet", None)
            time.sleep(sleep_seconds)
        candidates.update(discovered)
        rows = sorted(candidates.values(), key=lambda row: (row["collected_at"], row["video_id"]))
        atomic_csv(CANDIDATES_PATH, CANDIDATE_FIELDS, rows)
        atomic_csv(URLS_PATH, URL_FIELDS, [
            {"source_url": row["source_url"], "platform": "youtube", "video_id": row["video_id"]}
            for row in rows
        ])
        manifest.update({"status": "complete", "finished_at": utc_now(), "total_api_results": total_api_results,
                         "new_unique_videos": len(discovered), "final_unique_videos": len(rows)})
        atomic_json(manifest_path, manifest)
        return manifest
    except BaseException:
        manifest.update({"status": "incomplete", "total_api_results": total_api_results,
                         "new_unique_videos": len(discovered)})
        atomic_json(manifest_path, manifest)
        raise
    finally:
        if owned_client:
            client.close()
