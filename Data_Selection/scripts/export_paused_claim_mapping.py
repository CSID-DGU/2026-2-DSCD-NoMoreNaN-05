"""Export saved scores after a user-requested stop. Does not load/run any model."""
from collections import Counter
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sqlite3

from run_claim_evidence_pilot import MODEL, ROOT, atomic_json, pair_text


def main():
    folder = ROOT / "data/processed/claim_evidence_all"
    prepared = json.loads((folder / "prepared.json").read_text(encoding="utf-8"))
    revision = json.loads((folder / "model_revision.json").read_text(encoding="utf-8"))["revision"]
    # Opening the writable job cache lets SQLite recover a stopped transaction.
    # The original product/evidence database is not opened or modified.
    with closing(sqlite3.connect(folder / "reranker_scores.sqlite")) as connection:
        measured = dict(connection.execute("SELECT key,raw FROM scores"))
        last_keys = [row[0] for row in connection.execute("SELECT key FROM scores ORDER BY rowid DESC LIMIT 4")]
    complete_videos, partial_videos, complete_video_ids = [], [], []
    counts, last_contexts, video_stats = Counter(), [], []
    for video in prepared["videos"]:
        claims, complete_claims = [], []
        video_counts = Counter()
        for original in video["claims"]:
            candidates = original.pop("candidate_evidences")
            ranked, missing = [], 0
            for candidate in candidates:
                query, passage = pair_text(original, candidate)
                key = hashlib.sha256(json.dumps([MODEL, revision, query, passage, 512], ensure_ascii=False).encode()).hexdigest()
                if key in last_keys:
                    last_contexts.append(dict(saved_batch_key_order=last_keys.index(key), video_id=video["video_id"],
                                              url=video.get("url"), claim_id=original["claim_id"], source_ref=candidate["source_ref"]))
                if key not in measured:
                    missing += 1
                    continue
                raw = measured[key]
                value = 1 / (1 + math.exp(-raw)) if raw >= 0 else math.exp(raw) / (1 + math.exp(raw))
                candidate.update(reranker_raw_score=raw, relevance_score=value,
                                 relationship=candidate["material_scope"],
                                 score_method="BGE-reranker-v2-m3 sigmoid(logit); not a truth probability")
                ranked.append(candidate)
            ranked.sort(key=lambda row: (-row["reranker_raw_score"], row["source_ref"]))
            for rank, candidate in enumerate(ranked, 1):
                candidate["rank"] = rank
            if not candidates:
                state = "complete_no_candidates"
            elif not missing:
                state = "complete_scored"
            elif ranked:
                state = "partial"
            else:
                state = "not_started"
            record = dict(original, completion_status=state, ranking_is_final=not missing,
                          total_candidate_count=len(candidates), scored_candidate_count=len(ranked),
                          pending_candidate_count=missing, evidence_count=min(3, len(ranked)), evidences=ranked[:3],
                          retrieval_status="no_linkable_evidence" if not candidates else "candidates_ranked" if not missing else "incomplete_scoring",
                          retrieval_message="연결 가능한 Evidence 없음" if not candidates else "근거 후보 순위 완료" if not missing else "점수 계산 미완료; 현재 목록은 최종 Top-3가 아님")
            claims.append(record)
            if not missing:
                complete_claims.append(record)
            counts[state] += 1
            video_counts[state] += 1
        header = {key: value for key, value in video.items() if key != "claims"}
        partial_videos.append(dict(header, claims=claims))
        if complete_claims:
            complete_videos.append(dict(header, claims=complete_claims))
        all_complete = len(complete_claims) == len(claims)
        if all_complete:
            complete_video_ids.append(video["video_id"])
        video_stats.append(dict(video_id=video["video_id"], url=video.get("url"), claim_count=len(claims),
                                completed_claims=len(complete_claims), all_claims_complete=all_complete,
                                pending_candidate_links=sum(claim["pending_candidate_count"] for claim in claims),
                                states=dict(video_counts)))
    latest_contexts = [row for row in last_contexts if row["saved_batch_key_order"] == 0]
    total_unique = json.loads((folder / "progress.json").read_text(encoding="utf-8"))["total_unique_pairs"]
    summary = dict(status="paused_by_user", paused_at=datetime.now(timezone.utc).isoformat(),
                   input_claim_count=sum(counts.values()), input_video_count=len(partial_videos),
                   saved_unique_scores=len(measured), total_unique_pairs=total_unique,
                   score_progress_percent=round(100 * len(measured) / total_unique, 2),
                   claim_states=dict(counts), fully_processed_claims=counts["complete_scored"] + counts["complete_no_candidates"],
                   fully_processed_videos=len(complete_video_ids), fully_processed_video_ids=complete_video_ids,
                   complete_scored_claim_top3_links=sum(c["evidence_count"] for v in complete_videos for c in v["claims"]),
                   latest_saved_pair_contexts=latest_contexts,
                   ordering_note="Scored by input-pair length across videos, not a sequential URL queue. The latest saved pair can belong to multiple video URLs.",
                   video_stats=video_stats)
    metadata = dict(prepared["metadata"], status="paused_by_user", model=MODEL, revision=revision,
                    default_top_k=3, score_threshold=None, no_new_inference=True,
                    relationship_labels={"product_direct": "식별 제품의 직접 자료", "ingredient_reference": "원료 참고자료"})
    atomic_json(folder / "paused_complete_claims_top3.json", dict(metadata=metadata, summary=summary, videos=complete_videos))
    atomic_json(folder / "paused_partial_progress_top3.json", dict(metadata=metadata, summary=summary, videos=partial_videos))
    atomic_json(folder / "paused_summary.json", summary)
    for name in ("full_run_status.json", "progress.json"):
        path = folder / name
        status = json.loads(path.read_text(encoding="utf-8"))
        status.update(status="paused_by_user", paused_at=summary["paused_at"], saved_unique_scores=len(measured),
                      pause_summary="paused_summary.json", no_new_inference=True)
        atomic_json(path, status)
    printable = {key: value for key, value in summary.items() if key not in {"video_stats", "fully_processed_video_ids"}}
    print(json.dumps(printable, ensure_ascii=False))


if __name__ == "__main__":
    main()
