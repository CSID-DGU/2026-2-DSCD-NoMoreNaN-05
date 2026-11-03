"""
EFFECT Claim 입력 파일(B_EFFECT_180건_입력.json)을 NLI로 검증하고 최종 라벨까지 붙인다.

실행:
    python run_effect.py B_EFFECT_180건_입력.json
    python run_effect.py B_EFFECT_180건_입력.json --model 모델이름      # 다른 NLI 모델
결과:
    effect_nli_results.json        Claim별 NLI 상세 결과 (모든 문장 쌍의 E·N·C 포함)
    effect_verdicts.json           Claim별 최종 라벨
    effect_verdicts_report.md      발표용 요약 표

입력 한 줄(Claim 하나)에서 쓰는 것
    text, effect, ingredients        광고 주장
    product_name                     전제·가설의 주어
    evidence.MAIN_FNCTN              제품의 인정 기능성 → 전제 (기능성)
    evidence.INTAKE_HINT1            제품의 섭취 주의사항 → 전제 (주의사항)
    evidence.RAWMTRL_STD_INFO        원료별 기준 기능성·주의사항 → 원료에 대한 주장일 때 사용
"""
import argparse
import json
import time
from collections import OrderedDict

from verify import Verifier
import summarize


def to_videos(rows):
    """Claim 단위 목록을 (영상, 제품) 단위로 묶어 verify.py 입력 형식으로 바꾼다"""
    groups = OrderedDict()
    for r in rows:
        key = (r["video_id"], r.get("product_ref"))
        if key not in groups:
            ev = r.get("evidence") or {}
            pid = r.get("manufacturing_report_number")
            groups[key] = {
                "video_id": r["video_id"],
                "product_ref": r.get("product_ref"),
                "product": {
                    "match": {"status": "confirmed"},
                    "evi_product": {"product_id": pid, "product_name": r.get("product_name")},
                    "main_functionality_sources": [{"product_id": pid, "text": ev.get("MAIN_FNCTN")}],
                    "intake_precautions_sources": [{"product_id": pid, "text": ev.get("INTAKE_HINT1")}],
                    "ingredient_sources": [
                        {"name": x.get("RAWMTRL_NM"), "functionality": x.get("PRIMARY_FNCLTY"),
                         "precaution": x.get("IFTKN_ATNT_MATR_CN")}
                        for x in (ev.get("RAWMTRL_STD_INFO") or []) if x.get("RAWMTRL_NM")],
                },
                "claims": [],
            }
        groups[key]["claims"].append({
            "claim_id": r["claim_id"], "claim_type": "EFFECT", "text": r.get("text"),
            "effect": r.get("effect"), "ingredients": r.get("ingredients") or []})
    return list(groups.values())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="B_EFFECT_180건_입력.json")
    ap.add_argument("--model", default=None)
    ap.add_argument("--hyp-source", choices=["text", "effect", "both"], default="both")
    ap.add_argument("--prefix", default="effect")
    args = ap.parse_args()

    with open(args.input, "rb") as f:
        rows = json.loads(f.read().decode("utf-8-sig"))
    videos = to_videos(rows)
    print(f"Claim {len(rows)}개 / 영상·제품 {len(videos)}개")

    v = Verifier(None, None, model_name=args.model)
    t0 = time.time()
    results = [v.verify_video(x, hyp_source=args.hyp_source) for x in videos]
    print(f"NLI 완료: {time.time() - t0:.1f}초")

    with open(f"{args.prefix}_nli_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    out = summarize.summarize(results)
    with open(f"{args.prefix}_verdicts.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(f"{args.prefix}_verdicts_report.md", "w", encoding="utf-8") as f:
        f.write(summarize.to_markdown(out))
    print("최종 라벨:", out["요약"]["최종 라벨"])
    print(f"저장: {args.prefix}_nli_results.json, {args.prefix}_verdicts.json, {args.prefix}_verdicts_report.md")
