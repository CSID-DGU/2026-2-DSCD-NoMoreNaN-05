"""Probe access to the official imported-food labeling API, without key logs."""
from pathlib import Path
import sys
from urllib.parse import unquote
import requests
from dotenv import dotenv_values

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.collectors.mfds_products import parse_page


def main():
    key=unquote(dotenv_values(ROOT/'.env').get('DATA_GO_KR_API_KEY') or '')
    endpoint='https://apis.data.go.kr/1471000/IprtFoodPrdtKoreanLabelingItem/getIprtFoodPrdtKoreanLabelingItem'
    try:
        response=requests.get(endpoint,params=dict(serviceKey=key,pageNo=1,numOfRows=10,type='json',dclPrductSeCdNm='건강기능식품',prductKoreanNm='더블엑스'),timeout=35)
        print('http',response.status_code,flush=True)
        # Only report known numeric gateway errors, never raw request URLs.
        import re
        code=re.search(r'<returnReasonCode>([^<]+)',response.text)
        if code:print('gateway_code',code.group(1),flush=True)
        body,items=parse_page(response.content)
        print('total',body['totalCount'],'fields',list(items[0]) if items else [],flush=True)
        (ROOT/'data/raw/external_product_enrichment_20261102/import_api_probe.json').write_bytes(response.content)
    except Exception as error:print('import_api_failed',type(error).__name__,flush=True)


if __name__=='__main__':main()
