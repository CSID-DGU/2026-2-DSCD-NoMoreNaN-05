"""Add traceable notation/abbreviation/context candidates to a saved mapping.

No invented translations or cross-product claim assignments. By default only
no-candidate entries change; --prefer-notation also refines fuzzy-only matches.
"""
from collections import Counter,defaultdict
from contextlib import closing
from functools import lru_cache
import copy
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata
from urllib.parse import parse_qs,urlparse

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.claim_evidence_experiment import GENERIC_PRODUCT_NAMES,name_key
from src.product_identity_filtered import company_core
from scripts.evaluate_relaxed_product_mapping import strip_brand
from scripts.disambiguate_product_candidates import resolve_multiple
from scripts.export_product_functionality_handoff import build_record,FIELDS


def notation_key(value):
    text=unicodedata.normalize('NFKC',re.sub(r'[™®©]','',value or '')).casefold()
    text=re.sub(r'[\u4e00-\u9fff]+\s*\(([가-힣\s]+)\)',r'\1',text)
    text=re.sub(r'[™®©]','',text)
    # Decimal/range separators between digits also distinguish dose/version:
    # never collapse 1.0 to 10 or 1-2 to 12.
    text=re.sub(r'(?<!\d)[.\-]|[.\-](?!\d)','',text)
    return re.sub(r'[^가-힣a-z0-9+%µμ.\-]','',text)


@lru_cache(maxsize=100000)
def normalized_text(text):
    return unicodedata.normalize('NFKC',re.sub(r'[™®©]','',text or '')).casefold()


@lru_cache(maxsize=100000)
def compiled_phrase(needle):
    tokens=normalized_text(needle).split()
    if not tokens:
        return None
    pattern=r'(?<![가-힣a-z0-9])'+r'\s*'.join(re.escape(t) for t in tokens)+r'(?![가-힣a-z0-9])'
    return re.compile(pattern)


def phrase_in(needle,haystack):
    pattern=compiled_phrase(needle)
    return bool(pattern and pattern.search(normalized_text(haystack)))


def brand_present(brand,text):
    return bool(brand and notation_key(brand) in notation_key(text))


def same_numbers(a,b):
    left=set(re.findall(r'\d+(?:\.\d+)?',a))
    right=set(re.findall(r'\d+(?:\.\d+)?',b))
    return not left or not right or left==right


