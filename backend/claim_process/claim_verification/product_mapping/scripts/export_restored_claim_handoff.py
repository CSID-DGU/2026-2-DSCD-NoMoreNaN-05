"""Restore the agreed claim_type_db_format.md schema, without v2 fields.

Reuse the saved 70-point search; resolve companies before deciding status.
Only actual report-number or name/company agreement uses the corresponding
agreed method. No blanket unresolved for recovered matches; no arbitrary
promotion of competing candidates. Diagnostics stay outside the handoff JSON.
"""
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import zipfile

from ..src.claim_type_db_format import build_product, TYPE_FIELDS, ARRAYS
from ..src.claim_product_identity import declarations
from ..src.claim_evidence_experiment import name_key
from ..src.product_identity_filtered import company_core
from ..src.product_name_groups import ProductGroups
from .export_candidate_db_handoff import source_ids


def select_product(original,row,claims,grouping):
    ids=source_ids(row)
    keys={grouping.key(grouping.products[pid]) for pid in ids}
    maker=original.get('manufacturer_name')
    # Only explicit declarations, and only names present among retrieved companies.
    observed=declarations(claims,original['product_ref'])
    matching_claim_makers={grouping.company(o['value']) for o in observed
        if o['role']=='manufacturer_name' and any(grouping.company(o['value'])==k[1] for k in keys)}
    source=None;companies=set()
    if maker:
        source='manufacturer_name';companies={grouping.company(maker)}
        if matching_claim_makers and companies!=matching_claim_makers:
            return None,None,'input_and_claim_manufacturer_conflict',ids,source
    elif matching_claim_makers:
        source='same_product_claim_manufacturer';companies=matching_claim_makers
    elif original.get('brand_name'):
        source='brand_name';companies={grouping.company(original['brand_name'])}
    if len(companies)>1:
        return None,None,'multiple_declared_manufacturers',ids,source
    matching=[k for k in keys if k[1] in companies]
    if len(matching)==1:
        group=grouping.group(matching[0])
        rows=group['rows']
        # Prefer the observed legal manufacturer/factory when available.
        if maker:
            from ..src.claim_evidence_experiment import company_key
            exact_site=[p for p in rows if company_key(p['company_name'])==company_key(maker)]
            exact_legal=[p for p in rows if company_core(p['company_name'])==company_core(maker)]
            rows=exact_site or exact_legal or rows
        report=name_key(original.get('manufacturing_report_number'))
        preferred=[p for p in rows if report and name_key(p['manufacturing_report_number'])==report]
        chosen=min(preferred or rows,key=lambda p:p['product_id'])
        return chosen,'name_and_company','unique_name_company_group',ids,source
    # The agreed report policy is fallback, not a veto against a name/company match.
    report=name_key(original.get('manufacturing_report_number'))
    reported=grouping.reports.get(report,[]) if report else []
    report_groups={grouping.key(p) for p in reported}
    if len(report_groups)==1:
        if maker and any(grouping.company(p['company_name'])!=grouping.company(maker) for p in reported):
            return None,None,'report_and_manufacturer_conflict',ids,source
        chosen=min(reported,key=lambda p:p['product_id'])
        return chosen,'report_number','report_number_fallback',sorted(set(ids)|{p['product_id'] for p in reported}),source
    if not ids:return None,None,'no_candidates',ids,source
    if len(matching)>1:return None,None,'multiple_name_company_groups',ids,source
    if maker:return None,None,'manufacturer_conflict',ids,source
    if len(keys)==1:return None,None,'name_only_company_not_verified',ids,source
    return None,None,'no_unique_company_matching_group',ids,source


def validate(videos,originals):
    assert len(videos)==len(originals)
    for video,original in zip(videos,originals):
        assert set(video)=={'video_id','url','db_version','products','claims'}
        assert video['claims']==[c for c in original['claims'] if c.get('claim_type')!='ETC']
        for before,product in zip(original['products'],video['products']):
            assert set(product)==set(before)|{'match','DB'}
            assert set(product['match'])=={'status','method','candidates','matched_name','matched_company'}
            match=product['match'];db=product['DB']
            assert match['status'] in {'confirmed','unresolved','not_found'}
            if match['status']=='confirmed':
                assert match['method'] in {'name_and_company','report_number'}
                assert db is not None and set(db)==set(TYPE_FIELDS)
                for typ,fields in TYPE_FIELDS.items():
                    assert list(db[typ])==fields
                    assert all(isinstance(db[typ][field],list if field in ARRAYS else str) for field in fields)
            else:
                assert db is None and match['method'] is None
                assert match['matched_name'] is None and match['matched_company'] is None
                assert match['status']!='not_found' or match['candidates']==0
            for field in before:
                if field!='manufacturing_report_number' or match['status']!='confirmed':
                    assert product[field]==before[field]
