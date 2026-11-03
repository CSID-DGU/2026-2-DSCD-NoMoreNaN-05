import unittest
from src.claim_type_db_format import build_product,db_sections,TYPE_FIELDS


class ClaimTypeFormatTests(unittest.TestCase):
    def product(self):
        return dict(product_name='DB 제품',company_name='DB 회사',manufacturing_report_number='12345',
            main_functionality=' 기능성 원문\n',specification='규격',RAWMTRL_STD_INFO='[{"RAWMTRL_NM":"원료"}]')

    def test_effect_section_and_verbatim_functionality_are_always_included(self):
        result=db_sections(self.product())
        self.assertEqual(set(result),set(TYPE_FIELDS))
        self.assertEqual(result['EFFECT']['MAIN_FNCTN'],' 기능성 원문\n')
        self.assertEqual(result['CERTIFICATION']['MAIN_FNCTN'],result['EFFECT']['MAIN_FNCTN'])

    def test_missing_arrays_and_text_have_distinct_defaults(self):
        result=db_sections({})
        self.assertEqual(result['EFFECT']['RAWMTRL_STD_INFO'],[])
        self.assertEqual(result['EFFECT']['MAIN_FNCTN'],'')

    def test_unresolved_must_not_publish_candidate_db(self):
        result=build_product(dict(product_ref='p1',manufacturing_report_number=None),
            dict(product=dict(match=dict(status='unresolved',method='name_and_company'))),self.product(),2)
        self.assertIsNone(result['DB'])
        self.assertIsNone(result['match']['method'])
        self.assertIsNone(result['match']['matched_name'])
        self.assertIsNone(result['manufacturing_report_number'])

    def test_confirmed_report_is_actual_db_report_and_input_is_unchanged(self):
        original=dict(product_ref='p1',manufacturing_report_number=None)
        result=build_product(original,dict(product=dict(match=dict(status='confirmed',method='name_and_company'))),self.product(),1)
        self.assertEqual(result['manufacturing_report_number'],'12345')
        self.assertIsNone(original['manufacturing_report_number'])
        self.assertEqual(result['match']['matched_company'],'DB 회사')

    def test_corrupt_json_array_does_not_silently_turn_into_empty(self):
        with self.assertRaises(ValueError):db_sections(dict(RAWMTRL_STD_INFO='not JSON'))

    def test_wrong_array_type_is_rejected(self):
        with self.assertRaises(ValueError):db_sections(dict(RAWMTRL_STD_INFO='{}'))


if __name__=='__main__':unittest.main()
