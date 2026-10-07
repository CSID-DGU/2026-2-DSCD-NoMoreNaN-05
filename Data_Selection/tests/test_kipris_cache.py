import hashlib
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import kipris_cache as cache


class CacheTest(unittest.TestCase):
    def test_reimport_search_and_tamper_protection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            source=root/'raw'
            source.mkdir()
            body='<response><PatentUtilityInfo><ApplicationNumber>1001</ApplicationNumber><InventionName>홍삼 제품</InventionName><Abstract>면역 관련 기술</Abstract></PatentUtilityInfo></response>'.encode()
            (source/'page_001.xml').write_bytes(body)
            meta={'query':'홍삼','endpoint':'test','collected_at':'2026-10-05','status':'complete',
                  'total_results':1,'records_observed':1,'pages':[{'page':1,'file':'page_001.xml','records':1,'sha256':hashlib.sha256(body).hexdigest()}]}
            (source/'metadata.json').write_text(json.dumps(meta),encoding='utf-8')
            db=root/'cache.sqlite'
            with patch.object(cache,'ROOT',root):
                self.assertEqual(cache.import_directory(source,db),1)
                self.assertEqual(cache.import_directory(source,db),1)
                result=cache.search_candidates('홍삼',db=db)
                self.assertEqual(result[0]['xml_path'],'raw/page_001.xml')
                self.assertEqual(result[0]['evidence_role'],'PATENT_CANDIDATE')
                self.assertEqual(cache.search_candidates('%',db=db),[])
                (source/'page_001.xml').write_bytes(body+b' ')
                with self.assertRaises(ValueError): cache.import_directory(source,db)
            with closing(sqlite3.connect(db)) as con:
                self.assertEqual(con.execute('SELECT count(*) FROM patents').fetchone()[0],1)
                self.assertEqual(con.execute('PRAGMA foreign_key_check').fetchall(),[])


if __name__=='__main__': unittest.main()
