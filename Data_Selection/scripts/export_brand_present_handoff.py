"""Exclude products with missing brand_name and export existing brand-based matches.

Uses saved matches for the identical input; does not run retrieval again or
change the matching threshold. Claims follow their own video/product reference.
"""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.claim_evidence_experiment import name_key


def partition(videos):
    kept, excluded, orphans = [], [], []
    allowed = set()
    for video in videos:
        refs = [p['product_ref'] for p in video.get('products', [])]
        if len(refs) != len(set(refs)):
            raise ValueError('Duplicate product_ref within video')
        retained = []
        for product in video.get('products', []):
            brand = product.get('brand_name')
            if isinstance(brand, str) and brand.strip():
                retained.append(copy.deepcopy(product))
                allowed.add((video['video_id'], product['product_ref']))
            else:
                excluded.append(dict(video_id=video['video_id'], url=video.get('url'),
                    product=copy.deepcopy(product), reason='missing_brand_name',
                    claims=[copy.deepcopy(c) for c in video.get('claims', []) if c.get('product_ref') == product['product_ref']]))
        claims = [copy.deepcopy(c) for c in video.get('claims', [])
                  if (video['video_id'], c.get('product_ref')) in allowed]
        orphan_claims = [copy.deepcopy(c) for c in video.get('claims', []) if c.get('product_ref') not in refs]
        if orphan_claims:
            orphans.append(dict(video_id=video['video_id'], claims=orphan_claims, reason='unknown_product_ref'))
        if retained:
            item = copy.deepcopy(video)
            item.update(products=retained, claims=claims)
            kept.append(item)
    return kept, excluded, orphans, allowed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir', type=Path, default=ROOT/'data/processed/product_functionality_handoff_y_final_brand_company')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'data/processed/product_functionality_handoff_brand_present')
    args = parser.parse_args()
    base, out = args.base_dir, args.output_dir
    load = lambda name: json.loads((base/name).read_text(encoding='utf-8'))
    summary = load('summary.json')
    if summary.get('company_comparison_field') != 'brand_name':
        raise ValueError('Only brand_name-based mapping results can be used')
    videos, rows, records = load('source_input.json'), load('product_matches.json'), load('all_results.json')
    if len({v['video_id'] for v in videos}) != len(videos):
        raise ValueError('Duplicate video_id')
    kept, excluded, orphans, allowed = partition(videos)
    rows = [r for r in rows if (r['video_id'], r['product_ref']) in allowed]
    records = [r for r in records if (r['video_id'], r['product_ref']) in allowed]
    assert len(rows) == len(records) == len(allowed)
    assert all(r.get('comparison_company_field') == 'brand_name' for r in rows)
    claim_counts = lambda items: Counter(json.dumps([v['video_id'], c], ensure_ascii=False, sort_keys=True)
                                        for v in items for c in v.get('claims', []))
    assert claim_counts(kept) == claim_counts(records)
    assert claim_counts(videos) == claim_counts(kept) + claim_counts(excluded) + claim_counts(orphans)
    selected = [r for r in records if r['product']['evi_product'] is not None]
    unresolved = [r for r in records if r['product']['evi_product'] is None]
    groups = {}
    for row in rows:
        if name_key(row.get('product_name')):
            groups.setdefault((name_key(row['product_name']), name_key(row['brand_name'])), []).append(row)
    rate = lambda n, d: round(100*n/d, 2) if d else None
    candidate_count = sum(bool(r['candidates']) for r in rows)
    named_candidates = sum(any(r['candidates'] for r in group) for group in groups.values())
    named_selected = sum(any(r['selected_product'] for r in group) for group in groups.values())
    result = dict(company_comparison_field='brand_name', source_input_sha256=hashlib.sha256((base/'source_input.json').read_bytes()).hexdigest(),
        original_product_entries=sum(len(v.get('products', [])) for v in videos), excluded_missing_brand_entries=len(excluded),
        retained_product_entries=len(rows), retained_videos=len(kept),
        candidate_product_entries=candidate_count, candidate_rate=rate(candidate_count, len(rows)),
        selected_product_entries=len(selected), selected_rate=rate(len(selected), len(rows)),
        deduplicated_named_input_products=len(groups), deduplicated_candidate_groups=named_candidates,
        deduplicated_candidate_rate=rate(named_candidates, len(groups)), deduplicated_selected_groups=named_selected,
        deduplicated_selected_rate=rate(named_selected, len(groups)), retained_missing_product_name_entries=sum(not name_key(r.get('product_name')) for r in rows),
        selected_unique_urls=len({r['url'] for r in selected}), selected_claims=sum(len(r['claims']) for r in selected),
        excluded_claims=sum(len(r['claims']) for r in excluded), orphan_claims=sum(len(r['claims']) for r in orphans),
        note='Existing 70-point brand/company matching results filtered by nonempty brand_name. Coverage, not measured accuracy. Selected groups can retain unresolved identity status; see product.match.')
    out.mkdir(parents=True, exist_ok=True)
    for filename, value in {'input_brand_present.json': kept, 'excluded_missing_brand.json': excluded,
        'orphan_claims.json': orphans, 'product_matches.json': rows, 'all_results.json': records,
        'mapped_products.json': selected, 'unmapped_products.json': unresolved, 'summary.json': result}.items():
        (out/filename).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
