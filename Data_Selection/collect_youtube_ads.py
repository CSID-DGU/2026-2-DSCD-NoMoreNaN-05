"""Resumable, metadata-only YouTube collection. No API credentials in state/logs."""
import argparse
from collections import defaultdict
from contextlib import contextmanager
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import random
import re
import sqlite3
import time
import unicodedata
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
POLICY_VERSION = 3
VIDEO_CACHE_PREFIX = "video-v2:"
# Explicit conservative rules, not a learned probability threshold.
GENERIC_SHORT_MAX = 3
GENERIC_NAMES = {
    "마그네슘", "밀크씨슬", "홍삼정", "홍삼", "유산균", "비타민", "종합비타민",
    "멀티비타민", "오메가3", "칼슘", "루테인", "프로폴리스", "철분", "아연",
    "비타민c", "비타민d", "콜라겐", "프로바이오틱스",
}


class QuotaStop(Exception):
    pass


class ApiError(Exception):
    pass


def comparison_key(text):
    return re.sub(r"[^가-힣a-z0-9]", "", unicodedata.normalize("NFC", text).lower())


def duration_seconds(value):
    if not isinstance(value, str) or value.endswith("T"):
        return None
    match = re.fullmatch(
        r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?)?", value or ""
    )
    if not match or not any(x is not None for x in match.groups()):
        return None
    days, hours, minutes, seconds = (float(x or 0) for x in match.groups())
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def matches(product, video, official_ids=()):
    """Legacy strict check retained for compatibility; collection uses assess()."""
    snippet = video.get("snippet", {})
    duration = duration_seconds(video.get("contentDetails", {}).get("duration"))
    if duration is None or not 0 < duration <= 60:
        return False
    text_keys = [comparison_key(snippet.get("title", "") + " " + snippet.get("description", ""))]
    pk, ck = product["product_key"], product["company_key"]
    return bool(pk and ck and any(pk in key for key in text_keys) and (
        any(ck in key for key in text_keys)
        or ck in comparison_key(snippet.get("channelTitle", ""))
        or snippet.get("channelId") in official_ids
    ))


def assess(product, video, manufacturer_channel_ids=()):
    """Separate product candidates from manufacturer evidence and ad hints."""
    snippet = video.get("snippet", {})
    title = snippet.get("title", "")
    description = snippet.get("description", "")
    channel = snippet.get("channelTitle", "")
    text = title + " " + description
    ck = product["company_key"]
    locations = [name for name, value in (("title", title), ("description", description),
                                         ("channel_title", channel))
                 if ck and ck in comparison_key(value)]
    manufacturer_label = False
    for match in re.finditer(r"(?:제조업소|제조원|제조사)\s*[:：]?\s*([^\r\n;|]{1,120})", description):
        label_value = re.split(r"(?:판매원|판매사|유통전문판매원|수입원)\s*[:：]", match.group(1))[0]
        if ck and ck in comparison_key(label_value):
            manufacturer_label = True
    paid = video.get("paidProductPlacementDetails", {}).get("hasPaidProductPlacement")
    if not isinstance(paid, bool):
        paid = None
    keywords = [word for word in ("광고", "15초", "30초") if word in text]
    for word, pattern in (("#ad", r"#ad(?![a-z])"), ("CF", r"(?<![a-z])(?:tv)?cf(?![a-z])")):
        if re.search(pattern, text, flags=re.IGNORECASE):
            keywords.append(word)
    generic_reasons = list(product.get("generic_reasons", []))
    evidence = dict(manufacturer_in_text=bool(locations), manufacturer_locations=locations,
                    manufacturer_label=manufacturer_label, paid_promotion=paid,
                    ad_keywords=keywords,
                    manufacturer_channel_candidate=snippet.get("channelId") in manufacturer_channel_ids)
    duration = duration_seconds(video.get("contentDetails", {}).get("duration"))
    reasons = []
    if duration is None or not 0 < duration <= 60:
        reasons.append("duration_out_of_range_or_unknown")
    if not product["product_key"] or product["product_key"] not in comparison_key(text):
        reasons.append("product_name_not_in_title_or_description")
    strong = evidence["manufacturer_in_text"] or manufacturer_label
    if product.get("generic", False) and not strong:
        reasons.append("generic_without_manufacturer_evidence")
    return dict(status="rejected" if reasons else ("confirmed" if strong else "needs_review"),
                evidence=evidence, generic=product.get("generic", False), generic_reasons=generic_reasons,
                rejection_reasons=reasons)


