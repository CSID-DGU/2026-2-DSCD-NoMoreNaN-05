import unittest
from src.claim_product_identity import declarations,resolve_claim_identity
from src.product_name_groups import ProductGroups
from scripts.recover_product_candidates import RecoveryIndex


def product(pid,name='테스트 복합 건강제품',company='제조업체A'):
    return dict(product_id=pid,product_name=name,company_name=company,manufacturing_report_number=str(2004000000000+pid),main_functionality='원문')


class ClaimIdentityTests(unittest.TestCase):
    def setUp(self):
        self.products=[product(1),product(2,company='제조업체B')]
        self.grouping=ProductGroups(self.products,set())
        self.index=RecoveryIndex(self.products)
        self.row=dict(product_ref='p1',product_name=self.products[0]['product_name'],brand_name='광고브랜드',manufacturer_name='제조업체B',candidates=self.products)

    def resolve(self,claims,row=None):
        return resolve_claim_identity(row or self.row,claims,self.index,self.grouping)

    def test_separates_manufacturer_seller_and_uses_only_claim_manufacturer(self):
        claims=[dict(product_ref='p1',claim_id='c1',text='제조원: 제조업체A 판매원: 광고브랜드')]
        group,obs,reason=self.resolve(claims)
        self.assertEqual(group['representative']['product_id'],1)
        self.assertEqual([o['role'] for o in obs],['manufacturer_name','seller_name'])

    def test_other_product_claim_does_not_leak(self):
        self.assertIsNone(self.resolve([dict(product_ref='p2',text='제조원: 제조업체A')])[0])

    def test_seller_does_not_substitute_for_manufacturer(self):
        self.assertIsNone(self.resolve([dict(product_ref='p1',text='판매원: 제조업체A')])[0])

    def test_ingredient_manufacturer_is_not_product_manufacturer(self):
        self.assertEqual(declarations([dict(product_ref='p1',text='원료 제조사: 제조업체A')],'p1'),[])

    def test_conflicting_manufacturers_fail_closed(self):
        claims=[dict(product_ref='p1',text='제조원: '+v) for v in ['제조업체A','제조업체B']]
        self.assertIsNone(self.resolve(claims)[0])

    def test_numeric_version_conflict_is_not_resolved_by_manufacturer(self):
        row=dict(self.row,product_name='테스트 복합 건강제품 1000')
        products=[product(1,name='테스트 복합 건강제품 2000')]
        group,_,_=resolve_claim_identity(dict(row,candidates=products),[dict(product_ref='p1',text='제조원: 제조업체A')],RecoveryIndex(products),ProductGroups(products,set()))
        # same_numbers requires a conflict on both sides; both names have digits.
        self.assertIsNone(group)

    def test_explicit_report_can_resolve_without_maker(self):
        group,obs,reason=self.resolve([dict(product_ref='p1',text='품목제조신고번호: 2004000000001')])
        self.assertEqual(group['representative']['product_id'],1)
        self.assertEqual(reason,'claim_report_number_fallback')

    def test_generic_ingredient_claim_does_not_become_product(self):
        products=[product(1,name='Magnesium')]
        row=dict(self.row,candidates=[],product_name='더블엑스',brand_name='뉴트리라이트')
        group,_,_=resolve_claim_identity(row,[dict(product_ref='p1',text='Calcium / Mg Magnesium / Vit.B')],RecoveryIndex(products),ProductGroups(products,set()))
        self.assertIsNone(group)

    def test_product_list_does_not_select_longest_nonbrand_variant(self):
        products=[product(1,name='수퍼바이오틱스'),product(2,name='수퍼바이오틱스+철분',company='제조업체B')]
        row=dict(self.row,candidates=products,product_name='수퍼바이오틱스',brand_name='CENOVIS')
        group,_,_=resolve_claim_identity(row,[dict(product_ref='p1',text='수퍼바이오틱스, 수퍼바이오틱스+철분')],RecoveryIndex(products),ProductGroups(products,set()))
        self.assertIsNone(group)

    def test_unpunctuated_foreign_manufacturer_is_still_recorded(self):
        obs=declarations([dict(product_ref='p1',text='제조원 UAS Labs | 판매원: 에이스바이옴')],'p1')
        self.assertEqual(obs[0]['value'],'UAS Labs')

    def test_brand_awareness_phrase_is_not_brand_declaration(self):
        self.assertEqual(declarations([dict(product_ref='p1',text='브랜드 인지도 NO.1')],'p1'),[])
