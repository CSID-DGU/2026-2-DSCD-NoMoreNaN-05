"""Compare a complete official refresh with the existing read-only SQLite DB."""
from collections import Counter
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.collectors.mfds_products import FIELDS,write_json
from src.claim_evidence_experiment import name_key
from src.product_identity_filtered import ApprovedPairProductCatalog,company_core
from src.product_name_groups import ProductGroups
from scripts.evaluate_relaxed_product_mapping import search


def main():
    folder=ROOT/'data/processed/external_product_enrichment_20261102'
    status=json.loads((folder/'domestic_collection_status.json').read_text(encoding='utf-8'))
    if status['status']!='complete':raise ValueError('Collection not complete')
    latest=json.loads((folder/'domestic_latest_products.json').read_text(encoding='utf-8'))
    source=ROOT/'Data_List_Claim_Verification/claim_verification.sqlite'
    before_hash=hashlib.sha256(source.read_bytes()).hexdigest()
    with closing(sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        old=[dict(r) for r in db.execute('SELECT * FROM products')]
    old_by_report={p['manufacturing_report_number']:p for p in old}
    new_by_report={p['manufacturing_report_number']:p for p in latest}
    added=[p for report,p in new_by_report.items() if report not in old_by_report]
    absent=[p for report,p in old_by_report.items() if report not in new_by_report]
    updates=[]
    for report,p in new_by_report.items():
        if report not in old_by_report:continue
        changes={field:dict(before=old_by_report[report].get(field),after=p.get(field))
                 for field in FIELDS.values() if old_by_report[report].get(field)!=p.get(field)}
        if changes:updates.append(dict(manufacturing_report_number=report,product_id=old_by_report[report]['product_id'],changes=changes))
    for filename,value in {'domestic_added_products.json':added,'domestic_changed_products.json':updates,
                           'domestic_not_returned_historical_products.json':absent}.items():write_json(folder/filename,value)
    # Keep the original historical snapshot, and only append newly discovered reports.
    # Existing-name/company changes require review; do not silently rewrite old ads.
    enriched=folder/'claim_verification_enriched.sqlite'
    if enriched.exists():raise ValueError('Enriched database already exists; inspect existing run')
    with closing(sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True)) as src,closing(sqlite3.connect(enriched)) as dst:
        src.backup(dst)
        columns=list(FIELDS.values())+['product_name_normalized']
        for p in added:
            values={**p,'product_name_normalized':name_key(p['product_name'])}
            dst.execute('INSERT INTO products ('+','.join(columns)+') VALUES ('+','.join('?' for _ in columns)+')',[values[k] for k in columns])
        dst.commit()
    catalog=ApprovedPairProductCatalog(enriched,ROOT/'configs/manufacturer_pairs.json')
    choices=[name_key(p['product_name']) for p in catalog.products]
    pairs={frozenset(company_core(v) for v in pair) for pair in json.loads((ROOT/'configs/manufacturer_pairs.json').read_text(encoding='utf-8'))['pairs']}
    grouping=ProductGroups(catalog.products,pairs)
    cases=json.loads((ROOT/'data/processed/product_functionality_handoff_brand_present/unmatched_named_cases.json').read_text(encoding='utf-8'))
    result=[]
    for index,case in enumerate(cases):
        product=dict(product_name=case['product_name'],brand_name=case['brand_name'])
        candidates,route,score=search(catalog,product,dict(status='unmatched'),choices,threshold=70,brand_recombine=True,report_fallback_only=True)
        # Preserve previously recovered metadata/OCR candidates, since this step adds data only.
        combined={c['product_id']:c for c in case['candidates']}
        for c in candidates:combined[c['product_id']]=c
        audit=dict(product_name=case['product_name'],brand_name=case['brand_name'],comparison_company_field='brand_name',candidates=list(combined.values()))
        selected,reason=grouping.select(audit)
        new_candidates=[p for p in combined.values() if p['manufacturing_report_number'] not in old_by_report]
        result.append(dict(input_product_name=case['product_name'],input_brand_name=case['brand_name'],previous_reason=case['reason'],
                           new_candidates=new_candidates,selected_product=selected['representative'] if selected else None,
                           selection_reason=reason,search_route=route,top_name_score=score))
        if (index+1)%40==0:print('Domestic matching',index+1,len(cases),flush=True)
    write_json(folder/'domestic_unmatched_recheck.json',result)
    selected=sum(bool(r['selected_product']) for r in result)
    no_candidates_before=sum(c['reason']=='no_candidates' for c in cases)
    recovered_candidate_groups=sum(c['previous_reason']=='no_candidates' and bool(c['new_candidates']) for c in result)
    summary=dict(original_db_count=len(old),official_latest_count=len(latest),added_report_count=len(added),changed_report_count=len(updates),
        historical_reports_not_in_latest=len(absent),merged_count=len(old)+len(added),original_db_sha256=before_hash,
        rechecked_named_groups=len(cases),groups_with_new_candidates=sum(bool(r['new_candidates']) for r in result),
        newly_selected_groups=selected,previous_selected_groups=317,named_denominator=501,
        selected_groups_after=317+selected,selected_rate_after=round(100*(317+selected)/501,2),
        previous_candidate_groups=429,candidate_groups_after=429+recovered_candidate_groups,
        candidate_rate_after=round(100*(429+recovered_candidate_groups)/501,2),
        policy='Append newly discovered report numbers only in a separate database. Historical rows retained; changed existing fields exported for review. Brand vs company, threshold 70 unchanged.',
        import_status='Deferred by user after API returned HTTP 403',original_db_unchanged=before_hash==hashlib.sha256(source.read_bytes()).hexdigest())
    assert summary['original_db_unchanged']
    write_json(folder/'summary.json',summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
