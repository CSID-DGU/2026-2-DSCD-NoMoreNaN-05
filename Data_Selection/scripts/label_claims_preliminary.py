"""Conservative, offline first-pass labels under the supplied Mechanism A PDF.

This is a rule-based screening, not an LLM/NLI verdict or legal conclusion.
Original delivered claims are preserved; ETC is excluded only in a new copy.
Unresolved cases require semantic review, not automatic negative judgments.
"""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
LABELS = ('VIOLATION', 'OVERCLAIM', 'UNCLEAR', 'SUPPORTED', 'OUT_OF_SCOPE', 'DISCLAIMER')


def key(value):
    return re.sub(r'[^가-힣a-z0-9]', '', unicodedata.normalize('NFC', value or '').lower())


def decision(label, reason, evidence=None):
    return dict(label=label, reason_code=reason, evidence=evidence or [],
                method='conservative_offline_rules', provisional=True,
                needs_semantic_review=label == 'UNCLEAR')


def scope_decision(claim):
    text = claim.get('text') or ''
    compact = key(text)
    # Full statements only: a disease word or a single negation is insufficient.
    disclaimer = (
        r'(인체\s*적용\s*시험|인체\s*시험|시험\s*결과|연구\s*결과).{0,100}'
        r'(모든\s*사람|개인차).{0,60}(아[님니]|않|있)',
        r'(개인에\s*따라|개인별로).{0,30}(차이|다를).{0,20}(있|수)',
        r'질병의?\s*(예방\s*(및|과|·|,|ㆍ|/)\s*치료|치료\s*(및|과)\s*예방).{0,30}의약품[이가은는\s]*아[님니]',
        r'(원료|성분)에?\s*(대한|관한)\s*(설명|정보|내용)(입니다|임|이며|에\s*한)',
    )
    if any(re.search(pattern, text, re.S) for pattern in disclaimer):
        return decision('DISCLAIMER', 'EXPLICIT_DISCLAIMER')
    typ = claim.get('claim_type')
    if typ == 'PERSON_CREDENTIAL':
        return decision('OUT_OF_SCOPE', 'PERSON_CREDENTIAL_OUTSIDE_PDF_SCOPE')
    # Do not classify a mixed registration + patent statement as wholly outside scope.
    if typ == 'CERTIFICATION':
        pure_gmp = re.fullmatch(r'(우수)?건강기능식품제조기준gmp|gmp(인증|마크|시설|인증시설|인증업소)?', compact)
        in_scope = re.search(r'건강기능식품|식약처|개별인정|인정번호|기능성인정|국내최초', compact)
        outside = re.search(r'특허|haccp|수상|어워드|awards?|광고심의|심의필|ccm|소비자중심경영|논문|시험기관|시험조건|iso\d|fda|할랄|코셔', compact)
        if pure_gmp:
            return decision('OUT_OF_SCOPE', 'GMP_NOT_PROVEN_BY_INDUSTRY_FIELD')
        if outside and not in_scope:
            return decision('OUT_OF_SCOPE', 'CERTIFICATION_OUTSIDE_AVAILABLE_SOURCES')
    if typ == 'QUANTITY':
        has_comparable = bool(claim.get('ingredients') or claim.get('effect'))
        if not has_comparable and re.search(r'가격|할인|\d[\d,]*\s*원|판매량|판매액|매출|리뷰|후기|재구매|누적|수출액|\d\s*위|no\.?\s*1|1등', text, re.I):
            return decision('OUT_OF_SCOPE', 'PRICE_REVIEW_RANKING_OUTSIDE_PDF_SCOPE')
        if not has_comparable:
            packaging = re.sub(r'(총|내용량|제품|포장|당|당량|정제|캡슐|캅셀|개월분|개월|개입|밀리그램|그램|킬로그램|알|포|병|정|개|입|세트|상자|박스|팩|통|짜리|들이|g|mg|kg|ml|l|cc|x|×)', '', text.lower())
            if re.search(r'\d', text) and not re.sub(r'[\d\s.,:;()\[\]/*+\-=]', '', packaging):
                return decision('OUT_OF_SCOPE', 'PACKAGING_SIZE_OUTSIDE_PDF_SCOPE')
    if typ == 'COMPOSITION' and not claim.get('effect'):
        # Only isolated origin/process claims; mixed composition claims stay reviewable.
        if re.fullmatch(r'(100[%％]?\s*)?(한국산|국내산|국산|미국산|캐나다산|독일산|덴마크산|스위스산|프랑스산)(\s*원료)?', text.strip()):
            return decision('OUT_OF_SCOPE', 'ORIGIN_OUTSIDE_PDF_SCOPE')
    return None


