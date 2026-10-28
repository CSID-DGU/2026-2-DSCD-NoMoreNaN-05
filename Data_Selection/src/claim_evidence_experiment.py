"""Product identity and source-grounded candidate preparation following the supplied PDF."""
from collections import Counter, defaultdict
from contextlib import closing
import copy
import hashlib
import json
from pathlib import Path
import random
import re
import sqlite3
import unicodedata

from rapidfuzz.distance import DamerauLevenshtein


def name_key(value):
    return re.sub(r"\s+", "", unicodedata.normalize("NFC", str(value or "")).casefold())


def company_key(value):
    text = unicodedata.normalize("NFC", str(value or "")).casefold()
    text = re.sub(r"\(\s*주\s*\)|㈜|주식회사|\(\s*유\s*\)|유한회사", "", text)
    text = re.sub(r"제(?=\s*\d+\s*공장)", "", text)
    return re.sub(r"\s+", "", text)


def whole_phrase(needle, haystack):
    tokens = unicodedata.normalize("NFC", needle or "").casefold().split()
    if not tokens:
        return False
    pattern = r"(?<![가-힣a-z0-9])" + r"\s+".join(re.escape(token) for token in tokens) + r"(?![가-힣a-z0-9])"
    return re.search(pattern, unicodedata.normalize("NFC", haystack or "").casefold()) is not None


GENERIC_PRODUCT_NAMES = {"유산균", "멀티비타민", "종합비타민", "비타민", "마그네슘", "홍삼정", "홍삼", "칼슘", "루테인", "밀크씨슬", "오메가3", "콜라겐", "프로폴리스"}


class Catalog:
    company_normalizer = staticmethod(company_key)

    def __init__(self, database):
        with closing(sqlite3.connect(Path(database).resolve().as_uri() + "?mode=ro", uri=True)) as db:
            db.row_factory = sqlite3.Row
            self.products = [dict(row) for row in db.execute("SELECT * FROM products")]
            self.ingredients = [dict(row) for row in db.execute("SELECT * FROM ingredients")]
            self.evidences = [dict(row) for row in db.execute("SELECT * FROM evidence")]
        self.by_id = {row["product_id"]: row for row in self.products}
        self.names, self.reports, self.companies = defaultdict(list), defaultdict(list), defaultdict(list)
        for row in self.products:
            self.names[name_key(row["product_name"])].append(row)
            self.reports[name_key(row["manufacturing_report_number"])].append(row)
            self.companies[self.company_normalizer(row["company_name"])].append(row)
        self.ingredient_by_id = {row["ingredient_id"]: row for row in self.ingredients}
        self.evidence_by_ingredient = defaultdict(list)
        for row in self.evidences:
            self.evidence_by_ingredient[row["ingredient_id"]].append(row)
        self.ingredient_names = {row["ingredient_id"]: ingredient_aliases(row) for row in self.ingredients}

    def identify(self, product):
        raw_name = product.get("product_name") or ""
        name = name_key(raw_name)
        manufacturer = self.company_normalizer(product.get("manufacturer_name"))
        report = name_key(product.get("manufacturing_report_number"))
        base = dict(status="unmatched", product_id=None, route=None, name_score=None,
                    reason=None, candidate_count=0, candidate_examples=[],
                    observed_manufacturer=product.get("manufacturer_name"),
                    observed_report_number=product.get("manufacturing_report_number"))
        if product.get("identity_observation_conflicts"):
            return dict(base, reason="conflicting_input_identity_observations")
        if not name and not report:
            return dict(base, reason="missing_product_name_and_report_number")

        def resolve(rows, route, require_manufacturer=False, scores=None):
            result = dict(base, route=route, candidate_count=len(rows),
                          candidate_examples=[{k: row[k] for k in ("product_id", "product_name", "company_name", "manufacturing_report_number")} for row in rows[:5]])
            if require_manufacturer and not manufacturer:
                return dict(result, reason="manufacturer_missing")
            valid = [row for row in rows
                     if (not manufacturer or manufacturer == self.company_normalizer(row["company_name"]))
                     and (not report or report == name_key(row["manufacturing_report_number"]))]
            if len(valid) == 1:
                row = valid[0]
                return dict(result, status="matched", product_id=row["product_id"], reason="unique_candidate_without_known_identity_conflict",
                            matched_product_name=row["product_name"], matched_manufacturer=row["company_name"],
                            matched_report_number=row["manufacturing_report_number"],
                            name_score=None if scores is None else scores[row["product_id"]])
            return dict(result, reason="known_identity_conflict" if rows and not valid else "multiple_candidates" if valid else "no_candidates")

        if report:
            reported = self.reports.get(report, [])
            if reported:
                # A known report-number/name contradiction is not erased by fuzzy matching.
                if name and not any(name_key(row["product_name"]) == name or whole_phrase(raw_name, row["product_name"]) for row in reported):
                    return dict(base, route="exact_report_number", reason="report_number_and_name_conflict",
                                candidate_count=len(reported))
                return resolve(reported, "exact_report_number")
        exact = self.names.get(name, [])
        if exact:
            if name in GENERIC_PRODUCT_NAMES and not manufacturer and not report:
                return dict(base, route="exact_name", reason="generic_name_without_disambiguation", candidate_count=len(exact))
            return resolve(exact, "exact_name", scores={row["product_id"]: 100.0 for row in exact})
        if name in GENERIC_PRODUCT_NAMES:
            return dict(base, reason="generic_product_name")
        phrases = [row for row in self.products if whole_phrase(raw_name, row["product_name"])] if name else []
        if phrases:
            return resolve(phrases, "whole_phrase_and_manufacturer", require_manufacturer=True)
        if not manufacturer:
            return dict(base, route="full_name_damerau_levenshtein", reason="manufacturer_missing_for_typo_route")
        same_company = self.companies.get(manufacturer, [])
        scores = {row["product_id"]: 100 * DamerauLevenshtein.normalized_similarity(name, name_key(row["product_name"])) for row in same_company}
        passed = [row for row in same_company if scores[row["product_id"]] >= 80]
        result = resolve(passed, "full_name_damerau_levenshtein", require_manufacturer=True, scores=scores)
        if not passed:
            result["reason"] = "no_same_manufacturer_product_at_80_or_above"
        return result


