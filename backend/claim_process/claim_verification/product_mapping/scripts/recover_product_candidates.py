"""Add traceable notation/abbreviation/context candidates to a saved mapping.

No invented translations or cross-product claim assignments. By default only
no-candidate entries change; --prefer-notation also refines fuzzy-only matches.
"""
from collections import Counter,defaultdict
from contextlib import closing
from functools import lru_cache
import copy
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import unicodedata
from urllib.parse import parse_qs,urlparse

from ..src.claim_evidence_experiment import GENERIC_PRODUCT_NAMES,name_key
from ..src.product_identity_filtered import company_core
from .evaluate_relaxed_product_mapping import strip_brand
from .disambiguate_product_candidates import resolve_multiple
from .export_product_functionality_handoff import build_record,FIELDS


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
