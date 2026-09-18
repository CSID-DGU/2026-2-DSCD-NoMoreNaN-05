"""Filter YouTube candidates conservatively, then classify retained rows with an LLM."""

import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time

import requests
from dotenv import load_dotenv

from src.collectors.youtube_candidate_collector import CANDIDATES_PATH, ROOT


RULE_OUTPUT_PATH = ROOT / "data" / "processed" / "youtube_rule_filtered.csv"
CLASSIFICATIONS_PATH = ROOT / "data" / "processed" / "youtube_ad_classifications.csv"
CONFIRMED_URLS_PATH = ROOT / "data" / "input" / "ad_urls.csv"
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"

RULE_FIELDS = [
    "video_id", "title", "source_url", "channel_title", "search_keywords",
    "rule_result", "rule_reason",
]
CLASSIFICATION_FIELDS = [
    "video_id", "title", "source_url", "channel_title", "search_keywords",
    "rule_result", "llm_result", "confidence", "reason", "model", "classified_at", "input_hash",
]
CONFIRMED_URL_FIELDS = ["source_url", "platform", "video_id"]

# These terms identify an informational format, rather than a product promotion.  The list
# intentionally stays narrow: rows without one of these cues are sent to the LLM.
NON_AD_PATTERNS = (
    ("뉴스룸", "뉴스 보도"), ("뉴스", "뉴스 보도"), ("기자", "뉴스 보도"),
    ("속보", "뉴스 보도"), ("브리핑", "뉴스 보도"), ("팩트체크", "팩트체크"),
    ("시사", "시사 콘텐츠"), ("강의", "강의 콘텐츠"), ("세미나", "세미나 콘텐츠"),
    ("학회", "학술 행사"), ("학술", "학술 콘텐츠"), ("대학 특강", "강의 콘텐츠"),
    ("다큐", "다큐멘터리"), ("토론", "토론 콘텐츠"),
)


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


def load_csv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        return []
    required = {"video_id", "title", "source_url", "description", "channel_title", "search_keywords"}
    missing = required - set(rows[0])
    if missing:
        raise RuntimeError(f"Candidate CSV is missing columns: {', '.join(sorted(missing))}")
    return rows


def normalise(value):
    return re.sub(r"\s+", " ", (value or "").casefold()).strip()


def rule_filter(row):
    """Reject only candidates that explicitly present as news, classes, or academic content."""
    title = normalise(row.get("title"))
    channel = normalise(row.get("channel_title"))
    text = f"{title} {channel}"
    for term, reason in NON_AD_PATTERNS:
        if normalise(term) in text:
            return "REJECT", f"{reason}: '{term}' 표시"
    return "PASS", "명백한 뉴스·강의·학술 비광고 신호 없음"


def rule_rows(candidates):
    rows = []
    for candidate in candidates:
        result, reason = rule_filter(candidate)
        rows.append({
            "video_id": candidate["video_id"], "title": candidate["title"],
            "source_url": candidate["source_url"], "channel_title": candidate["channel_title"],
            "search_keywords": candidate["search_keywords"], "rule_result": result, "rule_reason": reason,
        })
    return rows