def identity_observations(video, product):
    result = copy.deepcopy(product)
    observations = []
    for claim in video.get("claims", []):
        if claim.get("product_ref") != product.get("product_ref"):
            continue
        match = re.search(r"(?:제조업소|제조원|제조사)\s*[:：]\s*([^\r\n;|]+)", claim.get("text", ""))
        if match:
            value = re.split(r"(?:판매원|유통전문판매원)\s*[:：]", match.group(1))[0].strip().rstrip(".")
            observations.append(dict(field="manufacturer_name", value=value, claim_id=claim.get("claim_id")))
    if result.get("manufacturer_name"):
        observations.append(dict(field="manufacturer_name", value=result["manufacturer_name"], claim_id=None))
    values = {company_key(row["value"]) for row in observations if row["value"]}
    result["identity_observations"] = observations
    result["identity_observation_conflicts"] = len(values) > 1
    if not result.get("manufacturer_name") and len(values) == 1:
        result["manufacturer_name"] = observations[0]["value"]
    return result


def ingredient_key(value):
    return re.sub(r"[^가-힣a-z0-9]", "", unicodedata.normalize("NFC", value or "").casefold())


def ingredient_alias(row):
    name = row["ingredient_name"]
    return re.sub(r"\((?:기능성원료인정)?제?\s*\d{4}\s*-\s*\d+\s*호?\)", "", name)


def ingredient_aliases(row):
    full = ingredient_alias(row)
    base = re.sub(r"\([a-zA-Z0-9®Ⓡ™ ._-]+\)", "", full)
    return {ingredient_key(full), ingredient_key(base)}


def ingredient_candidates(catalog, texts, direct_product_text=""):
    structured = {ingredient_key(text) for text in texts if text}
    context = ingredient_key(direct_product_text)
    matches = []
    for ingredient in catalog.ingredients:
        # Only actual evidence-backed names. No guessed brand/manufacturer aliases.
        if not catalog.evidence_by_ingredient.get(ingredient["ingredient_id"]):
            continue
        aliases = [alias for alias in catalog.ingredient_names[ingredient["ingredient_id"]]
                   if len(alias) >= 2 and alias not in {"비타민", "미네랄", "콜라겐", "유산균"}]
        if any(alias in structured or (len(alias) >= 3 and any(alias in text for text in structured))
               or (context and alias in context) for alias in aliases):
            matches.append(ingredient)
    return matches


