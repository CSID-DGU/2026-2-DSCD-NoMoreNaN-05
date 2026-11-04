"""
TRUEAD NLI 검증 (Mechanism B)

입력: 제품 식별·Claim 매핑 결과 (mapped_products.json, 영상 단위 목록)
출력: 영상별·Claim별 NLI 결과 (판정 단계로 넘김)

처리 흐름 (영상 하나)
  1. 제품 확인: product.match.status가 confirmed일 때만 제품 기능성을 근거로 사용
  2. 근거 문장 만들기: main_functionality 원문 → 기능성 1개 = 문장 1개 (evidence_prep)
     주의사항은 nli_premises.sqlite에서 product_id로 가져옴 (DB가 없으면 생략)
  3. EFFECT Claim만 NLI로 비교 (QUANTITY·COMPOSITION·CERTIFICATION은 Mechanism A 담당)
     - ingredients가 비어 있으면 제품에 대한 주장 → 제품 문장 전부와 비교
     - 원료가 1개면 그 원료의 문장만 골라 비교
     - 원료가 여러 개면 해당 원료들의 문장만 모아 비교
  4. 가설: Claim 원문(text)과 추출된 효과 문구(effect)를 각각 문장으로 만들고, 동의어를 바꾼 문장도 추가
  5. 질병·의약품 표현 검사(법 제8조 1·2호 템플릿)와 '건강 효과 문장인가' 확인도 함께 실행
  6. 영상 하나의 모든 문장 쌍을 모아 NLI를 한 번에 실행

실행
  python verify.py mapped_products.json --premises-db nli_premises.sqlite --out nli_results.json
  옵션: --allow-unresolved (확정 안 된 제품 후보도 사용, 실험용)
        --only-confirmed (제품 확정된 영상만)   --limit 20 (영상 20개만)
        --hyp-source text|effect|both   --no-templates
        --model 모델이름            --save (nli_result 테이블에 저장)
"""
import argparse
import json
import re
import sqlite3
import time
from collections import Counter

from evidence_prep import make_premise, parse_functionality, parse_precautions, topic_particle
from hypothesis import make_hypothesis, synonym_variant

TAU_HIGH = 0.9      # 템플릿 '성립' 기준 (임시값)
TAU_LOW = 0.1       # 템플릿 '불성립' 기준 (임시값)
NLI_CLAIM_TYPES = ("EFFECT",)

# 법 제8조 1·2호 금지 표현 템플릿 (같은 뜻 3개씩). {t} = 대상 이름
TEMPLATES = {
    "1호 가 (질병 예방)": [
        "{t}은 질병을 예방한다", "{t}을 먹으면 질병이 예방된다", "{t}은 병을 막아 준다"],
    "1호 나 (질병 치료)": [
        "{t}은 질병을 치료한다", "{t}을 먹으면 병이 낫는다", "{t}은 병을 고쳐 준다"],
    "2호 다 (의약품 대체)": [
        "{t}은 약을 대신할 수 있다", "{t}을 먹으면 약을 끊어도 된다", "{t}은 약 대신 먹는 것이다"],
    "2호 라 (약효 증대)": [
        "{t}은 약의 효과를 높인다", "{t}을 약과 같이 먹으면 치료 효과가 커진다", "{t}은 약효를 강하게 만든다"],
}