class RecoveryIndex:
    def __init__(self,products,ingredient_names=()):
        self.products=products
        self.generic=set(GENERIC_PRODUCT_NAMES)|{name_key(n) for n in ingredient_names}|{
            '프로바이오틱스','속편한유산균','프리미엄유산균','장건강유산균','장건강프로바이오틱스',
            '멀티비타민미네랄','비타민d','비타민c','브로멜라인','베이비','키즈','캡슐','데일리',
            '다이어트','코엔자임q10','포스파티딜세린','비타민b1','비타민b2','비타민b6','비타민b12'}
        self.keys={p['product_id']:name_key(p['product_name']) for p in products}
        self.numbers={p['product_id']:set(re.findall(r'\d+(?:\.\d+)?',p['product_name'])) for p in products}
        self.notation=defaultdict(list)
        self.bilingual=defaultdict(list)
        self.context_trie={}
        self.context_cache={}
        for p in products:
            self.notation[notation_key(p['product_name'])].append(p)
            if len(self.keys[p['product_id']])>=5 and self.keys[p['product_id']] not in self.generic:
                node=self.context_trie
                for char in ''.join(normalized_text(p['product_name']).split()):
                    node=node.setdefault(char,{})
                node.setdefault(None,[]).append(p)
            for alias in re.findall(r'\(([^()]*)\)',p['product_name']):
                if re.search(r'[a-zA-Z]',alias) and not re.search(r'[가-힣]',alias) and len(notation_key(alias))>=5:
                    if notation_key(alias) not in {'capsule','powder','tablet','export','probiotics'}:
                        self.bilingual[notation_key(alias)].append(p)

    def context_products(self,text):
        """Scan known full names once, keeping original text word boundaries."""
        text=normalized_text(text)
        if text in self.context_cache:return self.context_cache[text]
        positions=[i for i,char in enumerate(text) if not char.isspace()]
        compact=''.join(text[i] for i in positions)
        def word(char):return '가'<=char<='힣' or 'a'<=char<='z' or '0'<=char<='9'
        found={}
        for start,char in enumerate(compact):
            origin=positions[start]
            if (origin and word(text[origin-1])) or char not in self.context_trie:continue
            node=self.context_trie
            for end in range(start,len(compact)):
                node=node.get(compact[end])
                if node is None:break
                after=positions[end]+1
                if None in node and (after==len(text) or not word(text[after])):
                    for p in node[None]:found[p['product_id']]=p
        result=list(found.values())
        if len(self.context_cache)<4096:self.context_cache[text]=result
        return result

    def exact_notation(self,row):
        raw=row.get('product_name') or ''
        brand=row.get('brand_name') or ''
        variants=[raw,strip_brand(raw,brand)]
        if brand and raw and not brand_present(brand,raw):
            variants.append(brand+' '+raw)
        previous=row.get('previous_match',{})
        report=None if previous.get('report_policy')=='fallback_only' else previous.get('observed_report_number')
        result={}
        for variant in variants:
            key=notation_key(variant)
            if len(key)<3 or key in self.generic:continue
            for p in self.notation.get(key,[])+self.bilingual.get(key,[]):
                if not report or name_key(report)==name_key(p['manufacturing_report_number']):
                    result[p['product_id']]=p
        return list(result.values())

    def search(self,row,video,metadata):
        raw=row.get('product_name') or ''
        brand=row.get('brand_name') or ''
        observed_bilingual=bool(re.search(r'[a-zA-Z]',raw)) and not re.search(r'[가-힣]',raw) and len(video.get('products',[]))==1
        observations=[]
        source=''
        variants=[raw,strip_brand(raw,brand)] if raw else []
        previous=row.get('previous_match',{})
        report=None if previous.get('report_policy')=='fallback_only' else previous.get('observed_report_number')
        def allowed(p):
            return not report or name_key(report)==name_key(p['manufacturing_report_number'])
        candidates={}
        if raw and (name_key(raw) not in self.generic or brand):
            for variant in variants:
                key=notation_key(variant)
                if len(key)<3 or key in self.generic:
                    continue
                for p in self.notation.get(key,[])+self.bilingual.get(key,[]):
                    if allowed(p):candidates[p['product_id']]=p
            if candidates:
                return list(candidates.values()),'notation_or_db_bilingual_alias',[dict(source='input_product_name',text=raw)]
            # A short name must be scoped by the observed brand. No generic
            # brand-stripped keyword such as '키즈 골드' is searched across all DB.
            phrases=[]
            if len(name_key(raw))>=4 and name_key(raw) not in self.generic and (not brand or brand_present(brand,raw)):
                phrases.append(raw)
            if brand and not brand_present(brand,raw):
                phrases.append(brand+' '+raw)
            raw_numbers=set(re.findall(r'\d+(?:\.\d+)?',raw))
            for p in self.products:
                numbers=self.numbers[p['product_id']]
                if not allowed(p) or (raw_numbers and numbers and raw_numbers!=numbers) or self.keys[p['product_id']] in self.generic:
                    continue
                full=p['product_name']
                forward=any(phrase_in(q,full) for q in phrases)
                reverse=len(self.keys[p['product_id']])>=6 and phrase_in(full,raw) and (not brand or brand_present(brand,full))
                if forward or reverse:
                    candidates[p['product_id']]=p
            if candidates:
                return list(candidates.values()),'whole_phrase_brand_scoped',[dict(source='input_product_name',text=raw)]
            if not observed_bilingual:
                return [],'no_recovery',[]
        if raw and not observed_bilingual:
            return [],'generic_name_not_expanded',[]
        # Missing product name: exact, distinctive DB names in this product's
        # own claims are preferred over whole-video title/description.
        own=[dict(source='claim',claim_id=c.get('claim_id'),text=c.get('text') or '')
             for c in video.get('claims',[]) if c.get('product_ref')==row['product_ref']]
        single_video_product=len(video.get('products',[]))==1
        other_same_brand=any(p.get('product_ref')!=row['product_ref'] and name_key(p.get('brand_name'))==name_key(brand)
                             for p in video.get('products',[])) if brand else False
        metadata_allowed=single_video_product or bool(brand and not other_same_brand)
        external=[[dict(source='video_title',text=metadata.get('title',''))],
                  [dict(source='video_description',text=metadata.get('description',''))],
                  [dict(source='video_thumbnail_ocr',text=metadata.get('thumbnail_ocr',''))]] if metadata_allowed else []
        contexts=external+[own] if observed_bilingual else [own]+external
        for group in contexts:
            for context in group:
                for p in self.context_products(context['text']):
                    full=p['product_name']
                    if not allowed(p):continue
                    if brand and not brand_present(brand,full) and len(name_key(full))<6:continue
                    if group is not own and not single_video_product and not brand_present(brand,full):continue
                    candidates[p['product_id']]=p
                    observations.append(dict(context,matched_product_name=full))
            if candidates:
                # Prefer the specific full name over its overlapping base name
                # in the same title/claim, without discarding duplicate DB rows.
                keep={pid:p for pid,p in candidates.items() if not any(
                    self.keys[pid]!=self.keys[other] and self.keys[pid] in self.keys[other]
                    for other in candidates)}
                candidates=keep
                kept_names={p['product_name'] for p in candidates.values()}
                observations=[o for o in observations if o['matched_product_name'] in kept_names]
                source='video_observed_bilingual_name' if observed_bilingual else 'recovered_from_own_claims' if group is own else 'recovered_from_thumbnail_ocr' if group[0]['source']=='video_thumbnail_ocr' else 'recovered_from_video_metadata'
                return list(candidates.values()),source,observations
        return [],'missing_name_not_recoverable',[]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir',type=Path,default=ROOT/'data/processed/product_functionality_handoff_real_t70')
    parser.add_argument('--output-dir',type=Path,default=ROOT/'data/processed/product_functionality_handoff_real_t70_recovered')
    parser.add_argument('--prefer-notation',action='store_true',help='Prefer exact normalized/bilingual names over earlier fuzzy-only candidates')
    parser.add_argument('--database',type=Path,default=ROOT/'Data_List_Claim_Verification/claim_verification.sqlite')
    args=parser.parse_args()
    base,out=args.base_dir,args.output_dir
    rows=json.loads((base/'product_matches.json').read_text(encoding='utf-8'))
    previous_connected=sum(bool(r['candidates']) for r in rows)
    previous_selected=sum(r.get('selected_product') is not None for r in rows)
    base_summary=json.loads((base/'summary.json').read_text(encoding='utf-8'))
    videos=json.loads((base/'source_input.json').read_text(encoding='utf-8'))
    by_video={v['video_id']:v for v in videos}
    cached_path=base/'recovery_cached_metadata.json'
    metadata=json.loads(cached_path.read_text(encoding='utf-8')) if cached_path.exists() else {}
    config=json.loads((ROOT/'configs/manufacturer_pairs.json').read_text(encoding='utf-8'))
    pairs={frozenset(company_core(v) for v in p) for p in config['pairs']}
    with closing(sqlite3.connect(args.database.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        db.row_factory=sqlite3.Row
        products=[dict(r) for r in db.execute('SELECT '+','.join(FIELDS)+' FROM products')]
        ingredient_names=[r[0] for r in db.execute('SELECT ingredient_name FROM ingredients')]
        version=db.execute("SELECT loaded_at FROM dataset_registry WHERE dataset_key='products'").fetchone()[0]
    product_rows={p['product_id']:p for p in products}
    ingredient_names += [re.sub(r'\([^()]*\)','',n) for n in ingredient_names]
    ingredient_names += [term for v in videos for c in v.get('claims',[]) for term in c.get('ingredients',[]) or [] if isinstance(term,str)]
    index=RecoveryIndex(products,ingredient_names)
    # Candidate rows exclude functionality to keep audit compact.
    def identity(p):return {k:v for k,v in p.items() if k!='main_functionality'}
    added=[]
    refined=[]
    for row in rows:
        was_connected=bool(row['candidates'])
        if was_connected and (not args.prefer_notation or not row['route'].startswith('full_name_distance_')):continue
        video=by_video[row['video_id']]
        external_id=parse_qs(urlparse(row['url']).query).get('v',[''])[0]
        if was_connected:
            candidates=index.exact_notation(row)
            route='exact_notation_over_fuzzy'
            observations=[dict(source='input_product_name',text=row.get('product_name'))] if candidates else []
            if not candidates:continue
            row['previous_fuzzy_candidates']=row['candidates']
        else:
            candidates,route,observations=index.search(row,video,metadata.get(external_id,{}))
        row['recovery_attempt']=dict(route=route,observations=observations)
        if not candidates:
            continue
        row['route']=route
        row['candidates']=[identity(p) for p in candidates]
        row['candidate_count']=len(candidates)
        row['top_name_score']=None  # Not a distance score; never invent 100.
        row['status']='single_candidate' if len(candidates)==1 else 'multiple_candidates'
        if len(candidates)==1:
            row['selected_product']=row['candidates'][0]
            row['selection_status']='single_recovery_candidate'
        else:
            # Prior comparison rules require an exact-name route for pair
            # expansion. Recovery remains normalized-company-only here.
            narrowed,reason=resolve_multiple(row,pairs)
            row['manufacturer_filtered_candidates']=narrowed
            row['manufacturer_resolution']=reason
            row['selected_product']=narrowed[0] if len(narrowed)==1 else None
            row['selection_status']=('selected_by_brand' if row.get('comparison_company_field')=='brand_name' else 'selected_by_manufacturer') if len(narrowed)==1 else 'unresolved_multiple'
        (refined if was_connected else added).append(copy.deepcopy(row))
    records=[]
    for row in rows:
        record=build_record(by_video[row['video_id']],row,product_rows,version,pairs)
        if row.get('recovery_attempt',{}).get('observations'):
            record['product']['match']['status']='unresolved'
            record['product']['match']['method']=None
            record['product']['match']['note']='추가 검색 후보: '+row['route']+'; 동일 제품 확인 필요'
            record['product']['match']['recovery_sources']=row['recovery_attempt']['observations']
        records.append(record)
    for v in videos:
        refs={p['product_ref'] for p in v.get('products',[])}
        claims=[copy.deepcopy(c) for c in v.get('claims',[]) if c.get('product_ref') not in refs]
        if claims:
            records.append(dict(video_id=v['video_id'],url=v.get('url'),product_ref=None,db_version=version,
                                product=dict(match=dict(status='unresolved',method=None,note='입력 제품 참조 없음'),evi_product=None),claims=claims))
    selected=[r for r in records if r['product']['evi_product'] is not None]
    def keys(items):return Counter(json.dumps([r['video_id'],c],sort_keys=True,ensure_ascii=False) for r in items for c in r.get('claims',[]))
    assert keys(records)==keys(videos)
    counts=Counter(r['route'] for r in added)
    connected=sum(bool(r['candidates']) for r in rows)
    summary=dict(products=len(rows),previous_connected=previous_connected,previous_selected=previous_selected,additional_candidates=len(added),
                 input_file=base_summary.get('input_file'),input_sha256=base_summary.get('input_sha256'),
                 input_videos=len(videos),input_claims=sum(len(v.get('claims',[])) for v in videos),
                 threshold=base_summary.get('name_similarity_threshold'),brand_recombine=base_summary.get('brand_recombine',False),
                 report_fallback_only=base_summary.get('report_fallback_only',False),
                 company_comparison_field=base_summary.get('company_comparison_field','manufacturer_name'),
                 connected_products=connected,candidate_rate=round(100*connected/len(rows),2),
                 selected_products=len(selected),selected_rate=round(100*len(selected)/len(rows),2),
                 additional_selected=sum(r['selected_product'] is not None for r in added),recovery_routes=dict(counts),
                 prefer_notation=args.prefer_notation,notation_refined_products=len(refined),
                 remaining_no_candidates=sum(not r['candidates'] for r in rows),
                 remaining_multiple=sum(r['selected_product'] is None and bool(r['candidates']) for r in rows),
                 all_claims=sum(len(r['claims']) for r in records),selected_claims=sum(len(r['claims']) for r in selected),
                 cached_recovery_video_metadata_count=len(metadata),
                 cached_null_name_video_metadata_count=len({parse_qs(urlparse(r['url']).query).get('v',[''])[0] for r in rows if not r['product_name']} & set(metadata)),
                 missing_name_entries=sum(not r['product_name'] for r in rows),
                 recovered_missing_name_entries=sum(not r['product_name'] for r in added),
                 ocr_executed=any(v.get('ocr_status')=='ok' and not v.get('ocr_reused',False) for v in metadata.values()),
                 ocr_information_available=any('thumbnail_ocr' in v for v in metadata.values()),video_download_executed=False,ranking_executed=False,
                 thumbnail_ocr_images=sum(v.get('ocr_status')=='ok' for v in metadata.values()),
                 thumbnail_ocr_images_reused=sum(v.get('ocr_status')=='ok' and v.get('ocr_reused',False) for v in metadata.values()),
                 note='New recoveries are review candidates, not confirmed identities. Original input/previous mappings unchanged.')
    groups=defaultdict(list)
    for r in rows:
        if name_key(r.get('product_name')):
            groups[(name_key(r['product_name']),name_key(r.get('brand_name')))].append(r)
    summary['deduplicated_named_input_products']=len(groups)
    summary['deduplicated_candidate_groups']=sum(any(r['candidates'] for r in g) for g in groups.values())
    summary['deduplicated_selected_groups']=sum(any(r.get('selected_product') for r in g) for g in groups.values())
    summary['selected_unique_urls']=len({r['url'] for r in selected if r.get('url')})
    summary['selected_unique_db_products']=len({r['product']['evi_product']['product_id'] for r in selected})
    out.mkdir(parents=True,exist_ok=True)
    for name,value in {'summary.json':summary,'product_matches.json':rows,'recovered_candidates.json':added,'notation_refinements.json':refined,
                       'mapped_products.json':selected,'all_results.json':records}.items():
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'source_input.json').write_bytes((base/'source_input.json').read_bytes())
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)
    print(json.dumps([dict(name=r['product_name'],brand=r['brand_name'],route=r['route'],candidate_names=[p['product_name'] for p in r['candidates']][:5]) for r in added[:12]],ensure_ascii=False,indent=2))


if __name__=='__main__':main()
