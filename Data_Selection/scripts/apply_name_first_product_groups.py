"""Apply user's name-first/report-fallback policy to the latest saved product search."""
from collections import Counter,defaultdict
from contextlib import closing
import copy
import argparse
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.claim_evidence_experiment import name_key
from src.product_identity_filtered import company_core
from src.product_name_groups import ProductGroups
from scripts.export_product_functionality_handoff import FIELDS,build_record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir',type=Path,default=ROOT/'data/processed/product_functionality_handoff_y_final')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'data/processed/product_functionality_handoff_y_final_name_first')
    parser.add_argument('--company-field',choices=['brand_name','manufacturer_name'],default='brand_name')
    parser.add_argument('--database',type=Path,default=ROOT/'Data_List_Claim_Verification/claim_verification.sqlite')
    args=parser.parse_args()
    base,out=args.base_dir,args.output_dir
    rows=json.loads((base/'product_matches.json').read_text(encoding='utf-8'))
    base_summary=json.loads((base/'summary.json').read_text(encoding='utf-8'))
    previous_selected_count=sum(r.get('selected_product') is not None for r in rows)
    videos=json.loads((base/'source_input.json').read_text(encoding='utf-8'))
    by_video={v['video_id']:v for v in videos}
    reports={r.get('previous_match',{}).get('observed_report_number') for r in rows}
    # Existing search is equivalent to the new report policy for this input,
    # because all input report-number fields are empty. Other inputs must rerun
    # map_claim_products.py with its new default name-first policy first.
    if any(reports) and not base_summary.get('report_fallback_only',False):
        raise ValueError('Regenerate name-first candidates before grouping inputs with report numbers')
    with closing(sqlite3.connect(args.database.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        products=[dict(p) for p in db.execute('SELECT '+','.join(FIELDS)+' FROM products')]
        version=db.execute("SELECT loaded_at FROM dataset_registry WHERE dataset_key='products'").fetchone()[0]
    product_rows={p['product_id']:p for p in products}
    pairs={frozenset(company_core(v) for v in pair) for pair in json.loads((ROOT/'configs/manufacturer_pairs.json').read_text(encoding='utf-8'))['pairs']}
    grouping=ProductGroups(products,pairs)
    records,changes=[],[]
    for row in rows:
        previous=copy.deepcopy(row.get('selected_product'))
        same_policy=row.get('comparison_company_field','manufacturer_name')==args.company_field
        row['comparison_company_field']=args.company_field
        if previous is not None and same_policy:
            group=grouping.group(grouping.key(product_rows[previous['product_id']]))
            reason='existing_name_selection_group'
        else:
            group,reason=grouping.select(row,report=row.get('previous_match',{}).get('observed_report_number'))
        row['previous_selected_product']=previous
        row['selection_group_reason']=reason
        if group and reason=='report_number_fallback':
            row['name_candidates_before_report_fallback']=row['candidates']
            row['candidates']=[{k:p[k] for k in FIELDS if k!='main_functionality'} for p in group['rows']]
        row['selected_product']=({k:group['representative'][k] for k in FIELDS if k!='main_functionality'} if group else None)
        if group:
            row['selected_group_id']=group['group_id']
            row['selected_group_product_ids']=[p['product_id'] for p in group['rows']]
        record=build_record(by_video[row['video_id']],row,product_rows,version,pairs)
        if group:
            representative=group['representative']
            if reason=='report_number_fallback':
                record['product']['match']=dict(status='confirmed',method='report_number',note='제품명 경로로 연결되지 않아 입력 신고번호로 보조 연결함.')
            elif row.get('recovery_attempt',{}).get('observations'):
                record['product']['match']=dict(status='unresolved',method=None,note='복원된 제품명 후보의 그룹 연결; 동일 제품 확인 필요',recovery_sources=row['recovery_attempt']['observations'])
            record['product']['match']['company_comparison_field']=args.company_field
            record['product']['group']=dict(group_id=group['group_id'],product_name_key=group['name_key'],manufacturer_key=group['company_key'],
                                           source_product_ids=[p['product_id'] for p in group['rows']],
                                           manufacturing_report_numbers=[p['manufacturing_report_number'] for p in group['rows']],
                                           representative_product_id=representative['product_id'])
            record['product']['group_records']=[{k:p[k] for k in FIELDS} for p in group['rows']]
            record['product']['main_functionality_sources']=[dict(product_id=p['product_id'],text=p['main_functionality']) for p in group['rows']]
            note=record['product']['match'].get('note') or ''
            if len(group['rows'])>1:
                record['product']['match']['note']=(note+'; ' if note else '')+'동일 제품명·제조사 그룹. 신고번호/공장별 원본은 group_records에 보존. evi_product는 대표 DB 행임.'
            if previous is None:
                changes.append(dict(video_id=row['video_id'],product_ref=row['product_ref'],product_name=row['product_name'],group=record['product']['group']))
        records.append(record)
    for video in videos:
        refs={p['product_ref'] for p in video.get('products',[])}
        orphan=[copy.deepcopy(c) for c in video.get('claims',[]) if c.get('product_ref') not in refs]
        if orphan:records.append(dict(video_id=video['video_id'],url=video.get('url'),product_ref=None,db_version=version,
                                      product=dict(match=dict(status='unresolved',method=None,note='입력 제품 참조 없음'),evi_product=None),claims=orphan))
    selected=[r for r in records if r['product']['evi_product']]
    keys=lambda items:Counter(json.dumps([r['video_id'],c],ensure_ascii=False,sort_keys=True) for r in items for c in r.get('claims',[]))
    assert keys(records)==keys(videos)
    for r in selected:
        evi=r['product']['evi_product']
        assert evi=={k:product_rows[evi['product_id']][k] for k in FIELDS}
        assert all(p=={k:product_rows[p['product_id']][k] for k in FIELDS} for p in r['product']['group_records'])
    named=defaultdict(list)
    for r in rows:
        if name_key(r.get('product_name')):named[(name_key(r['product_name']),name_key(r.get('brand_name')))].append(r)
    named_selected=sum(any(r['selected_product'] for r in g) for g in named.values())
    summary=dict(input_file=base_summary.get('input_file'),product_entries=len(rows),candidate_products=sum(bool(r['candidates']) for r in rows),
                 selected_product_entries=len(selected),selected_rate=round(100*len(selected)/len(rows),2),
                 deduplicated_named_input_products=len(named),deduplicated_selected_groups=named_selected,
                 deduplicated_selected_rate=round(100*named_selected/len(named),2),
                 newly_selected_entries=len(changes),previous_selected_entries=previous_selected_count,
                 selected_unique_urls=len({r['url'] for r in selected}),selected_db_groups=len({r['product']['group']['group_id'] for r in selected}),
                 selected_claims=sum(len(r['claims']) for r in selected),all_claims=sum(len(r['claims']) for r in records),
                 report_policy=f'Name/{args.company_field} first; report only as fallback; report differences do not reject a name group.',
                 group_policy='Identical normalized DB product name + factory-stripped manufacturer/approved pair. Source rows retained.',
                 representative_policy='Lowest product_id is a group representative, not identification of a specific report record.',
                 observed_report_number_count=sum(bool(r.get('previous_match',{}).get('observed_report_number')) for r in rows))
    summary['company_comparison_field']=args.company_field
    out.mkdir(parents=True,exist_ok=True)
    for filename,value in {'mapped_products.json':selected,'all_results.json':records,'product_matches.json':rows,'summary.json':summary,'new_group_matches.json':changes}.items():
        (out/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'source_input.json').write_bytes((base/'source_input.json').read_bytes())
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