# 건강 효과를 말하는 문장인지 확인 (v4의 범위 확인). 전제 = 광고 문장, 가설 = 아래 문장
SCOPE_TEMPLATES = ["{t}은 건강에 도움을 준다", "{t}은 몸에 좋은 효과가 있다"]
SCOPE_TAU = 0.1     # 둘 중 하나라도 E ≥ 0.1이면 건강 효과 문장으로 봄 (임시값, 진짜 효능 주장을 빼지 않으려고 낮게 둠)
# 효과를 나타내는 말이 있으면 NLI 결과와 상관없이 건강 효과 문장으로 봄 (광고 원문 기준)
EFFECT_WORDS = re.compile(
    # 효과를 나타내는 말
    r"(개선|감소|증가|증진|도움|튼튼|건강|활력|회복|예방|치료|완화|억제|보호|강화|케어|효과|효능|유지|늦추|채우|"
    r"좋아|편안|키우|키워|크게|자라|"
    # 몸의 부위·기능 (광고가 효과를 말할 때 거의 항상 함께 나옴)
    r"키\s*성장|키가|키를|숨겨진\s*키|성장판|성장기|노화|눈|시력|황반|침침|흐릿|건조|피부|보습|관절|연골|무릎|뼈|치아|"
    r"장\s*건강|위\s*불편|소화|배변|변비|배뇨|소변|뇨|화장실|수면|숙면|잠을|혈행|혈액|혈당|혈압|콜레스테롤|중성지질|"
    r"간\s*건강|피로|면역|기억력|인지|스트레스|긴장|체지방|다이어트|갱년기|전립선|모발|탈모|구강|잇몸|통증|붓기|저림|"
    # 추가: 실제 광고 1,326건에서 빠졌던 표현
    r"키\s*(크|더|가\s*크)|세포|대사|에너지\s*(생성|대사)|호르몬|갑상선|콧물|재채기|코\s*가려|비염|깬다|깨는|불면|피곤|"
    r"장\s*(건강|속|까지|에|을|이|관리|부착)|예민한\s*장|체지방|body\s*fat|촉촉|탱탱|모이스처|근력|지구력|체력|담즙|"
    r"위\s*(건강|불편|!)|간\s*!|이뮨|immune|항산화|antioxid)", re.IGNORECASE)
# 과장 표현 (v4 계획의 닫힌 목록 + 광고에 자주 나오는 표현). 위반 확정이 아니라 '과장 주의' 표시용
EXAGGERATION = re.compile(r"(깨끗이|완전히|100\s*%|싹|즉시|즉각|무조건|확실히|탁월|하나도\s*남김없이|단번에|"
                          r"\d+\s*배|(\d+|한|두|세)\s*(일|주|개월|달)\s*(만에|이면|면|안에|차))")
# 광고 속 면책 문구 (주장이 아니라 고지 문장)
DISCLAIMER = re.compile(r"(연출|주관적|개인\s*차|이해를\s*돕|제품\s*정보를\s*확인|섭취\s*시\s*주의사항|이상사례\s*발생\s*시|과량\s*섭취\s*시|모든\s*사람\S*\s*동일|동일하게\s*(적용|작용)\S*\s*(않|아니)|"
                        r"의약품이\s*아닙니다|개인에\s*따라\s*(차이|다를|다릅))")


def norm_name(s):
    """이름 비교용: 괄호 내용·공백·기호 제거, 소문자"""
    s = re.sub(r"[\(（][^)）]*[\)）]", "", s or "")
    return re.sub(r"[\s\-_·.,/]", "", s).lower()


def _fill(template, target):
    """템플릿의 {t}을 대상 이름으로 채우고 조사(은/는, 을/를)를 받침에 맞춤"""
    tp = topic_particle(target)
    obj = "을" if tp == "은" else "를"
    return template.replace("{t}은", target + tp).replace("{t}을", target + obj).replace("{t}", target)


def _sub_disease(sentence, disease):
    """템플릿의 '질병'·'병' 자리에 질병명을 넣고 뒤의 조사를 받침에 맞춤"""
    has_batchim = topic_particle(disease) == "은"
    obj, subj = ("을", "이") if has_batchim else ("를", "가")
    s = re.sub(r"(?:질병|병)(을|를)", disease + obj, sentence)
    s = re.sub(r"(?:질병|병)(이|가)(?=\s)", disease + subj, s)
    return re.sub(r"(?:질병|병)", disease, s)


def load_mapped(path):
    with open(path, "rb") as f:
        return json.loads(f.read().decode("utf-8-sig"))


