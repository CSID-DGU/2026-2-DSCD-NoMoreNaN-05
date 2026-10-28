"""Narrow saved multiple product candidates using manufacturer evidence."""
from collections import Counter
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.claim_evidence_experiment import company_key
from src.product_identity_filtered import company_core


def resolve_multiple(row, approved_pairs):
    candidates = row['candidates']
    manufacturer = row.get('manufacturer_name')
    if not manufacturer:
        return [], 'manufacturer_missing'
    observations = [manufacturer] + [obs['value'] for obs in row.get('identity_observations', []) if obs.get('value')]
    def paired(a,b):
        a,b = company_core(a),company_core(b)
        return bool(a and b) and (a==b or frozenset((a,b)) in approved_pairs)
    if any(not paired(a,b) for a in observations for b in observations):
        return [], 'conflicting_input_manufacturers'
    strict = [c for c in candidates if all(company_key(obs)==company_key(c['company_name']) for obs in observations)]
    if strict:
        return strict, 'manufacturer_original'
    normalized = [c for c in candidates if all(company_core(obs)==company_core(c['company_name']) for obs in observations)]
    if normalized:
        return normalized, 'manufacturer_factory_normalized'
    if row.get('route') in ('exact_name','brand_removed_exact_name'):
        aliases = [c for c in candidates if all(paired(obs,c['company_name']) for obs in observations)]
        if aliases:
            return aliases, 'manufacturer_approved_pair'
    return [], 'manufacturer_mismatch'


def main():
    rows=json.loads((ROOT/'data/processed/product_identity_relaxed/product_matches.json').read_text(encoding='utf-8'))
    config=json.loads((ROOT/'configs/manufacturer_pairs.json').read_text(encoding='utf-8'))
    pairs={frozenset(company_core(v) for v in p) for p in config['pairs']}
    prior=json.loads((ROOT/'data/processed/product_identity_approved_pairs/product_matches.json').read_text(encoding='utf-8'))
    obs={(r['video_id'],r['product_ref']):r.get('identity_observations',[]) for r in prior}
    reasons,counts=Counter(),Counter()
    output=[]
    for original in rows:
        row=copy.deepcopy(original)
        row['identity_observations']=obs.get((row['video_id'],row['product_ref']),[])
        row['original_candidate_count']=len(row['candidates'])
        row['selected_product']=None
        if row['status']=='multiple_candidates':
            narrowed,reason=resolve_multiple(row,pairs)
            row['manufacturer_resolution']=reason
            row['manufacturer_filtered_candidates']=narrowed
            if len(narrowed)==1:
                row['selection_status']='selected_by_manufacturer'
                row['selected_product']=narrowed[0]
                counts['resolved_from_multiple']+=1
            else:
                row['selection_status']='unresolved_multiple'
                reasons[reason]+=1
        elif row['status']=='single_candidate':
            row['selection_status']='single_search_candidate'
            row['selected_product']=row['candidates'][0]
        else:
            row['selection_status']='not_found'
        counts[row['selection_status']]+=1
        output.append(row)
    selected=sum(r['selected_product'] is not None for r in output)
    summary=dict(product_entries=len(output),original_single=210,original_multiple=52,
                 newly_resolved_multiple=counts['resolved_from_multiple'],selected_product_entries=selected,
                 selected_product_rate=round(100*selected/len(output),2),
                 unresolved_multiple=counts['unresolved_multiple'],not_found=counts['not_found'],
                 unresolved_reasons=dict(reasons),
                 claim_count_with_selected_product=sum(r['claim_count'] for r in output if r['selected_product']),
                 note='Single search candidate includes relaxed manufacturer mismatches; selection is not independently verified identity.',
                 evidence_retrieval_executed=False)
    out=ROOT/'data/processed/product_identity_disambiguated'
    out.mkdir(parents=True,exist_ok=True)
    (out/'product_matches.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps([dict(name=r['product_name'],manufacturer=r['manufacturer_name'],selected=r['selected_product']) for r in output if r['selection_status']=='selected_by_manufacturer'],ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
