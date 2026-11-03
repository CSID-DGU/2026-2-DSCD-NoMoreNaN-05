"""Read-only audit of the five feedback items; never rewrites DB or handoff."""
from collections import Counter,defaultdict
from contextlib import closing
from datetime import datetime,timezone
import csv
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.claim_evidence_experiment import name_key
from src.product_identity_filtered import company_core
from src.claim_product_identity import declarations
from src.md_db_enrichment import material_key


def compact(value):return re.sub(r'\s+','',str(value or ''))


def main():
    folder=ROOT/'exports/claim_type_db_20261103'
    target=folder/'claims_with_db.json'
    before=hashlib.sha256(target.read_bytes()).hexdigest()
    videos=json.loads(target.read_text(encoding='utf-8'))
    audit_dir=ROOT/'data/processed/md_enrichment_20261103/mapping_claim_identity'
    rows=json.loads((audit_dir/'product_matches.json').read_text(encoding='utf-8'))
    audits={(r['video_id'],r['product_ref']):r for r in rows}
    base=Path.home()/'Desktop'/'TRUEAD_DB_보강자료'
    with closing(sqlite3.connect((base/'claim_verification.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        identity=[dict(r) for r in db.execute('SELECT product_id,product_name,company_name,manufacturing_report_number FROM products')]
        names=defaultdict(list)
        for r in identity:names[name_key(r['product_name'])].append(r)
    confirmed=[];missing_maker=[];maker_mismatch=[];unresolved_one=[];zero_unresolved=[];unresolved_claims=0
    for video in videos:
        for product in video['products']:
            key=(video['video_id'],product['product_ref']);audit=audits[key]
            observations=declarations(video['claims'],product['product_ref'])
            maker=product.get('manufacturer_name')
            item=dict(video_id=video['video_id'],product_ref=product['product_ref'],input_product_name=product.get('product_name'),brand_name=product.get('brand_name'),
                manufacturer_name=maker,match=product['match'],linked_report=product.get('manufacturing_report_number'),
                actual_candidate_count=len(audit.get('candidates',[])),selected_product=audit.get('selected_product'),
                selection_reason=audit.get('selection_group_reason'),search_route=audit.get('route'),
                previous_match=audit.get('previous_match'),claim_identity_observations=observations)
            if product['match']['status']=='confirmed':
                confirmed.append((video,product,item))
                if not maker or not maker.strip():missing_maker.append(item)
                elif company_core(maker)!=company_core(product['match']['matched_company']):maker_mismatch.append(item)
            if product['match']['status']=='unresolved':
                unresolved_claims+=sum(c.get('product_ref')==product['product_ref'] for c in video['claims'])
                if product['match']['candidates']==1 and maker:
                    candidates=audit.get('candidates',[])
                    item['candidate_rows']=candidates
                    item['rows_matching_input_manufacturer']=[c for c in candidates if company_core(c['company_name'])==company_core(maker)]
                    unresolved_one.append(item)
                if product['match']['candidates']==0:zero_unresolved.append(item)
    reports={p['manufacturing_report_number'] for _,p,_ in confirmed}
    data_file=base/'data_collection/data.csv'
    reference={};total=0
    with data_file.open(encoding='utf-8-sig',newline='') as stream:
        for row in csv.DictReader(stream):
            total+=1
            if row['STTEMNT_NO'] in reports:reference[row['STTEMNT_NO']]=row
    diffs=defaultdict(list)
    for video,product,item in confirmed:
        report=product['manufacturing_report_number'];ref=reference.get(report)
        if ref is None:raise ValueError('Confirmed report missing from data.csv')
        for field,kind in [('INTAKE_HINT1','EFFECT'),('MAIN_FNCTN','EFFECT'),('BASE_STANDARD','QUANTITY')]:
            actual=product['DB'][kind][field]
            if compact(actual)!=compact(ref[field]):diffs[field].append(dict(video_id=video['video_id'],product_ref=product['product_ref'],report=report,name=product['match']['matched_name'],JSON=actual,data_csv=ref[field]))
        actual=product['DB']['CERTIFICATION']['RAWMTRL_CLASS_INFO'];expected=json.loads(ref['RAWMTRL_CLASS_INFO'] or '[]')
        canon=lambda row:json.dumps({k:compact(v) for k,v in row.items()},ensure_ascii=False,sort_keys=True)
        a,b={canon(x) for x in actual},{canon(x) for x in expected}
        if a!=b:
            diffs['RAWMTRL_CLASS_INFO'].append(dict(video_id=video['video_id'],product_ref=product['product_ref'],report=report,name=product['match']['matched_name'],
                JSON=actual,data_csv=expected,only_JSON=[json.loads(x) for x in sorted(a-b)],only_data_csv=[json.loads(x) for x in sorted(b-a)]))
    mismatch_names=sorted({x['input_product_name'] for x in maker_mismatch})
    # Export all same-name alternatives for exact factory/source-row inspection.
    alternatives=[]
    with closing(sqlite3.connect((base/'claim_verification.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        for name in mismatch_names:
            matches=names.get(name_key(name),[])
            alternatives.append(dict(product_name=name,rows=[dict(db.execute('select product_id,product_name,company_name,manufacturing_report_number,main_functionality from products where product_id=?',(r['product_id'],)).fetchone()) for r in matches]))
    summary=dict(confirmed=len(confirmed),confirmed_input_manufacturer_missing=len(missing_maker),confirmed_input_manufacturer_mismatch=len(maker_mismatch),
        mismatch_distinct_input_names=len(mismatch_names),mismatch_input_names=mismatch_names,
        missing_maker_comparison_sources=dict(Counter(x['brand_name'] for x in missing_maker)),
        unresolved_one_candidate_with_manufacturer=len(unresolved_one),unresolved_one_matching_input_manufacturer=sum(bool(x['rows_matching_input_manufacturer']) for x in unresolved_one),
        unresolved_claim_count=unresolved_claims,
        unresolved_zero_exported_candidates=len(zero_unresolved),zero_count_but_actual_candidates=sum(x['actual_candidate_count']>0 for x in zero_unresolved),
        zero_count_with_selected_product=sum(x['selected_product'] is not None for x in zero_unresolved),
        difference_counts={k:len(v) for k,v in diffs.items()},data_csv_rows=total,
        data_csv_modified_at=datetime.fromtimestamp(data_file.stat().st_mtime,timezone.utc).isoformat(),
        output_sha256=before,files_modified=False)
    out=ROOT/'data/processed/claim_json_feedback_audit';out.mkdir(exist_ok=True)
    for name,value in {'summary.json':summary,'confirmed_manufacturer_mismatch.json':maker_mismatch,'confirmed_missing_manufacturer.json':missing_maker,
        'unresolved_one_candidate_with_manufacturer.json':unresolved_one,'unresolved_zero_candidates.json':zero_unresolved,
        'reference_value_differences.json':dict(diffs),'same_name_alternative_functionality.json':alternatives}.items():
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    assert hashlib.sha256(target.read_bytes()).hexdigest()==before
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print('FIELD_DIFFERENCE_EXAMPLES')
    for field,items in diffs.items():
        item=items[0]
        if field=='RAWMTRL_CLASS_INFO':item={k:v for k,v in item.items() if k not in {'JSON','data_csv'}}
        print(json.dumps(dict(field=field,example=item),ensure_ascii=False)[:2200])


if __name__=='__main__':main()
