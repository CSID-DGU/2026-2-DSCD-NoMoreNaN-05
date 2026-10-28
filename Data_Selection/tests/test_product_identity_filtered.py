import unittest
from src.product_identity_filtered import FilteredProductCatalog, ApprovedPairProductCatalog, company_core
from tests.test_claim_evidence_experiment import catalog, product


def filtered(rows):
    db = catalog(rows)
    db.__class__ = FilteredProductCatalog
    from collections import defaultdict
    db.companies = defaultdict(list)
    for row in rows:
        db.companies[company_core(row['company_name'])].append(row)
    return db


class FilteredIdentityTests(unittest.TestCase):
    def test_factory_and_unit_suffixes(self):
        for name in ['콜마비앤에이치(주)음성공장', '콜마비앤에이치(주)푸디팜사업부문', '콜마비앤에이치(주)세종3공장']:
            self.assertEqual(company_core(name), '콜마비앤에이치')
        self.assertEqual(company_core('주식회사 네추럴웨이 포천 제2공장'), '네추럴웨이')
        self.assertNotEqual(company_core('(주)서흥'), company_core('(주)서흥헬스케어 2공장'))

    def test_factory_removal_does_not_choose_between_reports(self):
        db = filtered([product(company='제조사 1공장'), product(2, company='제조사 2공장', report='456')])
        result = db.identify(dict(product_name='올인원 멀티비타민 유산균', manufacturer_name='제조사'))
        self.assertEqual(result['reason'], 'multiple_candidates')

    def test_typo_can_match_after_factory_cleanup(self):
        db = filtered([product(company='제조사 2공장')])
        result = db.identify(dict(product_name='올인원 멀티비타민 유산근', manufacturer_name='제조사'))
        self.assertEqual(result['product_id'], 1)
        self.assertGreaterEqual(result['name_score'], 80)

    def test_report_conflict_still_blocks(self):
        result = filtered([product()]).identify(dict(product_name='올인원 멀티비타민 유산균', manufacturer_name='제조사', manufacturing_report_number='999'))
        self.assertEqual(result['reason'], 'known_identity_conflict')

    def test_specific_factory_information_is_used_before_broadening(self):
        db = filtered([product(company='제조사 1공장'), product(2, company='제조사 2공장', report='456')])
        result = db.identify(dict(product_name='올인원 멀티비타민 유산균', manufacturer_name='제조사 1공장'))
        self.assertEqual(result['product_id'], 1)
        self.assertEqual(result['manufacturer_comparison'], 'original_factory_specific')


class ApprovedPairTests(unittest.TestCase):
    def db(self, rows):
        db = filtered(rows)
        db.__class__ = ApprovedPairProductCatalog
        db.approved_pairs = {frozenset(('서흥','서흥헬스케어'))}
        return db

    def test_exact_name_uses_explicit_pair(self):
        result = self.db([product(company='서흥헬스케어 2공장')]).identify(
            dict(product_name='올인원 멀티비타민 유산균', manufacturer_name='서흥'))
        self.assertEqual(result['product_id'], 1)
        self.assertEqual(result['manufacturer_comparison'], 'user_approved_pair')

    def test_pair_does_not_relax_typo_and_report_conflict(self):
        db = self.db([product(company='서흥헬스케어')])
        for values in [dict(product_name='올인원 멀티비타민 유산근', manufacturer_name='서흥'),
                       dict(product_name='올인원 멀티비타민 유산균', manufacturer_name='서흥',manufacturing_report_number='999')]:
            self.assertEqual(db.identify(values)['status'], 'unmatched')

    def test_multiple_reports_remain_ambiguous(self):
        db = self.db([product(company='서흥헬스케어'),product(2,company='서흥헬스케어',report='456')])
        self.assertEqual(db.identify(dict(product_name='올인원 멀티비타민 유산균',manufacturer_name='서흥'))['status'],'unmatched')

    def test_pair_is_not_transitive(self):
        db = self.db([])
        db.approved_pairs.add(frozenset(('서흥헬스케어','세번째회사')))
        self.assertFalse(db.same_manufacturer('서흥','세번째회사'))

    def test_approved_observations_can_be_resolved(self):
        db = self.db([product(company='서흥헬스케어')])
        result = db.identify(dict(product_name='올인원 멀티비타민 유산균',manufacturer_name='서흥',
                                  identity_observation_conflicts=True,
                                  identity_observations=[dict(value='서흥'),dict(value='서흥헬스케어')]))
        self.assertEqual(result['product_id'],1)
