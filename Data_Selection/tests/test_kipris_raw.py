import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from collect_kipris_raw import collect_query, request_page, folder_name


def xml(page, ids, total=3):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<response>'
            f'<TotalSearchCount>{total}</TotalSearchCount><SearchStartNumber>{page}</SearchStartNumber>'
            + ''.join(f'<PatentUtilityInfo><ApplicationNumber>{i}</ApplicationNumber></PatentUtilityInfo>' for i in ids)
            + '</response>\n').encode()


class Response:
    def __init__(self, content, status=200):
        self.content, self.status_code, self.headers = content, status, {}


class Session:
    def __init__(self, responses):
        self.responses, self.calls = responses, []

    def get(self, url, **kwargs):
        self.calls.append(kwargs['params'].copy())
        return self.responses.pop(0)


class KiprisTests(unittest.TestCase):
    @patch('collect_kipris_raw.time.sleep')
    def test_full_pages_preserve_exact_bytes(self, sleep):
        bodies = [xml(1, ['A', 'B']), xml(2, ['C'])]
        client = Session([Response(body) for body in bodies])
        with tempfile.TemporaryDirectory() as root:
            result = collect_query('test', 'SECRET', Path(root), count=2, session=client)
            self.assertTrue(result['pagination_verified'])
            self.assertEqual(result['records_observed'], 3)
            self.assertEqual([c['docsStart'] for c in client.calls], [1, 2])
            for i, body in enumerate(bodies, 1):
                self.assertEqual((Path(root)/'test'/f'page_{i:03d}.xml').read_bytes(), body)
            self.assertNotIn('SECRET', (Path(root)/'test'/'metadata.json').read_text())

    @patch('collect_kipris_raw.time.sleep')
    def test_duplicate_page_stops(self, sleep):
        client = Session([Response(xml(1, ['A','B'])), Response(xml(2, ['A','B']))])
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(RuntimeError, 'Duplicate'):
                collect_query('test', 'SECRET', Path(root), count=2, session=client)

    @patch('collect_kipris_raw.time.sleep')
    def test_three_retries_only_and_error_bodies_preserved(self, sleep):
        client = Session([Response(b'<error/>', 500) for _ in range(4)])
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaisesRegex(RuntimeError, 'three retries'):
                request_page(client, {}, Path(root), 1, 1)
            self.assertEqual(len(client.calls), 4)
            self.assertEqual(len(list(Path(root).glob('*.xml'))), 4)

    def test_safe_folder_names(self):
        self.assertNotEqual(folder_name('a/b'), folder_name('a?b'))
        self.assertNotEqual(folder_name('CON'), 'CON')


if __name__ == '__main__':
    unittest.main()
