"""
TRUEAD NLI 검증 (Mechanism B) — 부품을 하나로 연결한 모듈

광고 주장 + 제품 정보를 넣으면
  전제 고르기 → 가설 만들기 → NLI → 주장별 요약 JSON
까지 한 번에 만든다. 라벨(SUPPORTED 등)은 정하지 않고, 판정 단계가 쓸 숫자와 근거만 넘긴다.

오늘 추가한 것
  ① 부품 연결: Verifier.verify_claims()
  ④ 원료 target 처리: _select_premises()
  ⑤ 동의어 가설: 원래 가설 + 공식 용어로 바꾼 가설 중 더 높은 E 사용
  ⑥ 1·2호 템플릿 검사: Verifier.check_templates()  (방향 반대: 전제 = 광고 주장, 가설 = 금지 템플릿)

실행 예시
  python verify.py                         # 2번 제품으로 데모
  python verify.py --model 다른모델이름      # large 모델 등으로 바꿔 실행
필요한 파일: nli.py, hypothesis.py, evidence_prep.py, nli_premises.sqlite
선택 파일: claim_verification.sqlite (원료 이름 → ingredient_id 찾기용)
"""
import argparse
import json
import re
import sqlite3

from evidence_prep import make_premise
from hypothesis import make_hypothesis, synonym_variant

TAU_HIGH = 0.9      # 1·2호 템플릿 '성립' 기준 (임시값, 정답 데이터로 조정)
TAU_LOW = 0.1       # 1·2호 템플릿 '불성립' 기준 (임시값)

# ⑥ v4 계획의 1·2호 템플릿 (같은 뜻 3개씩). {t} = target, {d} = 찾은 질병명
TEMPLATES = {
    "1호 가 (질병 예방)": [
        "{t}은 질병을 예방한다", "{t}을 먹으면 병에 걸리지 않는다", "{t}은 병을 막아 준다"],
    "1호 나 (질병 치료)": [
        "{t}은 질병을 치료한다", "{t}을 먹으면 병이 낫는다", "{t}은 병을 고쳐 준다"],
    "2호 다 (의약품 대체)": [
        "{t}은 약을 대신할 수 있다", "{t}을 먹으면 약을 끊어도 된다", "{t}은 약 대신 먹는 것이다"],
    "2호 라 (약효 증대)": [
        "{t}은 약의 효과를 높인다", "{t}을 약과 같이 먹으면 치료 효과가 커진다", "{t}은 약효를 강하게 만든다"],
}


def norm_name(s):
    """이름 비교용: 공백·괄호 내용·기호 제거, 소문자"""
    s = re.sub(r"[\(（][^)）]*[\)）]", "", s or "")
    return re.sub(r"[\s\-_·.,/]", "", s).lower()


def _fill(template, target):
    """템플릿의 {t}을 target으로 채우고 은/는·을/를을 받침에 맞춘다"""
    from evidence_prep import topic_particle
    s = template.replace("{t}은", target + topic_particle(target))
    obj = "을" if topic_particle(target) == "은" else "를"
    return s.replace("{t}을", target + obj).replace("{t}", target)


def _sub_disease(sentence, disease):
    """템플릿의 '질병'·'병' 자리에 질병명을 넣고 뒤의 조사(을/를, 이/가)를 받침에 맞춘다"""
    from evidence_prep import topic_particle
    has_batchim = topic_particle(disease) == "은"
    obj, subj = ("을", "이") if has_batchim else ("를", "가")
    s = re.sub(r"(?:질병|병)(을|를)", disease + obj, sentence)
    s = re.sub(r"(?:질병|병)(이|가)(?=\s)", disease + subj, s)
    return re.sub(r"(?:질병|병)", disease, s)


