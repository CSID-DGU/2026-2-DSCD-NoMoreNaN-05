import unittest
from scripts.disambiguate_product_candidates import resolve_multiple


class DisambiguationTests(unittest.TestCase):
    def row(self, manufacturer):
        return dict(manufacturer_name=manufacturer,route='exact_name',candidates=[
            dict(product_id=1,company_name='서흥 1공장'),dict(product_id=2,company_name='서흥헬스케어 2공장')])

    def test_original_manufacturer_precedes_pair_expansion(self):
        rows,reason=resolve_multiple(self.row('서흥 1공장'),{frozenset(('서흥','서흥헬스케어'))})
        self.assertEqual([r['product_id'] for r in rows],[1])

    def test_factory_normalized_company_disambiguates(self):
        rows,reason=resolve_multiple(self.row('서흥'),set())
        self.assertEqual([r['product_id'] for r in rows],[1])

    def test_multiple_records_same_company_are_not_arbitrarily_chosen(self):
        row=self.row('서흥')
        row['candidates'][1]['company_name']='서흥 2공장'
        self.assertEqual(len(resolve_multiple(row,set())[0]),2)

    def test_missing_or_mismatched_manufacturer_does_not_select(self):
        for value in (None,'다른회사'):
            self.assertEqual(resolve_multiple(self.row(value),set())[0],[])

    def test_conflicting_observations_do_not_select(self):
        row=self.row('서흥')
        row['identity_observations']=[dict(value='다른회사')]
        self.assertEqual(resolve_multiple(row,set())[1],'conflicting_input_manufacturers')
