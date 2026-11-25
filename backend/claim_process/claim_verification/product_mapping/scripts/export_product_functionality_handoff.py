"""Export original video claims plus database product functionality; no inference."""
from collections import Counter
from contextlib import closing
import copy
import hashlib
import json
from pathlib import Path
import sqlite3

from ..src.claim_evidence_experiment import company_key
from ..src.product_identity_filtered import company_core
from ..src.company_comparison import company_values,company_field

FIELDS=('product_id','product_name','company_name','manufacturing_report_number','main_functionality')


def match_status(row, pairs):
    selected=row.get('selected_product')
    if selected is None:
        if not row.get('candidates'):
            return dict(status='not_found',method=None,note='현재 검색 규칙으로 연결 가능한 DB 제품 후보 없음. DB 전체에 제품이 없다는 판정은 아님.')
        return dict(status='unresolved',method=None,note='후보 제품을 하나로 선택하지 못함: '+row.get('manufacturer_resolution','multiple_candidates'))
    previous=row.get('previous_match',{})
    if row.get('route')=='exact_report_number_fallback':
        return dict(status='confirmed',method='report_number',note='제품명 경로로 연결되지 않아 입력 신고번호로 보조 연결함.')
    if previous.get('status')=='matched' and previous.get('product_id')==selected['product_id'] and previous.get('route')=='exact_report_number':
        return dict(status='confirmed',method='report_number',note=None)
    observations=company_values(row)
    def equivalent(a,b):
        a,b=company_core(a),company_core(b)
        return bool(a and b) and (a==b or frozenset((a,b)) in pairs)
    # Approved pairs are permitted on exact-name routes only, as in matching.
    allow_pairs=row.get('route') in ('exact_name','brand_removed_exact_name','brand_added_exact_name')
    agrees=bool(observations) and all(
        company_core(o)==company_core(selected['company_name']) or (allow_pairs and equivalent(o,selected['company_name']))
        for o in observations)
    if agrees:
        note='제품명 검색 경로: '+row.get('route','unknown')
        if company_field(row)=='brand_name':note+='; 입력 brand_name과 DB company_name 비교'
        if any(company_key(o)!=company_key(selected['company_name']) for o in observations):
            note+='; 제조사 공장 표기 정리 또는 사용자 승인 PAIR 적용'
        if row.get('top_name_score') is not None and row['top_name_score']<100:
            note+='; 전체 제품명 유사도 '+str(round(row['top_name_score'],2))
        return dict(status='confirmed',method='name_and_company',note=note)
    label='브랜드' if company_field(row)=='brand_name' else '제조사'
    return dict(status='unresolved',method=None,
                note='DB 후보는 하나이나 '+label+' 미확인 또는 DB 회사명 불일치/충돌. 광고: '+str(row.get(company_field(row)))+' / DB: '+str(selected['company_name']))


def build_record(video, row, product_rows, version, pairs):
    selected=row.get('selected_product')
    evi={k:product_rows[selected['product_id']][k] for k in FIELDS} if selected else None
    product=dict(match=match_status(row,pairs),evi_product=evi)
    if company_field(row)=='brand_name':product['match']['company_comparison_field']='brand_name'
    if not selected and row.get('candidates'):
        # Never select an arbitrary first record when multiple candidates remain.
        product['candidates']=[{k:product_rows[c['product_id']][k] for k in FIELDS} for c in row['candidates']]
    return dict(video_id=video['video_id'],url=video.get('url'),product_ref=row.get('product_ref'),
                db_version=version,product=product,
                claims=[copy.deepcopy(c) for c in video.get('claims',[]) if c.get('product_ref')==row.get('product_ref')])