class Verifier:
    def __init__(self, premises_db="nli_premises.sqlite", source_db=None, scorer=None, model_name=None):
        """
        premises_db: build_premises_db.py로 만든 DB
        source_db:   claim_verification.sqlite (원료 이름 → ingredient_id 찾기). 없으면 None
        scorer:      NLIScorer (테스트할 때는 가짜를 넣을 수 있음)
        model_name:  scorer를 새로 만들 때 쓸 모델 이름 (⑤ large 모델 비교용)
        """
        self.db = sqlite3.connect(f"file:{premises_db}?mode=ro", uri=True)
        self.src = sqlite3.connect(f"file:{source_db}?mode=ro&immutable=1", uri=True) if source_db else None
        if scorer is None:
            from nli import NLIScorer, MODEL_NAME
            scorer = NLIScorer(model_name=model_name or MODEL_NAME)
        self.scorer = scorer
        self.model_name = getattr(scorer, "model_name", None) or model_name or "unknown"

    # ── 전제 가져오기 ──────────────────────────────────────────
    def _product_premises(self, product_id):
        rows = self.db.execute(
            "SELECT ref, evidence_type, ingredient_label, core FROM premise_product "
            "WHERE product_id = ? ORDER BY ref", (product_id,)).fetchall()
        return [dict(ref=r[0], evidence_type=r[1], ingredient_label=r[2], core=r[3]) for r in rows]

    def _ingredient_premises(self, ingredient_ids):
        q = ",".join("?" * len(ingredient_ids))
        rows = self.db.execute(
            f"SELECT ref, evidence_type, core FROM premise_ingredient WHERE ingredient_id IN ({q}) ORDER BY ref",
            ingredient_ids).fetchall()
        return [dict(ref=r[0], evidence_type="FUNCTIONALITY" if "FUNCTIONALITY" in r[1] else "PRECAUTION",
                     ingredient_label=None, core=r[2]) for r in rows]

    def _find_ingredient_ids(self, name):
        if self.src is None:
            return []
        rows = self.src.execute(
            "SELECT ingredient_id, ingredient_name FROM ingredients").fetchall()
        key = norm_name(name)
        return [i for i, n in rows if norm_name(n) == key]

    # ── ④ target에 맞는 전제 고르기 ────────────────────────────
    def _select_premises(self, target, target_kind, product_id):
        """
        반환: (전제 목록, basis, basis_reason)
          basis
            PRODUCT             제품 문장 전부 (target이 제품)
            PRODUCT_INGREDIENT  제품 문장 중 원료명이 target과 같은 것 + 제품 주의사항
            PRODUCT_UNLABELED   제품 문장에 원료명이 아예 없어서 제품 문장 전부 사용 (단일 원료 제품 등)
            INGREDIENT          원료 단위 문장 (evidence 테이블)
            NONE                비교할 문장 없음 → 판정 단계에서 UNDETERMINED
        """
        if not target:
            return [], "NONE", "TARGET_UNRESOLVED"

        prod = self._product_premises(product_id) if product_id is not None else []

        if target_kind == "product":
            if prod:
                return prod, "PRODUCT", "제품 문장 전부"
            return [], "NONE", "PRODUCT_NOT_FOUND"

        # target_kind == "ingredient"
        if prod:
            labels = {p["ingredient_label"] for p in prod
                      if p["evidence_type"] == "FUNCTIONALITY" and p["ingredient_label"]}
            key = norm_name(target)
            exact = {l for l in labels if norm_name(l) == key}
            part = {l for l in labels if len(key) >= 2 and (key in norm_name(l) or norm_name(l) in key)}
            matched = exact or (part if len(part) == 1 else set())   # 부분 일치가 여러 개면 애매하므로 사용 안 함
            if matched:
                chosen = [p for p in prod if p["evidence_type"] == "PRECAUTION"
                          or p["ingredient_label"] in matched]
                return chosen, "PRODUCT_INGREDIENT", f"제품 문장 중 원료명 {sorted(matched)}"
            if not labels:
                return prod, "PRODUCT_UNLABELED", "제품 문장에 원료명이 없어 전부 사용"

        ids = self._find_ingredient_ids(target)
        if ids:
            prem = self._ingredient_premises(ids)
            if prem:
                return prem, "INGREDIENT", f"원료 단위 문장 (ingredient_id {ids})"

        reason = "INGREDIENT_NOT_IN_PRODUCT" if prod else "INGREDIENT_NOT_FOUND"
        return [], "NONE", reason

    # ── ① 주장 여러 개를 한 번에 검증 ──────────────────────────
    def verify_claims(self, claims, product_id=None, use_synonyms=True):
        """
        claims: [{"claim_id", "text"(원문 조각), "target", "target_kind": "product"|"ingredient"}, ...]
        product_id: 제품 식별 결과 (못 찾았으면 None)
        반환: 주장별 요약 목록
        """
        plans, all_pairs = [], []
        for c in claims:
            target = c.get("target")
            prem, basis, reason = self._select_premises(target, c.get("target_kind", "product"), product_id)
            h = make_hypothesis(c["text"], target) if target else {"hypothesis": c["text"], "is_question": False}
            hyps = [h["hypothesis"]]
            variant = synonym_variant(h["hypothesis"]) if use_synonyms else None
            if variant:
                hyps.append(variant)
            pairs = []
            for p in prem:
                premise = p["core"] if p["evidence_type"] == "PRECAUTION" else make_premise(target, p["core"])
                for k, hyp in enumerate(hyps):
                    pairs.append(dict(ref=p["ref"], evidence_type=p["evidence_type"], premise=premise,
                                      hypothesis=hyp, variant=k == 1))
            plans.append((c, basis, reason, h, variant, pairs))
            all_pairs.extend(pairs)

        # NLI는 모든 주장의 쌍을 모아서 한 번에 (중복은 nli.py가 제거)
        scores = self.scorer.score([(x["premise"], x["hypothesis"]) for x in all_pairs]) if all_pairs else []
        for x, s in zip(all_pairs, scores):
            x.update(s)

        return [self._summarize(*plan) for plan in plans]

    @staticmethod
    def _summarize(claim, basis, reason, h, variant, pairs):
        func = [x for x in pairs if x["evidence_type"] == "FUNCTIONALITY"]
        prec = [x for x in pairs if x["evidence_type"] == "PRECAUTION"]
        best_f = max(func, key=lambda x: x["E"]) if func else None
        best_p = max(prec, key=lambda x: x["C"]) if prec else None
        return {
            "claim_id": claim["claim_id"],
            "span": claim["text"],
            "target": claim.get("target"),
            "target_kind": claim.get("target_kind"),
            "hypothesis": h["hypothesis"],
            "hypothesis_variant": variant,                        # ⑤ 동의어를 바꾼 가설 (없으면 null)
            "is_question": h.get("is_question", False),
            "basis": basis,
            "basis_reason": reason,
            "candidate_count": len({x["ref"] for x in pairs}),
            "max_entail_function": round(best_f["E"], 4) if best_f else None,
            "best_function_ref": best_f["ref"] if best_f else None,
            "best_function_text": best_f["premise"] if best_f else None,
            "best_function_from_variant": best_f["variant"] if best_f else None,
            "max_contra_precaution": round(best_p["C"], 4) if best_p else None,
            "best_precaution_ref": best_p["ref"] if best_p else None,
            "best_precaution_text": best_p["premise"] if best_p else None,
            "checks": [{k: x[k] for k in ("ref", "evidence_type", "premise", "hypothesis", "variant", "E", "N", "C")}
                       for x in pairs],
        }

    # ── ⑥ 1·2호 템플릿 검사 (방향 반대) ─────────────────────────
    def check_templates(self, claim_text, target, disease=None, tau_high=TAU_HIGH, tau_low=TAU_LOW):
        """
        전제 = 광고 주장(주어를 target으로 맞춘 문장), 가설 = 금지 템플릿
        v4 공통 판정 틀: 템플릿 3개 모두 E ≥ τ_high면 HOLDS(성립), 모두 E < τ_low면 NOT_HOLD,
        그 외는 UNCLEAR. 질문형이면 성립이어도 UNCLEAR로 낮춘다 (1차 실험의 질문형 오판 대응).
        disease를 주면 '질병·병' 자리에 질병명을 넣은 구체 템플릿도 함께 본다.
        """
        h = make_hypothesis(claim_text, target)
        premise = h["hypothesis"]
        sets = {}
        for name, temps in TEMPLATES.items():
            sets[name] = [_fill(t, target) for t in temps]
            if disease and name.startswith("1호"):
                sets[name + " · 구체"] = [_sub_disease(_fill(t, target), disease) for t in temps]
        flat = [(premise, hyp) for hyps in sets.values() for hyp in hyps]
        scores = iter(self.scorer.score(flat))
        out = {}
        for name, hyps in sets.items():
            es = [next(scores)["E"] for _ in hyps]
            if all(e >= tau_high for e in es):
                status = "UNCLEAR" if h["is_question"] else "HOLDS"
            elif all(e < tau_low for e in es):
                status = "NOT_HOLD"
            else:
                status = "UNCLEAR"
            out[name] = {"status": status, "E": [round(e, 4) for e in es], "templates": hyps}
        return {"premise": premise, "is_question": h["is_question"], "results": out}

    # ── 결과 저장 (③과 연결, nli_result 테이블) ─────────────────
    def save(self, summaries, out_db="nli_premises.sqlite"):
        con = sqlite3.connect(out_db)
        with con:
            for s in summaries:
                for c in s["checks"]:
                    con.execute(
                        "INSERT INTO nli_result (claim_id, premise_ref, evidence_type, target, premise, hypothesis,"
                        " p_entail, p_neutral, p_contra, model) VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (s["claim_id"], c["ref"], c["evidence_type"], s["target"], c["premise"], c["hypothesis"],
                         c["E"], c["N"], c["C"], self.model_name))
        con.close()


