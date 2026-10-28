"""Mine review-only manufacturer pairs from product records; no alias rules applied."""
from collections import defaultdict
import json
from pathlib import Path
import sys
from itertools import combinations

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from rapidfuzz.distance import DamerauLevenshtein
from src.claim_evidence_experiment import name_key
from src.product_identity_filtered import FilteredProductCatalog, company_core


def main():
    catalog = FilteredProductCatalog(ROOT/'Data_List_Claim_Verification/claim_verification.sqlite')
    matches = json.loads((ROOT/'data/processed/product_identity_filtered/product_matches.json').read_text(encoding='utf-8'))
    names = {key: {name_key(r['product_name']): r['product_name'] for r in rows} for key, rows in catalog.companies.items()}
    observed = defaultdict(list)
    for row in matches:
        if row['filtered']['status'] == 'matched':
            continue
        a = company_core(row['manufacturer'])
        if not a:
            continue
        for candidate in catalog.names.get(name_key(row['product_name']), []):
            b = company_core(candidate['company_name'])
            if a == b or not b:
                continue
            key = tuple(sorted((a,b)))
            observed[key].append(dict(video_id=row['video_id'], product_name=row['product_name'],
                                      input_manufacturer=row['manufacturer'], db_manufacturer=candidate['company_name'],
                                      product_id=candidate['product_id'], claim_count=row['claim_count']))
    keys = set(observed)
    for a,b in combinations(sorted(catalog.companies), 2):
        similarity = 100*DamerauLevenshtein.normalized_similarity(a,b)
        if (min(len(a),len(b)) >= 3 and (a in b or b in a)) or similarity >= 80:
            keys.add((a,b))
    result = []
    for a,b in keys:
        shared = sorted(set(names.get(a,{})) & set(names.get(b,{})))
        obs = observed.get((a,b), [])
        result.append(dict(company_a=a, company_b=b,
                           name_similarity=round(100*DamerauLevenshtein.normalized_similarity(a,b),2),
                           shared_product_name_count=len(shared),
                           shared_product_examples=[names[a][k] for k in shared[:5]],
                           affected_video_count=len({r['video_id'] for r in obs}),
                           observed_exact_product_conflicts=obs,
                           status='review_only_not_verified_equivalent'))
    result.sort(key=lambda r:(-r['shared_product_name_count'],-r['affected_video_count'],-r['name_similarity']))
    output = ROOT/'data/processed/product_identity_filtered/manufacturer_pair_candidates.json'
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
