"""Read existing public video metadata/OCR caches for a fresh mapping run."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse,parse_qs

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir',type=Path,required=True)
    parser.add_argument('--attach-ocr',action='store_true')
    parser.add_argument('--reuse-metadata',type=Path,help='Reuse title/description/OCR for identical public video IDs')
    parser.add_argument('--fetch-missing',action='store_true',help='Fetch public oEmbed titles only for missing/English product names without cached metadata')
    args=parser.parse_args()
    folder=args.base_dir
    rows=json.loads((folder/'product_matches.json').read_text(encoding='utf-8'))
    ids={parse_qs(urlparse(r.get('url') or '').query).get('v',[''])[0] for r in rows if not r['candidates']}
    ids.discard('')
    target=folder/'recovery_cached_metadata.json'
    found=json.loads(target.read_text(encoding='utf-8')) if target.exists() else {}
    inherited=ROOT/'data/processed/product_functionality_handoff_real_t70/recovery_cached_metadata.json'
    if inherited.exists():
        for k,v in json.loads(inherited.read_text(encoding='utf-8')).items():
            if k in ids and k not in found:
                found[k]=dict(v)
                if 'thumbnail_ocr' in v:found[k]['ocr_reused']=True
    if args.reuse_metadata:
        for k,v in json.loads(args.reuse_metadata.read_text(encoding='utf-8')).items():
            if k in ids:
                found[k]=dict(found.get(k,{}),**v)
                if 'thumbnail_ocr' in v:found[k]['ocr_reused']=True
    cache=ROOT/'state/collection.sqlite'
    if cache.exists():
        with closing(sqlite3.connect(cache.resolve().as_uri()+'?mode=ro',uri=True)) as db:
            for (raw,) in db.execute('SELECT value FROM cache'):
                try: value=json.loads(raw)
                except json.JSONDecodeError:continue
                if not isinstance(value,dict):continue
                for item in value.get('items',[]):
                    key=item.get('id')
                    key=key.get('videoId') if isinstance(key,dict) else key
                    if key not in ids:continue
                    snippet=item.get('snippet',{})
                    score=lambda v:len(v.get('title',''))+len(v.get('description',''))
                    if score(snippet)>score(found.get(key,{})):
                        found[key]=dict(found.get(key,{}),**snippet)
    if args.attach_ocr:
        ocr=folder/'recovery_thumbnails/ocr.json'
        if ocr.exists():
            for r in json.loads(ocr.read_text(encoding='utf-8')):
                if r['video_id'] in ids and r['status']=='ok':
                    found.setdefault(r['video_id'],{}).update(thumbnail_ocr=r['text'],ocr_language=r.get('language'),ocr_status='ok',ocr_reused=False)
    fetch_report=[]
    if args.fetch_missing:
        import requests
        videos=json.loads((folder/'source_input.json').read_text(encoding='utf-8'))
        product_counts={v['video_id']:len(v.get('products',[])) for v in videos}
        eligible={parse_qs(urlparse(r.get('url') or '').query).get('v',[''])[0] for r in rows if not r['candidates'] and
                  (not r.get('product_name') or (re.search('[a-zA-Z]',r['product_name']) and not re.search('[가-힣]',r['product_name']) and product_counts[r['video_id']]==1))}
        missing=[k for k in eligible if re.fullmatch(r'[A-Za-z0-9_-]{11}',k) and not found.get(k,{}).get('title')]
        def fetch(video_id):
            try:
                response=requests.get('https://www.youtube.com/oembed',params={'url':'https://www.youtube.com/watch?v='+video_id,'format':'json'},timeout=8)
                response.raise_for_status()
                value=response.json()
                return video_id,dict(title=value.get('title',''),channelTitle=value.get('author_name',''),metadata_source='youtube_public_oembed'), 'ok'
            except (requests.RequestException,ValueError):
                return video_id,{},'unavailable'
        with ThreadPoolExecutor(max_workers=4) as pool:
            for video_id,value,status in pool.map(fetch,missing):
                fetch_report.append(dict(video_id=video_id,status=status))
                if status=='ok':found[video_id]=dict(found.get(video_id,{}),**value)
        (folder/'recovery_metadata_fetch_report.json').write_text(json.dumps(fetch_report,ensure_ascii=False,indent=2),encoding='utf-8')
    target.write_text(json.dumps(found,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(unmatched_video_ids=len(ids),cached_metadata=len(found),cached_ocr=sum(v.get('ocr_status')=='ok' for v in found.values()),
                         fetched_titles=sum(r['status']=='ok' for r in fetch_report),fetch_attempts=len(fetch_report)),ensure_ascii=False))


if __name__=='__main__':main()
