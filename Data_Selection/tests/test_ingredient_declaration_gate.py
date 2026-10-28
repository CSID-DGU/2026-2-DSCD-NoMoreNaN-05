from collections import defaultdict
import unittest
from src.claim_evidence_experiment import Catalog, candidates_for_claim, declared_product_ingredients


class DeclarationGateTests(unittest.TestCase):
    def setUp(self):
        self.db = Catalog.__new__(Catalog)
        self.db.by_id = {}
        self.db.ingredients = [dict(ingredient_id=1,ingredient_name='홍삼',recognition_number=None)]
        self.db.ingredient_names = {1:{'홍삼'}}
        self.db.evidence_by_ingredient = defaultdict(list,{1:[dict(evidence_id=1,evidence_text='홍삼 기능성',evidence_type='OFFICIAL_FUNCTIONALITY',source_authority='MFDS')]})
        self.product = dict(product_ref='p1',product_name='홍삼제품',db_match=dict(status='unmatched'))

    def claim(self,text,kind='COMPOSITION',ref='p1'):
        return dict(claim_id='c1',product_ref=ref,text=text,claim_type=kind,ingredients=['홍삼'])

    def test_composition_assertion_opens_gate_for_same_product_other_claim(self):
        composition = self.claim('이 제품에는 홍삼이 함유되어 있다')
        effect = self.claim('면역력에 도움',kind='FUNCTIONALITY')
        candidates,_ = candidates_for_claim(self.db,dict(claims=[composition,effect]),self.product,effect)
        self.assertEqual(len(candidates),1)
        self.assertEqual(candidates[0]['ingredient_search_basis']['declaration_claim_ids'],['c1'])

    def test_efficacy_and_bare_ingredient_fields_do_not_open_gate(self):
        for claim in [self.claim('홍삼을 먹으면 힘이 난다',kind='FUNCTIONALITY'),self.claim('건강을 위한 제품')]:
            self.assertEqual(declared_product_ingredients(self.db,dict(claims=[claim]),self.product)[0],[])

    def test_negation_and_other_product_do_not_open_gate(self):
        for claim in [self.claim('이 제품에는 홍삼이 포함되지 않는다'),self.claim('홍삼 함유',ref='p2')]:
            self.assertEqual(declared_product_ingredients(self.db,dict(claims=[claim]),self.product)[0],[])

    def test_product_name_alone_does_not_open_gate(self):
        self.assertEqual(declared_product_ingredients(self.db,dict(claims=[]),self.product)[0],[])
