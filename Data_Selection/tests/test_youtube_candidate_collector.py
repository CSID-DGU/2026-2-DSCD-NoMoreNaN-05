import csv
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.collectors import youtube_candidate_collector as y


class FakeClient:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def get(self, resource, params):
        self.calls.append((resource, params))
        return self.responses.pop(0)


def search(items, next_token=None):
    value = {"items": [{"id": {"videoId": video_id}, "snippet": {
        "title": f"search {video_id}", "description": "search description",
        "channelId": "channel", "channelTitle": "channel title", "publishedAt": "2026-01-01T00:00:00Z",
    }} for video_id in items]}
    if next_token:
        value["nextPageToken"] = next_token
    return value


def videos(items):
    return {"items": [{"id": video_id, "snippet": {"title": f"title {video_id}", "description": "description",
        "channelId": "channel", "channelTitle": "channel title", "publishedAt": "2026-01-01T00:00:00Z"},
        "contentDetails": {"duration": "PT30S"}, "statistics": {"viewCount": "5"}} for video_id in items]}


class YouTubeCollectorTests(unittest.TestCase):
    def configured_paths(self, directory):
        root = Path(directory)
        config = root / "configs" / "youtube_search_keywords.yaml"
        config.parent.mkdir()
        config.write_text("general:\n  - 일반 광고\nomega:\n  - 오메가 광고\n", encoding="utf-8")
        return patch.multiple(y, ROOT=root, KEYWORDS_PATH=config, RAW_ROOT=root / "data/raw/youtube_search",
                              CANDIDATES_PATH=root / "data/processed/youtube_ad_candidates.csv",
                              URLS_PATH=root / "data/input/ad_urls.csv")

    def test_deduplicates_context_batches_metadata_and_writes_csvs(self):
        with tempfile.TemporaryDirectory() as directory, self.configured_paths(directory):
            client = FakeClient([search(["A", "B"]), search(["B", "C"]), videos(["A", "B", "C"])])
            manifest = y.collect(3, client=client, run_id="test", sleep_seconds=0)
            self.assertEqual(manifest["total_api_results"], 4)
            self.assertEqual(manifest["final_unique_videos"], 3)
            self.assertEqual([call[0] for call in client.calls], ["search", "search", "videos"])
            with y.CANDIDATES_PATH.open(encoding="utf-8", newline="") as stream:
                rows = {row["video_id"]: row for row in csv.DictReader(stream)}
            self.assertEqual(rows["B"]["search_keywords"], "일반 광고|오메가 광고")
            self.assertEqual(rows["B"]["search_categories"], "general|omega")
            self.assertEqual(rows["A"]["duration"], "PT30S")
            self.assertEqual(rows["A"]["view_count"], "5")
            self.assertEqual(y.candidate_scoring_inputs(rows["A"])["title"], "title A")
            self.assertTrue((y.RAW_ROOT / "test" / "001_일반_광고_page_001.json").is_file())
            with y.URLS_PATH.open(encoding="utf-8", newline="") as stream:
                self.assertEqual(len(list(csv.DictReader(stream))), 3)

    def test_pagination_and_existing_candidate_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory, self.configured_paths(directory):
            y.CANDIDATES_PATH.parent.mkdir(parents=True)
            with y.CANDIDATES_PATH.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=y.CANDIDATE_FIELDS)
                writer.writeheader()
                writer.writerow({"video_id": "OLD", "source_url": "https://www.youtube.com/watch?v=OLD",
                                 "search_keywords": "old", "search_categories": "old", "collected_at": "2026-01-01T00:00:00Z"})
            client = FakeClient([search(["A"], "next"), search(["B"]), videos(["A", "B"])])
            manifest = y.collect(3, max_pages_per_keyword=2, client=client, run_id="page", sleep_seconds=0)
            self.assertEqual(manifest["final_unique_videos"], 3)
            self.assertEqual([call[0] for call in client.calls], ["search", "search", "videos"])
            self.assertEqual(client.calls[1][1]["pageToken"], "next")
            with y.CANDIDATES_PATH.open(encoding="utf-8", newline="") as stream:
                self.assertEqual({row["video_id"] for row in csv.DictReader(stream)}, {"OLD", "A", "B"})

    def test_missing_key_is_clear(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(y, "ROOT", Path(directory)), patch.dict(y.os.environ, {}, clear=True):
            with self.assertRaisesRegex(RuntimeError, "YOUTUBE_API_KEY is missing"):
                y.require_api_key()

    def test_max_results_is_a_hard_final_unique_limit(self):
        with tempfile.TemporaryDirectory() as directory, self.configured_paths(directory):
            client = FakeClient([search(["A", "B", "C"]), videos(["A", "B"])])
            manifest = y.collect(2, client=client, run_id="limit", sleep_seconds=0)
            self.assertEqual(manifest["final_unique_videos"], 2)
            with y.CANDIDATES_PATH.open(encoding="utf-8", newline="") as stream:
                self.assertEqual({row["video_id"] for row in csv.DictReader(stream)}, {"A", "B"})


if __name__ == "__main__":
    unittest.main()
