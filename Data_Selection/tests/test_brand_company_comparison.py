import unittest
from scripts.map_claim_products import map_video
from scripts.export_product_functionality_handoff import match_status
from src.product_name_groups import ProductGroups
from src.company_comparison import company_values
from tests.test_claim_evidence_experiment import product,catalog
from src.claim_evidence_experiment import name_key


class BrandCompanyTests(unittest.TestCase):
    def rows(self):return [product(company='BrandCo'),product(2,company='MakerCo',report='456')]

    def test_brand_wins_over_conflicting_manufacturer(self):
        rows=self.rows()
        video=dict(video_id='v',products=[dict(product_ref='p1',product_name=rows[0]['product_name'],brand_name='BrandCo',manufacturer_name='MakerCo')],
                   claims=[dict(product_ref='p1',text='제조원: MakerCo')])
        db=catalog(rows)
        sources={r['product_id']:dict(r,main_functionality='원문') for r in rows}
        mapped,records=map_video(video,db,[name_key(r['product_name']) for r in rows],set(),sources,'version',{},company_field='brand_name')
        self.assertEqual(mapped[0]['selected_product']['product_id'],1)
        self.assertEqual(mapped[0]['manufacturer_name'],'MakerCo')
        self.assertEqual(company_values(mapped[0]),['BrandCo','BrandCo'])
        self.assertEqual(records[0]['product']['match']['status'],'confirmed')

    def test_missing_brand_does_not_fall_back_to_manufacturer(self):
        row=dict(candidates=self.rows(),brand_name=None,manufacturer_name='MakerCo',comparison_company_field='brand_name',identity_observations=[dict(field='manufacturer_name',value='MakerCo')])
        self.assertEqual(company_values(row),[])
        self.assertIsNone(ProductGroups(self.rows(),set()).select(row)[0])

    def test_group_selection_uses_brand_not_manufacturer(self):
        row=dict(candidates=self.rows(),brand_name='BrandCo',manufacturer_name='MakerCo',comparison_company_field='brand_name')
        group,reason=ProductGroups(self.rows(),set()).select(row)
        self.assertEqual(group['representative']['product_id'],1)
        self.assertEqual(reason,'name_and_brand_company_group')

    def test_brand_mismatch_cannot_be_confirmed_by_manufacturer(self):
        row=dict(selected_product=self.rows()[1],brand_name='BrandCo',manufacturer_name='MakerCo',comparison_company_field='brand_name',route='exact_name')
        self.assertEqual(match_status(row,set())['status'],'unresolved')