class Verifier:
    def __init__(self, premises_db=None, source_db=None, scorer=None, model_name=None):
        """
        premises_db: nli_premises.sqlite (주의사항, 원료 단위 문장). 없으면 None → 기능성만 비교
        source_db:   claim_verification.sqlite (원료 이름 → ingredient_id). 없으면 None
        scorer:      NLIScorer (테스트 때는 가짜 채점기를 넣을 수 있음)
        """
        self.db = sqlite3.connect(f"file:{premises_db}?mode=ro", uri=True) if premises_db else None
        self.src = sqlite3.connect(f"file:{source_db}?mode=ro&immutable=1", uri=True) if source_db else None
        if scorer is None:
            from nli import NLIScorer, MODEL_NAME
            scorer = NLIScorer(model_name=model_name or MODEL_NAME)
        self.scorer = scorer
        self.model_name = getattr(scorer, "model_name", None) or model_name or "unknown"

    # ── 근거 문장 ───────────────────────────────────────────
    def _precautions(self, product_ids):
        if self.db is None or not product_ids:
            return []
        q = ",".join("?" * len(product_ids))
        rows = self.db.execute(
            f"SELECT ref, core FROM premise_product WHERE evidence_type = 'PRECAUTION' "
            f"AND product_id IN ({q}) ORDER BY ref", list(product_ids)).fetchall()
        seen, out = set(), []
        for ref, core in rows:
            if core not in seen:
                seen.add(core)
                out.append(dict(ref=ref, evidence_type="PRECAUTION", ingredient_label=None, core=core))
        return out

    def _ingredient_premises(self, name):
        """제품 근거가 없을 때, 원료 이름으로 원료 단위 문장(evidence 테이블)을 찾음"""
        if self.db is None or self.src is None:
            return []
        key = norm_name(name)
        ids = [i for i, n in self.src.execute("SELECT ingredient_id, ingredient_name FROM ingredients")
               if norm_name(n) == key]
        if not ids:
            return []
        q = ",".join("?" * len(ids))
        rows = self.db.execute(
            f"SELECT ref, evidence_type, core FROM premise_ingredient WHERE ingredient_id IN ({q})", ids).fetchall()
        return [dict(ref=r, evidence_type="FUNCTIONALITY" if "FUNCTIONALITY" in t else "PRECAUTION",
                     ingredient_label=name, core=c) for r, t, c in rows]

    def product_premises(self, video, allow_unresolved=False):
        """영상의 매핑 결과에서 제품 근거 문장을 만듦. 반환: (문장 목록, 상태, 제품명, product_id 목록)"""
        prod = video.get("product") or {}
        status = (prod.get("match") or {}).get("status", "unresolved")
        evi = prod.get("evi_product") or {}
        name = evi.get("product_name")
        if status != "confirmed" and not allow_unresolved:
            return [], status, name, []
        sources = prod.get("main_functionality_sources") or (
            [{"product_id": evi.get("product_id"), "text": evi.get("main_functionality")}] if evi else [])
        premises, seen, pids = [], set(), []
        for src in sources:
            pid = src.get("product_id")
            pids.append(pid)
            for k, r in enumerate(parse_functionality(src.get("text") or "")):
                if r["core"] in seen:
                    continue
                seen.add(r["core"])
                premises.append(dict(ref=f"product:{pid}:F{k}", evidence_type="FUNCTIONALITY",
                                     ingredient_label=r["ingredient_label"], core=r["core"]))
        prec_sources = prod.get("intake_precautions_sources")
        if prec_sources:                                   # 입력에 주의사항이 들어 있으면 그것을 사용
            seen_p = set()
            for src in prec_sources:
                pid = src.get("product_id")
                for k, r in enumerate(parse_precautions(src.get("text") or "")):
                    if r["core"] not in seen_p:
                        seen_p.add(r["core"])
                        premises.append(dict(ref=f"product:{pid}:P{k}", evidence_type="PRECAUTION",
                                             ingredient_label=None, core=r["core"]))
        else:                                              # 없으면 nli_premises.sqlite에서 가져옴
            premises += self._precautions([p for p in pids if p is not None])
        self._ing_std = prod.get("ingredient_sources") or []   # 원료별 기준 기능성 (있으면 원료 주장에 사용)
        return premises, status, name, pids

    def _ingredient_std_premises(self, ing):
        """입력에 원료별 기준 기능성(RAWMTRL_STD_INFO)이 있을 때, 원료 이름으로 찾아 문장을 만듦"""
        key = norm_name(ing)
        std = getattr(self, "_ing_std", [])
        exact = [x for x in std if norm_name(x.get("name")) == key]
        part = [x for x in std if len(key) >= 2 and (key in norm_name(x.get("name")) or norm_name(x.get("name")) in key)]
        hit = exact or (part if len({norm_name(x.get("name")) for x in part}) == 1 else [])
        out = []
        for x in hit:
            for k, r in enumerate(parse_functionality(x.get("functionality") or "")):
                out.append(dict(ref=f"ingredient:{x.get('name')}:F{k}", evidence_type="FUNCTIONALITY",
                                ingredient_label=x.get("name"), core=r["core"]))
            for k, r in enumerate(parse_precautions(x.get("precaution") or "")):
                out.append(dict(ref=f"ingredient:{x.get('name')}:P{k}", evidence_type="PRECAUTION",
                                ingredient_label=x.get("name"), core=r["core"]))
        return out

    # ── 대상에 맞는 문장 고르기 ──────────────────────────────
    def select(self, ingredients, prod_premises, product_name, product_status):
        """
        반환: (문장 목록, basis, 이유, 주어)
          PRODUCT              제품에 대한 주장 → 제품 문장 전부
          PRODUCT_INGREDIENT   원료에 대한 주장 → 그 원료(들)의 문장 + 제품 주의사항
          PRODUCT_UNLABELED    제품 문장에 원료명이 없어 전부 사용 (원료 하나인 제품으로 봄)
          INGREDIENT           제품 근거가 없어 원료 단위 문장 사용
          NONE                 비교할 문장 없음 → 판정 단계에서 판단 보류
        """
        ingredients = [i for i in (ingredients or []) if i]
        func = [p for p in prod_premises if p["evidence_type"] == "FUNCTIONALITY"]
        prec = [p for p in prod_premises if p["evidence_type"] == "PRECAUTION"]

        if not ingredients:
            if func:
                return prod_premises, "PRODUCT", "제품 문장 전부", product_name
            reason = "PRODUCT_UNRESOLVED" if product_status != "confirmed" else "NO_PRODUCT_TEXT"
            return [], "NONE", reason, product_name

        labels = {p["ingredient_label"] for p in func if p["ingredient_label"]}
        matched = set()
        for ing in ingredients:
            key = norm_name(ing)
            exact = {l for l in labels if norm_name(l) == key}
            part = {l for l in labels if len(key) >= 2 and (key in norm_name(l) or norm_name(l) in key)}
            matched |= exact or (part if len(part) == 1 else set())   # 부분 일치가 여러 개면 애매해서 안 씀

        subject = ingredients[0] if len(ingredients) == 1 else product_name
        if matched:
            chosen = [p for p in func if p["ingredient_label"] in matched] + prec
            return chosen, "PRODUCT_INGREDIENT", f"원료명 {sorted(matched)}", subject
        std_prem = []
        for ing in ingredients:
            std_prem += self._ingredient_std_premises(ing)
        if std_prem:
            return std_prem + prec, "INGREDIENT_STANDARD", "원료별 기준 기능성 (RAWMTRL_STD_INFO)", subject
        if func and not labels:
            return prod_premises, "PRODUCT_UNLABELED", "제품 문장에 원료명이 없어 전부 사용", subject
        if len(ingredients) == 1:
            ing_prem = self._ingredient_premises(ingredients[0])
            if ing_prem:
                return ing_prem, "INGREDIENT", "원료 단위 문장", ingredients[0]
        reason = "INGREDIENT_NOT_IN_PRODUCT" if func else (
            "PRODUCT_UNRESOLVED" if product_status != "confirmed" else "NO_PRODUCT_TEXT")
        return [], "NONE", reason, subject

    # ── 영상 하나 검증 ───────────────────────────────────────
    def verify_video(self, video, allow_unresolved=False, hyp_source="both",
                     use_synonyms=True, templates=True):
        prem_all, status, pname, pids = self.product_premises(video, allow_unresolved)
        claims = video.get("claims") or []
        jobs, plans = [], []

        seen, dup_of = {}, {}
        for c in claims:
            if c.get("claim_type") not in NLI_CLAIM_TYPES:
                continue
            key = (re.sub(r"\s+", "", c.get("text") or ""), tuple(c.get("ingredients") or []))
            if key in seen:                       # 같은 문장이 또 나오면 비교하지 않고 앞의 결과를 가져다 씀
                dup_of[c.get("claim_id")] = seen[key]
                continue
            seen[key] = c.get("claim_id")
            prem, basis, reason, subject = self.select(c.get("ingredients"), prem_all, pname, status)
            subj = subject or "이 제품"

            # 가설: 원문(text)과 효과 문구(effect)를 각각 문장으로, 동의어를 바꾼 문장도 추가
            sources = []
            if hyp_source in ("text", "both"):
                sources.append(("text", c.get("text")))
            if hyp_source in ("effect", "both") and c.get("effect") and c.get("effect") != c.get("text"):
                sources.append(("effect", c.get("effect")))
            sources = [(t, s) for t, s in sources if s] or [("text", c.get("text") or c.get("effect") or "")]
            hyps = []
            for tag, s in sources:
                h = make_hypothesis(s, subj)
                hyps.append(dict(source=tag, text=h["hypothesis"], is_question=h["is_question"]))
                v = synonym_variant(h["hypothesis"]) if use_synonyms else None
                if v:
                    hyps.append(dict(source=tag + "+동의어", text=v, is_question=h["is_question"]))

            pairs = []
            for p in prem:
                premise = p["core"] if p["evidence_type"] == "PRECAUTION" else make_premise(subj, p["core"])
                for h in hyps:
                    pairs.append(dict(kind="func", ref=p["ref"], evidence_type=p["evidence_type"],
                                      premise=premise, hypothesis=h["text"], hyp_source=h["source"]))

            tsets = {}
            t_premise = make_hypothesis(c.get("text") or "", subj)["hypothesis"]
            for hyp in [_fill(t, subj) for t in SCOPE_TEMPLATES]:
                pairs.append(dict(kind="scope", premise=t_premise, hypothesis=hyp))
            if templates:
                for name, temps in TEMPLATES.items():
                    tsets[name] = [_fill(t, subj) for t in temps]
                    for hyp in tsets[name]:
                        pairs.append(dict(kind="tmpl", set=name, premise=t_premise, hypothesis=hyp))

            plans.append((c, basis, reason, subj, hyps, pairs, tsets))
            jobs.extend(pairs)

        scores = self.scorer.score([(j["premise"], j["hypothesis"]) for j in jobs]) if jobs else []
        for j, s in zip(jobs, scores):
            j.update(s)

        first = {p[0].get("claim_id"): self._summarize(*p) for p in plans}
        results = []
        for c in claims:
            cid = c.get("claim_id")
            if cid in first:
                results.append(first[cid])
            elif cid in dup_of:
                results.append({**first[dup_of[cid]], "claim_id": cid, "duplicate_of": dup_of[cid]})
        skipped = Counter(c.get("claim_type") for c in claims if c.get("claim_type") not in NLI_CLAIM_TYPES)
        return {
            "video_id": video.get("video_id"),
            "product_ref": video.get("product_ref"),       # 한 영상에 제품이 여러 개면 제품별로 나뉨
            "url": video.get("url"),
            "product_status": status,
            "product_ids": pids,
            "product_name": pname,
            "product_match_note": ((video.get("product") or {}).get("match") or {}).get("note"),
            "nli_claims": results,
            "not_nli_claims": dict(skipped),     # Mechanism A 등 다른 단계 담당
        }

    @staticmethod
    def _summarize(claim, basis, reason, subject, hyps, pairs, tsets):
        func = [x for x in pairs if x["kind"] == "func" and x["evidence_type"] == "FUNCTIONALITY"]
        prec = [x for x in pairs if x["kind"] == "func" and x["evidence_type"] == "PRECAUTION"]
        best_f = max(func, key=lambda x: x["E"]) if func else None
        best_p = max(prec, key=lambda x: x["C"]) if prec else None
        is_q = any(h["is_question"] for h in hyps)

        tmpl = {}
        for name in tsets:
            es = [x["E"] for x in pairs if x["kind"] == "tmpl" and x["set"] == name]
            if all(e >= TAU_HIGH for e in es):
                st = "UNCLEAR" if is_q else "HOLDS"
            elif sum(e >= 0.5 for e in es) >= 2:
                st = "UNCLEAR"          # 3개 중 2개 이상이 같은 말 쪽이면 확인 필요
            else:
                st = "NOT_HOLD"         # 1개만 높은 건 템플릿 하나의 오탐으로 봄
            tmpl[name] = {"status": st, "E": [round(e, 4) for e in es]}

        def r(v):
            return round(v, 4) if v is not None else None

        scope_e = max([x["E"] for x in pairs if x["kind"] == "scope"], default=None)
        text = claim.get("text") or ""
        is_disclaimer = bool(DISCLAIMER.search(text))
        is_health = (not is_disclaimer) and (bool(EFFECT_WORDS.search(text))
                                             or (scope_e is not None and scope_e >= SCOPE_TAU))

        return {
            "claim_id": claim.get("claim_id"),
            "claim_type": claim.get("claim_type"),
            "text": claim.get("text"),
            "effect": claim.get("effect"),
            "ingredients": claim.get("ingredients"),
            "subject": subject,
            "hypotheses": hyps,
            "is_question": is_q,
            "health_claim_E": r(scope_e),                                  # 건강 효과 문장일 확률
            "is_health_claim": is_health,
            "is_disclaimer": is_disclaimer,
            "exaggeration_terms": sorted({m.group(0) for m in EXAGGERATION.finditer(text)}),
            "basis": basis,
            "basis_reason": reason,
            "candidate_count": len({x["ref"] for x in pairs if x["kind"] == "func"}),
            "max_entail_function": r(best_f["E"]) if best_f else None,
            "best_function_ref": best_f["ref"] if best_f else None,
            "best_function_text": best_f["premise"] if best_f else None,
            "best_function_hypothesis": best_f["hypothesis"] if best_f else None,
            "best_function_hyp_source": best_f["hyp_source"] if best_f else None,
            "max_contra_precaution": r(best_p["C"]) if best_p else None,
            "best_precaution_ref": best_p["ref"] if best_p else None,
            "best_precaution_text": best_p["premise"] if best_p else None,
            "templates": tmpl,
            "checks": [{k: x[k] for k in ("ref", "evidence_type", "premise", "hypothesis", "hyp_source", "E", "N", "C")}
                       for x in pairs if x["kind"] == "func"],
        }

    # ── 결과 저장 (nli_result 테이블) ───────────────────────────
    def save(self, video_results, out_db):
        con = sqlite3.connect(out_db)
        with con:
            for v in video_results:
                for s in v["nli_claims"]:
                    for c in s["checks"]:
                        con.execute(
                            "INSERT INTO nli_result (claim_id, premise_ref, evidence_type, target, premise, hypothesis,"
                            " p_entail, p_neutral, p_contra, model) VALUES (?,?,?,?,?,?,?,?,?,?)",
                            (f"{v['video_id']}:{v['product_ref']}:{s['claim_id']}", c["ref"], c["evidence_type"], s["subject"],
                             c["premise"], c["hypothesis"], c["E"], c["N"], c["C"], self.model_name))
        con.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mapped", help="mapped_products.json")
    ap.add_argument("--premises-db", default=None, help="nli_premises.sqlite (주의사항·원료 문장, 선택)")
    ap.add_argument("--source-db", default=None, help="claim_verification.sqlite (원료 이름 찾기, 선택)")
    ap.add_argument("--out", default="nli_results.json")
    ap.add_argument("--allow-unresolved", action="store_true", help="확정 안 된 제품 후보도 근거로 사용 (실험용)")
    ap.add_argument("--only-confirmed", action="store_true", help="제품이 확정(confirmed)된 영상만 처리")
    ap.add_argument("--limit", type=int, default=None, help="앞에서부터 영상 N개만")
    ap.add_argument("--hyp-source", choices=["text", "effect", "both"], default="both")
    ap.add_argument("--no-templates", action="store_true")
    ap.add_argument("--model", default=None)
    ap.add_argument("--save", action="store_true", help="결과를 premises-db의 nli_result 테이블에 저장")
    args = ap.parse_args()

    videos = load_mapped(args.mapped)
    if args.only_confirmed:
        videos = [x for x in videos if ((x.get("product") or {}).get("match") or {}).get("status") == "confirmed"]
    videos = videos[: args.limit]
    v = Verifier(args.premises_db, args.source_db, model_name=args.model)
    t0 = time.time()
    results = [v.verify_video(x, args.allow_unresolved, args.hyp_source, templates=not args.no_templates)
               for x in videos]
    elapsed = time.time() - t0

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    if args.save and args.premises_db:
        v.save(results, args.premises_db)

    claims = [c for r in results for c in r["nli_claims"]]
    print(f"영상 {len(results)}개 / NLI 대상 Claim {len(claims)}개 / {elapsed:.1f}초")
    print("제품 상태:", dict(Counter(r["product_status"] for r in results)))
    print("비교 근거(basis):", dict(Counter(c["basis"] for c in claims)))
    print("판단 보류 이유:", dict(Counter(c["basis_reason"] for c in claims if c["basis"] == "NONE")))
    print(f"저장: {args.out}")
