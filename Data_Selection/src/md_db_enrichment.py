"""Exact-key enrichment rules transcribed from db_enrichment_guide.md.

No fuzzy product/ingredient joins, no inferred ingredient names, no changes to
existing ingredient records. Original CSV cell values are retained on output.
"""
import csv
from collections import defaultdict,Counter
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP
import json
import re

HEALTH_FIELDS={'ENTRPS':'company_name','PRDUCT':'product_name','STTEMNT_NO':'manufacturing_report_number',
    'REGIST_DT':'registration_date','DISTB_PD':'shelf_life','SUNGSANG':'appearance','SRV_USE':'intake_method',
    'PRSRV_PD':'storage_and_distribution_standard','INTAKE_HINT1':'intake_precautions',
    'MAIN_FNCTN':'main_functionality','BASE_STANDARD':'specification'}
ITEM_FIELDS=['LCNS_NO','PRMS_DT','LAST_UPDT_DTM','INDUTY_CD_NM','PRDLST_CDNM','RAWMTRL_NM',
    'INDIV_RAWMTRL_NM','ETC_RAWMTRL_NM','CAP_RAWMTRL_NM','PRDT_SHAP_CD_NM','FRMLC_MTRQLT','FRMLC_MTHD']
STD_FIELDS=['RCOGN_NO','RAWMTRL_NM','DAY_INTK_LOWLIMIT','DAY_INTK_HIGHLIMIT','INTK_UNIT','INTK_MEMO',
    'SKLL_IX_IRDNT_RAWMTRL','PRIMARY_FNCLTY','IFTKN_ATNT_MATR_CN']
CLASS_FIELDS=['HELT_ITM_GRP_CD','HELT_ITM_GRP_NM','LCLAS_CD','LCLAS_NM','MLSFC_CD','MLSFC_NM','SCLAS_CD','SCLAS_NM']
DICT_FIELDS=['LCLAS_NM','MLSFC_NM','RPRSNT_RAWMTRL_NM','RAWMTRL_NCKNM','ENG_NM','SCNM','REGN_CD_NM','RAWMTRL_STATS_CD_NM','USE_CND_NM']
HISTORY_FIELDS=['CHNG_DT','LCNS_LEDG_CI_CDNM','CHNG_BF_CN','CHNG_AF_CN']
RECALL_FIELDS=['PRDTNM','RTRVLPRVNS','RTRVL_GRDCD_NM','RTRVLPLANDOC_RTRVLMTHD','MNFDT','DISTBTMLMT','FRMLCUNIT','BRCDNO','IMG_FILE_PATH','CRET_DTM']
ARRAY_FIELDS=['BSSH_CHNG_HIST','RAWMTRL_STD_INFO','RAWMTRL_CLASS_INFO','RAWMTRL_DICT_INFO','RECALL_INFO']
ADDED_FIELDS=ITEM_FIELDS+['BSSH_ADDR','BSSH_PRMS_DT','INSTT_NM']+ARRAY_FIELDS


def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:
        yield from csv.DictReader(stream)


def number(value):
    match=re.search(r'(\d{4})\s*-\s*(\d+)',value or '')
    return f'{match[1]}-{int(match[2])}' if match else ''


def material_key(value,remove_product=False):
    if remove_product:value=re.sub(r'\s*제품$','',value or '')
    return re.sub(r'[\s·\-,]','',re.sub(r'\(.*?\)','',value or '')).lower()


def split_materials(value):
    return [v.strip() for v in re.split(r',(?![^()]*\))',value or '') if v.strip()]


def pick(*values):
    return next((v for v in values if v is not None and str(v).strip()),'')


def distinct(values):
    result=[];seen=set()
    for value in values:
        key=json.dumps(value,ensure_ascii=False,sort_keys=True)
        if key not in seen:seen.add(key);result.append(value)
    return result


def numeric(value):
    match=re.match(r'\s*([+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?)(?=\s*(?:\(|$))',value or '')
    return Decimal(match[1].replace(',','')) if match else None


