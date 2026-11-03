"""Search every unmatched named product without a cutoff; report only, no mapping changes."""
from collections import Counter
import csv
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rapidfuzz import process
from rapidfuzz.distance import DamerauLevenshtein
from src.claim_evidence_experiment import name_key,GENERIC_PRODUCT_NAMES
from src.product_identity_filtered import FilteredProductCatalog,company_core
from src.product_name_groups import ProductGroups
from scripts.evaluate_relaxed_product_mapping import strip_brand


def main():
    folder=ROOT/'data/processed/product_functionality_handoff_y_final_name_first'
    cases=[r for r in json.loads((folder/'unmatched_named_cases.json').read_text(encoding='utf-8')) if not r['candidates']]
    catalog=FilteredProductCatalog(ROOT/'Data_List_Claim_Verification/claim_verification.sqlite')
    choices=[name_key(p['product_name']) for p in catalog.products]
    pairs={frozenset(company_core(v) for v in pair) for pair in json.loads((ROOT/'configs/manufacturer_pairs.json').read_text(encoding='utf-8'))['pairs']}
    grouping=ProductGroups([],pairs)
    output=[]
    for row in cases:
        raw,brand=row['product_name'],row.get('brand_name') or ''
        variants=[('original',raw),('brand_removed',strip_brand(raw,brand))]
        if brand and name_key(brand) not in name_key(raw):variants.append(('brand_added',brand+' '+raw))
        makers={grouping.company(m) for m in row.get('observed_manufacturers',[])}
        candidates={}
        used=[]
        seen=set()
        for method,text in variants:
            key=name_key(text)
            if not key or key in GENERIC_PRODUCT_NAMES or key in seen:continue
            seen.add(key)
            used.append(dict(method=method,text=text))
            for _,score,index in process.extract(key,choices,scorer=DamerauLevenshtein.normalized_similarity,score_cutoff=0,limit=5):
                product=catalog.products[index]
                pid=product['product_id']
                if pid not in candidates or candidates[pid]['score']<score*100:
                    candidates[pid]=dict(product,score=score*100,query_variant=method,query_text=text,
                                         manufacturer_match=grouping.company(product['company_name']) in makers if makers else None)
        ordered=sorted(candidates.values(),key=lambda p:(-p['score'],p['product_id']))[:5]
        output.append(dict(product_name=raw,brand_name=brand,observed_manufacturers=row.get('observed_manufacturers',[]),
                           query_variants=used,best_score=ordered[0]['score'] if ordered else None,
                           closest_products=ordered,videos=row['videos']))
    baseline=434
    total=510
    sweep=[]
    for threshold in (70,69,68,67,66,65,64,63,62,61,60,55,50):
        count=sum(r['best_score'] is not None and r['best_score']>=threshold for r in output)
        sweep.append(dict(threshold=threshold,additional_named_groups=count,
                          candidate_groups=baseline+count,candidate_rate=round(100*(baseline+count)/total,2)))
    summary=dict(searched_product_groups=len(cases),database_products=len(catalog.products),
                 best_score_bands=dict(Counter('60_to_below_70' if r['best_score'] is not None and r['best_score']>=60 else
                                              '50_to_below_60' if r['best_score'] is not None and r['best_score']>=50 else 'below_50_or_none' for r in output)),
                 threshold_sweep=sweep,mapping_outputs_modified=False,
                 note='Nearest string match is not a verified product. Candidate coverage only; no single-product selection or accuracy measured.')
    (folder/'unmatched_76_nearest_products.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    (folder/'unmatched_76_threshold_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    with (folder/'unmatched_76_nearest_products.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['입력 제품명','브랜드','입력 제조사','순위','DB 제품명','DB 제조사','DB product_id','이름 점수','검색에 사용한 이름','제조사 일치'])
        for r in output:
            for rank,p in enumerate(r['closest_products'],1):
                writer.writerow([r['product_name'],r['brand_name'],' / '.join(r['observed_manufacturers']),rank,
                                 p['product_name'],p['company_name'],p['product_id'],round(p['score'],2),p['query_text'],p['manufacturer_match']])
    lines=['# 미연결 76개 제품명 전체 검색','',
           'DB 전체 제품명을 비교한 문자상 최근접 후보임. 정답 또는 자동 연결 결과가 아님. 기존 전달 JSON은 변경하지 않음.','',
           '| 입력 제품명 | 브랜드 | 가장 가까운 DB 제품명 | DB 제조사 | 이름 점수 |',
           '|---|---|---|---|---:|']
    for r in output:
        p=r['closest_products'][0] if r['closest_products'] else {}
        cells=[r['product_name'],r['brand_name'] or '',p.get('product_name',''),p.get('company_name',''),str(round(p['score'],2)) if p else '']
        lines.append('| '+' | '.join(str(x).replace('|','/').replace('\n',' ') for x in cells)+' |')
    (folder/'unmatched_76_nearest_products.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    assert len(output)==76
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    print(json.dumps([dict(name=r['product_name'],brand=r['brand_name'],score=round(r['best_score'],2) if r['best_score'] is not None else None,
                           closest=r['closest_products'][0]['product_name'] if r['closest_products'] else None) for r in output[:12]],ensure_ascii=False,indent=2))


if __name__=='__main__':main()
