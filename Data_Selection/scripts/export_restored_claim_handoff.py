"""Restore the agreed claim_type_db_format.md schema, without v2 fields.

Reuse the saved 70-point search; resolve companies before deciding status.
Only actual report-number or name/company agreement uses the corresponding
agreed method. No blanket unresolved for recovered matches; no arbitrary
promotion of competing candidates. Diagnostics stay outside the handoff JSON.
"""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.claim_type_db_format import build_product, TYPE_FIELDS, ARRAYS
from src.claim_product_identity import declarations
from src.claim_evidence_experiment import name_key
from src.product_identity_filtered import company_core
from src.product_name_groups import ProductGroups
from scripts.export_candidate_db_handoff import source_ids


def select_product(original,row,claims,grouping):
    ids=source_ids(row)
    keys={grouping.key(grouping.products[pid]) for pid in ids}
    maker=original.get('manufacturer_name')
    # Only explicit declarations, and only names present among retrieved companies.
    observed=declarations(claims,original['product_ref'])
    matching_claim_makers={grouping.company(o['value']) for o in observed
        if o['role']=='manufacturer_name' and any(grouping.company(o['value'])==k[1] for k in keys)}
    source=None;companies=set()
    if maker:
        source='manufacturer_name';companies={grouping.company(maker)}
        if matching_claim_makers and companies!=matching_claim_makers:
            return None,None,'input_and_claim_manufacturer_conflict',ids,source
    elif matching_claim_makers:
        source='same_product_claim_manufacturer';companies=matching_claim_makers
    elif original.get('brand_name'):
        source='brand_name';companies={grouping.company(original['brand_name'])}
    if len(companies)>1:
        return None,None,'multiple_declared_manufacturers',ids,source
    matching=[k for k in keys if k[1] in companies]
    if len(matching)==1:
        group=grouping.group(matching[0])
        rows=group['rows']
        # Prefer the observed legal manufacturer/factory when available.
        if maker:
            from src.claim_evidence_experiment import company_key
            exact_site=[p for p in rows if company_key(p['company_name'])==company_key(maker)]
            exact_legal=[p for p in rows if company_core(p['company_name'])==company_core(maker)]
            rows=exact_site or exact_legal or rows
        report=name_key(original.get('manufacturing_report_number'))
        preferred=[p for p in rows if report and name_key(p['manufacturing_report_number'])==report]
        chosen=min(preferred or rows,key=lambda p:p['product_id'])
        return chosen,'name_and_company','unique_name_company_group',ids,source
    # The agreed report policy is fallback, not a veto against a name/company match.
    report=name_key(original.get('manufacturing_report_number'))
    reported=grouping.reports.get(report,[]) if report else []
    report_groups={grouping.key(p) for p in reported}
    if len(report_groups)==1:
        if maker and any(grouping.company(p['company_name'])!=grouping.company(maker) for p in reported):
            return None,None,'report_and_manufacturer_conflict',ids,source
        chosen=min(reported,key=lambda p:p['product_id'])
        return chosen,'report_number','report_number_fallback',sorted(set(ids)|{p['product_id'] for p in reported}),source
    if not ids:return None,None,'no_candidates',ids,source
    if len(matching)>1:return None,None,'multiple_name_company_groups',ids,source
    if maker:return None,None,'manufacturer_conflict',ids,source
    if len(keys)==1:return None,None,'name_only_company_not_verified',ids,source
    return None,None,'no_unique_company_matching_group',ids,source