def source_chunks(row, field):
    text = row.get(field) or ""
    offset = 0
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if stripped:
            start = offset + len(line) - len(line.lstrip())
            # Preserve exact original spans; long lines use overlapping windows.
            for window_start in range(0, len(stripped), 600):
                end = min(window_start + 800, len(stripped))
                yield stripped[window_start:end], start + window_start, start + end
                if end == len(stripped):
                    break
        offset += len(line)


def declared_product_ingredients(catalog, video, product):
    """Only affirmative product-composition assertions from this product's claims.

    These are advertisement observations, not verified product composition.
    Bare ingredient fields, product names and DB functionality never open the gate.
    """
    if not product or not product.get('product_ref'):
        return [], {}
    terms, provenance = set(), defaultdict(list)
    for other in video.get('claims', []):
        if other.get('product_ref') != product['product_ref']:
            continue
        text = other.get('text') or ''
        composition = str(other.get('claim_type') or '').upper() == 'COMPOSITION'
        explicit_subject = bool(re.search(r'이\s*제품|본\s*제품|제품에는|제품은', text))
        if not composition and not explicit_subject:
            continue
        # Fail closed on negation/hypothetical wording. No inference from an
        # efficacy statement such as '홍삼을 먹으면 힘이 난다'.
        if re.search(r'무첨가|미함유|불포함|없|않|아니|제외|미사용|가정|경우|한다면|라면|\?', text):
            continue
        if not re.search(r'함유|포함|배합|첨가|사용|주원료|원료로|들어\s*있', text):
            continue
        context = ingredient_key(text)
        explicit = [term for term in other.get('ingredients') or []
                    if ingredient_key(term) and ingredient_key(term) in context]
        for ingredient in catalog.ingredients:
            aliases = catalog.ingredient_names[ingredient['ingredient_id']]
            if any(len(alias) >= 3 and alias in context for alias in aliases):
                explicit.append(ingredient_alias(ingredient))
        for term in explicit:
            terms.add(term)
            provenance[ingredient_key(term)].append(other.get('claim_id'))
    return sorted(terms), dict(provenance)


def candidates_for_claim(catalog, video, product, claim):
    result = []
    match = product["db_match"] if product else dict(status="unmatched")
    db_product = catalog.by_id.get(match.get("product_id")) if match["status"] == "matched" else None
    explicit_terms, declaration_sources = declared_product_ingredients(catalog, video, product)
    materials = ingredient_candidates(catalog, explicit_terms)
    if db_product:
        for field in ("main_functionality", "specification", "intake_method", "intake_precautions", "appearance", "shelf_life", "storage_and_distribution_standard", "company_name", "manufacturing_report_number", "registration_date"):
            for text, start, end in source_chunks(db_product, field):
                result.append(dict(source_ref=f"products:{db_product['product_id']}/{field}@{start}:{end}",
                                   text=text, material_scope="product_direct", product_id=db_product["product_id"],
                                   source=dict(table="products", record_id=db_product["product_id"], column=field,
                                               start_char=start, end_char=end),
                                   target=db_product["product_name"], evidence_type=field,
                                   applicability_note="제품 기록의 직접 자료. Claim의 참·거짓은 미판정."))
    for ingredient in materials:
        for evidence in catalog.evidence_by_ingredient[ingredient["ingredient_id"]]:
            result.append(dict(source_ref=f"evidence:{evidence['evidence_id']}", evidence_id=evidence["evidence_id"],
                               text=evidence["evidence_text"], evidence_type=evidence["evidence_type"],
                               material_scope="ingredient_reference", ingredient_id=ingredient["ingredient_id"],
                               ingredient_search_basis=dict(rule='explicit_product_composition_claim',
                                                            observed_terms=explicit_terms,
                                                            declaration_claim_ids=sorted({cid for ids in declaration_sources.values() for cid in ids if cid})),
                               target=ingredient["ingredient_name"], recognition_number=ingredient.get("recognition_number"),
                               source=dict(table="evidence", record_id=evidence["evidence_id"], column="evidence_text", source_authority=evidence["source_authority"]),
                               applicability_note="원료 수준 참고자료. 검색됐다는 이유로 제품 함유나 원료 형태의 동일성을 확인하지 않음."))
    # Same text/source/verification item is one candidate, not filled to Top-K.
    dedup = {}
    for candidate in result:
        key = (candidate["source_ref"], candidate["text"], candidate["evidence_type"])
        dedup[key] = candidate
    return list(dedup.values()), [dict(ingredient_id=i["ingredient_id"], ingredient_name=i["ingredient_name"],
                                      recognition_number=i.get("recognition_number")) for i in materials]


