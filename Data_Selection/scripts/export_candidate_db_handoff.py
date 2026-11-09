"""Export DB evidence for ALL retrieved products, without identity-status gating.

Schema v2: matched means retrieved DB candidates, not verified product identity.
Every candidate carries its own type-specific DB; competing products are never
merged into one fictitious formulation. Original claim fields are preserved.
"""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.claim_type_db_format import db_sections
from src.claim_evidence_experiment import name_key
from src.product_identity_filtered import company_core


def source_ids(row):
    found={p['product_id'] for p in row.get('candidates',[])}
    selected=row.get('selected_product')
    if selected:found.add(selected['product_id'])
    found.update(row.get('selected_group_product_ids',[]))
    return sorted(found)


def choose_primary(original,row,candidates,pairs):
    """A convenient singleton only; full retrieval evidence remains available."""
    if not candidates:return None,'no_candidates'
    maker=original.get('manufacturer_name')
    brand=original.get('brand_name')
    company=maker or brand
    if company:
        core=company_core(company)
        matching=[]
        for candidate in candidates:
            other=company_core(candidate['company_name'])
            exact_name=name_key(candidate['product_name']) in {
                name_key(original.get('product_name')),name_key(row.get('brand_removed_name'))}
            if core==other or (exact_name and frozenset((core,other)) in pairs):matching.append(candidate)
        if len(matching)==1:
            return matching[0],'manufacturer_priority' if maker else 'brand_fallback'
        if matching:return None,'multiple_company_matching_rows'
        if maker:return None,'manufacturer_conflict_candidates_retained'
    if len(candidates)==1:return candidates[0],'single_retrieved_candidate'
    return None,'multiple_retrieved_candidates'


