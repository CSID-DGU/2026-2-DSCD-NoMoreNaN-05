"""Replay a higher name cutoff using complete >=70 candidates and the same recovery rules."""
import argparse
from collections import defaultdict
from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rapidfuzz.distance import DamerauLevenshtein
from src.claim_evidence_experiment import name_key,GENERIC_PRODUCT_NAMES
from src.product_identity_filtered import FilteredProductCatalog
from scripts.evaluate_relaxed_product_mapping import strip_brand
from scripts.recover_product_candidates import RecoveryIndex


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--threshold',type=float,default=75)
    args=parser.parse_args()
    if not 70<=args.threshold<=100:parser.error('Cached replay supports only thresholds from 70 through 100')
    folder=ROOT/'data/processed/product_functionality_handoff_y_final'
    base=folder/'base70'
    original=json.loads((base/'product_matches.json').read_text(encoding='utf-8'))
    final=json.loads((folder/'product_matches.json').read_text(encoding='utf-8'))
    lookup={(r['video_id'],r['product_ref']):r for r in final}
    videos=json.loads((base/'source_input.json').read_text(encoding='utf-8'))
    by_video={v['video_id']:v for v in videos}
    metadata=json.loads((base/'recovery_cached_metadata.json').read_text(encoding='utf-8'))
    database=ROOT/'Data_List_Claim_Verification/claim_verification.sqlite'
    catalog=FilteredProductCatalog(database)
    with closing(sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        ingredients=[r[0] for r in db.execute('SELECT ingredient_name FROM ingredients')]
    ingredients += [re.sub(r'\([^()]*\)','',n) for n in ingredients]
    ingredients += [term for v in videos for c in v.get('claims',[]) for term in c.get('ingredients',[]) or [] if isinstance(term,str)]
    recovery=RecoveryIndex(catalog.products,ingredients)
    out=[]
    from urllib.parse import urlparse,parse_qs
    for row in original:
        current=lookup[(row['video_id'],row['product_ref'])]
        candidates=current['candidates']
        route=current['route']
        if route.startswith('full_name_distance_') and row['candidates']:
            raw,brand=row.get('product_name') or '',row.get('brand_name') or ''
            variants={name_key(raw),name_key(strip_brand(raw,brand))}
            if brand and name_key(brand) not in name_key(raw):variants.add(name_key(brand+' '+raw))
            variants={v for v in variants if v and v not in GENERIC_PRODUCT_NAMES}
            scored=[(p,max((100*DamerauLevenshtein.normalized_similarity(v,name_key(p['product_name'])) for v in variants),default=0)) for p in row['candidates']]
            assert any(score>=70 for _,score in scored)
            candidates=[p for p,score in scored if score>=args.threshold]
            route='full_name_distance_'+str(args.threshold)
            if not candidates:
                external_id=parse_qs(urlparse(row.get('url') or '').query).get('v',[''])[0]
                candidates,route,_=recovery.search(row,by_video[row['video_id']],metadata.get(external_id,{}))
        out.append(dict(video_id=row['video_id'],product_ref=row['product_ref'],product_name=row.get('product_name'),brand_name=row.get('brand_name'),
                        had_candidate_70=bool(current['candidates']),has_candidate=bool(candidates),route=route,candidate_count=len(candidates)))
    groups=defaultdict(list)
    for r in out:
        if name_key(r.get('product_name')):groups[(name_key(r['product_name']),name_key(r.get('brand_name')))].append(r)
    named=sum(any(r['has_candidate'] for r in g) for g in groups.values())
    previous=sum(any(r['had_candidate_70'] for r in g) for g in groups.values())
    entries=sum(r['has_candidate'] for r in out)
    summary=dict(threshold=args.threshold,named_input_groups=len(groups),candidate_named_groups=named,
                 deduplicated_candidate_rate=round(100*named/len(groups),2),previous_candidate_named_groups_70=previous,
                 total_product_entries=len(out),candidate_product_entries=entries,
                 entry_candidate_rate=round(100*entries/len(out),2),
                 lost_named_groups=sum(any(r['had_candidate_70'] for r in g) and not any(r['has_candidate'] for r in g) for g in groups.values()),
                 mapping_outputs_changed=False,selection_recomputed=False,
                 method='Complete >=70 distance candidate cache filtered at higher cutoff; unchanged strong routes; full recovery retried when distance candidates disappear.')
    destination=ROOT/'data/processed/product_functionality_handoff_y_final_name_first'
    (destination/f'candidate_coverage_t{args.threshold:g}.json').write_text(json.dumps(dict(summary=summary,products=out),ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
