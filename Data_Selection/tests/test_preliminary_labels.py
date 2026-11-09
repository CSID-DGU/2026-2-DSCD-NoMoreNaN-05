import unittest

from scripts.label_claims_preliminary import label_claim, scope_decision


class PreliminaryLabelTests(unittest.TestCase):
    def test_disclaimer_before_product_lookup(self):
        claim = dict(text='인체적용시험결과가 모든사람에게 동일적용되는 것은 아님', claim_type='EFFECT')
        self.assertEqual(label_claim(claim, None, None)['label'], 'DISCLAIMER')

    def test_disease_word_alone_is_not_a_disclaimer(self):
        self.assertIsNone(scope_decision(dict(text='질병 예방에 좋습니다', claim_type='EFFECT')))

    def test_mixed_registration_patent_not_wholly_outside(self):
        self.assertIsNone(scope_decision(dict(text='특허받은 건강기능식품', claim_type='CERTIFICATION')))

    def test_daily_intake_not_packaging(self):
        self.assertIsNone(scope_decision(dict(text='1일 1정', claim_type='QUANTITY')))

    def test_quarantined_product_cannot_be_supported(self):
        p = dict(match=dict(status='confirmed'), DB=dict(CERTIFICATION=dict(STTEMNT_NO='123')))
        c = dict(text='건강기능식품', claim_type='CERTIFICATION')
        self.assertEqual(label_claim(c, p, 'IDENTITY_MANUFACTURER_CONFLICT')['label'], 'UNCLEAR')

    def test_b1_does_not_match_b12(self):
        p = dict(match=dict(status='confirmed'), DB=dict(COMPOSITION=dict(RAWMTRL_NM='비타민 B12')))
        c = dict(text='비타민B1', claim_type='COMPOSITION', ingredients=['비타민B1'])
        self.assertEqual(label_claim(c, p, None)['label'], 'UNCLEAR')

    def test_missing_ingredient_is_not_violation(self):
        p = dict(match=dict(status='confirmed'), DB=dict(COMPOSITION=dict(RAWMTRL_NM='아연')))
        c = dict(text='콜라겐', claim_type='COMPOSITION', ingredients=['콜라겐'])
        self.assertEqual(label_claim(c, p, None)['label'], 'UNCLEAR')

    def test_extra_promise_not_supported_by_ingredient(self):
        p = dict(match=dict(status='confirmed'), DB=dict(COMPOSITION=dict(RAWMTRL_NM='아연')))
        c = dict(text='특허 아연', claim_type='COMPOSITION', ingredients=['아연'])
        self.assertEqual(label_claim(c, p, None)['label'], 'UNCLEAR')

    def test_registration_requires_valid_reference(self):
        self.assertEqual(label_claim(dict(text='건강기능식품', claim_type='CERTIFICATION'), None, None)['label'], 'UNCLEAR')

    def test_composition_literal_support(self):
        p = dict(match=dict(status='confirmed'), DB=dict(COMPOSITION=dict(RAWMTRL_NM='비타민 B1, 아연')))
        c = dict(text='비타민B1 + 아연', claim_type='COMPOSITION', ingredients=['비타민B1', '아연'])
        result = label_claim(c, p, None)
        self.assertEqual(result['label'], 'SUPPORTED')
        self.assertEqual(len(result['evidence']), 2)


if __name__ == '__main__':
    unittest.main()
