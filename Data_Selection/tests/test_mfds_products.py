import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.collectors import mfds_products as m


def payload(page, items):
    return json.dumps({"header": {"resultCode": "00"}, "body": {
        "pageNo": page, "numOfRows": 1, "totalCount": 2,
        "items": [{"item": row} for row in items]}}).encode()


class CollectorTests(unittest.TestCase):
    def test_nested_item_and_korean(self):
        _, items = m.parse_page(payload(1, [{"PRDUCT": "제품", "STTEMNT_NO": "001"}]))
        self.assertEqual(items[0]["PRDUCT"], "제품")
        self.assertEqual(items[0]["STTEMNT_NO"], "001")

    def test_api_errors(self):
        for content in [b'{"header":{"resultCode":"30"}}',
                        b'<OpenAPI_ServiceResponse><returnReasonCode>30</returnReasonCode></OpenAPI_ServiceResponse>']:
            with self.assertRaisesRegex(RuntimeError, "30"):
                m.parse_page(content)

    def test_resume_preserves_rows_and_detects_repeated_page(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, "ROOT", Path(tmp)), \
                patch.dict(m.os.environ, {"DATA_GO_KR_API_KEY": "test"}), \
                patch.object(m.requests.Session, "get", side_effect=AssertionError("Must use cached pages")):
            for op in m.OPERATIONS:
                folder = Path(tmp) / "data/raw/mfds_products/test" / op
                folder.mkdir(parents=True)
                for page in (1, 2):
                    (folder / f"page_{page:06d}.json").write_bytes(payload(page, [
                        {"PRDUCT": "제품", "STTEMNT_NO": str(page)}]))
            manifest, processed = m.collect("test", 1)
            self.assertEqual(json.loads(manifest.read_text())["status"], "complete")
            rows = [json.loads(line) for line in (processed / 'getHtfsItem01.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertIsNone(rows[0]["main_functionality"])
            folder = Path(tmp) / "data/raw/mfds_products/test/getHtfsList01"
            (folder / "page_000002.json").write_bytes(payload(2, [{"PRDUCT": "제품", "STTEMNT_NO": "1"}]))
            with self.assertRaisesRegex(RuntimeError, "Repeated"):
                m.collect("test", 1)
            self.assertEqual(json.loads(manifest.read_text())["status"], "incomplete")


if __name__ == "__main__":
    unittest.main()