DEMO_CLAIMS = [
    {"claim_id": "demo-1", "text": "이 제품은 면역력을 높여 줍니다", "target": "고려홍삼정", "target_kind": "product"},
    {"claim_id": "demo-2", "text": "암까지 예방해 줍니다", "target": "고려홍삼정", "target_kind": "product"},
    {"claim_id": "demo-3", "text": "당뇨약 드시는 분도 걱정 없이 드세요", "target": "고려홍삼정", "target_kind": "product"},
    {"claim_id": "demo-4", "text": "피로가 싹 풀려요", "target": "홍삼", "target_kind": "ingredient"},
    {"claim_id": "demo-5", "text": "혈액순환을 원활하게 해주고", "target": "고려홍삼정", "target_kind": "product"},
]

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--premises-db", default="nli_premises.sqlite")
    ap.add_argument("--source-db", default=None, help="claim_verification.sqlite 경로 (원료 찾기용, 선택)")
    ap.add_argument("--product-id", type=int, default=2)
    ap.add_argument("--model", default=None, help="NLI 모델 이름 (예: large 모델 비교)")
    ap.add_argument("--save", action="store_true", help="결과를 nli_result 테이블에 저장")
    args = ap.parse_args()

    v = Verifier(args.premises_db, args.source_db, model_name=args.model)
    summaries = v.verify_claims(DEMO_CLAIMS, product_id=args.product_id)
    for s in summaries:
        brief = {k: s[k] for k in s if k != "checks"}
        print(json.dumps(brief, ensure_ascii=False, indent=2))

    print("\n[1·2호 템플릿 검사]")
    for text, target, disease in [("알파아이는 당뇨를 치료합니다", "알파아이", "당뇨"),
                                  ("알파아이가 당뇨를 치료할까요?", "알파아이", "당뇨"),
                                  ("혈압약 대신 알파아이만 드세요", "알파아이", None)]:
        r = v.check_templates(text, target, disease)
        print(f"- {text}  (질문: {r['is_question']})")
        for name, res in r["results"].items():
            print(f"    {name:<18} {res['status']:<9} E={res['E']}")

    if args.save:
        v.save(summaries, args.premises_db)
        print("\nnli_result 테이블에 저장했어요.")
