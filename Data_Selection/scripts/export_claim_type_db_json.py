"""Write one video JSON per input video plus a combined file, preserving effect."""
import argparse
from collections import Counter,defaultdict
from contextlib import closing
import copy
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.claim_type_db_format import build_product,TYPE_FIELDS,ARRAYS
from src.claim_evidence_experiment import name_key
from scripts.evaluate_relaxed_product_mapping import strip_brand


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mapping-dir',type=Path,required=True)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args()
    inputs=json.loads(args.input.read_text(encoding='utf-8-sig'))
    mappings=json.loads((args.mapping_dir/'all_results.json').read_text(encoding='utf-8'))
    audit=json.loads((args.mapping_dir/'product_matches.json').read_text(encoding='utf-8'))
    lookup={(r['video_id'],r['product_ref']):r for r in mappings if r['product_ref'] is not None}
    audits={(r['video_id'],r['product_ref']):r for r in audit}
    metadata=json.loads((ROOT/'data/processed/md_enrichment_20261103/enrichment_summary.json').read_text(encoding='utf-8'))
    version=metadata['finished_at']
    out=args.output_dir;video_dir=out/'videos';video_dir.mkdir(parents=True,exist_ok=True)
    # Fetch enriched arrays only for the specific confirmed source rows.
    ids={r['product']['evi_product']['product_id'] for r in mappings
         if r['product']['match']['status']=='confirmed' and r['product']['evi_product'] is not None}
    with closing(sqlite3.connect(args.database.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        products={pid:dict(db.execute('SELECT * FROM products WHERE product_id=?',(pid,)).fetchone()) for pid in ids}
        names=Counter(name_key(r[0]) for r in db.execute('SELECT product_name FROM products'))
    result=[];statuses=Counter();effects=0;nonempty_effects=0;type_counts=Counter();excluded_brand=0
    for video in inputs:
        if not re.fullmatch(r'[A-Za-z0-9_.-]+',video['video_id']):raise ValueError('Unsafe video ID filename')
        item=dict(video_id=video['video_id'],url=video.get('url'),db_version=version,products=[],claims=copy.deepcopy(video.get('claims',[])))
        for original in video.get('products',[]):
            key=(video['video_id'],original['product_ref'])
            mapping=lookup.get(key);row=audits.get(key,{})
            product=None
            if mapping and mapping['product'].get('evi_product'):
                product=products.get(mapping['product']['evi_product']['product_id'])
            raw=original.get('product_name') or '';brand=original.get('brand_name') or ''
            variants={name_key(raw),name_key(strip_brand(raw,brand)),name_key(brand+' '+raw)}-{''}
            if product:count=names[name_key(product['product_name'])]
            else:count=sum(names[k] for k in variants)
            # Keep excluded products/claims in the transport schema, but do not
            # silently reintroduce them into the approved brand-present cohort.
            if not isinstance(original.get('brand_name'),str) or not original['brand_name'].strip():
                excluded_brand+=1
                mapping=dict(product=dict(match=dict(status='unresolved' if row.get('candidates') else 'not_found')))
                product=None
            exported=build_product(original,mapping,product,count)
            statuses[exported['match']['status']]+=1
            item['products'].append(exported)
        assert item['claims']==video.get('claims',[])
        for original,claim in zip(video.get('claims',[]),item['claims']):
            if 'effect' not in original:raise ValueError('Input claim missing effect; no fabrication allowed')
            assert 'effect' in claim and claim['effect']==original['effect']
            effects+=1;nonempty_effects+=bool(claim['effect']);type_counts[claim.get('claim_type')]+=1
        for product in item['products']:
            if product['match']['status']=='confirmed':
                assert product['DB'] is not None and set(product['DB'])==set(TYPE_FIELDS)
                assert 'EFFECT' in product['DB']
                for kind,fields in TYPE_FIELDS.items():
                    assert list(product['DB'][kind])==fields
                    for field,value in product['DB'][kind].items():assert isinstance(value,list if field in ARRAYS else str)
            else:
                assert product['DB'] is None
                assert product['match']['method'] is None
                assert product['match']['matched_name'] is None
                assert product['match']['matched_company'] is None
        path=video_dir/(video['video_id']+'.json')
        path.write_text(json.dumps(item,ensure_ascii=False,indent=2),encoding='utf-8')
        assert json.loads(path.read_text(encoding='utf-8'))==item
        result.append(item)
    combined=out/'claims_with_db.json'
    combined.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    reread=json.loads(combined.read_text(encoding='utf-8'))
    assert [v['claims'] for v in reread]==[v.get('claims',[]) for v in inputs]
    summary=dict(videos=len(result),products=sum(len(v['products']) for v in result),claims=effects,
        claim_effect_fields_preserved=effects,nonempty_effect_values_preserved=nonempty_effects,product_match_statuses=dict(statuses),
        claims_types=dict(type_counts),db_sections_only_for_confirmed=True,db_effect_section_included=True,
        excluded_missing_brand_product_entries=excluded_brand,all_original_products_and_claims_retained_for_transport=True,
        database=str(args.database),db_version=version,input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
        note='Selected product groups and confirmed identity are different. Prior unresolved selections remain unresolved with DB=null. Product candidates count raw DB rows with the same normalized product name; fuzzy-candidate audits remain in mapping files.')
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    with zipfile.ZipFile(out/'video_jsons.zip','w',compression=zipfile.ZIP_DEFLATED) as archive:
        for v in result:archive.write(video_dir/(v['video_id']+'.json'),'videos/'+v['video_id']+'.json')
        archive.write(out/'summary.json','summary.json')
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
