"""Count source availability under explicit video product-composition gating."""
from collections import Counter
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.claim_evidence_experiment import Catalog, declared_product_ingredients, ingredient_candidates


def main():
    videos=json.loads((ROOT/'data/processed/claim_evidence_all/prepared.json').read_text(encoding='utf-8'))['videos']
    matches=json.loads((ROOT/'data/processed/product_identity_relaxed/product_matches.json').read_text(encoding='utf-8'))
    lookup={(r['video_id'],r['product_ref']):r for r in matches}
    catalog=Catalog(ROOT/'Data_List_Claim_Verification/claim_verification.sqlite')
    counts=Counter(total_claims=0,product_source_claims=0,ingredient_only_claims=0,no_sources=0,ingredient_search_eligible_claims=0)
    observations=[]
    for video in videos:
        products={p['product_ref']:p for p in video['products']}
        cached={}
        for ref,product in products.items():
            terms,sources=declared_product_ingredients(catalog,video,product)
            materials=ingredient_candidates(catalog,terms)
            cached[ref]=(terms,materials)
            observations.append(dict(video_id=video['video_id'],product_ref=ref,observed_ingredient_terms=terms,
                                     declaration_claim_ids=sources,ingredient_ids=[i['ingredient_id'] for i in materials]))
        for claim in video['claims']:
            counts['total_claims']+=1
            key=(video['video_id'],claim.get('product_ref'))
            has_product=bool(lookup.get(key,{}).get('candidates'))
            terms,materials=cached.get(claim.get('product_ref'),([],[]))
            counts['ingredient_search_eligible_claims']+=bool(terms)
            if has_product:
                counts['product_source_claims']+=1
            elif materials:
                counts['ingredient_only_claims']+=1
            else:
                counts['no_sources']+=1
    result=dict(rule='explicit_product_composition_claim_only',counts=dict(counts),
                candidate_connected_claims=counts['product_source_claims']+counts['ingredient_only_claims'],
                ranking_executed=False,observations=observations,
                note='Advertisement composition assertion is not verified composition. Previous unconditional ingredient fallback is obsolete.')
    out=ROOT/'data/processed/product_identity_relaxed/evidence_availability_declaration_gated.json'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='observations'},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
