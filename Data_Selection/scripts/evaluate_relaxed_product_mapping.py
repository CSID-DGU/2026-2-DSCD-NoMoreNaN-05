"""Product-level candidate coverage with explicitly relaxed identity requirements."""
from collections import Counter
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rapidfuzz import process
from rapidfuzz.distance import DamerauLevenshtein
from src.claim_evidence_experiment import GENERIC_PRODUCT_NAMES, name_key
from src.product_identity_filtered import FilteredProductCatalog, company_core


def strip_brand(name, brand):
    text = unicodedata.normalize('NFC', name or '').strip()
    brand = unicodedata.normalize('NFC', brand or '').strip()
    if not brand:
        return text
    text = re.sub(r'^'+re.escape(brand)+r'(?=\s|$)\s*', '', text, flags=re.I)
    return re.sub(r'\s+'+re.escape(brand)+r'$', '', text, flags=re.I).strip()


def search(catalog, product, previous, name_choices):
    raw = product.get('product_name') or ''
    variants = [('exact_name', name_key(raw))]
    stripped = name_key(strip_brand(raw, product.get('brand_name')))
    if stripped and stripped != variants[0][1]:
        variants.append(('brand_removed_exact_name', stripped))
    report = name_key(product.get('manufacturing_report_number'))
    for route,key in variants:
        if not key or key in GENERIC_PRODUCT_NAMES:
            continue
        rows = catalog.names.get(key, [])
        if rows:
            rows = [r for r in rows if not report or name_key(r['manufacturing_report_number']) == report]
            return rows,route,100.0  # A known report conflict stops fallback.
    if previous['status'] == 'matched':
        return [next(r for r in catalog.products if r['product_id']==previous['product_id'])], 'previous_identity_match', previous.get('name_score')
    # Score full names, including a separately labeled brand-stripped variant.
    # This is candidate search only: manufacturer is not an exclusion criterion.
    found = {}
    for route,key in variants:
        if not key or key in GENERIC_PRODUCT_NAMES:
            continue
        for _,score,index in process.extract(key,name_choices,scorer=DamerauLevenshtein.normalized_similarity,score_cutoff=.8,limit=None):
            row = catalog.products[index]
            if report and name_key(row['manufacturing_report_number']) != report:
                continue
            old = found.get(row['product_id'])
            if old is None or score > old[1]:
                found[row['product_id']] = (row,score)
    ordered = sorted(found.values(),key=lambda r:(-r[1],r[0]['product_id']))
    return [r[0] for r in ordered], 'full_name_distance_80_candidates', (ordered[0][1]*100 if ordered else None)


def main():
    prepared = json.loads((ROOT/'data/processed/claim_evidence_all/prepared.json').read_text(encoding='utf-8'))
    prev = json.loads((ROOT/'data/processed/product_identity_approved_pairs/product_matches.json').read_text(encoding='utf-8'))
    lookup = {(r['video_id'],r['product_ref']):r['filtered'] for r in prev}
    catalog = FilteredProductCatalog(ROOT/'Data_List_Claim_Verification/claim_verification.sqlite')
    choices = [name_key(r['product_name']) for r in catalog.products]
    rows, routes, statuses = [],Counter(),Counter()
    baseline_products = baseline_claims = connected_claims = 0
    for video in prepared['videos']:
        counts = Counter(c.get('product_ref') for c in video['claims'])
        for product in video['products']:
            previous = lookup[(video['video_id'],product.get('product_ref'))]
            baseline_products += previous['status']=='matched'
            baseline_claims += counts[product.get('product_ref')] * (previous['status']=='matched')
            candidates,route,score = search(catalog,product,previous,choices)
            status = 'no_candidates' if not candidates else 'single_candidate' if len(candidates)==1 else 'multiple_candidates'
            statuses[status]+=1
            if candidates:
                routes[route]+=1
                connected_claims+=counts[product.get('product_ref')]
            rows.append(dict(video_id=video['video_id'],url=video.get('url'),product_ref=product.get('product_ref'),
                             product_name=product.get('product_name'),brand_name=product.get('brand_name'),
                             brand_removed_name=strip_brand(product.get('product_name'),product.get('brand_name')),
                             manufacturer_name=product.get('manufacturer_name'),previous_match=previous,
                             status=status,route=route,top_name_score=score,claim_count=counts[product.get('product_ref')],
                             candidate_count=len(candidates),candidates=candidates,
                             identity_confirmed=(previous['status']=='matched'),
                             note='Candidate connection only; manufacturer mismatch allowed, no truth or identity guarantee.'))
    summary = dict(product_entries=len(rows),videos=len(prepared['videos']),previous_confirmed_product_entries=baseline_products,
                   candidate_connected_product_entries=len(rows)-statuses['no_candidates'],statuses=dict(statuses),routes=dict(routes),
                   previous_confirmed_claims=baseline_claims,candidate_connected_claims=connected_claims,total_claims=3400,
                   accuracy='Not measured; candidate coverage is not precision or confirmed identity.',
                   rules=['Exact product name; strip only observed brand prefix/suffix; full-name normalized Damerau-Levenshtein >=80',
                          'Manufacturer mismatch and multiple DB products allowed as candidates; report conflicts not overridden',
                          'No Evidence retrieval or model inference'])
    out = ROOT/'data/processed/product_identity_relaxed'
    out.mkdir(parents=True,exist_ok=True)
    (out/'product_matches.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
