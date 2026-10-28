"""Build compact Top-K handoffs and a human review table from measured ranks."""
import argparse
from collections import Counter
import copy
import json
from pathlib import Path


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def cell(value, limit=None):
    text = str(value or "").replace("|", " / ").replace("\n", " ").replace("\r", " ")
    return text if limit is None or len(text) <= limit else text[:limit] + "…"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data/processed/claim_evidence_pilot100")
    args = parser.parse_args()
    directory = args.output_dir
    original = json.loads((directory / "claim_evidence_ranked.json").read_text(encoding="utf-8"))
    claims = [claim for video in original["videos"] for claim in video["claims"]]
    for k in (1, 3, 5):
        handoff = copy.deepcopy(original)
        handoff["metadata"]["export_top_k"] = k
        handoff["metadata"]["default_top_k"] = k
        handoff["metadata"]["all_candidate_ranks_file"] = "claim_evidence_ranked.json"
        for video in handoff["videos"]:
            for claim in video["claims"]:
                claim["evidences"] = claim.pop("ranked_evidences")[:k]
                claim.pop("top3_evidences", None)
                claim["evidence_count"] = len(claim["evidences"])
        save(directory / f"top{k}_handoff.json", handoff)

    measured = [claim["ranked_evidences"][0]["relevance_score"] for claim in claims if claim["ranked_evidences"]]
    summary = copy.deepcopy(original["summary"])
    summary["sampled_claim_product_status_counts"] = dict(Counter(claim["product_match_status"] for claim in claims))
    summary["total_candidate_links"] = sum(claim["candidate_count"] for claim in claims)
    summary["unique_matched_product_ids"] = len({p["db_match"]["product_id"] for video in original["videos"] for p in video["products"] if p["db_match"]["status"] == "matched"})
    summary["top1_score_distribution_exploratory"] = {
        "below_0_1": sum(score < .1 for score in measured),
        "0_1_to_below_0_5": sum(.1 <= score < .5 for score in measured),
        "0_5_to_below_0_9": sum(.5 <= score < .9 for score in measured),
        "at_least_0_9": sum(score >= .9 for score in measured),
    }
    summary["score_distribution_warning"] = "Descriptive buckets only; not calibrated cutoffs, evidence sufficiency, or truth probabilities."
    save(directory / "summary_review.json", summary)
    lines = [f"# Claim {len(claims)}개 Evidence 순위 검토", "",
             "실제 BGE-reranker-v2-m3 점수. sigmoid(logit)은 관련성 점수이며 참·거짓 확률이 아닙니다.",
             "제품명 유사도 80점과 별개입니다. 관련성 임계값 없이 정렬했으므로 낮은 관련성의 자료도 포함될 수 있습니다.",
             "원료 자료는 제품 함유를 입증하지 않습니다. 세부 항목별 충분성과 최종 판정은 아직 미평가입니다.", "",
             f"- Claim: {len(claims)}개",
             f"- 후보 있음: {summary['claims_with_candidates']}개 / 후보 없음: {summary['claims_without_candidates']}개", "",
             "| K | 전달되는 근거 연결 수 | 후보가 K개 이상인 Claim 수 |",
             "| ---: | ---: | ---: |"]
    for k, value in summary["top_k_comparison"].items():
        lines.append(f"| {k} | {value['total_links']} | {value['claims_with_k_candidates']} |")
    for video in original["videos"]:
        products = {p["product_ref"]: p for p in video["products"]}
        for claim in video["claims"]:
            product = products.get(claim.get("product_ref"))
            lines.extend(["", f"## {cell(video['video_id'])} / {cell(claim['claim_id'])}", "",
                          f"- 영상: {video.get('url') or '입력 URL 없음'}",
                          f"- 제품명: {cell(product.get('product_name') if product else '제품 참조 미확인')}",
                          f"- 제품 식별: {cell(claim['product_match_status'])}",
                          f"- Claim: **{cell(claim['text'])}**"])
            if product:
                match = product["db_match"]
                lines.append(f"- 식별 경로/사유: {cell(match['route'])} / {cell(match['reason'])}; product_id={match['product_id']}")
            if not claim["ranked_evidences"]:
                lines.extend(["", "**연결 가능한 Evidence 없음**"])
                continue
            lines.extend([f"- 전체 후보: {claim['candidate_count']}개. 아래는 상위 5개.", "",
                          "| 순위 | 관련성 점수 | 자료 구분 | 대상 | 원문 | 출처 |",
                          "| ---: | ---: | --- | --- | --- | --- |"])
            for evidence in claim["ranked_evidences"][:5]:
                lines.append("| " + " | ".join([str(evidence["rank"]), format(evidence["relevance_score"], ".6g"),
                             cell(evidence["material_scope"]), cell(evidence["target"], 80),
                             cell(evidence["text"], 220), cell(evidence["source_ref"])]) + " |")
    (directory / "review_top5.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
