import importlib.util
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/calibrate_product_name_thresholds.py'
SPEC = importlib.util.spec_from_file_location('product_calibration', SCRIPT)
cal = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cal)


def product(identifier, name, company='제조사 A'):
    return {'product_id': identifier, 'product_name': name, 'company_name': company,
            'manufacturing_report_number': str(100000 + identifier)}


class ProductCalibrationTests(unittest.TestCase):
    def test_unknown_product_is_not_given_its_held_out_answer(self):
        rows = [product(1, '브랜드 멀티비타민 유산균'), product(2, '다른 이름')]
        catalog = cal.Catalog(rows)
        trial = {'source_index': 0, 'expected_product_id': None,
                 'query': rows[0]['product_name'], 'route': 'typo'}
        ranking = catalog.rank(trial, 'company_unknown')
        self.assertNotIn(1, [r['product_id'] for r in ranking['top']])
        self.assertEqual(cal.decision(ranking, 100)[0], None)

    def test_ties_and_multiple_passing_records_are_not_resolved_by_first_row(self):
        ranking = {'top': [{'product_id': 10, 'score': 95}, {'product_id': 11, 'score': 95}]}
        self.assertEqual(cal.decision(ranking, 90), (None, 'ambiguous'))
        ranking['top'][1]['score'] = 89
        self.assertEqual(cal.decision(ranking, 90), (10, 'accepted'))

    def test_whole_phrase_not_internal_substring_and_company_filter(self):
        rows = [product(1, '올인원 뉴트리션 멀티비타민 유산균'),
                product(2, '다른 뉴트리션 멀티비타민 유산균', '제조사 B'),
                product(3, '뉴트리션 멀티비타민 유산균분말')]
        catalog = cal.Catalog(rows)
        self.assertEqual(catalog.phrase_candidates('유산'), [])
        phrase = '뉴트리션 멀티비타민 유산균'
        self.assertEqual(catalog.phrase_candidates(phrase), [0, 1])
        trial = {'source_index': 0, 'expected_product_id': 1, 'query': phrase, 'route': 'omission'}
        ranking = catalog.rank(trial, 'company_known')
        self.assertEqual(ranking['literal_candidates_before_company'], 2)
        self.assertEqual(ranking['candidate_count'], 1)
        self.assertEqual(ranking['top'][0]['product_id'], 1)

    def test_generic_name_is_abstained_and_punctuation_is_preserved(self):
        catalog = cal.Catalog([product(1, '홍삼')])
        ranking = catalog.rank({'source_index': 0, 'expected_product_id': 1,
                                'query': '홍삼', 'route': 'typo'}, 'company_known')
        self.assertEqual(ranking['blocked_reason'], 'generic_only')
        self.assertNotEqual(cal.normalize('1.5 mg'), cal.normalize('15 mg'))

    def test_wrong_link_counts_as_false_link_and_missed_correct_record(self):
        trial = {'expected_product_id': 1, 'rankings': {'company_known': {
            'top': [{'product_id': 2, 'score': 99}]}}}
        metrics = cal.evaluate([trial], 'company_known', 90)
        self.assertEqual(metrics['wrong_links'], 1)
        self.assertEqual(metrics['recall'], 0)
        self.assertEqual(metrics['precision'], 0)

    def test_threshold_can_be_refused_instead_of_recommending_a_tiny_perfect_sample(self):
        sweep = [{'threshold': 99, 'metrics': {'precision': 1, 'recall': .01, 'accepted': 1}}]
        self.assertIsNone(cal.choose_threshold(sweep, .99, 30))

    def test_test_scores_do_not_change_the_selected_threshold(self):
        def trial(split, expected, identifier, score):
            ranking = {'top': [{'product_id': identifier, 'score': score}]}
            return {'route': 'typo', 'kind': 'typo_1', 'split': split,
                    'expected_product_id': expected,
                    'rankings': {'company_known': ranking, 'company_unknown': ranking}}
        cases = [trial('calibration', 1, 1, 90), trial('calibration', None, 2, 80),
                 trial('test', 3, 3, 95)]
        before, _ = cal.summarize(cases, {}, .99, 1, 5)
        cases[-1] = trial('test', 3, 999, 100)
        after, _ = cal.summarize(cases, {}, .99, 1, 5)
        key = 'company_known/typo'
        self.assertEqual(before['recommendations'][key]['recommended_threshold'], 90)
        self.assertEqual(after['recommendations'][key]['recommended_threshold'], 90)
        self.assertEqual(after['recommendations'][key]['test_metrics']['wrong_links'], 1)

    def test_catalog_is_read_only_and_rejects_unresolvable_report_duplicates(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'catalog.sqlite'
            with closing(sqlite3.connect(path)) as db:
                db.execute('CREATE TABLE products (product_id, product_name, company_name, manufacturing_report_number)')
                db.execute('INSERT INTO products VALUES (1, ?, ?, ?)', ('시험 제품', '제조사', '123'))
                db.commit()
            before = path.read_bytes()
            rows, _ = cal.load_catalog(path)
            self.assertEqual(rows[0]['product_id'], 1)
            self.assertEqual(path.read_bytes(), before)
            with closing(sqlite3.connect(path)) as db:
                db.execute('INSERT INTO products VALUES (2, ?, ?, ?)', ('다른 제품', '제조사', '123'))
                db.commit()
            with self.assertRaises(ValueError):
                cal.load_catalog(path)

    def test_generated_sources_do_not_leak_between_splits(self):
        rows = [product(i, f'브랜드{i} 복합 성분 제품') for i in range(1, 101)]
        trials = cal.make_trials(rows, 40, 123)
        self.assertEqual(len(trials), 40)
        self.assertEqual(trials, cal.make_trials(rows, 40, 123))
        development = {cal.normalize(t['source_name']) for t in trials if t['split'] == 'calibration'}
        test = {cal.normalize(t['source_name']) for t in trials if t['split'] == 'test'}
        self.assertFalse(development & test)
        self.assertEqual(len({t['source_product_id'] for t in trials}), 40)


if __name__ == '__main__':
    unittest.main()
