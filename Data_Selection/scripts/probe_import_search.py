"""Check the public imported-food search form using its documented UI fields."""
from pathlib import Path
import re
import requests

ROOT=Path(__file__).resolve().parents[1]


def main():
    folder=ROOT/'data/raw/external_product_enrichment_20261102'
    html=(folder/'import_search.html').read_text(encoding='utf-8')
    select=re.search(r'<select[^>]*id="dclPrductSeCd".*?</select>',html,re.S).group()
    print(re.sub(r'\s+',' ',select)[:1500],flush=True)
    session=requests.Session()
    session.get('https://impfood.mfds.go.kr/CFCCC01F01',timeout=40)
    form=re.search(r'<form id="frmSrch".*?</form>',html,re.S).group()
    params={}
    for tag in re.findall(r'<input\b[^>]*>',form):
        attrs=dict(re.findall(r'(\w+)="([^"]*)"',tag))
        if attrs.get('type')!='checkbox' and 'name' in attrs:params[attrs['name']]=attrs.get('value','')
    params.update(page='1',limit='50',dclPrductSeCd='7',prductNm='더블엑스',srchStrtDt='2026-08-02',srchEndDt='2026-11-02',srchNtncd='')
    response=session.post('https://impfood.mfds.go.kr/CFCCC01F01/getList',data=params,headers={'Referer':'https://impfood.mfds.go.kr/CFCCC01F01'},timeout=40)
    print('http',response.status_code,flush=True)
    (folder/'import_probe.html').write_bytes(response.content)
    table=re.search(r'<table[^>]*class="board_list.*?</table>',response.text,re.S)
    print((table.group() if table else 'No result table')[:15000],flush=True)
    response=session.get('https://www.data.go.kr/data/15110214/openapi.do',timeout=40)
    (folder/'import_api_docs.html').write_bytes(response.content)
    print('docs_http',response.status_code,'size',len(response.content),flush=True)


if __name__=='__main__':
    try:main()
    except Exception as error:print(type(error).__name__)
