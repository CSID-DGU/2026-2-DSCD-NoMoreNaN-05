"""Export all 70-point candidate-connected name/brand groups with original functionality."""
from collections import defaultdict
import argparse
from contextlib import closing
import copy
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.claim_evidence_experiment import name_key
from scripts.export_product_functionality_handoff import FIELDS


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder',type=Path,default=ROOT/'data/processed/product_functionality_handoff_y_final_name_first')
    folder=parser.parse_args().folder
    rows=json.loads((folder/'product_matches.json').read_text(encoding='utf-8'))
    records=json.loads((folder/'all_results.json').read_text(encoding='utf-8'))
    lookup={(r['video_id'],r['product_ref']):r for r in records if r['product_ref'] is not None}
    groups=defaultdict(list)
    for row in rows:
        if name_key(row.get('product_name')):
            groups[(name_key(row['product_name']),name_key(row.get('brand_name')))].append(row)
    with closing(sqlite3.connect((ROOT/'Data_List_Claim_Verification/claim_verification.sqlite').resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        products={r['product_id']:dict(r) for r in db.execute('SELECT '+','.join(FIELDS)+' FROM products')}
    grouped,flat=[],[]
    for group in groups.values():
        if not any(r['candidates'] for r in group):continue
        ids=set()
        bundle=[]
        for row in group:
            record=copy.deepcopy(lookup[(row['video_id'],row['product_ref'])])
            bundle.append(record)
            ids.update(p['product_id'] for p in row['candidates'])
            ids.update(record['product'].get('group',{}).get('source_product_ids',[]))
            if row['candidates']:
                flat.append(record)
        grouped.append(dict(input_product_name=group[0]['product_name'],input_brand_name=group[0].get('brand_name'),
                            db_version=bundle[0]['db_version'],
                            db_candidates=[{k:products[pid][k] for k in FIELDS} for pid in sorted(ids)],
                            videos=bundle))
    for group in grouped:
        assert group['db_candidates']
        for product in group['db_candidates']:
            assert product=={k:products[product['product_id']][k] for k in FIELDS}
    (folder/f'candidate_groups_{len(grouped)}_main_functionality.json').write_text(json.dumps(grouped,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'candidate_video_handoff_70.json').write_text(json.dumps(flat,ensure_ascii=False,indent=2),encoding='utf-8')
    summary=dict(named_candidate_groups=len(grouped),flat_video_product_records=len(flat),
                 unique_video_urls=len({r['url'] for r in flat}),
                 single_selected_named_groups=sum(any(r['product']['evi_product'] is not None for r in g['videos']) for g in grouped),
                 fields='db_candidates[].main_functionality; videos[] preserves original video/claim handoff',
                 note='Group candidates are a union for review; not a confirmed match for every video. Prior mapping files unchanged.')
    (folder/'candidate_handoff_70_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
