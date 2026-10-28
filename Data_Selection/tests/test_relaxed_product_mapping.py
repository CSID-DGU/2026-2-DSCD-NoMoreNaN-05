import unittest
from scripts.evaluate_relaxed_product_mapping import search, strip_brand
from tests.test_claim_evidence_experiment import catalog, product
from src.claim_evidence_experiment import name_key


class RelaxedMappingTests(unittest.TestCase):
    def run_search(self, rows, value):
        return search(catalog(rows), value, {'status':'unmatched'}, [name_key(r['product_name']) for r in rows])

    def test_brand_boundary_is_preserved(self):
        self.assertEqual(strip_brand('GNM 멀티비타민','GNM'),'멀티비타민')
        self.assertEqual(strip_brand('GNMPLUS 제품','GNM'),'GNMPLUS 제품')

    def test_manufacturer_mismatch_and_multiple_candidates_are_retained(self):
        rows = [product(company='회사A'),product(2,company='회사B',report='456')]
        found,route,score = self.run_search(rows,dict(product_name=rows[0]['product_name'],manufacturer_name='회사C'))
        self.assertEqual(len(found),2)

    def test_known_report_conflict_is_not_ignored(self):
        found,_,_ = self.run_search([product()],dict(product_name='올인원 멀티비타민 유산균',manufacturing_report_number='999'))
        self.assertEqual(found,[])

    def test_distance_returns_candidates_without_manufacturer(self):
        found,route,score = self.run_search([product()],dict(product_name='올인원 멀티비타민 유산근'))
        self.assertEqual(len(found),1)
        self.assertEqual(route,'full_name_distance_80_candidates')
        self.assertGreaterEqual(score,80)
