from collections import defaultdict
import unittest

from src.claim_evidence_experiment import Catalog, candidates_for_claim, company_key, name_key, sample_claims, source_chunks, whole_phrase


def catalog(rows):
    result = Catalog.__new__(Catalog)
    result.products = rows
    result.names, result.reports, result.companies = defaultdict(list), defaultdict(list), defaultdict(list)
    for row in rows:
        result.names[name_key(row["product_name"])].append(row)
        result.reports[name_key(row["manufacturing_report_number"])].append(row)
        result.companies[company_key(row["company_name"])].append(row)
    return result


def product(id=1, name="올인원 멀티비타민 유산균", company="(주)제조사 2공장", report="123"):
    return dict(product_id=id, product_name=name, company_name=company, manufacturing_report_number=report)


class IdentityTests(unittest.TestCase):
    def test_null_product_name_can_return_no_candidates(self):
        db = Catalog.__new__(Catalog)
        db.ingredients, db.by_id, db.ingredient_names, db.evidence_by_ingredient = [], {}, {}, {}
        product_row = dict(product_ref="p1", product_name=None, db_match=dict(status="unmatched"))
        candidates, ingredients = candidates_for_claim(db, dict(claims=[]), product_row,
                                                       dict(text="광고", ingredients=None))
        self.assertEqual(candidates, [])
        self.assertEqual(ingredients, [])

    def test_exact_name_is_not_overridden_by_known_conflict(self):
        db = catalog([product(), product(2, "올인원 멀티비타민 유산근", "다른회사", "456")])
        match = db.identify(dict(product_name="올인원 멀티비타민 유산균", manufacturer_name="다른회사"))
        self.assertEqual(match["status"], "unmatched")
        self.assertEqual(match["reason"], "known_identity_conflict")

    def test_exact_name_requires_no_missing_manufacturer_when_unique(self):
        result = catalog([product()]).identify(dict(product_name="올인원멀티비타민 유산균"))
        self.assertEqual(result["product_id"], 1)

    def test_legal_and_ordinal_variations_are_not_company_aliases(self):
        self.assertEqual(company_key("주식회사 제조사 제2공장"), company_key("(주)제조사 2공장"))
        self.assertNotEqual(company_key("(주)서흥"), company_key("(주)서흥헬스케어 2공장"))

    def test_whole_phrase_requires_boundary_and_manufacturer(self):
        self.assertFalse(whole_phrase("유산", "멀티 유산균"))
        self.assertTrue(whole_phrase("멀티비타민 유산균", "올인원 멀티비타민 유산균"))
        db = catalog([product()])
        match = db.identify(dict(product_name="멀티비타민 유산균"))
        self.assertEqual(match["reason"], "manufacturer_missing")
        match = db.identify(dict(product_name="멀티비타민 유산균", manufacturer_name="제조사 제2공장"))
        self.assertEqual(match["product_id"], 1)

    def test_typo_does_not_choose_best_of_multiple_passing_candidates(self):
        db = catalog([product(1, "정확한제품이름에이"), product(2, "정확한제품이름비이", report="456")])
        match = db.identify(dict(product_name="정확한제품이름씨이", manufacturer_name="제조사2공장"))
        self.assertEqual(match["reason"], "multiple_candidates")
        self.assertIsNone(match["product_id"])

    def test_report_conflict_cannot_be_ignored_by_exact_name(self):
        db = catalog([product()])
        result = db.identify(dict(product_name="올인원 멀티비타민 유산균", manufacturing_report_number="999"))
        self.assertEqual(result["reason"], "known_identity_conflict")

    def test_product_specification_difference_is_preserved(self):
        self.assertNotEqual(name_key("칼슘 100mg"), name_key("칼슘 1000mg"))
        self.assertNotEqual(name_key("제품+"), name_key("제품"))

    def test_sample_is_reproducible_and_not_dominated_by_first_video(self):
        videos = [dict(claims=[{}] * 30) for _ in range(120)]
        first = sample_claims(videos, 100, 42)
        self.assertEqual(first, sample_claims(videos, 100, 42))
        self.assertEqual(sum(map(len, first.values())), 100)
        self.assertEqual(len(first), 100)

    def test_source_locations_point_to_verbatim_original_text(self):
        text = "  원문 첫 줄\n\n 두 번째 줄  \n" + "가" * 1800
        chunks = list(source_chunks(dict(field=text), "field"))
        self.assertTrue(len(chunks) > 3)
        for chunk, start, end in chunks:
            self.assertEqual(chunk, text[start:end])


if __name__ == "__main__":
    unittest.main()
