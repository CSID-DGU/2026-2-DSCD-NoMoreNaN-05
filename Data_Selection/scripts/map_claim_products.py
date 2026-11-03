"""Map any video/claims JSON using the established rules and export functionality.

No API calls, embedding, reranking, or ingredient retrieval are performed.
"""
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
from src.claim_evidence_experiment import identity_observations, name_key
from src.product_identity_filtered import ApprovedPairProductCatalog, company_core
from scripts.evaluate_relaxed_product_mapping import search, strip_brand
from scripts.disambiguate_product_candidates import resolve_multiple
from scripts.export_product_functionality_handoff import build_record, FIELDS


def identity_cache_key(product):
    return json.dumps(dict(name=product.get('product_name'),brand=product.get('brand_name'),manufacturer=product.get('manufacturer_name'),
                           report=product.get('manufacturing_report_number'),
                           conflict=product.get('identity_observation_conflicts',False),
                           observations=sorted({o['value'] for o in product.get('identity_observations',[]) if o.get('value')})),
                      sort_keys=True,ensure_ascii=False)


def map_video(video,catalog,choices,pairs,product_rows,version,cache,threshold=80,brand_recombine=False,report_fallback_only=False,company_field='manufacturer_name'):
    refs=[p.get('product_ref') for p in video.get('products',[])]
    if None in refs or len(refs)!=len(set(refs)):
        raise ValueError('Product references must be non-null and unique within video '+str(video.get('video_id')))
    claims_by_ref=Counter(c.get('product_ref') for c in video.get('claims',[]))
    audit,records=[],[]
    for original in video.get('products',[]):
        if company_field=='brand_name':
            product=copy.deepcopy(original)
            product['identity_observations']=[dict(field='brand_name',value=product['brand_name'],claim_id=None)] if product.get('brand_name') else []
            product['identity_observation_conflicts']=False
        else:
            product=identity_observations(video,original)
        key=f'{threshold:g}:{brand_recombine}:{report_fallback_only}:{company_field}:'+identity_cache_key(product)
        if key not in cache:
            name_product=dict(product)
            name_product['manufacturer_name']=product.get(company_field)
            if report_fallback_only:name_product['manufacturing_report_number']=None
            previous=catalog.identify(name_product)
            candidates,route,score=search(catalog,product,previous,choices,threshold=threshold,brand_recombine=brand_recombine,report_fallback_only=report_fallback_only)
            if report_fallback_only:
                previous=dict(previous,observed_report_number=product.get('manufacturing_report_number'),report_policy='fallback_only')
            previous=dict(previous,company_comparison_field=company_field,observed_company_value=product.get(company_field))
            if company_field=='brand_name':previous['observed_manufacturer']=product.get('manufacturer_name')
            cache[key]=(previous,candidates,route,score)
        previous,candidates,route,score=cache[key]
        row=dict(video_id=video['video_id'],url=video.get('url'),product_ref=product['product_ref'],
                 product_name=product.get('product_name'),brand_name=product.get('brand_name'),
                 brand_removed_name=strip_brand(product.get('product_name'),product.get('brand_name')),
                 manufacturer_name=product.get('manufacturer_name'),previous_match=previous,
                 comparison_company_field=company_field,
                 identity_observations=product.get('identity_observations',[]),
                 status='no_candidates' if not candidates else 'single_candidate' if len(candidates)==1 else 'multiple_candidates',
                 route=route,top_name_score=score,claim_count=claims_by_ref[product['product_ref']],
                 candidates=candidates,candidate_count=len(candidates),original_candidate_count=len(candidates),
                 selected_product=None)
        if len(candidates)==1:
            row.update(selection_status='single_search_candidate',selected_product=candidates[0])
        elif candidates:
            narrowed,reason=resolve_multiple(row,pairs)
            row.update(manufacturer_resolution=reason,manufacturer_filtered_candidates=narrowed,
                       selection_status=('selected_by_brand' if company_field=='brand_name' else 'selected_by_manufacturer') if len(narrowed)==1 else 'unresolved_multiple',
                       selected_product=narrowed[0] if len(narrowed)==1 else None)
        else:
            row['selection_status']='not_found'
        audit.append(row)
        records.append(build_record(video,row,product_rows,version,pairs))
    unassigned=[copy.deepcopy(c) for c in video.get('claims',[]) if c.get('product_ref') not in set(refs)]
    if unassigned:
        records.append(dict(video_id=video['video_id'],url=video.get('url'),product_ref=None,db_version=version,
                            product=dict(match=dict(status='unresolved',method=None,note='Claim의 product_ref에 대응하는 입력 제품 정보 없음'),evi_product=None),
                            claims=unassigned))
    return audit,records


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--database',type=Path,default=ROOT/'Data_List_Claim_Verification/claim_verification.sqlite')
    parser.add_argument('--pairs',type=Path,default=ROOT/'configs/manufacturer_pairs.json')
    parser.add_argument('--threshold',type=float,default=80,help='Full-name candidate similarity threshold (0 < value <= 100)')
    parser.add_argument('--brand-recombine',action='store_true',help='Also search the observed brand + product name')
    parser.add_argument('--strict-report-match',action='store_true',help='Legacy policy: require known report number to agree with name candidates')
    parser.add_argument('--company-field',choices=['brand_name','manufacturer_name'],default='brand_name',help='Input field to compare with DB company_name; defaults to brand_name')
    args=parser.parse_args()
    if not 0 < args.threshold <= 100:
        parser.error('--threshold must be above 0 and at most 100')
    raw=args.input.read_bytes()
    videos=json.loads(raw.decode('utf-8-sig'))
    if not isinstance(videos,list) or any(not isinstance(v,dict) for v in videos):
        raise ValueError('Input must be a list of video objects')
    ids=[v.get('video_id') for v in videos]
    if None in ids or len(ids)!=len(set(ids)):
        raise ValueError('video_id must be present and unique')
    digest=hashlib.sha256(raw).hexdigest()
    summary_path=args.output_dir/'summary.json'
    if summary_path.exists():
        previous_summary=json.loads(summary_path.read_text(encoding='utf-8'))
        if previous_summary['input_sha256']!=digest or previous_summary.get('name_similarity_threshold',80)!=args.threshold or previous_summary.get('brand_recombine',False)!=args.brand_recombine or previous_summary.get('report_fallback_only',False)!=(not args.strict_report_match) or previous_summary.get('company_comparison_field','manufacturer_name')!=args.company_field:
            raise ValueError('Output belongs to a different input or threshold; use a new output directory')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    catalog=ApprovedPairProductCatalog(args.database,args.pairs)
    choices=[name_key(r['product_name']) for r in catalog.products]
    pairs={frozenset(company_core(v) for v in p) for p in json.loads(args.pairs.read_text(encoding='utf-8'))['pairs']}
    with closing(sqlite3.connect(args.database.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        product_rows={r['product_id']:dict(r) for r in db.execute('SELECT '+','.join(FIELDS)+' FROM products')}
        version=db.execute("SELECT loaded_at FROM dataset_registry WHERE dataset_key='products'").fetchone()[0]
    cache,audit,records={},[],[]
    for index,video in enumerate(videos,1):
        rows,export=map_video(video,catalog,choices,pairs,product_rows,version,cache,threshold=args.threshold,brand_recombine=args.brand_recombine,report_fallback_only=not args.strict_report_match,company_field=args.company_field)
        audit.extend(rows)
        records.extend(export)
        if index%25==0 or index==len(videos):
            print(json.dumps(dict(videos_processed=index,total_videos=len(videos),products_processed=len(audit)),ensure_ascii=False),flush=True)
    selected=[r for r in records if r['product']['evi_product'] is not None]
    confirmed=[r for r in selected if r['product']['match']['status']=='confirmed']
    def claim_keys(items):
        return Counter(json.dumps([r['video_id'],c],sort_keys=True,ensure_ascii=False) for r in items for c in r.get('claims',[]))
    if claim_keys(videos)!=claim_keys(records):
        raise AssertionError('Claims changed, lost or duplicated')
    for record in records:
        evi=record['product']['evi_product']
        if evi and evi!={k:product_rows[evi['product_id']][k] for k in FIELDS}:
            raise AssertionError('Export differs from original DB row')
    status_counts=Counter(r['status'] for r in audit)
    connected=sum(bool(r['candidates']) for r in audit)
    summary=dict(input_file=args.input.name,input_sha256=digest,db_version=version,
                 name_similarity_threshold=args.threshold,
                 brand_recombine=args.brand_recombine,
                 report_fallback_only=not args.strict_report_match,
                 company_comparison_field=args.company_field,
                 database_sha256=hashlib.sha256(args.database.read_bytes()).hexdigest(),
                 rules_config_sha256=hashlib.sha256(args.pairs.read_bytes()).hexdigest(),
                 input_video_count=len(videos),input_claim_count=sum(len(v.get('claims',[])) for v in videos),
                 product_entry_count=len(audit),candidate_connected_products=connected,
                 candidate_connection_rate=round(100*connected/len(audit),2) if audit else 0,
                 original_candidate_statuses=dict(status_counts),selected_product_records=len(selected),
                 single_selection_rate=round(100*len(selected)/len(audit),2) if audit else 0,
                 resolved_from_multiple=sum(r['selection_status'] in ('selected_by_manufacturer','selected_by_brand') for r in audit),
                 unresolved_multiple=sum(r['selection_status']=='unresolved_multiple' for r in audit),
                 selected_record_statuses=dict(Counter(r['product']['match']['status'] for r in selected)),
                 selected_claims=sum(len(r['claims']) for r in selected),confirmed_records=len(confirmed),
                 all_records=len(records),all_claims=sum(len(r['claims']) for r in records),
                 unassigned_claims=sum(len(r['claims']) for r in records if r['product_ref'] is None),
                 accuracy='Not measured; candidate coverage and single selection rate are not precision.',
                 evidence_retrieval_executed=False,ranking_executed=False)
    for filename,value in {'mapped_products.json':selected,'confirmed_products.json':confirmed,
                           'all_results.json':records,'product_matches.json':audit,'summary.json':summary}.items():
        (args.output_dir/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    (args.output_dir/'source_input.json').write_bytes(raw)
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    main()