def validate(videos,originals):
    assert len(videos)==len(originals)
    for video,original in zip(videos,originals):
        assert set(video)=={'video_id','url','db_version','products','claims'}
        assert video['claims']==[c for c in original['claims'] if c.get('claim_type')!='ETC']
        for before,product in zip(original['products'],video['products']):
            assert set(product)==set(before)|{'match','DB'}
            assert set(product['match'])=={'status','method','candidates','matched_name','matched_company'}
            match=product['match'];db=product['DB']
            assert match['status'] in {'confirmed','unresolved','not_found'}
            if match['status']=='confirmed':
                assert match['method'] in {'name_and_company','report_number'}
                assert db is not None and set(db)==set(TYPE_FIELDS)
                for typ,fields in TYPE_FIELDS.items():
                    assert list(db[typ])==fields
                    assert all(isinstance(db[typ][field],list if field in ARRAYS else str) for field in fields)
            else:
                assert db is None and match['method'] is None
                assert match['matched_name'] is None and match['matched_company'] is None
                assert match['status']!='not_found' or match['candidates']==0
            for field in before:
                if field!='manufacturing_report_number' or match['status']!='confirmed':
                    assert product[field]==before[field]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=ROOT/'data/processed/product_functionality_handoff_y_final_brand_company/source_input.json')
    parser.add_argument('--mapping-dir',type=Path,default=ROOT/'data/processed/md_enrichment_20261103/mapping_claim_identity')
    parser.add_argument('--database',type=Path,default=ROOT/'TRUEAD_DB_보강자료/claim_verification.sqlite')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'exports/claim_type_db_restored_20261104')
    args=parser.parse_args()
    raw=args.input.read_bytes();originals=json.loads(raw.decode('utf-8-sig'))
    dbhash=hashlib.sha256(args.database.read_bytes()).hexdigest()
    audit=json.loads((args.mapping_dir/'product_matches.json').read_text(encoding='utf-8'))
    audits={(r['video_id'],r['product_ref']):r for r in audit}
    pairs={frozenset(company_core(x) for x in p) for p in
        json.loads((ROOT/'configs/manufacturer_pairs.json').read_text(encoding='utf-8'))['pairs']}
    with sqlite3.connect(args.database.resolve().as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        identity=[dict(r) for r in db.execute('SELECT product_id,product_name,company_name,manufacturing_report_number FROM products')]
        grouping=ProductGroups(identity,pairs)
        result=[];detail=[];status_counts=Counter();claim_counts=Counter();reason_counts=Counter()
        for video in originals:
            item=dict(video_id=video['video_id'],url=video.get('url'),db_version='2026-11-03T04:09:56.363154+00:00',
                      products=[],claims=[copy.deepcopy(c) for c in video['claims'] if c.get('claim_type')!='ETC'])
            for original in video['products']:
                row=audits[(video['video_id'],original['product_ref'])]
                selected,method,reason,ids,source=select_product(original,row,video['claims'],grouping)
                status='confirmed' if selected else 'unresolved' if ids else 'not_found'
                record=dict(db.execute('SELECT * FROM products WHERE product_id=?',(selected['product_id'],)).fetchone()) if selected else None
                mapping=dict(product=dict(match=dict(status=status,method=method)))
                product=build_product(original,mapping,record,len(ids))
                item['products'].append(product);status_counts[status]+=1;reason_counts[reason]+=1
                detail.append(dict(video_id=video['video_id'],product_ref=original['product_ref'],
                    product_name=original.get('product_name'),manufacturer_name=original.get('manufacturer_name'),
                    brand_name=original.get('brand_name'),company_source=source,status=status,reason=reason,
                    selected_product_id=selected['product_id'] if selected else None,
                    candidate_ids=ids,
                    original_selected_product_id=row.get('selected_product',{}).get('product_id') if row.get('selected_product') else None))
            refs={p['product_ref']:p for p in item['products']}
            for claim in item['claims']:
                p=refs.get(claim.get('product_ref'))
                claim_counts[p['match']['status'] if p else 'invalid_product_ref']+=1
            result.append(item)
    validate(result,originals)
    assert args.input.read_bytes()==raw
    assert hashlib.sha256(args.database.read_bytes()).hexdigest()==dbhash
    args.output_dir.mkdir(parents=True,exist_ok=True)
    output=args.output_dir/'claims_with_db.json'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    assert json.loads(output.read_text(encoding='utf-8'))==result
    named=defaultdict(list)
    for video in result:
        for p in video['products']:
            if p.get('product_name') and p.get('brand_name'):
                named[(name_key(p['product_name']),name_key(p['brand_name']))].append(p)
    confirmed_named=sum(any(p['match']['status']=='confirmed' for p in ps) for ps in named.values())
    summary=dict(videos=len(result),products=sum(len(v['products']) for v in result),claims=sum(len(v['claims']) for v in result),
        excluded_etc=sum(c.get('claim_type')=='ETC' for v in originals for c in v['claims']),
        product_statuses=dict(status_counts),claims_by_product_status=dict(claim_counts),resolution_reasons=dict(reason_counts),
        deduplicated_brand_present_products=len(named),confirmed_brand_present_products=confirmed_named,
        confirmed_brand_present_rate=round(100*confirmed_named/len(named),2),
        confirmed_claim_percentage=round(100*claim_counts['confirmed']/sum(claim_counts.values()),2),
        schema='Original claim_type_db_format.md; no matched/candidate_products/preferred_product_id/schema_version',
        mapping_policy='Saved 70-point candidate search; manufacturer then explicit claim manufacturer then brand; unique company group; report fallback. Name-only without company agreement is unresolved pending user decision.',
        input_sha256=hashlib.sha256(raw).hexdigest(),database_sha256=dbhash,
        output_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),original_files_changed=False,
        actual_A_B_runtime_tested=False)
    for name,value in [('summary.json',summary),('product_resolution_audit.json',detail)]:
        (args.output_dir/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    with zipfile.ZipFile(args.output_dir/'handoff.zip','w',zipfile.ZIP_DEFLATED) as archive:
        archive.write(output,'claims_with_db.json')
        archive.write(args.output_dir/'summary.json','summary.json')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
