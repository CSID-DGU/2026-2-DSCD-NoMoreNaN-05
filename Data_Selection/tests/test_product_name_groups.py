import unittest
from src.product_name_groups import ProductGroups
from tests.test_claim_evidence_experiment import product,catalog
from scripts.evaluate_relaxed_product_mapping import search
from src.claim_evidence_experiment import name_key


class NameGroupTests(unittest.TestCase):
    def test_same_name_company_factories_reports_are_one_group(self):
        rows=[product(company='제조사 1공장'),product(2,company='제조사 2공장',report='456')]
        index=ProductGroups(rows,set())
        group,reason=index.select(dict(candidates=rows,manufacturer_name='제조사'))
        self.assertEqual(len(group['rows']),2)
        self.assertEqual(group['representative']['product_id'],1)

    def test_name_success_is_not_vetoed_by_different_report(self):
        rows=[product()]
        group,_=ProductGroups(rows,set()).select(dict(candidates=rows),report='999')
        self.assertEqual(group['representative']['product_id'],1)

    def test_different_product_names_are_not_merged(self):
        rows=[product(),product(2,name='다른제품',report='456')]
        group,reason=ProductGroups(rows,set()).select(dict(candidates=rows,manufacturer_name='제조사'))
        self.assertIsNone(group)

    def test_report_resolves_failed_name_selection_without_name_agreement(self):
        rows=[product(),product(2,name='다른제품',company='다른회사',report='456')]
        group,reason=ProductGroups(rows,set()).select(dict(candidates=rows),report='456')
        self.assertEqual(group['representative']['product_id'],2)
        self.assertEqual(reason,'report_number_fallback')

    def test_unknown_manufacturers_do_not_merge(self):
        rows=[product(company=''),product(2,company='',report='456')]
        self.assertIsNone(ProductGroups(rows,set()).select(dict(candidates=rows))[0])

    def test_name_first_search_ignores_nonmatching_report(self):
        rows=[product()]
        found,route,_=search(catalog(rows),dict(product_name=rows[0]['product_name'],manufacturing_report_number='999'),
                             dict(status='unmatched'),[name_key(rows[0]['product_name'])],report_fallback_only=True)
        self.assertEqual(found,rows)
        self.assertEqual(route,'exact_name')

    def test_report_search_fallback_accepts_different_name(self):
        rows=[product()]
        found,route,_=search(catalog(rows),dict(product_name='완전히다른이름',manufacturing_report_number='123'),
                             dict(status='unmatched'),[name_key(rows[0]['product_name'])],report_fallback_only=True)
        self.assertEqual(found,rows)
        self.assertEqual(route,'exact_report_number_fallback')
