import csv
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.collectors import youtube_ad_filter as f


class YouTubeAdFilterTests(unittest.TestCase):
    def candidate(self, video_id, title, channel="브랜드 공식"):
        return {"video_id": video_id, "title": title, "source_url": f"https://www.youtube.com/watch?v={video_id}",
                "description": "건강기능식품 제품 소개", "channel_title": channel, "search_keywords": "유산균 광고"}

    def test_rule_filter_rejects_explicit_news_and_preserves_ambiguous_rows(self):
        self.assertEqual(f.rule_filter(self.candidate("A", "건강기능식품 허위광고 적발 뉴스"))[0], "REJECT")
        self.assertEqual(f.rule_filter(self.candidate("B", "유산균 효능 비교"))[0], "PASS")
        self.assertEqual(f.rule_filter(self.candidate("C", "OO 유산균 신제품 소개"))[0], "PASS")

    def test_rules_only_writes_every_candidate_without_overwriting_confirmed_urls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "candidates.csv"
            fields = ["video_id", "title", "source_url", "description", "channel_title", "search_keywords"]
            with source.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows([self.candidate("A", "건강기능식품 뉴스"), self.candidate("B", "OO 유산균 신제품")])
            confirmed = root / "ad_urls.csv"
            confirmed.write_text("source_url,platform,video_id\nold,youtube,OLD\n", encoding="utf-8")
            result = f.classify_candidates(input_path=source, rule_output_path=root / "rules.csv",
                                           classifications_path=root / "classified.csv", confirmed_urls_path=confirmed,
                                           rules_only=True)
            self.assertEqual(result["candidate_count"], 2)
            self.assertEqual(result["rule_pass_count"], 1)
            self.assertIn("OLD", confirmed.read_text(encoding="utf-8"))
            with (root / "rules.csv").open(encoding="utf-8", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 2)

    def test_classification_reuses_matching_previous_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = self.candidate("A", "OO 유산균 신제품")
            source = root / "candidates.csv"
            with source.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=candidate)
                writer.writeheader()
                writer.writerow(candidate)
            prior = {"video_id": "A", "title": candidate["title"], "source_url": candidate["source_url"],
                     "channel_title": candidate["channel_title"], "search_keywords": candidate["search_keywords"],
                     "rule_result": "PASS", "llm_result": "ADVERTISEMENT", "confidence": "0.95", "reason": "제품 구매 홍보",
                     "model": "test-model", "classified_at": "2026-01-01T00:00:00Z", "input_hash": f.input_fingerprint(candidate)}
            previous = root / "classified.csv"
            with previous.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=f.CLASSIFICATION_FIELDS)
                writer.writeheader()
                writer.writerow(prior)
            with patch.object(f, "classify_with_openai", side_effect=AssertionError("should reuse")):
                result = f.classify_candidates(input_path=source, rule_output_path=root / "rules.csv",
                                               classifications_path=previous, confirmed_urls_path=root / "ad_urls.csv",
                                               model="test-model", api_key="test")
            self.assertEqual(result["confirmed_count"], 1)


if __name__ == "__main__":
    unittest.main()
