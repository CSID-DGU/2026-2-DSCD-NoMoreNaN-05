"""Recheck saved unmapped products using their own claims; preserve all originals."""
from collections import defaultdict, Counter
import argparse
from contextlib import closing
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.claim_evidence_experiment import name_key
from src.product_identity_filtered import company_core
from src.product_name_groups import ProductGroups
from src.claim_product_identity import resolve_claim_identity
from scripts.recover_product_candidates import RecoveryIndex
from scripts.export_product_functionality_handoff import FIELDS


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir',type=Path,default=ROOT/'data/processed/product_functionality_handoff_brand_present')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'data/processed/product_functionality_handoff_claim_identity')
    parser.add_argument('--database',type=Path,default=ROOT/'Data_List_Claim_Verification/claim_verification.sqlite')
    args=parser.parse_args()
    base,out=args.base_dir,args.output_dir
    out.mkdir(parents=True,exist_ok=True)
    load=lambda name:json.loads((base/name).read_text(encoding='utf-8'))
    input_file='input_brand_present.json' if (base/'input_brand_present.json').exists() else 'source_input.json'
    rows,records,videos=load('product_matches.json'),load('all_results.json'),load(input_file)
    database=args.database
    database_hash=hashlib.sha256(database.read_bytes()).hexdigest()
    with closing(sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        products=[dict(p) for p in db.execute('SELECT '+','.join(FIELDS)+' FROM products')]
        ingredients=[r[0] for r in db.execute('SELECT ingredient_name FROM ingredients')]
    by_id={p['product_id']:p for p in products}
    pairs={frozenset(company_core(v) for v in pair) for pair in json.loads((ROOT/'configs/manufacturer_pairs.json').read_text(encoding='utf-8'))['pairs']}
    grouping=ProductGroups(products,pairs)
    index=RecoveryIndex(products,ingredients)
    record_map={(r['video_id'],r['product_ref']):r for r in records}
    video_map={v['video_id']:v for v in videos}
    before_selected=sum(r['product']['evi_product'] is not None for r in records)
    previous_named=defaultdict(list)
    for row in rows:
        if name_key(row.get('product_name')):previous_named[(name_key(row['product_name']),name_key(row.get('brand_name')))].append(row)
    previous_selected_named=sum(any(r.get('selected_product') is not None for r in group) for group in previous_named.values())
    changes,audit=[],[]
    for row in rows:
        record=record_map[(row['video_id'],row['product_ref'])]
        if record['product']['evi_product'] is not None:
            continue
        group,observations,reason=resolve_claim_identity(row,video_map[row['video_id']]['claims'],index,grouping)
        item=dict(video_id=row['video_id'],product_ref=row['product_ref'],input_product_name=row.get('product_name'),
            input_brand_name=row.get('brand_name'),reason=reason,observations=observations,
            selected_product_id=group['representative']['product_id'] if group else None)
        audit.append(item)
        record['product']['claim_identity_observations']=observations
        record['product']['claim_identity_resolution']=reason
        if group is None:
            continue
        representative=group['representative']
        source_records=[{k:p[k] for k in FIELDS} for p in group['rows']]
        record['product']['evi_product']={k:representative[k] for k in FIELDS}
        record['product']['match']=dict(status='unresolved',method=None,
            note='Claim 원문에서 식별 정보를 추출해 제품 그룹을 선택함. 제품 동일성은 별도 검토 대상이며 Claim의 참·거짓은 미판정.',
            recovery_method=reason,company_comparison_field='claim_manufacturer_name' if reason=='claim_manufacturer_and_product_name' else 'claim_identity',
            identity_source='same_video_same_product_ref_claims')
        record['product']['group']=dict(group_id=group['group_id'],source_product_ids=[p['product_id'] for p in group['rows']],representative_product_id=representative['product_id'])
        record['product']['group_records']=source_records
        record['product']['main_functionality_sources']=[dict(product_id=p['product_id'],text=p['main_functionality']) for p in group['rows']]
        row['selected_product']={k:representative[k] for k in FIELDS if k!='main_functionality'}
        row['selected_group_id']=group['group_id']
        row['selection_group_reason']=reason
        row['claim_identity_observations']=observations
        item.update(db_product_name=representative['product_name'],db_company_name=representative['company_name'])
        changes.append(item)
    selected=[r for r in records if r['product']['evi_product'] is not None]
    unselected=[r for r in records if r['product']['evi_product'] is None]
    claim_counts=lambda items:Counter(json.dumps([r['video_id'],c],sort_keys=True,ensure_ascii=False) for r in items for c in r.get('claims',[]))
    assert claim_counts(records)==claim_counts(videos)
    assert len(selected)==before_selected+len(changes)
    for r in selected:
        p=r['product']['evi_product']
        assert p=={k:by_id[p['product_id']][k] for k in FIELDS}
    named=defaultdict(list)
    for r in rows:
        if name_key(r.get('product_name')):named[(name_key(r['product_name']),name_key(r.get('brand_name')))].append(r)
    selected_named=sum(any(r.get('selected_product') is not None for r in group) for group in named.values())
    candidate_named=sum(any(r.get('candidates') or r.get('selected_product') for r in group) for group in named.values())
    summary=dict(named_denominator=len(named),previous_selected_named_groups=previous_selected_named,selected_named_groups=selected_named,
        newly_selected_named_groups=selected_named-previous_selected_named,selected_named_rate=round(100*selected_named/len(named),2),
        input_product_entries=len(rows),previous_selected_entries=before_selected,newly_selected_entries=len(changes),
        selected_product_entries=len(selected),remaining_unselected_entries=len(unselected),
        claim_declaration_roles=dict(Counter(o['role'] for a in audit for o in a['observations'] if o['role']!='db_product_name_in_claim')),
        resolution_methods=dict(Counter(c['reason'] for c in changes)),
        selected_claim_count=sum(len(r['claims']) for r in selected),all_claim_count=sum(len(r['claims']) for r in records),
        database_sha256=database_hash,threshold_lowered=False,input_manufacturer_used=False,
        candidate_named_groups=candidate_named,candidate_named_rate=round(100*candidate_named/len(named),2),
        remaining_unmapped_named_groups=len(named)-selected_named,candidate_only_named_groups=candidate_named-selected_named,
        no_candidate_named_groups=len(named)-candidate_named,
        external_api_or_llm_used=False,notes='Only formerly unmapped records rechecked. Claims restricted to same video/product_ref. New selections retain unresolved identity status and full claim provenance. Coverage is not precision; original files/DB unchanged.')
    assert hashlib.sha256(database.read_bytes()).hexdigest()==database_hash
    for filename,value in {'mapped_products.json':selected,'unmapped_products.json':unselected,'all_results.json':records,
        'product_matches.json':rows,'claim_identity_audit.json':audit,'newly_mapped_products.json':[record_map[(r['video_id'],r['product_ref'])] for r in changes],
        'new_matches.json':changes,'summary.json':summary}.items():
        (out/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'source_input.json').write_text(json.dumps(videos,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    print(json.dumps(changes[:6],ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