def iter_claim_contexts(videos):
    """Consumer adapter: candidate DBs are usable even when product.DB is null."""
    for video in videos:
        refs=defaultdict(list)
        for product in video['products']:
            refs[product.get('product_ref')].append(product)
        for claim in video['claims']:
            products=refs.get(claim.get('product_ref'),[]) if claim.get('product_ref') is not None else []
            product=products[0] if len(products)==1 else None
            candidates=product.get('candidate_products',[]) if product else []
            yield dict(video_id=video['video_id'],claim=claim,
                       evidence_status='linked' if candidates else 'no_linkable_product',
                       preferred_product_id=product.get('preferred_product_id') if product else None,
                       candidates=candidates)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=ROOT/'data/processed/product_functionality_handoff_y_final_brand_company/source_input.json')
    parser.add_argument('--mapping-dir',type=Path,default=ROOT/'data/processed/md_enrichment_20261103/mapping_claim_identity')
    parser.add_argument('--database',type=Path,default=ROOT/'TRUEAD_DB_보강자료/claim_verification.sqlite')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'exports/candidate_db_handoff_20261104')
    args=parser.parse_args()
    raw=args.input.read_bytes(); database_hash=hashlib.sha256(args.database.read_bytes()).hexdigest()
    videos=json.loads(raw.decode('utf-8-sig'))
    audits=json.loads((args.mapping_dir/'product_matches.json').read_text(encoding='utf-8'))
    index={(r['video_id'],r['product_ref']):r for r in audits}
    pairs={frozenset(company_core(x) for x in pair) for pair in
           json.loads((ROOT/'configs/manufacturer_pairs.json').read_text(encoding='utf-8'))['pairs']}
    ids={pid for row in audits for pid in source_ids(row)}
    with sqlite3.connect(args.database.resolve().as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        records={pid:dict(db.execute('SELECT * FROM products WHERE product_id=?',(pid,)).fetchone()) for pid in ids}
    result=[]; counts=Counter(); named=defaultdict(list); branded=defaultdict(list)
    original_claims=0; excluded_etc=0
    for video in videos:
        item=copy.deepcopy(video)
        item['db_version']='2026-11-03T04:09:56.363154+00:00'
        item['schema_version']='2.0-candidate-evidence'
        item['claims']=[copy.deepcopy(c) for c in video['claims'] if c.get('claim_type')!='ETC']
        original_claims+=len(video['claims']);excluded_etc+=len(video['claims'])-len(item['claims'])
        item['products']=[]
        for original in video['products']:
            row=index[(video['video_id'],original['product_ref'])]
            candidates=[]
            for pid in source_ids(row):
                record=records[pid]
                candidates.append(dict(product_id=pid,product_name=record['product_name'],company_name=record['company_name'],
                    manufacturing_report_number=record['manufacturing_report_number'],DB=db_sections(record)))
            primary,reason=choose_primary(original,row,candidates,pairs)
            product=copy.deepcopy(original)
            product['match']=dict(status='matched' if candidates else 'not_found',method=row.get('route') if candidates else None,
                candidates=len(candidates),selection_reason=reason,
                matched_name=primary['product_name'] if primary else None,
                matched_company=primary['company_name'] if primary else None,
                identity_confirmed=False)
            product['preferred_product_id']=primary['product_id'] if primary else None
            product['DB']=copy.deepcopy(primary['DB']) if primary else None
            product['candidate_products']=candidates
            item['products'].append(product)
            counts[product['match']['status']]+=1
            counts['with_primary_DB']+=primary is not None
            counts['multiple_candidate_rows']+=len(candidates)>1
            counts['candidate_db_rows']+=len(candidates)
            if name_key(original.get('product_name')):
                group=(name_key(original['product_name']),name_key(original.get('brand_name')))
                named[group].append(bool(candidates))
                if original.get('brand_name') and original['brand_name'].strip():branded[group].append(bool(candidates))
        result.append(item)
    contexts=list(iter_claim_contexts(result))
    linked=[x for x in contexts if x['candidates']]
    claim_types=Counter(x['claim']['claim_type'] for x in linked)
    named_count=sum(any(v) for v in named.values())
    branded_count=sum(any(v) for v in branded.values())
    summary=dict(schema_version='2.0-candidate-evidence',videos=len(result),original_claims=original_claims,
        excluded_etc=excluded_etc,claims=len(contexts),product_entries=sum(len(v['products']) for v in result),
        product_counts=dict(counts),unique_named_products=len(named),unique_named_products_with_DB_candidates=named_count,
        named_product_candidate_rate=round(100*named_count/len(named),2),
        brand_present_named_products=len(branded),brand_present_named_products_with_candidates=branded_count,
        brand_present_candidate_rate=round(100*branded_count/len(branded),2),
        claims_with_product_DB_candidates=len(linked),claims_without_product_DB_candidates=len(contexts)-len(linked),
        claim_candidate_coverage_percent=round(100*len(linked)/len(contexts),2),linked_claim_types=dict(claim_types),
        matched_status_means='DB retrieval candidates exist; not independent identity verification or verdict',
        unresolved_product_entries=0,
        input_sha256=hashlib.sha256(raw).hexdigest(),database_sha256=database_hash,
        original_files_changed=False,
        consumer_rule='Use product.candidate_products[*].DB. Do not filter for confirmed or require top-level product.DB.',
        warning='Candidates can be different products/formulations. Evaluate separately; never union their ingredients or treat all as the advertised product.')
    # No ETC, effect preservation, no claim duplication, complete live DB copy.
    assert len(contexts)+excluded_etc==original_claims
    for before,after in zip(videos,result):
        assert [c for c in before['claims'] if c.get('claim_type')!='ETC']==after['claims']
        for product in after['products']:
            assert bool(product['candidate_products'])==(product['match']['status']=='matched')
            assert product['match']['status']!='unresolved'
            for candidate in product['candidate_products']:
                assert candidate['DB']==db_sections(records[candidate['product_id']])
                assert 'EFFECT' in candidate['DB']
    assert args.input.read_bytes()==raw
    assert hashlib.sha256(args.database.read_bytes()).hexdigest()==database_hash
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/'claims_with_db.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    (args.output_dir/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    # Light index: all claim IDs and actual candidate product IDs; no repeated DB payload.
    index_rows=[dict(video_id=x['video_id'],claim_id=x['claim']['claim_id'],product_ref=x['claim'].get('product_ref'),
                     status=x['evidence_status'],preferred_product_id=x['preferred_product_id'],
                     candidate_product_ids=[c['product_id'] for c in x['candidates']]) for x in contexts]
    (args.output_dir/'claim_candidate_index.json').write_text(json.dumps(index_rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
