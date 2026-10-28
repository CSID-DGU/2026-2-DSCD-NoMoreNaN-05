"""Product-only matching with auditable company-site suffix normalization."""
from collections import defaultdict
from contextlib import closing
from pathlib import Path
import re
import json
import sqlite3
import unicodedata

from src.claim_evidence_experiment import Catalog, company_key, name_key


def company_core(value):
    text = unicodedata.normalize("NFC", str(value or "")).casefold()
    # Preserve boundaries while removing corporate markers: these often separate
    # the legal company from an attached factory/business-unit name.
    text = re.sub(r"\(\s*주\s*\)|㈜|주식회사|\(\s*유\s*\)|유한회사", " ", text).strip()
    text = re.sub(r"\s+", " ", text)
    # A separated suffix can include a location/business-unit name. Never strip
    # arbitrary substrings such as '헬스케어' from the legal company name.
    text = re.sub(r"\s+[^\s]*(?:공장|지점|사업부문|사업부|사업장)$", "", text)
    text = re.sub(r"\s*(?:제\s*)?\d+\s*(?:공장|지점)$", "", text)
    text = re.sub(r"\s+(?:포천|음성|세종|청주|오송|천안|안성|익산|진천|평택|화성)$", "", text)
    return re.sub(r"\s+", "", text)


class FilteredProductCatalog(Catalog):
    company_normalizer = staticmethod(company_core)

    def __init__(self, database):
        # Intentionally read only product identity fields, not Evidence texts.
        with closing(sqlite3.connect(Path(database).resolve().as_uri() + "?mode=ro", uri=True)) as db:
            db.row_factory = sqlite3.Row
            self.products = [dict(row) for row in db.execute(
                "SELECT product_id, product_name, company_name, manufacturing_report_number FROM products")]
        self.names, self.reports, self.companies = defaultdict(list), defaultdict(list), defaultdict(list)
        for row in self.products:
            self.names[name_key(row["product_name"])].append(row)
            self.reports[name_key(row["manufacturing_report_number"])].append(row)
            self.companies[company_core(row["company_name"])].append(row)

    def identify(self, product):
        # Keep precise factory-level evidence when it already identifies a unique
        # record. Broaden to legal-company comparison only after strict failure.
        if not hasattr(self, '_strict_catalog'):
            strict = Catalog.__new__(Catalog)
            strict.products, strict.names, strict.reports = self.products, self.names, self.reports
            strict.companies = defaultdict(list)
            for row in self.products:
                strict.companies[company_key(row['company_name'])].append(row)
            self._strict_catalog = strict
        strict_match = self._strict_catalog.identify(product)
        if strict_match['status'] == 'matched':
            return dict(strict_match, manufacturer_comparison='original_factory_specific')
        product = dict(product)
        observations = product.get("identity_observations", [])
        if observations:
            values = {company_core(row["value"]) for row in observations if row.get("value")}
            product["identity_observation_conflicts"] = len(values) > 1
        return dict(super().identify(product), manufacturer_comparison='normalized_legal_company')


class ApprovedPairProductCatalog(FilteredProductCatalog):
    """Explicit pair equivalence applies only to exact product names."""

    def __init__(self, database, pairs_path):
        super().__init__(database)
        config = json.loads(Path(pairs_path).read_text(encoding='utf-8'))
        self.approved_pairs = {frozenset(company_core(v) for v in pair) for pair in config['pairs']}

    def same_manufacturer(self, a, b):
        a, b = company_core(a), company_core(b)
        return bool(a and b) and (a == b or frozenset((a,b)) in self.approved_pairs)

    def identify(self, product):
        previous = super().identify(product)
        if previous['status'] == 'matched':
            return previous
        rows = self.names.get(name_key(product.get('product_name')), [])
        if not rows:
            return previous  # Pair expansion never combines with fuzzy names.
        observations = [r['value'] for r in product.get('identity_observations', []) if r.get('value')]
        if product.get('manufacturer_name'):
            observations.append(product['manufacturer_name'])
        if not observations:
            return previous
        if product.get('identity_observation_conflicts') and not product.get('identity_observations'):
            return previous
        if any(not self.same_manufacturer(a,b) for a in observations for b in observations):
            return previous
        if previous['reason'] == 'report_number_and_name_conflict':
            return previous
        report = name_key(product.get('manufacturing_report_number'))
        valid = [r for r in rows
                 if all(self.same_manufacturer(obs,r['company_name']) for obs in observations)
                 and (not report or report == name_key(r['manufacturing_report_number']))]
        result = dict(previous, manufacturer_comparison='user_approved_pair', route='exact_name_approved_manufacturer_pair',
                      candidate_count=len(valid),
                      candidate_examples=[dict(r) for r in valid[:5]])
        if len(valid) != 1:
            if valid:
                return dict(result, reason='multiple_candidates_after_approved_pair')
            return previous
        row = valid[0]
        return dict(result, status='matched', product_id=row['product_id'], name_score=100.0,
                    reason='unique_exact_product_with_user_approved_manufacturer_pair',
                    matched_product_name=row['product_name'], matched_manufacturer=row['company_name'],
                    matched_report_number=row['manufacturing_report_number'],
                    applied_manufacturer_pairs=[list(sorted({company_core(obs),company_core(row['company_name'])}))
                                                for obs in set(observations)
                                                if company_core(obs) != company_core(row['company_name'])])
