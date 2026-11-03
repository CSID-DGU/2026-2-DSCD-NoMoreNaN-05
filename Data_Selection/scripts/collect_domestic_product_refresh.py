"""Fetch resumable current MFDS detail pages; credentials never logged."""
import concurrent.futures
import json
import math
from pathlib import Path
import sys
import time
from urllib.parse import unquote
import requests
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.collectors.mfds_products import parse_page, ENDPOINT, FIELDS, write_json


def main():
    folder=ROOT/'data/raw/external_product_enrichment_20261102'
    output=ROOT/'data/processed/external_product_enrichment_20261102'
    output.mkdir(parents=True,exist_ok=True)
    key=unquote(dotenv_values(ROOT/'.env').get('DATA_GO_KR_API_KEY') or '')
    if not key:raise RuntimeError('Missing API credential')
    def fetch(page):
        path=folder/f'domestic_page_{page:06d}.json'
        if path.exists():content=path.read_bytes()
        else:
            content=None
            for attempt in range(4):
                try:
                    response=requests.get(ENDPOINT+'/getHtfsItem01',params=dict(ServiceKey=key,pageNo=page,numOfRows=100,type='json'),timeout=(10,40))
                    if response.status_code!=200:raise RuntimeError('HTTP status '+str(response.status_code))
                    parse_page(response.content)
                    content=response.content
                    break
                except Exception:
                    if attempt==3:raise RuntimeError(f'Domestic fetch failed at page {page}; cached pages retained') from None
                    time.sleep(2**attempt)
            path.write_bytes(content)
        body,items=parse_page(content)
        if int(body['pageNo'])!=page:raise RuntimeError('Wrong page returned')
        return page,int(body['totalCount']),items
    _,total,first=fetch(1)
    all_pages={1:first}
    count=math.ceil(total/100)
    write_json(output/'domestic_collection_status.json',dict(status='running',total_count=total,pages=count,source=ENDPOINT+'/getHtfsItem01'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for page,returned,items in pool.map(fetch,range(2,count+1)):
            if returned!=total:raise RuntimeError('API totalCount changed during collection')
            if len(items)!=min(100,total-(page-1)*100):raise RuntimeError('Incomplete page')
            all_pages[page]=items
            if page%25==0:print(f'Domestic pages {page}/{count}',flush=True)
    rows=[r for page in sorted(all_pages) for r in all_pages[page]]
    assert len(rows)==total
    reports=[r.get('STTEMNT_NO') for r in rows]
    if len(reports)!=len(set(reports)):raise RuntimeError('Repeated report numbers; inspect source before enrichment')
    products=[dict({name:r.get(field) for field,name in FIELDS.items()},original_fields=r) for r in rows]
    write_json(output/'domestic_latest_products.json',products)
    write_json(output/'domestic_collection_status.json',dict(status='complete',total_count=total,pages=count,source=ENDPOINT+'/getHtfsItem01'))
    print('Domestic complete:',len(products),flush=True)


if __name__=='__main__':
    try:main()
    except Exception as error:
        print('Collection stopped:',type(error).__name__,flush=True)
        raise SystemExit(1)