class EnrichmentSources:
    def __init__(self,paths):
        self.paths=paths
        self.health={r['STTEMNT_NO']:r for r in rows(paths['health'])}
        self.items={r['PRDLST_REPORT_NO']:r for r in rows(paths['items'])}
        self.missing=Counter();self.blocked={};self.precedence_notes=[]
        wanted={r['LCNS_NO'] for r in self.items.values()}
        self.business={}
        for row in rows(paths['business']):
            if row['LCNS_NO'] in wanted:
                prior=self.business.get(row['LCNS_NO'])
                if prior and (prior['ADDR'],prior['PRMS_DT'])!=(row['ADDR'],row['PRMS_DT']):
                    raise ValueError('Conflicting exact license rows; preflight required')
                self.business[row['LCNS_NO']]=row
        self.institution={}
        for row in rows(paths['collagen']):
            key=row['LCNS_NO'];value=row['INSTT_NM']
            if key in self.institution and self.institution[key]!=value:
                raise ValueError('Conflicting institution for license')
            self.institution[key]=value
        self.history=defaultdict(list)
        for row in rows(paths['history']):
            self.history[row['LCNS_NO']].append({k:row[k] for k in HISTORY_FIELDS})
        self.recalls=defaultdict(list)
        for row in rows(paths['recall']):
            if row['PRDLST_REPORT_NO']:
                self.recalls[row['PRDLST_REPORT_NO']].append({k:row[k] for k in RECALL_FIELDS})
        std_numbers=defaultdict(list);std_names=defaultdict(list);approved=defaultdict(list)
        for row in rows(paths['standard']):
            code=number(row['PRDCT_NM'])
            if code:std_numbers[code].append(row)
            else:std_names[material_key(row['PRDCT_NM'],True)].append(row)
        for row in rows(paths['approved']):approved[number(row['HF_FNCLTY_MTRAL_RCOGN_NO'])].append(row)
        self.standard_number={};self.standard_name={}
        for code in sorted(set(std_numbers)|set(approved)):
            left,right=std_numbers.get(code,[]),approved.get(code,[])
            why=None
            if len(left)>1 or len(right)>1:why='duplicate_recognition_number'
            if code in {'2025-58','2022-35','2013-5'}:why='guide_flagged_intake_conflict'
            if not why and left and right:
                for k in ['DAY_INTK_LOWLIMIT','DAY_INTK_HIGHLIMIT']:
                    a,b=numeric(left[0][k]),numeric(right[0][k])
                    if a is not None and b is not None and a!=b:
                        # The guide explicitly gives I2710 precedence when I0050
                        # contains a rounded integer (for example 1.8 -> 2).
                        if b==a.quantize(Decimal('1'),rounding=ROUND_HALF_UP):
                            self.precedence_notes.append(dict(recognition_number=code,field=k,I2710=left[0][k],I0050=right[0][k],rule='documented_I2710_rounding_precedence'))
                        else:why='cross_source_intake_conflict'
            if why:
                self.blocked[code]=dict(reason=why,I2710=left,I0050=right)
                continue
            self.standard_number[code]=self.combine_standard(code,left[0] if left else {},right[0] if right else {})
        for key,values in std_names.items():
            if len(values)==1:self.standard_name[key]=self.combine_standard('',values[0],{})
            else:self.blocked['name:'+key]=dict(reason='duplicate_exact_material_name',I2710=values,I0050=[])
        self.classes=defaultdict(list)
        for row in rows(paths['class']):self.classes[material_key(row['HELT_ITM_GRP_NM'],True)].append({k:row[k] for k in CLASS_FIELDS})
        self.dictionary=defaultdict(list)
        for row in rows(paths['dictionary']):self.dictionary[material_key(row['RPRSNT_RAWMTRL_NM'])].append({k:row[k] for k in DICT_FIELDS})

    @staticmethod
    def combine_standard(code,std,approved):
        return dict(RCOGN_NO=code,RAWMTRL_NM=pick(approved.get('RAWMTRL_NM'),std.get('PRDCT_NM')),
            DAY_INTK_LOWLIMIT=pick(std.get('DAY_INTK_LOWLIMIT'),approved.get('DAY_INTK_LOWLIMIT')),
            DAY_INTK_HIGHLIMIT=pick(std.get('DAY_INTK_HIGHLIMIT'),approved.get('DAY_INTK_HIGHLIMIT')),
            INTK_UNIT=pick(std.get('INTK_UNIT'),approved.get('WT_UNIT')),INTK_MEMO=std.get('INTK_MEMO',''),
            SKLL_IX_IRDNT_RAWMTRL=std.get('SKLL_IX_IRDNT_RAWMTRL',''),
            PRIMARY_FNCLTY=pick(approved.get('PRIMARY_FNCLTY'),std.get('PRIMARY_FNCLTY')),
            IFTKN_ATNT_MATR_CN=pick(approved.get('IFTKN_ATNT_MATR_CN'),std.get('IFTKN_ATNT_MATR_CN')))

    def product_fields(self,report):
        row=self.items.get(report)
        if row is None:return {k:None for k in ADDED_FIELDS}
        result={k:row[k] for k in ITEM_FIELDS}
        license=row['LCNS_NO'];business=self.business.get(license,{})
        result.update(BSSH_ADDR=business.get('ADDR'),BSSH_PRMS_DT=business.get('PRMS_DT'),INSTT_NM=self.institution.get(license))
        result['BSSH_CHNG_HIST']=distinct(self.history.get(license,[]))
        result['RECALL_INFO']=distinct(self.recalls.get(report,[]))
        standard=[];seen=set()
        functional=split_materials(row['RAWMTRL_NM'])
        individual=split_materials(row['INDIV_RAWMTRL_NM'])
        for material in functional+[m for m in individual if '(고시형)' in m or number(m)]:
            code=number(material);key=code or material_key(material,True)
            if key in seen:continue
            seen.add(key)
            found=self.standard_number.get(code) if code else self.standard_name.get(key)
            if found:standard.append(found)
            else:self.missing[('standard',material,'blocked' if code in self.blocked or 'name:'+key in self.blocked else 'no_exact_match')]+=1
        result['RAWMTRL_STD_INFO']=standard
        classes=[]
        for material in functional:
            found=self.classes.get(material_key(material,True),[])
            classes.extend(found)
            if not found:self.missing[('class',material,'no_exact_match')]+=1
        result['RAWMTRL_CLASS_INFO']=distinct(classes)
        dictionary=[]
        for material in individual:
            found=self.dictionary.get(material_key(material),[])
            dictionary.extend(found)
            if not found:self.missing[('dictionary',material,'no_exact_match')]+=1
        result['RAWMTRL_DICT_INFO']=distinct(dictionary)
        return result
