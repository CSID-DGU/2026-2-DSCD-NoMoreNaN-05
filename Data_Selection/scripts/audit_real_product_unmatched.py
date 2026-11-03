"""Explain latest no-candidate results and measure proposed searches without applying them."""
from collections import Counter
import json
from pathlib import Path
import re
import sys
import unicodedata

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rapidfuzz import process
from rapidfuzz.distance import DamerauLevenshtein
from src.claim_evidence_experiment import GENERIC_PRODUCT_NAMES,name_key
from src.product_identity_filtered import FilteredProductCatalog
from scripts.evaluate_relaxed_product_mapping import strip_brand


def phrase_pattern(text):
    tokens=unicodedata.normalize('NFC',text).casefold().split()
    return re.compile(r'(?<![가-힣a-z0-9])'+r'\s+'.join(re.escape(t) for t in tokens)+r'(?![가-힣a-z0-9])')


def audit(rows,catalog):
    choices=[name_key(p['product_name']) for p in catalog.products]
    raw_db=[unicodedata.normalize('NFC',p['product_name']).casefold() for p in catalog.products]
    punctuation_index={}
    def punct(text):
        return re.sub(r'[^가-힣a-z0-9]','',name_key(text))
    for p in catalog.products:
        punctuation_index.setdefault(punct(p['product_name']),[]).append(p)
    results=[]
    for r in rows:
        if r['candidates']:
            continue
        raw=r.get('product_name') or ''
        brand=r.get('brand_name') or ''
        variants=list(dict.fromkeys(v for v in (raw,strip_brand(raw,brand)) if v))
        keys=[name_key(v) for v in variants]
        report=r['previous_match'].get('observed_report_number')
        exact_exists=any(catalog.names.get(k) for k in keys if k not in GENERIC_PRODUCT_NAMES)
        combined=(brand+' '+raw).strip() if brand and raw and name_key(brand) not in name_key(raw) else ''
        brand_rows=catalog.names.get(name_key(combined),[]) if combined else []
        punct_rows={p['product_id']:p for v in variants if len(punct(v))>=3 and name_key(v) not in GENERIC_PRODUCT_NAMES
                    for p in punctuation_index.get(punct(v),[])}
        partial={}
        for v in variants:
            if len(name_key(v))<3 or name_key(v) in GENERIC_PRODUCT_NAMES:
                continue
            pattern=phrase_pattern(v)
            for p,text in zip(catalog.products,raw_db):
                if pattern.search(text):
                    partial[p['product_id']]=p
        best={}
        for key in keys:
            if not key:
                continue
            for _,score,index in process.extract(key,choices,scorer=DamerauLevenshtein.normalized_similarity,limit=3):
                p=catalog.products[index]
                best[p['product_id']]=(p, max(score,best.get(p['product_id'],(None,0))[1]))
        ranked=sorted(best.values(),key=lambda x:-x[1])[:3]
        if not name_key(raw):
            reason='missing_product_name'
        elif all(k in GENERIC_PRODUCT_NAMES for k in keys):
            reason='generic_product_name_guard'
        elif report and exact_exists:
            reason='known_report_conflict'
        elif partial:
            reason='partial_name_candidates_not_accepted'
        else:
            reason='no_exact_match_and_full_name_below_80'
        results.append(dict(video_id=r['video_id'],product_ref=r['product_ref'],product_name=r['product_name'],
                            brand_name=brand,manufacturer_name=r.get('manufacturer_name'),reason=reason,
                            previous_strict_reason=r['previous_match'].get('reason'),
                            best_name_score=round(100*ranked[0][1],2) if ranked else None,
                            closest_products=[dict(p,name_score=round(100*s,2)) for p,s in ranked],
                            brand_plus_name=combined or None,brand_plus_exact_candidates=brand_rows,
                            punctuation_only_candidates=list(punct_rows.values()),
                            whole_phrase_candidate_count=len(partial),whole_phrase_examples=list(partial.values())[:5]))
    return results


def main():
    folder=ROOT/'data/processed/product_functionality_handoff_real'
    rows=json.loads((folder/'product_matches.json').read_text(encoding='utf-8'))
    results=audit(rows,FilteredProductCatalog(ROOT/'Data_List_Claim_Verification/claim_verification.sqlite'))
    reasons=Counter(r['reason'] for r in results)
    groups={key:[r for r in results if r[key]] for key in ('brand_plus_exact_candidates','punctuation_only_candidates','whole_phrase_candidate_count')}
    summary=dict(unmatched_products=len(results),reason_counts=dict(reasons),
                 potential_search_recovery_counts={k:len(v) for k,v in groups.items()},
                 potential_recovery_union=len({(r['video_id'],r['product_ref']) for group in groups.values() for r in group}),
                 below_80_score_bands=dict(Counter('70_to_below_80' if r['best_name_score'] is not None and r['best_name_score']>=70 else '50_to_below_70' if r['best_name_score'] is not None and r['best_name_score']>=50 else 'below_50_or_no_name' for r in results if r['reason']=='no_exact_match_and_full_name_below_80')),
                 applied=False,note='Diagnostics/proposed candidate retrieval only; existing handoff unchanged; not accuracy or confirmed identity.')
    (folder/'unmatched_diagnosis.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'unmatched_diagnosis_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    for key in reasons:
        print(key,json.dumps([dict(name=r['product_name'],brand=r['brand_name'],best_score=r['best_name_score'],closest=r['closest_products'][:1]) for r in results if r['reason']==key][:4],ensure_ascii=False))
    for key,group in groups.items():
        print(key,json.dumps([dict(name=r['product_name'],brand=r['brand_name'],combined=r['brand_plus_name'],examples=r[key] if isinstance(r[key],list) else r['whole_phrase_examples']) for r in group[:4]],ensure_ascii=False))


if __name__=='__main__':
    main()
