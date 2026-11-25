"""Export DB evidence for ALL retrieved products, without identity-status gating.

Schema v2: matched means retrieved DB candidates, not verified product identity.
Every candidate carries its own type-specific DB; competing products are never
merged into one fictitious formulation. Original claim fields are preserved.
"""
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import sqlite3

from ..src.claim_type_db_format import db_sections
from ..src.claim_evidence_experiment import name_key
from ..src.product_identity_filtered import company_core


def source_ids(row):
    found={p['product_id'] for p in row.get('candidates',[])}
    selected=row.get('selected_product')
    if selected:found.add(selected['product_id'])
    found.update(row.get('selected_group_product_ids',[]))
    return sorted(found)


def choose_primary(original,row,candidates,pairs):
    """A convenient singleton only; full retrieval evidence remains available."""
    if not candidates:return None,'no_candidates'
    maker=original.get('manufacturer_name')
    brand=original.get('brand_name')
    company=maker or brand
    if company:
        core=company_core(company)
        matching=[]
        for candidate in candidates:
            other=company_core(candidate['company_name'])
            exact_name=name_key(candidate['product_name']) in {
                name_key(original.get('product_name')),name_key(row.get('brand_removed_name'))}
            if core==other or (exact_name and frozenset((core,other)) in pairs):matching.append(candidate)
        if len(matching)==1:
            return matching[0],'manufacturer_priority' if maker else 'brand_fallback'
        if matching:return None,'multiple_company_matching_rows'
        if maker:return None,'manufacturer_conflict_candidates_retained'
    if len(candidates)==1:return candidates[0],'single_retrieved_candidate'
    return None,'multiple_retrieved_candidates'


def iter_claim_contexts(videos):
    """Consumer adapter: candidate DBs are usable even when product.DB is null."""
    for video in videos:
        refs=defaultdict(list)
        for product in video['products']:
            refs[product.get('product_ref')].append(product)
        for claim in video['claims']:
            products=refs.get(claim.get('product_ref'),[]) if claim.get('product_ref') is not None else []
            product=products[0] if len(products)==1 else None
            candidates=product.get('candidate_products',[]) if product else []
            yield dict(video_id=video['video_id'],claim=claim,
                       evidence_status='linked' if candidates else 'no_linkable_product',
                       preferred_product_id=product.get('preferred_product_id') if product else None,
                       candidates=candidates)
