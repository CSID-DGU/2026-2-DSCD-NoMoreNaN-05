"""Product-level candidate coverage with explicitly relaxed identity requirements."""
from collections import Counter
import json
from pathlib import Path
import re
import unicodedata

from rapidfuzz import process
from rapidfuzz.distance import DamerauLevenshtein
from ..src.claim_evidence_experiment import GENERIC_PRODUCT_NAMES, name_key
from ..src.product_identity_filtered import FilteredProductCatalog, company_core


def strip_brand(name, brand):
    text = unicodedata.normalize('NFC', name or '').strip()
    brand = unicodedata.normalize('NFC', brand or '').strip()
    if not brand:
        return text
    text = re.sub(r'^'+re.escape(brand)+r'(?=\s|$)\s*', '', text, flags=re.I)
    return re.sub(r'\s+'+re.escape(brand)+r'$', '', text, flags=re.I).strip()


def search(catalog, product, previous, name_choices, threshold=80, brand_recombine=False, report_fallback_only=False):
    if not 0 < threshold <= 100:
        raise ValueError('Threshold must be above 0 and at most 100')
    raw = product.get('product_name') or ''
    variants = [('exact_name', name_key(raw))]
    stripped = name_key(strip_brand(raw, product.get('brand_name')))
    if stripped and stripped != variants[0][1]:
        variants.append(('brand_removed_exact_name', stripped))
    brand=product.get('brand_name') or ''
    if brand_recombine and raw and brand and name_key(brand) not in name_key(raw):
        variants.append(('brand_added_exact_name',name_key(brand+' '+raw)))
    input_report = name_key(product.get('manufacturing_report_number'))
    report = '' if report_fallback_only else input_report
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
        # The library's cutoff can lose exact boundary matches (2 edits / 10
        # characters at 0.8). Evaluate uncut scores and filter explicitly.
        for _,score,index in process.extract(key,name_choices,scorer=DamerauLevenshtein.normalized_similarity,score_cutoff=0,limit=None):
            if score*100 < threshold:
                continue
            row = catalog.products[index]
            if report and name_key(row['manufacturing_report_number']) != report:
                continue
            old = found.get(row['product_id'])
            if old is None or score > old[1]:
                found[row['product_id']] = (row,score)
    ordered = sorted(found.values(),key=lambda r:(-r[1],r[0]['product_id']))
    if not ordered and report_fallback_only and input_report:
        return list(catalog.reports.get(input_report,[])), 'exact_report_number_fallback', None
    return [r[0] for r in ordered], f'full_name_distance_{threshold:g}_candidates', (ordered[0][1]*100 if ordered else None)