def input_fingerprint(row):
    text = "\n".join(row.get(key, "") for key in ("video_id", "title", "description", "channel_title", "search_keywords"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def require_openai_key():
    load_dotenv(ROOT / ".env")
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to .env to run LLM classification.")
    return key


def llm_prompt(row):
    description = (row.get("description") or "")[:4000]
    return {
        "video_id": row.get("video_id", ""),
        "title": row.get("title", ""),
        "description": description,
        "channel_title": row.get("channel_title", ""),
        "search_keywords": row.get("search_keywords", ""),
    }


def output_text(response):
    direct = response.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct
    for item in response.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and content.get("type") in {"output_text", "text"}:
                text = content.get("text", "")
                if isinstance(text, str) and text.strip():
                    return text
    raise RuntimeError("OpenAI response did not contain output text.")


def classify_with_openai(row, api_key, model, session=None):
    """Return one strict JSON classification from the Responses API; never sends a video file."""
    schema = {
        "type": "object", "additionalProperties": False,
        "properties": {
            "llm_result": {"type": "string", "enum": ["ADVERTISEMENT", "NON_ADVERTISEMENT", "UNCERTAIN"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "reason": {"type": "string", "minLength": 1, "maxLength": 240},
        },
        "required": ["llm_result", "confidence", "reason"],
    }
    instructions = (
        "You classify Korean YouTube metadata for a health-functional-food advertisement dataset. "
        "Use only the supplied title, description, channel, and search context. "
        "ADVERTISEMENT means the video primarily promotes a specific product, brand, seller, sponsored campaign, "
        "or purchase; product claims, price, discount, link, or call to buy are strong evidence. "
        "NON_ADVERTISEMENT means news, education, review, personal experience, general health information, or public service content. "
        "Use UNCERTAIN when metadata alone cannot support either result. Do not call something an ad merely because it discusses supplements. "
        "Write a brief Korean reason."
    )
    payload = {
        "model": model, "instructions": instructions,
        "input": json.dumps(llm_prompt(row), ensure_ascii=False),
        "store": False, "max_output_tokens": 180,
        "text": {"format": {"type": "json_schema", "name": "youtube_ad_classification", "strict": True, "schema": schema}},
    }
    session = session or requests.Session()
    try:
        response = session.post(OPENAI_RESPONSES_URL, headers={"Authorization": f"Bearer {api_key}"}, json=payload,
                                timeout=(15, 90))
    except requests.RequestException:
        raise RuntimeError("OpenAI API network failure during YouTube classification.") from None
    if response.status_code != 200:
        try:
            message = response.json().get("error", {}).get("message", "Unknown API error")
        except ValueError:
            message = "Unknown API error"
        raise RuntimeError(f"OpenAI classification failed (HTTP {response.status_code}): {message}")
    try:
        classification = json.loads(output_text(response.json()))
    except (ValueError, TypeError):
        raise RuntimeError("OpenAI classification returned invalid JSON.") from None
    result = classification.get("llm_result")
    confidence = classification.get("confidence")
    reason = classification.get("reason")
    if result not in {"ADVERTISEMENT", "NON_ADVERTISEMENT", "UNCERTAIN"}:
        raise RuntimeError("OpenAI classification returned an invalid label.")
    if not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise RuntimeError("OpenAI classification returned an invalid confidence.")
    if not isinstance(reason, str) or not reason.strip():
        raise RuntimeError("OpenAI classification returned an empty reason.")
    return {"llm_result": result, "confidence": f"{float(confidence):.2f}", "reason": reason.strip()[:240]}


def load_previous(path):
    if not Path(path).exists():
        return {}
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
        return {row["video_id"]: row for row in csv.DictReader(stream) if row.get("video_id")}


def classify_candidates(input_path=CANDIDATES_PATH, rule_output_path=RULE_OUTPUT_PATH,
                        classifications_path=CLASSIFICATIONS_PATH, confirmed_urls_path=CONFIRMED_URLS_PATH,
                        model="gpt-5-mini", minimum_confidence=0.85, limit=None, rules_only=False,
                        api_key=None, sleep_seconds=0.1):
    if not 0 <= minimum_confidence <= 1:
        raise ValueError("minimum-confidence must be between 0 and 1.")
    candidates = load_csv(input_path)
    filtered = rule_rows(candidates)
    atomic_csv(rule_output_path, RULE_FIELDS, filtered)
    if rules_only:
        return {"candidate_count": len(candidates), "rule_pass_count": sum(row["rule_result"] == "PASS" for row in filtered),
                "classified_count": 0, "confirmed_count": 0}

    rules_by_id = {row["video_id"]: row for row in filtered}
    previous = load_previous(classifications_path)
    api_key = api_key or require_openai_key()
    session = requests.Session()
    output = []
    newly_classified = 0
    try:
        for candidate in candidates:
            rule = rules_by_id[candidate["video_id"]]
            fingerprint = input_fingerprint(candidate)
            base = {key: rule[key] for key in ("video_id", "title", "source_url", "channel_title", "search_keywords", "rule_result")}
            prior = previous.get(candidate["video_id"])
            if rule["rule_result"] == "REJECT":
                classified = {"llm_result": "NOT_SENT_TO_LLM", "confidence": "", "reason": rule["rule_reason"],
                              "model": "", "classified_at": "", "input_hash": fingerprint}
            elif prior and prior.get("input_hash") == fingerprint and prior.get("model") == model:
                classified = {key: prior.get(key, "") for key in ("llm_result", "confidence", "reason", "model", "classified_at", "input_hash")}
            elif limit is not None and newly_classified >= limit:
                classified = {"llm_result": "NOT_CLASSIFIED", "confidence": "", "reason": "실행 제한으로 미분류",
                              "model": model, "classified_at": "", "input_hash": fingerprint}
            else:
                classified = classify_with_openai(candidate, api_key, model, session)
                classified.update({"model": model, "classified_at": utc_now(), "input_hash": fingerprint})
                newly_classified += 1
                time.sleep(sleep_seconds)
            output.append({**base, **classified})
    finally:
        session.close()
    atomic_csv(classifications_path, CLASSIFICATION_FIELDS, output)
    confirmed = [
        {"source_url": row["source_url"], "platform": "youtube", "video_id": row["video_id"]}
        for row in output
        if row["llm_result"] == "ADVERTISEMENT" and float(row["confidence"]) >= minimum_confidence
    ]
    atomic_csv(confirmed_urls_path, CONFIRMED_URL_FIELDS, confirmed)
    return {"candidate_count": len(candidates), "rule_pass_count": sum(row["rule_result"] == "PASS" for row in filtered),
            "classified_count": sum(row["llm_result"] in {"ADVERTISEMENT", "NON_ADVERTISEMENT", "UNCERTAIN"} for row in output),
            "confirmed_count": len(confirmed), "newly_classified_count": newly_classified}
