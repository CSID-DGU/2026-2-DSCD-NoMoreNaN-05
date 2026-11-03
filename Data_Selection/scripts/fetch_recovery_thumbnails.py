"""Fetch public thumbnails only for cached missing-product-name videos."""
import json
import argparse
from pathlib import Path
import re
import requests
from urllib.parse import urlparse,parse_qs

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir',type=Path,default=ROOT/'data/processed/product_functionality_handoff_real_t70')
    parser.add_argument('--mapping-dir',type=Path,help='Restrict download to still-unmatched missing/English product names in this result')
    args=parser.parse_args()
    folder=args.base_dir
    metadata=json.loads((folder/'recovery_cached_metadata.json').read_text(encoding='utf-8'))
    if args.mapping_dir:
        rows=json.loads((args.mapping_dir/'product_matches.json').read_text(encoding='utf-8'))
        ids={parse_qs(urlparse(r.get('url') or '').query).get('v',[''])[0] for r in rows if not r['candidates'] and
             (not r.get('product_name') or (re.search('[a-zA-Z]',r['product_name']) and not re.search('[가-힣]',r['product_name'])))}
        ids={k for k in ids if re.fullmatch(r'[A-Za-z0-9_-]{11}',k)}
        metadata={k:metadata.get(k,{}) for k in ids}
    output=folder/'recovery_thumbnails'
    output.mkdir(exist_ok=True)
    report=[]
    session=requests.Session()
    for video_id,info in metadata.items():
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}',video_id):
            raise ValueError('Invalid video ID')
        target=output/(video_id+'.jpg')
        if info.get('ocr_status')=='ok':
            report.append(dict(video_id=video_id,status='ocr_cached'))
            continue
        if target.exists():
            report.append(dict(video_id=video_id,status='cached',file=target.name))
            continue
        try:
            url='https://i.ytimg.com/vi/'+video_id+'/maxresdefault.jpg'
            response=session.get(url,timeout=10)
            if response.status_code==404:
                url='https://i.ytimg.com/vi/'+video_id+'/hqdefault.jpg'
                response=session.get(url,timeout=10)
            response.raise_for_status()
            if 'image' not in response.headers.get('content-type','') or len(response.content)>5*1024*1024:
                raise ValueError('Unexpected thumbnail response')
            target.write_bytes(response.content)
            report.append(dict(video_id=video_id,status='downloaded',file=target.name,source_url=url))
        except (requests.RequestException,ValueError):
            report.append(dict(video_id=video_id,status='unavailable'))
    (output/'downloads.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(dict(videos=len(report),available=sum(r['status']!='unavailable' for r in report)),ensure_ascii=False))


if __name__=='__main__':main()