class State:
    def __init__(self, directory):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(directory / "collection.sqlite")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS usage (day TEXT PRIMARY KEY, units INTEGER, searches INTEGER);
            CREATE TABLE IF NOT EXISTS results (product TEXT, video TEXT, value TEXT,
                                                PRIMARY KEY(product, video));
            CREATE TABLE IF NOT EXISTS done (key TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS assessments (product TEXT, video TEXT, value TEXT,
                                                     PRIMARY KEY(product, video));
        """)

    def cached(self, key):
        row = self.db.execute("SELECT value FROM cache WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None

    def put(self, key, value):
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO cache VALUES (?,?)", (key, json.dumps(value)))

    def reserve(self, search, unit_limit, search_limit):
        day = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
        # Conservative legacy-equivalent budget plus current separate search cap.
        cost = 100 if search else 1
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO usage VALUES (?,0,0)", (day,))
            units, searches = self.db.execute("SELECT units,searches FROM usage WHERE day=?", (day,)).fetchone()
            if units + cost > unit_limit or searches + int(search) > search_limit:
                raise QuotaStop("Local daily API budget reached; progress saved.")
            self.db.execute("UPDATE usage SET units=units+?, searches=searches+? WHERE day=?",
                            (cost, int(search), day))

    def complete(self, task):
        return self.db.execute("SELECT 1 FROM done WHERE key=?", (task,)).fetchone() is not None

    def mark(self, task):
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO done VALUES (?)", (task,))

    def add(self, product, video, method, assessment=None):
        snippet = video["snippet"]
        assessment = assessment or assess(product, video)
        record = {field: product[field] for field in ("id", "product_name", "company_name")}
        record.update(url="https://www.youtube.com/watch?v=" + video["id"], video_id=video["id"],
                      title=snippet.get("title", ""), channel_title=snippet.get("channelTitle", ""),
                      duration_sec=duration_seconds(video["contentDetails"]["duration"]),
                      published_at=snippet.get("publishedAt", ""), method=method,
                      description_preview=snippet.get("description", "")[:300],
                      logic_version=POLICY_VERSION, **assessment)
        with self.db:
            args = (str(product["id"]), video["id"], json.dumps(record, ensure_ascii=False))
            self.db.execute("INSERT OR REPLACE INTO assessments VALUES (?,?,?)", args)
            if assessment["status"] == "rejected":
                self.db.execute("DELETE FROM results WHERE product=? AND video=?", args[:2])
            else:
                self.db.execute("INSERT OR REPLACE INTO results VALUES (?,?,?)", args)

    def found(self, product):
        return any(json.loads(row[0]).get("logic_version") == POLICY_VERSION for row in
                   self.db.execute("SELECT value FROM results WHERE product=?", (str(product["id"]),)))

    def export(self, destination):
        rows = [json.loads(row[0]) for row in self.db.execute("SELECT value FROM results ORDER BY product,video")]
        rows = [row for row in rows if row.get("logic_version") == POLICY_VERSION]
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(destination)
        return len(rows)

    def report(self, destination, product_ids=None):
        selected = None if product_ids is None else {str(id) for id in product_ids}
        rows = [json.loads(row[0]) for row in self.db.execute("SELECT value FROM assessments ORDER BY product,video")]
        rows = [row for row in rows if row.get("logic_version") == POLICY_VERSION
                and (selected is None or str(row["id"]) in selected)]
        counts = {name: sum(row["status"] == name for row in rows)
                  for name in ("confirmed", "needs_review", "rejected")}
        report = dict(logic_version=POLICY_VERSION, counts=counts,
                      counted_unit="product-video pairs; unavailable IDs are not assessed",
                      examples={name: [row for row in rows if row["status"] == name][:5] for name in counts})
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(destination)
        return counts


class Client:
    def __init__(self, state, key, unit_limit=10000, search_limit=100, session=None, sleep=time.sleep,
                 max_api_calls=None):
        self.state, self.key = state, key
        self.unit_limit, self.search_limit = unit_limit, search_limit
        self.session, self.sleep = session or requests.Session(), sleep
        self.max_api_calls, self.api_calls = max_api_calls, 0

    def get(self, resource, **params):
        cache_key = json.dumps([resource, params], sort_keys=True, ensure_ascii=False)
        cached = self.state.cached(cache_key)
        if cached is not None:
            return cached
        for attempt in range(6):
            if self.max_api_calls is not None and self.api_calls >= self.max_api_calls:
                raise QuotaStop("Per-run API call limit reached; progress saved.")
            self.state.reserve(resource == "search", self.unit_limit, self.search_limit)
            self.api_calls += 1
            try:
                response = self.session.get("https://www.googleapis.com/youtube/v3/" + resource,
                                            params={**params, "key": self.key}, timeout=(10, 45))
            except requests.RequestException:
                # Never propagate requests exceptions: their URL can contain the key.
                if attempt == 5:
                    raise ApiError("Network request failed after retries; progress saved.") from None
                self.sleep(min(60, 2 ** attempt) + random.random())
                continue
            try:
                body = response.json()
            except ValueError:
                body = {}
            reasons = {e.get("reason") for e in body.get("error", {}).get("errors", [])}
            if reasons & {"quotaExceeded", "dailyLimitExceeded"}:
                raise QuotaStop("YouTube daily quota exceeded; progress saved.")
            if response.status_code == 404 and resource in {"channels", "playlistItems"}:
                # A channel can advertise an uploads playlist that is no longer
                # publicly available. Treat it as empty, not an authentication error.
                empty = {"items": [], "unavailable": True}
                self.state.put(cache_key, empty)
                return empty
            if response.status_code >= 500 or response.status_code == 429 or "rateLimitExceeded" in reasons:
                if attempt == 5:
                    raise ApiError("YouTube temporary failure after retries; progress saved.")
                self.sleep(min(60, 2 ** attempt) + random.random())
                continue
            if response.status_code != 200 or "error" in body:
                raise ApiError(f"YouTube API rejected {resource} request (HTTP {response.status_code}); check API access and request validity.")
            if not isinstance(body.get("items"), list):
                raise ApiError("YouTube returned an invalid response; progress saved.")
            self.state.put(cache_key, body)
            return body


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def details(client, state, ids):
    ids = list(dict.fromkeys(ids))
    missing = [id for id in ids if state.cached(VIDEO_CACHE_PREFIX + id) is None]
    for start in range(0, len(missing), 50):
        batch = missing[start:start + 50]
        items = client.get("videos", part="snippet,contentDetails,paidProductPlacementDetails", id=",".join(batch))["items"]
        returned = {item["id"]: item for item in items}
        for id in batch:
            # Empty object also caches inaccessible/deleted video IDs.
            state.put(VIDEO_CACHE_PREFIX + id, returned.get(id, {}))
    for id in ids:
        item = state.cached(VIDEO_CACHE_PREFIX + id)
        if item:
            yield item


def collect_channel(client, state, products, channel_results=5):
    task = f"channel-v{POLICY_VERSION + 1}:" + fingerprint([products, channel_results])
    if state.complete(task):
        return
    company = products[0]
    response = client.get("search", part="snippet", type="channel", q=company["company_core"],
                          regionCode="KR", maxResults=channel_results)
    channels = [item["id"]["channelId"] for item in response["items"]
                if item.get("id", {}).get("channelId")
                and company["company_key"] in comparison_key(item.get("snippet", {}).get("title", ""))]
    state.put("official:" + company["company_key"], channels)
    for channel in dict.fromkeys(channels):
        info = client.get("channels", part="contentDetails", id=channel)
        for item in info["items"]:
            uploads = item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
            if not uploads:
                continue
            token = ""
            seen = set()
            while True:
                params = dict(part="contentDetails", playlistId=uploads, maxResults=50)
                if token:
                    params["pageToken"] = token
                page = client.get("playlistItems", **params)
                ids = [entry["contentDetails"]["videoId"] for entry in page["items"]]
                for video in details(client, state, ids):
                    snippet = video.get("snippet", {})
                    text_key = comparison_key(snippet.get("title", "") + " " + snippet.get("description", ""))
                    for product in products:
                        if product["product_key"] in text_key:
                            state.add(product, video, "channel", assess(product, video, channels))
                token = page.get("nextPageToken")
                if not token:
                    break
                if token in seen:
                    raise ApiError("Repeated playlist page token; progress saved.")
                seen.add(token)
    state.mark(task)


def collect_search(client, state, product):
    task = f"search-v{POLICY_VERSION}:" + fingerprint(product)
    if state.found(product) or state.complete(task):
        return
    page = client.get("search", part="snippet", type="video", q=product["product_core"], videoDuration="short",
                      regionCode="KR", relevanceLanguage="ko", maxResults=25)
    ids = [item["id"]["videoId"] for item in page["items"] if item.get("id", {}).get("videoId")]
    for video in details(client, state, ids):
        state.add(product, video, "search", assess(product, video,
                  state.cached("official:" + product["company_key"]) or []))
    state.mark(task)


def load_products(path, limit=None, company_limit=None, selected_ids=None):
    rows = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(rows, list):
        raise ValueError("Input must be a JSON list.")
    company_sets = defaultdict(set)
    for row in rows:
        if row.get("product_key") and row.get("company_key"):
            company_sets[row["product_key"]].add(row["company_key"])
    requested = None if selected_ids is None else {str(id) for id in selected_ids}
    available = {str(row.get("id")) for row in rows if row.get("category") == "search"}
    if requested is not None and not requested <= available:
        raise ValueError("Some --ids are missing or excluded from search.")
    selected, companies, ids = [], set(), set()
    for row in rows:
        if row.get("category") != "search":
            continue
        for field in ("product_name", "company_name", "product_core", "company_core", "product_key", "company_key"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"Invalid search record field: {field}")
        if "id" not in row or str(row["id"]) in ids:
            raise ValueError("Input IDs must be present and unique.")
        ids.add(str(row["id"]))
        if requested is not None and str(row["id"]) not in requested:
            continue
        for field in ("product_key", "company_key"):
            if comparison_key(row[field]) != row[field]:
                raise ValueError(f"Non-normalized comparison key: {field}")
        company = row["company_core"]
        if company_limit and company not in companies and len(companies) >= company_limit:
            continue
        companies.add(company)
        row = dict(row)
        generic_reasons = []
        if len(company_sets[row["product_key"]]) > 1:
            generic_reasons.append("same_product_key_multiple_companies")
        if len(row["product_key"]) <= GENERIC_SHORT_MAX:
            generic_reasons.append("short_name_3_or_fewer_characters")
        if row["product_key"] in GENERIC_NAMES:
            generic_reasons.append("common_category_name")
        row.update(generic=bool(generic_reasons), generic_reasons=generic_reasons)
        selected.append(row)
        if limit and len(selected) >= limit:
            break
    return selected


@contextmanager
def exclusive_run(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    stream = (directory / "run.lock").open("a+b")
    stream.seek(0)
    if stream.read(1) == b"":
        stream.write(b"0")
        stream.flush()
    stream.seek(0)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        stream.close()
        raise ApiError("Another collector is already using this state directory.") from None
    try:
        yield
    finally:
        stream.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("channel", "search", "all", "export"))
    parser.add_argument("--input", type=Path, default=ROOT / "products_for_search.json")
    parser.add_argument("--state", type=Path, default=ROOT / "state")
    parser.add_argument("--output", type=Path, default=ROOT / "ad_video_urls.json")
    parser.add_argument("--report", type=Path, default=ROOT / "state" / "collection_report.json")
    parser.add_argument("--ids", nargs="+", help="Only these product IDs (space or comma separated)")
    parser.add_argument("--limit", type=int, help="Maximum products in this invocation")
    parser.add_argument("--company-limit", type=int, help="Maximum distinct companies")
    parser.add_argument("--channel-results", type=int, choices=range(1, 51), default=5,
                        metavar="1..50", help="Channel search candidates per company (default: 5)")
    parser.add_argument("--daily-unit-limit", type=int, default=10000)
    parser.add_argument("--daily-search-limit", type=int, default=100)
    parser.add_argument("--max-api-calls", type=int, help="Maximum uncached HTTP attempts, including retries, this run")
    args = parser.parse_args(argv)
    for value in (args.limit, args.company_limit, args.daily_unit_limit, args.daily_search_limit, args.max_api_calls):
        if value is not None and value <= 0:
            parser.error("Limits must be positive.")
    state = None
    products = None
    try:
        with exclusive_run(args.state):
            state = State(args.state)
            try:
                if args.mode != "export":
                    input_hash = fingerprint(json.loads(args.input.read_text(encoding="utf-8-sig")))
                    previous = state.cached("input-hash")
                    if previous is not None and previous != input_hash:
                        raise ApiError("Input changed. Use a different --state directory to avoid mixing datasets.")
                    selected_ids = [id for item in (args.ids or []) for id in item.split(",") if id]
                    products = load_products(args.input, args.limit, args.company_limit, selected_ids or None)
                    state.put("input-hash", input_hash)
                    load_dotenv(ROOT / ".env")
                    key = (os.environ.get("YT_API_KEY") or os.environ.get("YOUTUBE_API_KEY") or "").strip()
                    if not key:
                        raise ApiError("YT_API_KEY is missing. No API requests made.")
                    client = Client(state, key, args.daily_unit_limit, args.daily_search_limit,
                                    max_api_calls=args.max_api_calls)
                    print(f"Selected {len(products)} products; {len({p['company_core'] for p in products})} companies.")
                    groups = defaultdict(list)
                    for product in products:
                        groups[product["company_core"]].append(product)
                    if args.mode in ("search", "all"):
                        for product in products:
                            collect_search(client, state, product)
                    if args.mode in ("channel", "all"):
                        for group in groups.values():
                            collect_channel(client, state, group, args.channel_results)
            finally:
                print(f"Exported {state.export(args.output)} matches to {args.output}")
                counts = state.report(args.report, None if products is None else [p["id"] for p in products])
                print("Assessment counts: " + json.dumps(counts))
                state.db.close()
    except QuotaStop as error:
        print(str(error))
        return 0
    except (ApiError, ValueError, OSError) as error:
        print(f"Stopped: {error}")
        return 1
    except KeyboardInterrupt:
        print("Interrupted; progress saved.")
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
