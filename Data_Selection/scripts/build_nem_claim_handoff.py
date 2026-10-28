"""DB-grounded NEM case example; reviewed source routes, lexical TF-IDF scores.

This is a case-specific handoff example, not the general semantic retriever.
No model/API calls, no truth verdict, no writes to the source database.
"""
import argparse
from collections import Counter
from contextlib import closing
import hashlib
import json
import math
from pathlib import Path
import re
import sqlite3
import unicodedata

ROOT = Path(__file__).resolve().parents[1]


def grams(text):
    value = re.sub(r"[^a-z0-9가-힣]", "", unicodedata.normalize("NFC", text).lower())
    return Counter(value[start:start + size] for size in (2, 3, 4)
                   for start in range(len(value) - size + 1))


def vectors(texts):
    counts = [grams(text) for text in texts]
    frequencies = Counter(term for document in counts for term in document)
    idf = {term: math.log((1 + len(texts)) / (1 + count)) + 1
           for term, count in frequencies.items()}

    def vector(text):
        weighted = {term: count * idf[term] for term, count in grams(text).items() if term in idf}
        norm = math.sqrt(sum(value * value for value in weighted.values()))
        return {term: value / norm for term, value in weighted.items()} if norm else {}

    return vector


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "docs/nem_claim_evidence_handoff.json")
    parser.add_argument("--threshold", type=float, default=0.10)
    args = parser.parse_args()
    if not 0 < args.threshold < 1:
        parser.error("Threshold must be strictly between zero and one.")
    original = args.input.read_bytes()
    bundle = json.loads(original.decode("utf-8-sig"))
    if [p["product_name"] for p in bundle["products"]] != ["관절연골엔 난각막NEM"]:
        parser.error("This example is reviewed only for the supplied NEM case.")
    database = ROOT / "Data_List_Claim_Verification/claim_verification.sqlite"
    with closing(sqlite3.connect(database.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        product = dict(db.execute("SELECT * FROM products WHERE product_id=6411").fetchone())
        ingredient = dict(db.execute("SELECT * FROM ingredients WHERE ingredient_id=1151").fetchone())
        sources = {}

        def add(key, text, table, record_id, column, relation, **extra):
            sources[key] = dict(source_ref=key, text=text,
                                source=dict(database="claim_verification.sqlite", table=table,
                                            record_id=record_id, column=column, **extra),
                                relationship=relation,
                                requires_product_identity_confirmation=table == "products")

        for row in db.execute("SELECT * FROM evidence WHERE ingredient_id=1151"):
            row = dict(row)
            add("evidence:" + str(row["evidence_id"]), row["evidence_text"], "evidence",
                row["evidence_id"], "evidence_text", "ingredient_reference",
                ingredient_id=1151, recognition_number=ingredient["recognition_number"],
                evidence_type=row["evidence_type"], source_authority=row["source_authority"])
        for index, line in enumerate(product["main_functionality"].splitlines(), 1):
            add(f"product:6411:functionality:{index}", line, "products", 6411,
                "main_functionality", "unconfirmed_product_candidate_reference", line=index)
        for field in ("intake_method", "company_name", "manufacturing_report_number"):
            add("product:6411:" + field, product[field], "products", 6411, field,
                "unconfirmed_product_candidate_reference")
        for index, line in enumerate(product["specification"].splitlines(), 1):
            if "Ser-Trp" in line or "비타민D" in line:
                add(f"product:6411:specification:{index}", line, "products", 6411,
                    "specification", "unconfirmed_product_candidate_reference", line=index)
        add("ingredient:1151:name", ingredient["ingredient_name"], "ingredients", 1151,
            "ingredient_name", "ingredient_reference", recognition_number=ingredient["recognition_number"])

    # Reviewed candidate routes distinguish related functionality from unavailable
    # trial, patent, packaging, seller and market-share evidence. They do not infer
    # that collagen/chondroitin/hyaluronan occurs in this product from other ingredients.
    functional = ["evidence:2864", "product:6411:functionality:1"]
    vitamin = ["product:6411:functionality:2", "product:6411:specification:3"]
    routes = {
        "c01": functional, "c02": functional, "c07": functional,
        "c11": ["evidence:2865", "product:6411:intake_method"],
        "c14": functional, "c15": ["product:6411:functionality:1", *vitamin, "ingredient:1151:name"],
        "c16": functional,
        "c19": ["product:6411:specification:2", "product:6411:intake_method"],
        "c22": ["product:6411:company_name"],
    }
    notes = {
        "c03": "현재 자료에는 인체연골 구성성분 목록이나 해당 제품의 전체 원재료 목록이 없습니다.",
        "c04": "콜라겐 계열 원료 자료는 DB에 있으나 이 제품의 콜라겐 함유를 확인하는 자료는 선택한 범위에 없습니다.",
        "c05": "콘드로이친 계열 자료만으로 이 제품의 콘드로이친황산 함유를 연결하지 않았습니다.",
        "c06": "히알루론산 원료 자료만으로 이 제품의 히알루론산 함유를 연결하지 않았습니다.",
        "c07": "관련 기능성 자료만 연결합니다. WOMAC 24개 전 항목 개선과 12주 임상시험 결과는 확인되지 않았습니다.",
        "c08": "인체적용시험 대상자의 연령 자료가 현재 검색 범위에 없습니다.",
        "c09": "섭취군 46명·대조군 45명에 대응하는 시험 보고서가 현재 검색 범위에 없습니다.",
        "c10": "12주 인체적용시험 기간에 대응하는 자료가 현재 검색 범위에 없습니다.",
        "c11": "500mg/일은 원료 인정 섭취량입니다. 광고가 인용한 시험의 섭취량·제품 함량을 확인한 것은 아닙니다.",
        "c12": "광고가 인용한 2023년 인체적용시험 보고서는 현재 검색 범위에 없습니다.",
        "c13": "해당 개인차 고지에 직접 대응하는 문장이 현재 검색 범위에 없습니다.",
        "c15": "DB 제품 후보의 기능성·규격에 원료명이 나타납니다. 광고 제품과의 동일성은 제조원 불일치로 미확정입니다.",
        "c17": "특허번호·특허 등록 자료는 이번 검색 범위에 없습니다. 기능성 인정번호를 특허번호로 대체하지 않습니다.",
        "c18": "건강기능식품 제품정보 DB의 동명 제품은 있으나 제품 동일성 및 등록 지위 확인은 별도 단계입니다.",
        "c19": "DB의 0.72g 규격·1회 2캡슐 자료는 관련 맥락입니다. 총 21.6g·60캡슐 포장을 입증한 것은 아닙니다.",
        "c20": "구입률 1위·시장점유율 조사 자료가 현재 검색 범위에 없습니다.",
        "c21": "이 광고의 심의번호·심의 결과 자료가 현재 검색 범위에 없습니다.",
        "c22": "광고 제조원은 (주)서흥헬스케어 제2공장, DB 동명 제품 제조사는 (주)서흥으로 다릅니다. 검토 자료로만 연결합니다.",
        "c23": "종근당건강은 입력의 브랜드·판매원 정보입니다. DB 제조사 필드로 판매원 일치를 대체하지 않습니다.",
    }
    vector = vectors([source["text"] for source in sources.values()])
    source_vectors = {key: vector(source["text"]) for key, source in sources.items()}
    for claim in bundle["claims"]:
        query_parts = [claim["text"], claim.get("effect") or "", *claim.get("ingredients", [])]
        query = " ".join(dict.fromkeys(part for part in query_parts if part))
        query_vector = vector(query)
        links = []
        for key in routes.get(claim["claim_id"], []):
            score = sum(value * source_vectors[key].get(term, 0) for term, value in query_vector.items())
            if score > args.threshold:
                links.append(dict(sources[key], similarity=round(score, 8)))
        links.sort(key=lambda row: (-row["similarity"], row["source_ref"]))
        links = links[:5]
        for rank, link in enumerate(links, 1):
            link["rank"] = rank
        claim.update(retrieval_query=query, evidences=links, evidence_count=len(links),
                     retrieval_status="evidence_candidates_found" if links else "no_linkable_evidence",
                     retrieval_message="관련 Evidence 후보 있음" if links else "연결 가능한 Evidence 없음",
                     coverage_note=notes.get(claim["claim_id"], "관련 기능성 근거이며 최종 판정은 수행하지 않았습니다."),
                     judgment=dict(status="pending", verdict=None, reason=None))

    bundle["products"][0]["db_match"] = dict(
        status="unresolved_manufacturer_conflict", name_match="exact",
        candidate_product_id=6411, candidate_product_name=product["product_name"],
        database_manufacturer=product["company_name"],
        extracted_manufacturer="(주)서흥헬스케어 제2공장",
        manufacturer_source_claim_id="c22", manufacturing_report_number=product["manufacturing_report_number"],
        required_confirmation="광고 포장의 품목제조신고번호·제품 버전 확인",
    )
    bundle["retrieval"] = dict(
        method="character_ngram_tfidf_cosine", embedding_model=None,
        query_fields=["text", "effect", "ingredients"], character_ngram_range=[2, 4],
        threshold=args.threshold, threshold_operator=">", max_evidences_per_claim=5,
        ordering="similarity_descending", scores_are_measured=True,
        threshold_validation="재현율을 우선한 임시 비영(非零) 기준. 정밀도 검증 및 임베딩 점수와의 호환성 없음.",
        candidate_selection="이 23개 Claim에 대해 검토한 사례별 출처 경로. 범용 자동 검색 엔진이 아님.",
        source_scope="SQLite 동명 제품 6411 및 NEM 원료 1151 관련 선택 문장. 외부 임상·특허·브랜드 DB 미검색.",
        product_identity_warning="제품 직접 자료는 동일성 미확정 후보 자료입니다. 원료 근거는 별도로 구분합니다.",
        corpus_document_count=len(sources),
        corpus_sha256=hashlib.sha256(json.dumps(sources, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        input_sha256=hashlib.sha256(original).hexdigest(),
    )
    bundle["summary"] = dict(
        claim_count=len(bundle["claims"]),
        claims_with_evidence=sum(bool(claim["evidences"]) for claim in bundle["claims"]),
        claims_without_evidence=sum(not claim["evidences"] for claim in bundle["claims"]),
        evidence_link_count=sum(len(claim["evidences"]) for claim in bundle["claims"]),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(bundle["summary"]))


if __name__ == "__main__":
    main()
