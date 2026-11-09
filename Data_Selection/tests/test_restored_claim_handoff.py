import unittest

from scripts.export_restored_claim_handoff import select_product
from src.product_name_groups import ProductGroups


def row(pid,name,company,report=None):
    return dict(product_id=pid,product_name=name,company_name=company,
                manufacturing_report_number=report or str(pid))


class RestoredHandoffTests(unittest.TestCase):
    def resolve(self,original,rows,claims=None,pairs=None):
        grouping=ProductGroups(rows,pairs or set())
        audit=dict(candidates=rows,selected_product=None)
        return select_product(dict(product_ref='p1',**original),audit,claims or [],grouping)

    def test_manufacturer_before_brand(self):
        result=self.resolve(dict(product_name='제품',manufacturer_name='제조사',brand_name='브랜드'),
                            [row(1,'제품','브랜드'),row(2,'제품','제조사')])
        self.assertEqual(result[0]['product_id'],2)
        self.assertEqual(result[1],'name_and_company')

    def test_claim_manufacturer_recovers_company_match(self):
        claim=dict(product_ref='p1',claim_id='c1',text='제조원: (주)비오팜')
        result=self.resolve(dict(product_name='관절선생',manufacturer_name=None,brand_name='자생바이오'),
                            [row(1,'관절선생','(주)비오팜'),row(2,'관절선생','프롬바이오')],[claim])
        self.assertEqual(result[0]['product_id'],1)
        self.assertEqual(result[4],'same_product_claim_manufacturer')

    def test_unique_name_does_not_fabricate_company_agreement(self):
        result=self.resolve(dict(product_name='제품',brand_name='광고브랜드'),[row(1,'제품','실제제조사')])
        self.assertIsNone(result[0]);self.assertIsNone(result[1])
        self.assertEqual(result[2],'name_only_company_not_verified')

    def test_manufacturer_conflict_stays_unresolved(self):
        result=self.resolve(dict(product_name='제품',manufacturer_name='다른제조사',brand_name='브랜드'),
                            [row(1,'제품','브랜드')])
        self.assertIsNone(result[0]);self.assertEqual(result[2],'manufacturer_conflict')

    def test_distinct_product_names_not_chosen_by_company_alone(self):
        result=self.resolve(dict(product_name='제품',manufacturer_name='제조사'),
                            [row(1,'제품듀얼','제조사'),row(2,'제품트리플','제조사')])
        self.assertIsNone(result[0])

    def test_factory_suffix_group_uses_observed_factory(self):
        result=self.resolve(dict(product_name='제품',manufacturer_name='(주)제조사 제2공장'),
                            [row(1,'제품','(주)제조사'),row(2,'제품','(주)제조사 제2공장')])
        self.assertEqual(result[0]['product_id'],2)

    def test_report_fallback(self):
        grouping=ProductGroups([row(1,'정식제품','제조사','R1')],set())
        result=select_product(dict(product_ref='p1',product_name='별칭',manufacturing_report_number='R1'),
                              dict(candidates=[]),[],grouping)
        self.assertEqual(result[0]['product_id'],1)
        self.assertEqual(result[1],'report_number')

    def test_report_is_not_required_when_name_company_matches(self):
        result=self.resolve(dict(product_name='제품',manufacturer_name='제조사',manufacturing_report_number='OTHER'),
                            [row(1,'제품','제조사','R1')])
        self.assertEqual(result[0]['product_id'],1)
        self.assertEqual(result[1],'name_and_company')


if __name__=='__main__':unittest.main()
