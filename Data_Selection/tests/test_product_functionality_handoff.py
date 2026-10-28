import unittest
from scripts.export_product_functionality_handoff import build_record,match_status


class ProductHandoffTests(unittest.TestCase):
    def setUp(self):
        self.product=dict(product_id=1,product_name='제품',company_name='회사',manufacturing_report_number='123',main_functionality='원본\n기능성')
        self.row=dict(selected_product=self.product,candidates=[self.product],product_ref='p1',manufacturer_name='회사',route='exact_name')

    def test_claim_partition_and_source_text(self):
        video=dict(video_id='v',url='https://example.com',claims=[dict(claim_id='c1',product_ref='p1',text='원문'),dict(claim_id='c2',product_ref='p2',text='다른 제품')])
        record=build_record(video,self.row,{1:self.product},'version',set())
        self.assertEqual(record['claims'],video['claims'][:1])
        self.assertEqual(record['product']['evi_product']['main_functionality'],'원본\n기능성')
        self.assertEqual(record['product']['match']['method'],'name_and_company')

    def test_db_report_number_does_not_imply_report_match(self):
        self.row['manufacturer_name']=None
        self.assertEqual(match_status(self.row,set())['status'],'unresolved')
        self.assertIsNone(match_status(self.row,set())['method'])

    def test_unresolved_multiple_does_not_pick_first(self):
        self.row['selected_product']=None
        record=build_record(dict(video_id='v',claims=[]),self.row,{1:self.product},'version',set())
        self.assertIsNone(record['product']['evi_product'])
        self.assertEqual(len(record['product']['candidates']),1)
