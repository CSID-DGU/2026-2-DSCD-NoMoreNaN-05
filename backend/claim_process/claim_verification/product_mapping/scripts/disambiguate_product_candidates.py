"""Narrow saved multiple product candidates using manufacturer evidence."""
from collections import Counter
import copy
import json
from pathlib import Path

from ..src.claim_evidence_experiment import company_key
from ..src.product_identity_filtered import company_core
from ..src.company_comparison import company_values,company_field


def resolve_multiple(row, approved_pairs):
    candidates = row['candidates']
    observations = company_values(row)
    if not observations:
        return [], 'brand_missing' if company_field(row)=='brand_name' else 'manufacturer_missing'
    def paired(a,b):
        a,b = company_core(a),company_core(b)
        return bool(a and b) and (a==b or frozenset((a,b)) in approved_pairs)
    if any(not paired(a,b) for a in observations for b in observations):
        return [], 'conflicting_input_manufacturers'
    strict = [c for c in candidates if all(company_key(obs)==company_key(c['company_name']) for obs in observations)]
    if strict:
        return strict, 'manufacturer_original'
    normalized = [c for c in candidates if all(company_core(obs)==company_core(c['company_name']) for obs in observations)]
    if normalized:
        return normalized, 'manufacturer_factory_normalized'
    if row.get('route') in ('exact_name','brand_removed_exact_name','brand_added_exact_name'):
        aliases = [c for c in candidates if all(paired(obs,c['company_name']) for obs in observations)]
        if aliases:
            return aliases, 'manufacturer_approved_pair'
    return [], 'manufacturer_mismatch'
