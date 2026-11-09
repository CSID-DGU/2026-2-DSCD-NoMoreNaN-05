"""
새 Claim 파일(claims.json, DB 없음)에 예전 claims_with_db.json의 제품 DB를 붙인다.

같은 영상 안에서 제품 이름으로 짝을 찾는다 (새 추출은 product_ref·제품명이 예전과 다를 수 있음).
  exact          공백·기호 뺀 이름이 같음
  contains       한쪽 이름이 다른 쪽에 들어 있음 ("듀오락" ⊂ "듀오락 골드")
  similar        글자 유사도 0.6 이상
  single_product 양쪽 모두 제품이 1개뿐 (이름이 달라도 같은 제품으로 봄)
  ambiguous      후보가 둘 이상 비슷하게 맞음 ("락토핏" → 베베? 골드?) → DB 안 붙임
  not_found      맞는 후보 없음 → DB 안 붙임
붙인 결과는 product["db_join"]에 남긴다.

claim_type은 목록(["EFFECT", "QUANTITY"])이어도, 문자열이어도 된다 → claim_types()로 읽기
"""
import difflib
import json
import re

SIM = 0.6       # 이름 유사도 기준
TIE = 0.05      # 1·2등 차이가 이보다 작으면 애매


def load(path):
    with open(path, "rb") as f:
        return json.loads(f.read().decode("utf-8-sig"))


def claim_types(c):
    t = c.get("claim_type")
    return t if isinstance(t, list) else [t]


def _norm(s):
    return re.sub(r"[\s\W_]+", "", (s or "").lower())


def _score(name, old):
    n = _norm(name)
    names = [_norm(x) for x in (old.get("product_name"), (old.get("match") or {}).get("matched_name")) if x]
    if not n or not names:
        return 0.0
    if n in names:
        return 1.0
    if any(len(n) >= 2 and len(x) >= 2 and (n in x or x in n) for x in names):
        return 0.95
    return max(difflib.SequenceMatcher(None, n, x).ratio() for x in names)


def match_product(p, olds, n_new=1):
    """새 제품 p에 맞는 예전 제품을 찾는다. 반환: (예전 제품 또는 None, 방법, 점수)"""
    if not olds:
        return None, "not_found", 0.0
    sc = sorted(((_score(p.get("product_name"), q), q) for q in olds), key=lambda x: -x[0])
    best, q = sc[0]
    second = sc[1][0] if len(sc) > 1 else 0.0
    if len(olds) == 1 and n_new == 1 and best < SIM:
        return q, "single_product", best
    if best < SIM:
        return None, "not_found", best
    if best < 1.0 and second > best - TIE:
        return None, "ambiguous", best
    return q, ("exact" if best == 1.0 else "contains" if best == 0.95 else "similar"), best


def attach_db(videos, db_videos):
    """videos(새 claims.json)의 제품마다 db_videos(claims_with_db.json)에서 match·DB를 찾아 붙인다"""
    by_vid = {v["video_id"]: v for v in db_videos}
    for v in videos:
        olds = (by_vid.get(v["video_id"]) or {}).get("products", [])
        for p in v.get("products", []):
            q, how, s = match_product(p, olds, len(v.get("products", [])))
            p["db_join"] = {"method": how, "score": round(s, 2),
                            "from_ref": q and q.get("product_ref"), "from_name": q and q.get("product_name")}
            if q:
                for k in ("match", "preferred_product_id", "DB"):
                    if k in q:
                        p[k] = q[k]
    return videos
