"""Apply explicit assistant review decisions; no API calls or source rewrites.

Indices refer to the frozen reviewable.json (537 claims with a delivered
confirmed product, excluding nine known manufacturer-conflict product entries).
These are provisional judgments conditional on delivered product identity,
not human gold labels, legal judgments, or measured system accuracy.
"""
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import sqlite3

from scripts.label_claims_preliminary import LABELS
from src.claim_type_db_format import db_sections

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT/'data/processed/semantic_review_20261104/reviewable.json'
ORIGINAL = ROOT/'exports/claim_type_db_20261103/claims_with_db.json'
FIRST = ROOT/'exports/preliminary_labels_20261104/claims_labeled_preliminary.json'
OUT = ROOT/'exports/semantic_review_20261104'


def indices(text):
    result = set()
    for item in text.split():
        if '-' in item:
            a,b = map(int,item.split('-'))
            result.update(range(a,b+1))
        else:
            result.add(int(item))
    return result


# Explicit decisions following inspection of text, linked formulation, functional
# statements, intake instructions and recognition entries. Anything unspecified
# was reviewed but stays UNCLEAR; differences are not assumed to prove fraud.
GROUPS = [
    ('SUPPORTED', '영文・약어・아래첨자 등 성분명 표기를 대응하면 해당 원료가 DB에서 확인됨.',
     '18-40 50-72 75 127 146 161 171 183 203 210 222 235 247-250 263 284 304 334 344 368 371 380 387 391 398 402 406 414 418 446 458 459 466 472 479 488 498 501 502',
     ['COMPOSITION.RAWMTRL_NM','COMPOSITION.INDIV_RAWMTRL_NM','COMPOSITION.ETC_RAWMTRL_NM']),
    ('SUPPORTED', '일반적인 건강 지원・케어 또는 축약 표현을 등록 기능성 범위로 해석하면 DB와 부합함. 치료・보장 의미까지 인정하지 않음.',
     '6-8 150 154 172 191-193 201 208 209 219-221 231 233 234 244 252 270 275 277 279 289 290 294-297 299 300 318 333 343 367 369 375 376 378 384 385 388-390 395 396 399-401 405 411-413 417 422 447 448 457 460-462 464 465 469 475 477 478 485 496 497 504 521',
     ['EFFECT.MAIN_FNCTN','COMPOSITION.RAWMTRL_NM']),
    ('SUPPORTED', '원료 인정번호 또는 제품 등록 기능성 자료에서 해당 등록・기능성 주장이 확인됨.',
     '17 48 49 79 86 89 92 96 103 104 110 111 117 118 125 126 152 162 165 176 184 202 214 216 226 228 239 241 242 256 264 285 292 298 307 308 320 349 350 372 392 403 415 427 435 437 443 450 467 473 480 489 513',
     ['CERTIFICATION.STTEMNT_NO','CERTIFICATION.MAIN_FNCTN','CERTIFICATION.RAWMTRL_STD_INFO']),
    ('SUPPORTED', 'DB의 기능성 성분 목록을 세면 광고한 종류 수와 일치함. 한 알・한 포 표현은 섭취 방법도 대조함.',
     '9 15 46 47 77 84 87 90 129 145 147 370 505',
     ['COMPOSITION.RAWMTRL_NM','QUANTITY.SRV_USE','QUANTITY.BASE_STANDARD']),
    ('SUPPORTED', '1일 1포 또는 1캡슐 섭취라는 의미가 DB 섭취 방법과 일치함.',
     '198 206 302', ['QUANTITY.SRV_USE']),
    ('SUPPORTED', '제품 규격에 해당 성분・표시량이 있고 섭취 방법으로 비교 기준을 확인함. 기준 생략 문장은 DB의 표시 기준을 전제로 해석함.',
     '102 182 335 345 346 374 433 463 476 495', ['QUANTITY.BASE_STANDARD','QUANTITY.SRV_USE']),
    ('SUPPORTED', '루테인 표시량 20mg/0.5g, 1일 1캡슐 0.5g, 연결된 원료 기준 상한 20mg이 함께 확인됨.',
     '262', ['QUANTITY.BASE_STANDARD','QUANTITY.SRV_USE','QUANTITY.RAWMTRL_STD_INFO']),
    ('SUPPORTED', '광고의 세 가지 눈 건강 항목을 DB의 황반색소밀도 유지・건조한 눈 개선・눈 피로도 개선과 대응함.',
     '303', ['EFFECT.MAIN_FNCTN']),
    ('SUPPORTED', '광고의 주의 문구는 DB 섭취 주의사항과 같은 의미임. 효능 주장과 구분해 비교함.',
     '491-494', ['EFFECT.INTAKE_HINT1']),
    ('SUPPORTED', '비타민D 100μg/일은 1μg=40IU 변환 시 4,000IU/일이며 DB 규격・일일 섭취량과 부합함.',
     '500', ['QUANTITY.BASE_STANDARD','QUANTITY.SRV_USE']),
    ('OUT_OF_SCOPE', '판매・순위・리뷰・출처 표기・원산지・상표・공법・일반 구호・포장 규격 등 현재 PDF/DB 비교 범위 밖임.',
     '1-5 16 41-43 45 73 76 78 80-83 85 88 91 93-95 98-101 105-109 112-116 119-124 133 138-143 148 151 153 158-160 163 164 166-169 174 177-179 181 188 189 194-196 199 200 205 213 215 225 227 232 238 240 243 245 255 257 258 260 261 265 267 271-273 276 280 281 286-288 293 306 309 312 317 321 325-329 331 336 338 348 352 356-361 363 365 366 373 379 393 394 397 404 407 410 416 419 423 425 426 428 431 434 436 438-442 444 445 449 451 452 455 456 468 474 481 483 484 490 499 503 506-512 517-520 523 525 528 531-537', []),
    ('DISCLAIMER', '시험 결과의 비일반화・제품과 무관한 건강정보임을 명시한 면책 문구임.',
     '144 157 313 330 339 362', []),
    ('UNCLEAR', '단순 원료 인정 기능성으로 인체시험의 구체적 지표・결과까지 입증할 수 없음. 원문 시험 자료가 필요함.',
     '135-137 155 156 322-324 353-355', ['EFFECT.MAIN_FNCTN']),
    ('UNCLEAR', '브랜드 업력・연구 기간은 제조업체 인허가일로 입증할 수 없음.',
     '408 409 514 516', ['QUANTITY.BSSH_PRMS_DT']),
    ('UNCLEAR', '국내 최초・유일함을 판단할 전체 제품의 비교 자료나 시점 근거가 없음.',
     '185 190 211 223 236 253 301 305', ['CERTIFICATION.PRMS_DT','CERTIFICATION.MAIN_FNCTN']),
    ('UNCLEAR', '함량・원료・기능성 또는 제형 차이가 보이나 제품 버전/리뉴얼 여부가 확인되지 않아 위반으로 단정하지 않음.',
     '197 204 291 381 424 429 430 432 454 522 524 526 527 529 530',
     ['QUANTITY.BASE_STANDARD','QUANTITY.SRV_USE','COMPOSITION.RAWMTRL_NM','COMPOSITION.ETC_RAWMTRL_NM','EFFECT.MAIN_FNCTN']),
]


