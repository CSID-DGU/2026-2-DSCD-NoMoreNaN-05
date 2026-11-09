"""Select one <=60s longest video per original product ID, then unique URLs.

Output records keep the existing ad_video_urls schema. Cross-product video
associations remain in an audit file, not in new output fields.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def select(rows):
    products=defaultdict(list)
    for row in rows:
        duration=row.get('duration_sec')
        if isinstance(duration,(int,float)) and not isinstance(duration,bool) and 0<duration<=60:
            products[str(row['id'])].append(row)
    # max is stable: equal-duration alternatives keep their original file order.
    selected=[max(videos,key=lambda x:x['duration_sec']) for videos in products.values()]
    urls={};associations=defaultdict(list)
    for row in selected:
        urls.setdefault(row['url'],row)
        associations[row['url']].append({k:row[k] for k in ('id','product_name','company_name')})
    unique=list(urls.values())
    assert len({r['url'] for r in unique})==len(unique)
    assert len({r['video_id'] for r in unique})==len(unique)
    assert all(0<r['duration_sec']<=60 for r in unique)
    assert all(r in rows and r['duration_sec']==max(x['duration_sec'] for x in products[str(r['id'])]) for r in selected)
    assert {r['url'] for r in unique}=={r['url'] for r in selected}
    return unique,selected,dict(associations)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=ROOT/'exports/youtube_additional_20261104/ad_video_urls_all.json')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'exports/youtube_longest_unique_20261104')
    args=parser.parse_args()
    raw=args.input.read_bytes();rows=json.loads(raw.decode('utf-8-sig'))
    unique,selected,associations=select(rows)
    summary=dict(input_records=len(rows),input_unique_urls=len({r['url'] for r in rows}),
        products_with_valid_videos=len(selected),longest_per_product_records=len(selected),
        cross_product_duplicate_records_removed=len(selected)-len(unique),output_unique_videos=len(unique),
        output_min_duration_sec=min(r['duration_sec'] for r in unique),output_max_duration_sec=max(r['duration_sec'] for r in unique),
        group_key='Original product id',tie_break='First record in original input order',
        selection_order='Filter 0 < duration <= 60; longest per product ID; deduplicate URL',
        schema_unchanged=True,input_sha256=hashlib.sha256(raw).hexdigest(),original_input_changed=False,
        note='A shared video appears once in the final URL list. All product associations are retained in selection_audit.json.')
    args.output_dir.mkdir(parents=True,exist_ok=True)
    for filename,value in [('ad_video_urls.json',unique),('summary.json',summary),
                           ('selection_audit.json',dict(longest_per_product=selected,products_per_selected_url=associations))]:
        (args.output_dir/filename).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert args.input.read_bytes()==raw
    output=json.loads((args.output_dir/'ad_video_urls.json').read_text(encoding='utf-8'))
    assert output==unique and all(set(r)==set(rows[0]) for r in output)
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
