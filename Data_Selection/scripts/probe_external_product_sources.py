"""Probe official public sources without logging authenticated request URLs."""
from pathlib import Path
import sys
import requests
from dotenv import dotenv_values
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.collectors.mfds_products import parse_page,ENDPOINT


def main():
    folder=ROOT/'data/raw/external_product_enrichment_20261102'
    folder.mkdir(parents=True,exist_ok=True)
    key=unquote(dotenv_values(ROOT/'.env').get('DATA_GO_KR_API_KEY') or '')
    try:
        response=requests.get(ENDPOINT+'/getHtfsItem01',params=dict(ServiceKey=key,pageNo=1,numOfRows=100,type='json'),timeout=35)
        print('domestic_http',response.status_code,flush=True)
        body,items=parse_page(response.content)
        print('total',body['totalCount'],'page_size',body['numOfRows'],'fields',list(items[0]),flush=True)
        (folder/'domestic_page_000001.json').write_bytes(response.content)
    except Exception as error:
        print('domestic_failed',type(error).__name__,flush=True)
    try:
        response=requests.get('https://impfood.mfds.go.kr/CFCCC01F01',timeout=35)
        print('import_http',response.status_code,flush=True)
        (folder/'import_search.html').write_bytes(response.content)
    except Exception as error:
        print('import_failed',type(error).__name__,flush=True)


if __name__=='__main__':main()