def main():
    original_bytes = ORIGINAL.read_bytes()
    dbpath = ROOT/'TRUEAD_DB_보강자료/claim_verification.sqlite'
    dbhash = hashlib.sha256(dbpath.read_bytes()).hexdigest()
    original = json.loads(original_bytes)
    current = json.loads(FIRST.read_text(encoding='utf-8'))
    baseline = {(v['video_id'], c['claim_id']): copy.deepcopy(c['preliminary_assessment'])
                for v in current for c in v['claims']}
    lookup = {(v['video_id'], c['claim_id']):c for v in current for c in v['claims']}
    products = {(v['video_id'],p['product_ref']):p for v in current for p in v['products']}
    pack = json.loads(PACK.read_text(encoding='utf-8'))
    assert len(pack) == 537
    # Validate supplied evidence against live enriched SQLite, not model memory.
    with sqlite3.connect(dbpath.resolve().as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory = sqlite3.Row
        seen=set()
        for row in pack:
            product = products[(row['video_id'], row['claim']['product_ref'])]
            report = product['manufacturing_report_number']
            if report in seen:
                continue
            seen.add(report)
            found=db.execute('SELECT * FROM products WHERE manufacturing_report_number=?',(report,)).fetchone()
            assert found is not None and db_sections(dict(found)) == product['DB']
    assignments = {}
    for label,reason,selected,fields in GROUPS:
        for index in indices(selected):
            assert 1 <= index <= len(pack)
            assert index not in assignments, ('duplicate_review_index', index)
            assignments[index] = (label,reason,fields)
    reviewed=[]
    for row in pack:
        index=row['index']; claim=row['claim']; k=(row['video_id'],claim['claim_id'])
        assert lookup[k]['text'] == claim['text']
        label,reason,fields = assignments.get(index, ('UNCLEAR','검토한 DB 자료만으로 문장 전체를 확정할 수 없음. 비교 대상・용어・추가 근거 확인이 필요함.',[]))
        evidence=[]
        for path in fields:
            typ,field=path.split('.')
            value=row['DB'].get(typ,{}).get(field)
            if value not in (None,'',[]):
                evidence.append(dict(field=path, value=copy.deepcopy(value)))
        assert label != 'SUPPORTED' or evidence
        product=products[(row['video_id'],claim['product_ref'])]
        assessment=dict(label=label, reason=reason, evidence=evidence,
                        method='assistant_semantic_review', provisional=True,
                        conditional_on_delivered_product_identity=True,
                        missing_manufacturer=not bool(product.get('manufacturer_name')),
                        review_index=index,
                        needs_semantic_review=label=='UNCLEAR')
        lookup[k]['preliminary_assessment']=assessment
        reviewed.append(dict(index=index,video_id=row['video_id'],claim_id=claim['claim_id'],
                             product_name=row['product'],text=claim['text'],
                             previous_label=baseline[k]['label'],**copy.deepcopy(assessment)))
    # All other claims retain v1 screening. No implication of full LLM review.
    counts=Counter(c['preliminary_assessment']['label'] for v in current for c in v['claims'])
    before=Counter(x['previous_label'] for x in reviewed)
    after=Counter(x['label'] for x in reviewed)
    transitions=Counter((r['previous_label'],r['label']) for r in reviewed)
    fixed_condition=[r for r in reviewed if not r['missing_manufacturer']]
    changed=[]
    for v in current:
        for c in v['claims']:
            old=baseline[(v['video_id'],c['claim_id'])]['label']
            if old!=c['preliminary_assessment']['label']:
                changed.append(dict(video_id=v['video_id'],claim_id=c['claim_id'],text=c['text'],
                                    previous_label=old,**copy.deepcopy(c['preliminary_assessment'])))
    summary=dict(total_original_claims=8728, excluded_etc=1241,total_classified_claims=sum(counts.values()),
                 actually_semantically_reviewed=len(reviewed),
                 remaining_claims_keep_v1_screening=sum(counts.values())-len(reviewed),
                 reviewed_subset_before={k:before[k] for k in LABELS},
                 reviewed_subset_after={k:after[k] for k in LABELS},
                 reviewed_subset_unclear_before_percent=round(before['UNCLEAR']/len(reviewed)*100,2),
                 reviewed_subset_unclear_after_percent=round(after['UNCLEAR']/len(reviewed)*100,2),
                 overall_labels={k:counts[k] for k in LABELS},
                 overall_unclear_percent=round(counts['UNCLEAR']/sum(counts.values())*100,2),
                 changed_labels=len(changed),transitions={a+' -> '+b:n for (a,b),n in transitions.items()},
                 fixed_manufacturer_present_subset=dict(claims=len(fixed_condition),before=dict(Counter(r['previous_label'] for r in fixed_condition)),after=dict(Counter(r['label'] for r in fixed_condition))),
                 manufacturer_missing_released_from_automatic_hold=sum(r['missing_manufacturer'] for r in reviewed),
                 known_manufacturer_conflicts_remain_excluded=True,
                 input_sha256=hashlib.sha256(original_bytes).hexdigest(),database_sha256=dbhash,
                 product_mapping_modified=False, input_db_modified=False,
                 note='537 claims reviewed against supplied confirmed-product DB evidence; other claims retain v1. Missing manufacturer alone is not an automatic hold here. Product identity/formulation and time/version remain assumptions. Not human gold labels or accuracy measurements.')
    OUT.mkdir(parents=True,exist_ok=True)
    for name,value in [('claims_reassessed.json',current),('reviewed_537.json',reviewed),('changed_claims.json',changed),('summary.json',summary)]:
        (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    # Field preservation, including effect, and no original mutation.
    for v,out in zip(original,current):
        assert v['products']==out['products']
        a=[c for c in v['claims'] if c['claim_type']!='ETC']
        b=[{k:value for k,value in c.items() if k!='preliminary_assessment'} for c in out['claims']]
        assert a==b
    assert ORIGINAL.read_bytes()==original_bytes
    assert hashlib.sha256(dbpath.read_bytes()).hexdigest()==dbhash
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
