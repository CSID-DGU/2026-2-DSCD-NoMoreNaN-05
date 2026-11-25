def from_claims_with_db(videos):
    """claims_with_db.json(영상 → 제품·Claim) 형식에서 DB가 있는 제품의 EFFECT Claim만 골라 변환"""
    out, n = [], 0
    for v in videos:
        for p in v.get("products", []):
            db = p.get("DB")
            if not isinstance(db, dict):
                continue
            def is_effect(ct):
                return "EFFECT" in ct if isinstance(ct, list) else ct == "EFFECT"
            claims = [c for c in v.get("claims", [])
                      if c.get("product_ref") == p.get("product_ref") and is_effect(c.get("claim_type"))]
            if not claims:
                continue
            ev = db.get("EFFECT") or {}
            pid = p.get("preferred_product_id") or p.get("manufacturing_report_number")
            name = (p.get("match") or {}).get("matched_name") or p.get("product_name")
            out.append({
                "video_id": v.get("video_id"), "product_ref": p.get("product_ref"), "url": v.get("url"),
                "product": {
                    "match": {"status": "confirmed"},
                    "evi_product": {"product_id": pid, "product_name": name},
                    "main_functionality_sources": [{"product_id": pid, "text": ev.get("MAIN_FNCTN")}],
                    "intake_precautions_sources": [{"product_id": pid, "text": ev.get("INTAKE_HINT1")}],
                    "ingredient_sources": [
                        {"name": x.get("RAWMTRL_NM"), "functionality": x.get("PRIMARY_FNCLTY"),
                         "precaution": x.get("IFTKN_ATNT_MATR_CN")}
                        for x in (ev.get("RAWMTRL_STD_INFO") or []) if x.get("RAWMTRL_NM")],
                },
                "claims": [{"claim_id": c["claim_id"], "claim_type": "EFFECT", "claim_types": c.get("claim_type"),
                            "text": c.get("text"),
                            "effect": c.get("effect"), "ingredients": c.get("ingredients") or []} for c in claims],
            })
            n += len(claims)
    return out, n
