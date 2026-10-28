"""Prepare, score and resume a PDF-based Claim/Evidence pilot without DB writes."""
import argparse
from collections import Counter
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.claim_evidence_experiment import prepare

MODEL = "BAAI/bge-reranker-v2-m3"


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def pair_text(claim, candidate):
    context = claim["query_context"]
    query = "Claim: " + claim["text"]
    if context.get("effect"):
        query += "\nClaim effect: " + str(context["effect"])
    if context.get("ingredients"):
        query += "\nClaim ingredients: " + ", ".join(map(str, context["ingredients"]))
    if context.get("product_name"):
        query += "\nAdvertised product: " + context["product_name"]
    passage = "Target: " + candidate["target"] + "\nEvidence type: " + candidate["evidence_type"] + "\nEvidence: " + candidate["text"]
    return query, passage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--claim-limit", type=int, default=100)
    parser.add_argument("--video-limit", type=int)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/processed/claim_evidence_pilot100")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--reuse-cache", type=Path, help="Import measured scores from an existing SQLite cache")
    parser.add_argument("--revision", help="Pin an already downloaded model revision")
    parser.add_argument("--offline-model", action="store_true", help="Use local model files without network access")
    args = parser.parse_args()
    if min(args.claim_limit, args.batch_size, args.threads) <= 0 or (args.video_limit is not None and args.video_limit <= 0):
        parser.error("Limits must be positive.")
    directory = args.output_dir
    directory.mkdir(parents=True, exist_ok=True)
    prepared_path = directory / "prepared.json"
    signature = dict(input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
                     claim_limit=args.claim_limit, video_limit=args.video_limit, seed=args.seed,
                     pipeline_version=2)
    if prepared_path.exists():
        prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
        if prepared.get("run_signature") != signature:
            raise RuntimeError("Prepared input/settings differ. Use a separate --output-dir.")
    else:
        prepared = prepare(args.input, ROOT / "Data_List_Claim_Verification/claim_verification.sqlite",
                           args.claim_limit, args.seed, args.video_limit)
        prepared["run_signature"] = signature
        atomic_json(prepared_path, prepared)
    print(json.dumps(prepared["metadata"], ensure_ascii=False), flush=True)
    if args.prepare_only:
        return 0

    # Keep model assets inside the workspace. No private HF token is needed.
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    from huggingface_hub import HfApi, snapshot_download
    revision_path = directory / "model_revision.json"
    if revision_path.exists():
        model_info = json.loads(revision_path.read_text(encoding="utf-8"))
        if args.revision and args.revision != model_info["revision"]:
            raise RuntimeError("Requested model revision differs from the existing run.")
    elif args.revision:
        model_info = dict(model=MODEL, revision=args.revision)
        atomic_json(revision_path, model_info)
    else:
        if args.offline_model:
            raise RuntimeError("Offline mode requires --revision or an existing model_revision.json.")
        info = HfApi(token=False).model_info(MODEL)
        model_info = dict(model=MODEL, revision=info.sha)
        atomic_json(revision_path, model_info)
    model_path = snapshot_download(MODEL, revision=model_info["revision"],
                                   cache_dir=str(ROOT / ".tools/huggingface"), token=False,
                                   local_files_only=args.offline_model,
                                   allow_patterns=["config.json", "model.safetensors", "tokenizer.json",
                                                   "tokenizer_config.json", "special_tokens_map.json",
                                                   "sentencepiece.bpe.model"], max_workers=2)
    print("Model download/cache ready.", flush=True)
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    torch.set_num_threads(args.threads)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
    model.to(device).eval()

    scores = sqlite3.connect(directory / "reranker_scores.sqlite")
    scores.execute("CREATE TABLE IF NOT EXISTS scores (key TEXT PRIMARY KEY, raw REAL NOT NULL)")
    if args.reuse_cache:
        from contextlib import closing
        if args.reuse_cache.resolve() == (directory / "reranker_scores.sqlite").resolve():
            raise RuntimeError("Reuse cache must differ from this run's cache.")
        with closing(sqlite3.connect(args.reuse_cache.resolve().as_uri() + "?mode=ro", uri=True)) as previous:
            cursor = previous.execute("SELECT key,raw FROM scores")
            with scores:
                while rows := cursor.fetchmany(1000):
                    scores.executemany("INSERT OR IGNORE INTO scores VALUES (?,?)", rows)
    pair_lookup = {}
    for video in prepared["videos"]:
        for claim in video["claims"]:
            for candidate in claim["candidate_evidences"]:
                query, passage = pair_text(claim, candidate)
                key = hashlib.sha256(json.dumps([MODEL, model_info["revision"], query, passage, 512], ensure_ascii=False).encode()).hexdigest()
                candidate["score_cache_key"] = key
                pair_lookup[key] = (query, passage)
    remaining = [(key, pair) for key, pair in pair_lookup.items()
                 if scores.execute("SELECT 1 FROM scores WHERE key=?", (key,)).fetchone() is None]
    remaining.sort(key=lambda item: sum(map(len, item[1])))
    started = time.time()
    print(f"Scoring {len(remaining)} uncached pairs on {device}; {len(pair_lookup)} unique pairs total.", flush=True)
    for start in range(0, len(remaining), args.batch_size):
        batch = remaining[start:start + args.batch_size]
        encoded = tokenizer([list(pair) for _, pair in batch], padding=True, truncation=True,
                            max_length=512, return_tensors="pt").to(device)
        with torch.inference_mode():
            raw = model(**encoded, return_dict=True).logits.view(-1).float().cpu().tolist()
        with scores:
            scores.executemany("INSERT OR REPLACE INTO scores VALUES (?,?)", [(item[0], value) for item, value in zip(batch, raw)])
        done = min(start + len(batch), len(remaining))
        atomic_json(directory / "progress.json", dict(status="scoring", completed_pairs=done,
                    pending_pairs=len(remaining) - done, elapsed_seconds=round(time.time() - started, 2),
                    total_unique_pairs=len(pair_lookup), cached_pairs_at_start=len(pair_lookup) - len(remaining),
                    total_scored_pairs=len(pair_lookup) - len(remaining) + done,
                    model=MODEL, revision=model_info["revision"]))
        if start == 0 or done % 20 < args.batch_size or done == len(remaining):
            print(f"Scored {done}/{len(remaining)} pairs; {time.time() - started:.1f}s", flush=True)

    # Large full-dataset exports should not overlap with the model's weight memory.
    del model, tokenizer
    import gc
    gc.collect()
    output = copy.deepcopy(prepared)
    all_claims = []
    for video in output["videos"]:
        for claim in video["claims"]:
            ranked = claim.pop("candidate_evidences")
            for candidate in ranked:
                key = candidate.pop("score_cache_key")
                raw = scores.execute("SELECT raw FROM scores WHERE key=?", (key,)).fetchone()[0]
                sigmoid = 1 / (1 + math.exp(-raw)) if raw >= 0 else math.exp(raw) / (1 + math.exp(raw))
                candidate.update(reranker_raw_score=raw, relevance_score=sigmoid,
                                 relationship=candidate["material_scope"],
                                 score_method="BGE-reranker-v2-m3 sigmoid(logit); not a truth probability")
            ranked.sort(key=lambda candidate: (-candidate["reranker_raw_score"], candidate["source_ref"]))
            for rank, candidate in enumerate(ranked, 1):
                candidate["rank"] = rank
            claim.update(ranked_evidences=ranked, candidate_count=len(ranked),
                         top3_evidences=ranked[:3], retrieval_status="candidates_ranked" if ranked else "no_linkable_evidence",
                         retrieval_message="관련 근거 후보 있음; 충분성 미판정" if ranked else "연결 가능한 Evidence 없음",
                         coverage_assessment="not_evaluated; retrieval scores do not establish coverage of every subclaim")
            all_claims.append(claim)
    output["metadata"].update(model=MODEL, revision=model_info["revision"],
                               ranking="direct reranking of all scoped candidates as allowed by PDF for small candidate sets",
                               embedding_stage="not_needed_for_this_scoped_pilot", score_threshold=None,
                               default_top_k=3, max_token_length=512, device=device,
                               relationship_labels={"product_direct": "식별된 DB 제품의 직접 자료",
                                                    "ingredient_reference": "원료 참고자료; 제품 함유 확인 아님"},
                               evaluation_warning="No human relevance labels: cannot infer optimal K or precision from scores alone.")
    matched = [p for video in output["videos"] for p in video["products"] if p["db_match"]["status"] == "matched"]
    summary = dict(claim_count=len(all_claims), video_count=len(output["videos"]),
                   claims_with_candidates=sum(bool(c["candidate_count"]) for c in all_claims),
                   claims_without_candidates=sum(not c["candidate_count"] for c in all_claims),
                   candidate_count_distribution=dict(sorted(Counter(c["candidate_count"] for c in all_claims).items())),
                   matched_video_product_entries=len(matched),
                   identity_reason_counts=dict(Counter(p["db_match"]["reason"] for video in output["videos"] for p in video["products"])),
                   top_k_comparison={str(k): dict(total_links=sum(min(k, c["candidate_count"]) for c in all_claims),
                                                 claims_with_k_candidates=sum(c["candidate_count"] >= k for c in all_claims)) for k in (1, 3, 5, 10)},
                   caution="Candidate counts are not evidence sufficiency or ground-truth relevance judgments.")
    output["summary"] = summary
    atomic_json(directory / "claim_evidence_ranked.json", output)
    atomic_json(directory / "summary.json", summary)
    atomic_json(directory / "progress.json", dict(status="complete", summary=summary))
    scores.close()
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
