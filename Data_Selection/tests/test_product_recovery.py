import unittest
from scripts.recover_product_candidates import RecoveryIndex,notation_key,phrase_in
from tests.test_claim_evidence_experiment import product


class RecoveryTests(unittest.TestCase):
    def row(self,name,brand=None):
        return dict(product_name=name,brand_name=brand,product_ref='p1',previous_match={})

    def test_hanja_gloss_and_trademark_but_keep_version_numbers(self):
        self.assertEqual(notation_key('홍삼정 賢(현)™'),notation_key('홍삼정 현'))
        self.assertNotEqual(notation_key('제품100'),notation_key('제품1000'))
        self.assertNotEqual(notation_key('제품+'),notation_key('제품'))
        self.assertNotEqual(notation_key('제품 1.0mg'),notation_key('제품 10mg'))
        self.assertNotEqual(notation_key('제품 1-2'),notation_key('제품 12'))

    def test_exact_notation_finds_specific_hanja_product_before_fuzzy_base(self):
        index=RecoveryIndex([product(name='홍삼정'),product(2,name='홍삼정 賢(현)')])
        self.assertEqual([r['product_id'] for r in index.exact_notation(self.row('홍삼정 현'))],[2])

    def test_exact_bilingual_alias_comes_from_database(self):
        index=RecoveryIndex([product(name='고유제품(UniqueFormula)')])
        rows,route,_=index.search(self.row('UniqueFormula™'),dict(claims=[]),{})
        self.assertEqual(len(rows),1)
        self.assertEqual(route,'notation_or_db_bilingual_alias')

    def test_partial_name_does_not_drop_brand(self):
        index=RecoveryIndex([product(name='다른브랜드 키즈 골드')])
        rows,_,_=index.search(self.row('비오비타 키즈 골드','비오비타'),dict(claims=[]),{})
        self.assertEqual(rows,[])
        self.assertFalse(phrase_in('유산','유산균'))

    def test_brand_scopes_short_name(self):
        index=RecoveryIndex([product(name='드시모네 키즈 블루베리향'),product(2,name='다른회사 키즈 블루베리향')])
        rows,_,_=index.search(self.row('키즈','드시모네'),dict(claims=[]),{})
        self.assertEqual([r['product_id'] for r in rows],[1])

    def test_missing_name_uses_own_claim_not_other_product(self):
        index=RecoveryIndex([product(name='고유브랜드 고유제품')])
        video=dict(claims=[dict(product_ref='p2',claim_id='c2',text='고유브랜드 고유제품')])
        self.assertEqual(index.search(self.row(None),video,{})[0],[])
        video['claims'][0]['product_ref']='p1'
        rows,route,proof=index.search(self.row(None),video,{})
        self.assertEqual(len(rows),1)
        self.assertEqual(route,'recovered_from_own_claims')
        self.assertEqual(proof[0]['claim_id'],'c2')

    def test_generic_brand_only_does_not_invent_name(self):
        index=RecoveryIndex([product(name='고유브랜드 고유제품')])
        self.assertEqual(index.search(self.row(None,'고유브랜드'),dict(claims=[]),{'title':'고유브랜드 광고'})[0],[])

    def test_generic_or_ingredient_word_does_not_recover_missing_product(self):
        for name in ('프로바이오틱스','속편한유산균','아주긴원료이름','다이어트','코엔자임Q10','비타민 B1'):
            index=RecoveryIndex([product(name=name)],ingredient_names=['아주긴원료이름'])
            self.assertEqual(index.search(self.row(None),dict(claims=[]),{'title':name})[0],[])

    def test_title_prefers_specific_name_over_base_and_description(self):
        index=RecoveryIndex([product(name='트루바이타민'),product(2,name='트루바이타민 구미'),product(3,name='다른브랜드제품')])
        rows,_,_=index.search(self.row(None),dict(products=[dict(product_ref='p1')],claims=[]),{'title':'트루바이타민 구미','description':'다른브랜드제품'})
        self.assertEqual([r['product_id'] for r in rows],[2])

    def test_bilingual_name_can_be_observed_in_single_product_video_title(self):
        index=RecoveryIndex([product(name='트루바이타민'),product(2,name='트루바이타민 X')])
        rows,route,_=index.search(self.row('TruVitamin X™','Denps'),dict(products=[{}],claims=[dict(product_ref='p1',text='트루바이타민')]),{'title':'트루바이타민 X™ 광고'})
        self.assertEqual([r['product_id'] for r in rows],[2])
        self.assertEqual(route,'video_observed_bilingual_name')
        self.assertEqual(index.search(self.row('TruVitamin X™','Denps'),dict(products=[{},{}],claims=[]),{'title':'트루바이타민 X 광고'})[0],[])

    def test_shared_video_metadata_is_not_assigned_to_an_unknown_product_slot(self):
        index=RecoveryIndex([product(name='고유브랜드 고유제품')])
        video=dict(products=[dict(product_ref='p1'),dict(product_ref='p2')],claims=[])
        self.assertEqual(index.search(self.row(None),video,{'title':'고유브랜드 고유제품'})[0],[])
        video['products'][0]['brand_name']='고유브랜드'
        video['products'][1]['brand_name']='고유브랜드'
        self.assertEqual(index.search(self.row(None,'고유브랜드'),video,{'title':'고유브랜드 고유제품'})[0],[])

    def test_context_index_keeps_boundaries_and_handles_whitespace(self):
        index=RecoveryIndex([product(name='고유브랜드 제품명')])
        self.assertEqual(index.context_products('다른고유브랜드 제품명'),[])
        self.assertEqual(index.context_products('고유브랜드 제품명추가'),[])
        self.assertEqual([p['product_id'] for p in index.context_products('#고유브랜드제품명 광고')],[1])
        self.assertEqual([p['product_id'] for p in index.context_products('고유브랜드\n제품명')],[1])
