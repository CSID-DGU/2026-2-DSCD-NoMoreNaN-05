"""Same normalized product name + approved manufacturer group, independent of reports."""
from collections import defaultdict
import hashlib
import json

from src.claim_evidence_experiment import name_key
from src.product_identity_filtered import company_core
from src.company_comparison import company_values,company_field


class ProductGroups:
    def __init__(self,products,pairs):
        neighbors=defaultdict(set)
        for pair in pairs:
            values=list(pair)
            if len(values)!=2:continue
            a,b=values
            neighbors[a].add(b)
            neighbors[b].add(a)
        if any(len(v)>1 for v in neighbors.values()):
            raise ValueError('Overlapping manufacturer pairs need explicit group review; no transitive merging')
        self.company_labels={k:min({k}|v) for k,v in neighbors.items()}
        self.products={p['product_id']:p for p in products}
        self.groups=defaultdict(list)
        self.reports=defaultdict(list)
        for p in products:
            self.groups[self.key(p)].append(p)
            if p.get('manufacturing_report_number'):
                self.reports[name_key(p['manufacturing_report_number'])].append(p)

    def company(self,value):
        core=company_core(value)
        return self.company_labels.get(core,core)

    def key(self,product):
        company=self.company(product['company_name']) or 'unknown-company-record:'+str(product['product_id'])
        return name_key(product['product_name']),company

    def group(self,key,report=None):
        rows=sorted(self.groups[key],key=lambda p:p['product_id'])
        preferred=[p for p in rows if report and name_key(p.get('manufacturing_report_number'))==name_key(report)]
        representative=(preferred or rows)[0]
        return dict(group_id=hashlib.sha256(json.dumps(key,ensure_ascii=False).encode()).hexdigest()[:20],
                    name_key=key[0],company_key=key[1],rows=rows,representative=representative)

    def select(self,row,report=None):
        keys={self.key(self.products[p['product_id']]) for p in row.get('candidates',[])}
        if len(keys)==1:
            return self.group(next(iter(keys))),'unique_name_company_group'
        observations=company_values(row)
        observations={self.company(v) for v in observations if v and self.company(v)}
        if len(observations)==1:
            matching=[key for key in keys if key[1] in observations]
            if len(matching)==1:
                return self.group(matching[0]),'name_and_brand_company_group' if company_field(row)=='brand_name' else 'name_and_manufacturer_group'
        # Report lookup is a fallback, never an exclusion condition on names.
        if report:
            reported={self.key(p) for p in self.reports.get(name_key(report),[])}
            if len(reported)==1:
                return self.group(next(iter(reported)),report=report),'report_number_fallback'
        return None,'multiple_name_company_groups' if keys else 'no_candidates'
