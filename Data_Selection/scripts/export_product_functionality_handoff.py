"""Export original video claims plus database product functionality; no inference."""
import argparse
from collections import Counter
from contextlib import closing
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.claim_evidence_experiment import company_key
from src.product_identity_filtered import company_core

FIELDS=('product_id','product_name','company_name','manufacturing_report_number','main_functionality')


def match_status(row, pairs):
    selected=row.get('selected_product')
    if selected is None:
        if not row.get('candidates'):
            return dict(status='not_found',method=None,note='현재 검색 규칙으로 연결 가능한 DB 제품 후보 없음. DB 전체에 제품이 없다는 판정은 아님.')
        return dict(status='unresolved',method=None,note='후보 제품을 하나로 선택하지 못함: '+row.get('manufacturer_resolution','multiple_candidates'))
    previous=row.get('previous_match',{})
    if previous.get('status')=='matched' and previous.get('product_id')==selected['product_id'] and previous.get('route')=='exact_report_number':
        return dict(status='confirmed',method='report_number',note=None)
    observations=[o['value'] for o in row.get('identity_observations',[]) if o.get('value')]
    if row.get('manufacturer_name'):
        observations.append(row['manufacturer_name'])
    def equivalent(a,b):
        a,b=company_core(a),company_core(b)
        return bool(a and b) and (a==b or frozenset((a,b)) in pairs)
    # Approved pairs are permitted on exact-name routes only, as in matching.
    allow_pairs=row.get('route') in ('exact_name','brand_removed_exact_name')
    agrees=bool(observations) and all(
        company_core(o)==company_core(selected['company_name']) or (allow_pairs and equivalent(o,selected['company_name']))
        for o in observations)
    if agrees:
        note='제품명 검색 경로: '+row.get('route','unknown')
        if any(company_key(o)!=company_key(selected['company_name']) for o in observations):
            note+='; 제조사 공장 표기 정리 또는 사용자 승인 PAIR 적용'
        if row.get('top_name_score') is not None and row['top_name_score']<100:
            note+='; 전체 제품명 유사도 '+str(round(row['top_name_score'],2))
        return dict(status='confirmed',method='name_and_company',note=note)
    return dict(status='unresolved',method=None,
                note='DB 후보는 하나이나 제조사 미확인 또는 불일치/충돌. 광고: '+str(row.get('manufacturer_name'))+' / DB: '+str(selected['company_name']))


def build_record(video, row, product_rows, version, pairs):
    selected=row.get('selected_product')
    evi={k:product_rows[selected['product_id']][k] for k in FIELDS} if selected else None
    product=dict(match=match_status(row,pairs),evi_product=evi)
    if not selected and row.get('candidates'):
        # Never select an arbitrary first record when multiple candidates remain.
        product['candidates']=[{k:product_rows[c['product_id']][k] for k in FIELDS} for c in row['candidates']]
    return dict(video_id=video['video_id'],url=video.get('url'),product_ref=row.get('product_ref'),
                db_version=version,product=product,
                claims=[copy.deepcopy(c) for c in video.get('claims',[]) if c.get('product_ref')==row.get('product_ref')])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=Path.home()/'Documents/카카오톡 받은 파일/claims_all.json')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'data/processed/product_functionality_handoff')
    args=parser.parse_args()
    raw=args.input.read_bytes()
    prepared=json.loads((ROOT/'data/processed/claim_evidence_all/prepared.json').read_text(encoding='utf-8'))
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=prepared['metadata']['input_sha256']:
        raise ValueError('Input differs from the input used to produce saved mappings. Recompute mapping first.')
    videos=json.loads(raw.decode('utf-8-sig'))
    by_video={v['video_id']:v for v in videos}
    mapped=json.loads((ROOT/'data/processed/product_identity_disambiguated/product_matches.json').read_text(encoding='utf-8'))
    with closing(sqlite3.connect((ROOT/'Data_List_Claim_Verification/claim_verification.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        products={r['product_id']:dict(r) for r in db.execute('SELECT '+','.join(FIELDS)+' FROM products')}
        version=db.execute("SELECT loaded_at FROM dataset_registry WHERE dataset_key='products'").fetchone()[0]
    config=json.loads((ROOT/'configs/manufacturer_pairs.json').read_text(encoding='utf-8'))
    pairs={frozenset(company_core(v) for v in p) for p in config['pairs']}
    records=[build_record(by_video[r['video_id']],r,products,version,pairs) for r in mapped]
    # Preserve claims whose product_ref does not identify any supplied product.
    for video in videos:
        refs={p.get('product_ref') for p in video.get('products',[])}
        unassigned=[c for c in video.get('claims',[]) if c.get('product_ref') not in refs]
        if unassigned:
            records.append(dict(video_id=video['video_id'],url=video.get('url'),product_ref=None,db_version=version,
                                product=dict(match=dict(status='unresolved',method=None,note='Claim의 product_ref에 대응하는 입력 제품 정보 없음'),evi_product=None),
                                claims=copy.deepcopy(unassigned)))
    selected=[r for r in records if r['product']['evi_product'] is not None]
    confirmed=[r for r in selected if r['product']['match']['status']=='confirmed']
    all_claims=[(r['video_id'],c['claim_id']) for r in records for c in r['claims']]
    original=[(v['video_id'],c['claim_id']) for v in videos for c in v.get('claims',[])]
    assert Counter(all_claims)==Counter(original),'Claims lost or duplicated during product partitioning'
    assert len(selected)==238
    for record in records:
        evi=record['product']['evi_product']
        if evi:
            assert evi['main_functionality']==products[evi['product_id']]['main_functionality']
        for claim in record['claims']:
            assert claim in by_video[record['video_id']]['claims']
    summary=dict(input_sha256=digest,db_version=version,input_video_count=len(videos),input_claim_count=len(original),
                 product_entry_count=len(mapped),selected_product_records=len(selected),
                 selected_record_statuses=dict(Counter(r['product']['match']['status'] for r in selected)),
                 selected_claims=sum(len(r['claims']) for r in selected),
                 confirmed_records=len(confirmed),confirmed_claims=sum(len(r['claims']) for r in confirmed),
                 all_records=len(records),all_claims=len(all_claims),
                 notes=['One record per video/product_ref; original claims and URL preserved.',
                        'confirmed means passed configured identity rules, not independent human verification or claim truth.',
                        'Multiple unresolved products use candidates array and evi_product=null; no arbitrary first candidate.',
                        'No ingredient retrieval, evidence reranking or truth judgment.'])
    args.output_dir.mkdir(parents=True,exist_ok=True)
    files={'mapped_products.json':selected,'confirmed_products.json':confirmed,'all_results.json':records,'summary.json':summary}
    for filename,value in files.items():
        (args.output_dir/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
