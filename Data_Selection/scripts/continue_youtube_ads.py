"""Continue existing YouTube policy with a reviewed 99-product batch.

Existing input/output schemas and collection conditions are unchanged.
Original downloaded/root exports remain untouched; cumulative, added-pair and
new-URL exports are written separately. Credentials are never printed.
"""
import argparse
from collections import Counter, defaultdict, deque
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import collect_youtube_ads as collector

FAMILIES=('락토핏','듀오락','드시모네','에버콜라겐','트루바이타민','락피도','프로메가',
          '셀티아이','닥터린','정관장','GNM','덴프스','아이클리어','아이커','아이클타임',
          '하이뮨','비에날씬','엘레나','뉴트리원','뉴트리디데이','안국','고려은단')


def save(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def pair_key(row):return str(row['id']),row['video_id']


def prepare(out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=out/'manifest.json'
    if manifest.exists():return json.loads(manifest.read_text(encoding='utf-8'))
    products=collector.load_products(ROOT/'products_for_search.json')
    with sqlite3.connect((ROOT/'state/collection.sqlite').resolve().as_uri()+'?mode=ro',uri=True) as db:
        done={r[0] for r in db.execute('SELECT key FROM done')}
        found={str(r[0]) for r in db.execute('SELECT DISTINCT product FROM results')}
        cache={r[0] for r in db.execute('SELECT key FROM cache')}
    previous_keys=set()
    raw_products={str(p['id']):p for p in products}
    for previous in (ROOT/'docs').glob('youtube*manifest.json'):
        for item in json.loads(previous.read_text(encoding='utf-8')).get('products',[]):
            if str(item['id']) in raw_products:previous_keys.add(raw_products[str(item['id'])]['product_key'])
    queues=defaultdict(deque)
    selected_keys=set(previous_keys)
    for p in products:
        if p['generic'] or str(p['id']) in found:continue
        if f'search-v{collector.POLICY_VERSION}:'+collector.fingerprint(p) in done:continue
        if p['product_key'] in selected_keys:continue
        family=next((name for name in FAMILIES if p['product_core'].casefold().startswith(name.casefold())),None)
        if family:
            queues[family].append(p)
            selected_keys.add(p['product_key'])
    chosen=[]
    while len(chosen)<99 and any(queues.values()):
        for family in FAMILIES:
            if queues[family] and len(chosen)<99:chosen.append(queues[family].popleft())
    if len(chosen)!=99:raise ValueError('Fewer than 99 fresh named-product queries; review selection before running')
    baseline=ROOT/'ad_video_urls.json'
    shutil.copyfile(baseline,out/'baseline_ad_video_urls.json')
    plan=dict(policy_version=collector.POLICY_VERSION,requested_products=len(chosen),
              selection='Round-robin named-product families; non-generic unique product keys; prior manifests, completed and found products excluded. No collection rule changes.',
              baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest(),
              input_sha256=hashlib.sha256((ROOT/'products_for_search.json').read_bytes()).hexdigest(),
              products=[{k:p[k] for k in ('id','product_name','company_name','product_core','generic')} for p in chosen])
    save(manifest,plan)
    return plan


def summarize(out,plan,code):
    before=json.loads((out/'baseline_ad_video_urls.json').read_text(encoding='utf-8'))
    after=json.loads((out/'ad_video_urls_all.json').read_text(encoding='utf-8'))
    old_pairs={pair_key(r) for r in before};old_urls={r['url'] for r in before}
    added=[r for r in after if pair_key(r) not in old_pairs]
    new_urls=[r for r in added if r['url'] not in old_urls]
    if not old_pairs<={pair_key(r) for r in after}:
        raise ValueError('Cumulative export lost existing records; do not replace original export')
    save(out/'ad_video_urls_added.json',added)
    save(out/'ad_video_urls_new_urls.json',new_urls)
    selected={str(p['id']) for p in plan['products']}
    state=collector.State(ROOT/'state')
    try:
        products=collector.load_products(ROOT/'products_for_search.json',selected_ids=selected)
        completed=[p for p in products if state.complete(f'search-v{collector.POLICY_VERSION}:'+collector.fingerprint(p))]
        assessments=[json.loads(r[0]) for r in state.db.execute('SELECT value FROM assessments')]
        assessments=[r for r in assessments if str(r['id']) in selected and r.get('logic_version')==collector.POLICY_VERSION]
        usage=state.db.execute('SELECT day,units,searches FROM usage ORDER BY day DESC LIMIT 1').fetchone()
    finally:state.db.close()
    summary=dict(requested_products=len(plan['products']),completed_products=len(completed),
                 pending_products=len(plan['products'])-len(completed),
                 before_product_video_pairs=len(before),before_unique_urls=len(old_urls),
                 added_product_video_pairs=len(added),new_unique_urls=len({r['url'] for r in new_urls}),
                 after_product_video_pairs=len(after),after_unique_urls=len({r['url'] for r in after}),
                 after_distinct_product_ids=len({str(r['id']) for r in after}),
                 added_statuses=dict(Counter(r['status'] for r in added)),
                 batch_assessment_statuses=dict(Counter(r['status'] for r in assessments)),
                 local_daily_usage=dict(day=usage[0],units=usage[1],searches=usage[2]) if usage else None,
                 exit_code=code,original_root_export_unchanged=hashlib.sha256((ROOT/'ad_video_urls.json').read_bytes()).hexdigest()==plan['baseline_sha256'],
                 note='URLs are collection candidates, not confirmed ads or product-identity judgments. Output schema and policy unchanged.')
    save(out/'summary.json',summary)
    print(json.dumps(summary,ensure_ascii=False,indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'exports/youtube_additional_20261104')
    args=parser.parse_args()
    plan=prepare(args.output_dir)
    if not args.run:
        print(json.dumps(dict(requested_products=len(plan['products']),manifest=str(args.output_dir/'manifest.json'),
                             samples=plan['products'][:8]),ensure_ascii=False,indent=2))
        return 0
    if hashlib.sha256((ROOT/'products_for_search.json').read_bytes()).hexdigest()!=plan['input_sha256']:
        raise ValueError('Product input changed since planning')
    backup=args.output_dir/'collection_before.sqlite'
    if not backup.exists():
        with sqlite3.connect((ROOT/'state/collection.sqlite').resolve().as_uri()+'?mode=ro',uri=True) as source,sqlite3.connect(backup) as dest:
            source.backup(dest)
    code=collector.main(['search','--ids',*[str(p['id']) for p in plan['products']],
        '--output',str(args.output_dir/'ad_video_urls_all.json'),
        '--report',str(args.output_dir/'collection_report.json'),'--max-api-calls','200'])
    summarize(args.output_dir,plan,code)
    return code


if __name__=='__main__':raise SystemExit(main())
