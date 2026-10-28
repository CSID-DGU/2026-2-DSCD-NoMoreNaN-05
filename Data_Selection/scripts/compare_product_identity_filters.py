"""Compare saved baseline with factory-normalized product matching; no models/API."""
import argparse
from collections import Counter
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.product_identity_filtered import FilteredProductCatalog, ApprovedPairProductCatalog, company_core


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, default=ROOT / 'data/processed/claim_evidence_all/prepared.json')
    parser.add_argument('--database', type=Path, default=ROOT / 'Data_List_Claim_Verification/claim_verification.sqlite')
    parser.add_argument('--output', type=Path, default=ROOT / 'data/processed/product_identity_filtered')
    parser.add_argument('--approved-pairs', type=Path, help='Explicit user-approved pairs; exact product names only')
    args = parser.parse_args()
    prepared = json.loads(args.prepared.read_text(encoding='utf-8'))
    catalog = ApprovedPairProductCatalog(args.database, args.approved_pairs) if args.approved_pairs else FilteredProductCatalog(args.database)
    rows, before, after, changes, routes, reasons = [], Counter(), Counter(), Counter(), Counter(), Counter()
    for video in prepared['videos']:
        claims = Counter(c.get('product_ref') for c in video['claims'])
        refs = set()
        for product in video['products']:
            ref = product.get('product_ref')
            refs.add(ref)
            count = claims[ref]
            old = product['db_match']
            new = catalog.identify(product)
            before[old['status']] += count
            after[new['status']] += count
            transition = old['status'] + '->' + new['status']
            changes[transition] += count
            if new['status'] == 'matched':
                routes[new['route']] += count
            else:
                reasons[new['reason']] += count
            rows.append(dict(video_id=video['video_id'], url=video.get('url'), product_ref=ref,
                             product_name=product.get('product_name'), manufacturer=product.get('manufacturer_name'),
                             manufacturer_core=company_core(product.get('manufacturer_name')), claim_count=count,
                             transition=transition, baseline=old, filtered=new,
                             identity_observations=product.get('identity_observations', []),
                             requires_manual_validation=(old['status'] != 'matched' and new['status'] == 'matched')))
        unresolved = sum(n for ref, n in claims.items() if ref not in refs)
        before['unresolved_product_ref'] += unresolved
        after['unresolved_product_ref'] += unresolved
        reasons['unresolved_product_ref'] += unresolved
    summary = dict(claim_count=prepared['metadata']['claim_count'], baseline=dict(before), filtered=dict(after),
                   claim_transitions=dict(changes), matched_routes=dict(routes), unmatched_reasons=dict(reasons),
                   accuracy='Not measured: no independently annotated ground truth. Match rate is not accuracy.',
                   threshold=80, metric='100 * (1 - true Damerau-Levenshtein distance / max full-name length)',
                   evidence_retrieval_executed=False,
                   normalization='Factory suffix cleanup; explicitly approved pairs on exact product names only.' if args.approved_pairs else 'Corporate markers and separated factory/branch/business-unit suffixes; no legal-company aliases.',
                   approved_pairs_config=str(args.approved_pairs) if args.approved_pairs else None,
                   caveat='Distinct report numbers remain distinct products; multiple survivors are not auto-selected.')
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    (args.output/'product_matches.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
    with (args.output/'new_matches_review.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['video_id','url','product_name','manufacturer','manufacturer_core','claim_count','product_id','db_name','db_manufacturer','route','score','human_correct_1_wrong_0'])
        for row in rows:
            if row['requires_manual_validation']:
                m = row['filtered']
                writer.writerow([row['video_id'],row['url'],row['product_name'],row['manufacturer'],row['manufacturer_core'],row['claim_count'],m['product_id'],m['matched_product_name'],m['matched_manufacturer'],m['route'],m['name_score'],''])
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