def label_claim(claim, product, quarantine):
    scoped = scope_decision(claim)
    if scoped:
        return scoped
    if product is None:
        return decision('UNCLEAR', 'INVALID_PRODUCT_REFERENCE')
    status = product.get('match', {}).get('status')
    if status != 'confirmed':
        return decision('UNCLEAR', 'PRODUCT_' + str(status or 'UNKNOWN').upper())
    if quarantine:
        return decision('UNCLEAR', quarantine)
    db = product.get('DB')
    typ = claim.get('claim_type')
    if not db or typ not in db:
        return decision('UNCLEAR', 'NO_TYPE_SPECIFIC_DB')
    fields = db[typ]
    text = claim.get('text') or ''
    normalized = key(text)
    if not normalized:
        return decision('UNCLEAR', 'EMPTY_CLAIM')
    if typ == 'EFFECT':
        official = fields.get('MAIN_FNCTN') or ''
        # No negations, guarantees, or extra assertions may be hidden by this test.
        if len(normalized) >= 6 and normalized in key(official):
            return decision('SUPPORTED', 'LITERAL_PRODUCT_FUNCTIONALITY_MATCH',
                            [dict(field='EFFECT.MAIN_FNCTN', text=official)])
    if typ == 'COMPOSITION':
        ingredients = claim.get('ingredients') or []
        if ingredients and not re.search(r'무첨가|미함유|불포함|없는|없음|아니|제외|특허|\d+\s*%|원산지|국산', text):
            source_fields = ('RAWMTRL_NM', 'INDIV_RAWMTRL_NM', 'ETC_RAWMTRL_NM', 'CAP_RAWMTRL_NM')
            materials = defaultdict(list)
            for field in source_fields:
                for name in re.split(r',(?![^()]*\))', fields.get(field) or ''):
                    cleaned = re.sub(r'\([^()]*\)', '', name).strip()
                    if cleaned:
                        materials[key(cleaned)].append((field, name.strip()))
            # Match complete material tokens. B1 must not match B12.
            matches = [materials.get(key(ingredient), []) for ingredient in ingredients]
            remainder = normalized
            for ingredient in sorted(ingredients, key=len, reverse=True):
                remainder = remainder.replace(key(ingredient), '')
            for word in ('함유되어있다', '포함되어있다', '함유', '포함', '성분', '배합', '및', '와', '과'):
                remainder = remainder.replace(word, '')
            if all(matches) and not remainder:
                return decision('SUPPORTED', 'ALL_EXPLICIT_INGREDIENTS_FOUND',
                                [dict(field='COMPOSITION.' + found[0][0], text=found[0][1]) for found in matches])
    if typ == 'CERTIFICATION':
        # Pure healthy-functional-food registration claims only.
        pure = re.fullmatch(r'(본광고는|본제품은|이제품은|본광고|본제품|광고방송)?건강기능식품(광고)?(입니다|임)?', normalized)
        if pure and (fields.get('STTEMNT_NO') or '').strip():
            return decision('SUPPORTED', 'REGISTERED_HEALTH_FUNCTIONAL_FOOD',
                            [dict(field='CERTIFICATION.STTEMNT_NO', text=fields['STTEMNT_NO'])])
    if typ == 'QUANTITY':
        # Only a complete literal intake statement, never isolated digits.
        official = fields.get('SRV_USE') or ''
        if len(normalized) >= 6 and normalized == key(official):
            return decision('SUPPORTED', 'LITERAL_INTAKE_INSTRUCTION_MATCH',
                            [dict(field='QUANTITY.SRV_USE', text=official)])
    return decision('UNCLEAR', 'SEMANTIC_OR_NUMERICAL_REVIEW_REQUIRED')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT/'exports/claim_type_db_20261103/claims_with_db.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'exports/preliminary_labels_20261104')
    args = parser.parse_args()
    videos = json.loads(args.input.read_text(encoding='utf-8-sig'))
    audit = ROOT/'data/processed/claim_json_feedback_audit'
    quarantines = {}
    for filename, reason in [('confirmed_manufacturer_mismatch.json', 'IDENTITY_MANUFACTURER_CONFLICT'),
                             ('confirmed_missing_manufacturer.json', 'IDENTITY_MANUFACTURER_UNVERIFIED')]:
        for row in json.loads((audit/filename).read_text(encoding='utf-8')):
            quarantines[(row['video_id'], row['product_ref'])] = reason
    filtered = []
    labeled = []
    flat = []
    excluded = []
    counts = Counter()
    types = defaultdict(Counter)
    reasons = Counter()
    for video in videos:
        item = copy.deepcopy(video)
        item['claims'] = [copy.deepcopy(c) for c in video['claims'] if c.get('claim_type') != 'ETC']
        filtered.append(copy.deepcopy(item))
        refs = defaultdict(list)
        for product in video['products']:
            if product.get('product_ref') is not None:
                refs[product['product_ref']].append(product)
        for claim in video['claims']:
            if claim.get('claim_type') == 'ETC':
                excluded.append(dict(video_id=video['video_id'], claim=copy.deepcopy(claim)))
        for claim in item['claims']:
            candidates = refs.get(claim.get('product_ref'), [])
            product = candidates[0] if len(candidates) == 1 else None
            verdict = label_claim(claim, product, quarantines.get((video['video_id'], claim.get('product_ref'))))
            claim['preliminary_assessment'] = verdict
            counts[verdict['label']] += 1
            types[claim['claim_type']][verdict['label']] += 1
            reasons[verdict['reason_code']] += 1
            flat.append(dict(video_id=video['video_id'], url=video.get('url'), **copy.deepcopy(claim)))
        labeled.append(item)
    total = sum(counts.values())
    summary = dict(input=str(args.input), input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
                   original_claims=sum(len(v['claims']) for v in videos), excluded_etc=len(excluded),
                   classified_claims=total, labels={label:counts[label] for label in LABELS},
                   percentages={label:round(100*counts[label]/total, 2) for label in LABELS},
                   by_claim_type={k:dict(v) for k,v in types.items()}, reason_counts=dict(reasons),
                   method='conservative_offline_rules_not_llm_or_nli', provisional=True,
                   source='User-provided Mechanism A reconstruction PDF',
                   identity_quarantine_product_entries=len(quarantines),
                   notes=['ETC remains in the original delivered file; excluded only from this new output.',
                          'PDF scope and disclaimers are applied before identity checks.',
                          'Unconfirmed, invalid-reference and flagged confirmed products cannot yield DB-based support or violation.',
                          'VIOLATION and OVERCLAIM are not inferred by keyword absence; zero is not evidence of no violations.',
                          'No LLM/NLI, external API, legal validation or complete semantic/numerical evaluation was performed.',
                          'NOT_FOUND is a product match status, not one of the six verdict labels.'])
    # Preserve every original claim field including effect, apart from intentional ETC exclusion.
    assert sum(len(v['claims']) for v in filtered) == total
    for source, result in zip(filtered, labeled):
        for a, b in zip(source['claims'], result['claims']):
            assert a == {k:v for k,v in b.items() if k != 'preliminary_assessment'}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, value in [('summary.json', summary), ('claims_without_etc.json', filtered),
                        ('claims_labeled_preliminary.json', labeled), ('labels_flat.json', flat), ('excluded_etc.json', excluded)]:
        (args.output_dir/name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