def sample_claims(videos, limit=100, seed=42, video_limit=None):
    rng = random.Random(seed)
    indexed = list(enumerate(videos))
    rng.shuffle(indexed)
    if video_limit is not None:
        indexed = indexed[:video_limit]
        return {index: list(range(len(video.get("claims", [])))) for index, video in indexed}
    queues = []
    for index, video in indexed:
        claims = list(range(len(video.get("claims", []))))
        rng.shuffle(claims)
        queues.append((index, claims))
    selected = defaultdict(list)
    while sum(map(len, selected.values())) < limit:
        progress = False
        for index, queue in queues:
            if queue:
                selected[index].append(queue.pop())
                progress = True
            if sum(map(len, selected.values())) == limit:
                break
        if not progress:
            break
    return dict(selected)


def prepare(input_path, database, claim_limit=100, seed=42, video_limit=None):
    raw = Path(input_path).read_bytes()
    videos = json.loads(raw.decode("utf-8-sig"))
    selected = sample_claims(videos, claim_limit, seed, video_limit)
    catalog = Catalog(database)
    output = []
    pair_count = 0
    for video_index in sorted(selected):
        video = videos[video_index]
        product_rows = []
        for product in video.get("products", []):
            product = identity_observations(video, product)
            product["db_match"] = catalog.identify(product)
            product_rows.append(product)
        lookup = {product["product_ref"]: product for product in product_rows}
        new_claims = []
        for claim_index in sorted(selected[video_index]):
            claim = copy.deepcopy(video["claims"][claim_index])
            product = lookup.get(claim.get("product_ref"))
            candidates, materials = candidates_for_claim(catalog, video, product, claim)
            claim.update(candidate_evidences=candidates, identified_ingredient_candidates=materials,
                         product_match_status=product["db_match"]["status"] if product else "unresolved_product_ref",
                         query_context=dict(product_name=product.get("product_name") if product else None,
                                            claim_type=claim.get("claim_type"), effect=claim.get("effect"),
                                            ingredients=claim.get("ingredients")),
                         judgment=dict(status="pending", verdict=None, reason=None))
            pair_count += len(candidates)
            new_claims.append(claim)
        output.append(dict(video_id=video.get("video_id"), url=video.get("url"), products=product_rows, claims=new_claims))
    return dict(metadata=dict(input_sha256=hashlib.sha256(raw).hexdigest(),
                              source_database=str(Path(database).resolve()),
                              sample_seed=seed, selection="seeded round-robin across videos" if video_limit is None else "seeded video sample, all claims",
                              claim_count=sum(len(video["claims"]) for video in output), video_count=len(output),
                              candidate_pair_count=pair_count,
                              ingredient_search_rule="Only affirmative product-composition assertions from same video's same product_ref; no ingredient fallback from product identity failure, product name or DB functionality alone",
                              identity_rule="PDF: exact report/name; whole phrase plus manufacturer; full-name Damerau-Levenshtein >=80 plus manufacturer; no conflict override",
                              identity_normalization="NFC/case/whitespace; corporate markers and ordinal 제2공장/2공장 only. No factory/company aliases.",
                              default_top_k=3, ranking_threshold=None,
                              pdf_statistical_note="PDF의 95.6% 문구를 보장값으로 사용하지 않음. 80점은 초기 실험 규칙."),
                videos=output)
