from config import NLI_MODEL
from files import save_json

from . import nli, overclaim, run_effect, summarize, verify


def _types(claim: dict) -> list:
    claim_type = claim.get("claim_type")
    return [claim_type] if isinstance(claim_type, str) else claim_type


def fill_missing(videos: list[dict], records: list[dict]) -> list[dict]:
    done = {(r["video_id"], r["product_ref"], r["claim_id"]) for r in records}
    out = []
    for video in videos:
        names = {p.get("product_ref"): p.get("product_name") for p in video.get("products", [])}
        for claim in video.get("claims", []):
            types = _types(claim)
            if "EFFECT" not in types:
                continue
            key = (video["video_id"], claim.get("product_ref"), claim["claim_id"])
            if key in done:
                continue
            out.append({
                "video_id": key[0], "product_ref": key[1], "claim_id": key[2],
                "claim_type": types, "text": claim.get("text"), "mechanism": "B",
                "label": "UNCLEAR", "reason_code": "PRODUCT_UNRESOLVED",
                "reason": summarize.CODE_KO["PRODUCT_UNRESOLVED"], "evidence_text": None,
                "scores": {"E": None, "C": None, "reverse_E": None, "health_claim_E": None},
                "all_findings": [{"label": "UNCLEAR", "reason_code": "PRODUCT_UNRESOLVED"}],
                "flags": {"is_question": False, "exaggeration_terms": []},
                "parts": None, "duplicate_of": None, "product_name": names.get(key[1]),
            })
    return out


def run(videos: list[dict], run_dir, model_name: str = NLI_MODEL) -> dict:
    grouped, _ = run_effect.from_claims_with_db(videos)
    scorer = nli.NLIScorer(model_name)
    verifier = verify.Verifier(scorer=scorer)
    results = [verifier.verify_video(x, hyp_source="both") for x in grouped]
    overclaim.add_reverse_scores(results, scorer)
    records = summarize.export_records(results)
    records += fill_missing(videos, records)
    doc = {"mechanism": "B", "target_claim_type": "EFFECT", "label_order": summarize.ORDER,
           "thresholds": {"tau_high": summarize.TAU_HIGH, "tau_low": summarize.TAU_LOW}, "results": records}
    save_json(run_dir / "03_nli_results.json", results)
    save_json(run_dir / "03_verdict_b.json", doc)
    return doc
