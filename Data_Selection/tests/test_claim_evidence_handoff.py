import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pilot_summary", ROOT / "scripts/summarize_claim_evidence_pilot.py")
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


class HandoffTests(unittest.TestCase):
    def test_top_k_does_not_pad_and_empty_claim_is_preserved(self):
        evidence = [dict(rank=i, relevance_score=1 / i, text="실제 원문", material_scope="ingredient_reference",
                         target="원료", source_ref=f"evidence:{i}") for i in (1, 2)]
        original = dict(metadata={}, summary=dict(claims_with_candidates=1, claims_without_candidates=1,
                         top_k_comparison={"1": dict(total_links=1, claims_with_k_candidates=1),
                                           "3": dict(total_links=2, claims_with_k_candidates=0)}),
                        videos=[dict(video_id="v", url="https://example.test", products=[], claims=[
                            dict(claim_id="c1", text="원료 관련 주장", product_match_status="unmatched",
                                 candidate_count=2, ranked_evidences=evidence, top3_evidences=evidence),
                            dict(claim_id="c2", text="관련 자료가 없는 주장", product_match_status="unmatched",
                                 candidate_count=0, ranked_evidences=[], top3_evidences=[])])])
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            path = directory / "claim_evidence_ranked.json"
            path.write_text(json.dumps(original), encoding="utf-8")
            with patch("sys.argv", ["summary", "--output-dir", str(directory)]):
                summary.main()
            one = json.loads((directory / "top1_handoff.json").read_text(encoding="utf-8"))
            five = json.loads((directory / "top5_handoff.json").read_text(encoding="utf-8"))
            self.assertEqual(one["videos"][0]["claims"][0]["evidence_count"], 1)
            self.assertEqual(one["metadata"]["default_top_k"], 1)
            self.assertEqual(five["metadata"]["default_top_k"], 5)
            self.assertEqual(five["videos"][0]["claims"][0]["evidence_count"], 2)
            self.assertEqual(five["videos"][0]["claims"][1]["evidences"], [])
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), original)
            self.assertIn("연결 가능한 Evidence 없음", (directory / "review_top5.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
