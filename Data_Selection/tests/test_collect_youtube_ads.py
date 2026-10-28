import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

import requests

spec = importlib.util.spec_from_file_location("collect_ads", Path(__file__).resolve().parents[1] / "collect_youtube_ads.py")
y = importlib.util.module_from_spec(spec)
spec.loader.exec_module(y)


def product(id=1):
    return dict(id=id, product_name="멀티비타민 유산균", company_name="건강회사",
                product_core="멀티비타민 유산균", company_core="건강회사",
                product_key="멀티비타민유산균", company_key="건강회사",
                category="search", query="멀티비타민 유산균 건강회사")


def video(id="v", duration="PT60S", company=True):
    return dict(id=id, snippet=dict(title="멀티비타민 유산균", description="건강회사" if company else "",
                                    channelTitle="other", channelId="c", publishedAt="2026-01-01T00:00:00Z"),
                contentDetails=dict(duration=duration))


def response(body, status=200):
    return Mock(status_code=status, json=Mock(return_value=body))


class CollectorTests(unittest.TestCase):
    def test_durations(self):
        for raw, expected in [("PT60S", 60), ("PT1M", 60), ("PT1M1S", 61), ("PT0.5S", .5),
                              ("P1DT2H3M4S", 93784), ("P1D", 86400), ("PT", None),
                              ("P", None), ("60", None), (None, None), ("P1Y", None), ("P1DT", None)]:
            self.assertEqual(y.duration_seconds(raw), expected)

    def test_all_matching_conditions_and_normalization(self):
        p = product()
        self.assertTrue(y.matches(p, video()))
        for duration in ("PT61S", "PT0S", "", "PT2M"):
            self.assertFalse(y.matches(p, video(duration=duration)))
        self.assertFalse(y.matches(p, video(company=False)))
        self.assertTrue(y.matches(p, video(company=False), {"c"}))
        v = video(company=False)
        v["snippet"]["channelTitle"] = "건강회사 공식"
        self.assertTrue(y.matches(p, v))
        v["snippet"]["title"] = "다른 제품"
        self.assertFalse(y.matches(p, v, {"c"}))
        self.assertEqual(y.comparison_key("ABC (주) 건강-회사!"), "abc주건강회사")

    def test_cache_survives_reopening_and_does_not_store_key(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            session = Mock(get=Mock(return_value=response({"items": []})))
            y.Client(state, "secret-key", session=session).get("search", q="test")
            state.db.close()
            state = y.State(directory)
            second = Mock()
            self.assertEqual(y.Client(state, "different-key", session=second).get("search", q="test"), {"items": []})
            second.get.assert_not_called()
            self.assertNotIn("secret-key", "".join(str(row) for row in state.db.execute("SELECT * FROM cache")))
            state.db.close()

    def test_quota_response_not_cached_and_next_run_retries_only_failed_request(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            session = Mock(get=Mock(side_effect=[response({"items": []}), response(
                {"error": {"errors": [{"reason": "quotaExceeded"}]}}, 403)]))
            client = y.Client(state, "secret", session=session)
            client.get("search", q="done")
            with self.assertRaises(y.QuotaStop):
                client.get("search", q="pending")
            state.db.close()
            state = y.State(directory)
            session = Mock(get=Mock(return_value=response({"items": []})))
            client = y.Client(state, "secret", session=session)
            client.get("search", q="done")
            client.get("search", q="pending")
            self.assertEqual(session.get.call_count, 1)
            state.db.close()

    def test_retries_5xx_rate_and_network_without_leaking_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            session = Mock(get=Mock(side_effect=[response({}, 503), response(
                {"error": {"errors": [{"reason": "rateLimitExceeded"}]}}, 403),
                requests.ConnectionError("secret-key in URL"), response({"items": []})]))
            sleep = Mock()
            y.Client(state, "secret-key", session=session, sleep=sleep).get("videos", id="v")
            self.assertEqual(sleep.call_count, 3)
            delays = [call.args[0] for call in sleep.call_args_list]
            self.assertTrue(delays[0] < delays[1] < delays[2])
            session.get.side_effect = requests.ConnectionError("secret-key in URL")
            with self.assertRaises(y.ApiError) as caught:
                y.Client(state, "secret-key", session=session, sleep=Mock()).get("videos", id="other")
            self.assertNotIn("secret-key", str(caught.exception))
            state.db.close()

    def test_local_budget_stops_before_request(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            session = Mock()
            with self.assertRaises(y.QuotaStop):
                y.Client(state, "secret", unit_limit=99, session=session).get("search", q="x")
            session.get.assert_not_called()
            state.db.close()

    def test_per_run_limit_does_not_count_cached_requests(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            session = Mock(get=Mock(return_value=response({"items": []})))
            client = y.Client(state, "secret", session=session, max_api_calls=1)
            client.get("search", q="first")
            client.get("search", q="first")
            with self.assertRaises(y.QuotaStop):
                client.get("search", q="second")
            self.assertEqual(session.get.call_count, 1)
            state.db.close()

    def test_channel_pages_resume_then_search_skips_found(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            bodies = [
                {"items": [{"id": {"channelId": "bad"}, "snippet": {"title": "건강"}},
                           {"id": {"channelId": "c"}, "snippet": {"title": "건강회사 공식"}}]},
                {"items": [{"contentDetails": {"relatedPlaylists": {"uploads": "uploads"}}}]},
                {"items": [{"contentDetails": {"videoId": "v"}}], "nextPageToken": "p2"},
                {"items": [video(company=False)]},
                {"error": {"errors": [{"reason": "quotaExceeded"}]}},
            ]
            session = Mock(get=Mock(side_effect=[response(b, 403 if "error" in b else 200) for b in bodies]))
            with self.assertRaises(y.QuotaStop):
                y.collect_channel(y.Client(state, "secret", session=session), state, [product()])
            self.assertTrue(state.found(product()))
            state.db.close()
            state = y.State(directory)
            session = Mock(get=Mock(return_value=response({"items": []})))
            client = y.Client(state, "secret", session=session)
            y.collect_channel(client, state, [product()])
            self.assertEqual(session.get.call_count, 1)
            self.assertEqual(session.get.call_args.kwargs["params"]["pageToken"], "p2")
            y.collect_channel(client, state, [product()])
            y.collect_search(client, state, product())
            self.assertEqual(session.get.call_count, 1)
            output = Path(directory) / "out.json"
            self.assertEqual(state.export(output), 1)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))[0]["method"], "channel")
            state.db.close()

    def test_search_filters_deduplicates_and_marks_empty_results_done(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            bad = video("bad", duration="PT61S")
            client = Mock()
            client.get.side_effect = [{"items": [{"id": {"videoId": "v"}}, {"id": {"videoId": "bad"}}]},
                                      {"items": [video(), video(), bad]}]
            y.collect_search(client, state, product())
            y.collect_search(client, state, product())
            self.assertEqual(client.get.call_count, 2)
            self.assertEqual(state.db.execute("SELECT count(*) FROM results").fetchone()[0], 1)
            client.get.side_effect = [{"items": []}]
            y.collect_search(client, state, product(2))
            y.collect_search(client, state, product(2))
            self.assertEqual(client.get.call_count, 3)
            state.db.close()

    def test_load_exclusions_and_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            excluded = dict(product(0), category="excluded_export", query=None)
            rows = [excluded, product(1), dict(product(2), company_core="other"), product(3)]
            path.write_text(json.dumps(rows), encoding="utf-8")
            self.assertEqual(len(y.load_products(path)), 3)
            self.assertEqual(len(y.load_products(path, limit=1)), 1)
            self.assertEqual([p["id"] for p in y.load_products(path, company_limit=1)], [1, 3])
            rows[1]["product_key"] = ""
            path.write_text(json.dumps(rows), encoding="utf-8")
            with self.assertRaises(ValueError):
                y.load_products(path)

    def test_video_metadata_reused_across_different_search_batches(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            client = Mock()
            client.get.side_effect = [{"items": [video("a"), video("b")]}, {"items": [video("c")]}]
            self.assertEqual(len(list(y.details(client, state, ["a", "b", "a"]))), 2)
            self.assertEqual(len(list(y.details(client, state, ["b", "c"]))), 2)
            self.assertEqual(client.get.call_args_list[1].kwargs["id"], "c")
            state.db.close()

    def test_auth_error_not_retried_or_logged(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            session = Mock(get=Mock(return_value=response({"error": {
                "message": "secret-key", "errors": [{"reason": "keyInvalid"}]}}, 400)))
            with self.assertRaises(y.ApiError) as caught:
                y.Client(state, "secret-key", session=session).get("search", q="x")
            self.assertNotIn("secret-key", str(caught.exception))
            self.assertEqual(session.get.call_count, 1)
            state.db.close()

    def test_unavailable_upload_playlist_is_cached_as_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            session = Mock(get=Mock(return_value=response({"error": {
                "errors": [{"reason": "playlistNotFound"}]}}, 404)))
            client = y.Client(state, "secret", session=session)
            self.assertEqual(client.get("playlistItems", playlistId="gone")["items"], [])
            self.assertEqual(client.get("playlistItems", playlistId="gone")["items"], [])
            self.assertEqual(session.get.call_count, 1)
            state.db.close()

    def test_export_needs_no_key_or_input(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "output.json"
            self.assertEqual(y.main(["export", "--state", directory, "--output", str(output),
                                     "--report", str(Path(directory) / "report.json")]), 0)
            self.assertEqual(json.loads(output.read_text()), [])

    def test_product_only_is_review_and_ad_signals_do_not_confirm(self):
        v = video(company=False)
        v["snippet"]["description"] = "광고 #ad CF 30초"
        v["paidProductPlacementDetails"] = {"hasPaidProductPlacement": True}
        result = y.assess(product(), v)
        self.assertEqual(result["status"], "needs_review")
        self.assertTrue(result["evidence"]["paid_promotion"])
        self.assertEqual(set(result["evidence"]["ad_keywords"]), {"광고", "#ad", "CF", "30초"})
        self.assertIsNone(y.assess(product(), video())["evidence"]["paid_promotion"])
        v["snippet"]["description"] = "TVCF"
        self.assertIn("CF", y.assess(product(), v)["evidence"]["ad_keywords"])

    def test_generic_requires_manufacturer_evidence(self):
        p = dict(product(), generic=True, generic_reasons=["same_product_key_multiple_companies"])
        self.assertEqual(y.assess(p, video(company=False))["status"], "rejected")
        self.assertEqual(y.assess(p, video())["status"], "confirmed")
        v = video(company=False)
        v["snippet"]["channelTitle"] = "건강회사 공식"
        self.assertEqual(y.assess(p, v)["status"], "confirmed")
        # A previous channel-name match alone is not proof after a rename.
        v["snippet"]["channelTitle"] = "other"
        self.assertEqual(y.assess(p, v, {"c"})["status"], "rejected")

    def test_manufacturer_label_and_seller_are_distinguished(self):
        v = video(company=False)
        v["snippet"]["description"] = "제조원: 건강회사\n판매원: 다른회사"
        result = y.assess(product(), v)
        self.assertEqual(result["status"], "confirmed")
        self.assertTrue(result["evidence"]["manufacturer_label"])
        v["snippet"]["description"] = "제조원: 다른회사 / 판매원: 건강회사"
        self.assertFalse(y.assess(product(), v)["evidence"]["manufacturer_label"])

    def test_ids_and_generic_checks_use_entire_input(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            rows = [product(1), dict(product(2), company_key="다른회사", company_core="다른회사")]
            path.write_text(json.dumps(rows), encoding="utf-8")
            selected = y.load_products(path, selected_ids=["1"])
            self.assertEqual([p["id"] for p in selected], [1])
            self.assertTrue(selected[0]["generic"])
            self.assertIn("same_product_key_multiple_companies", selected[0]["generic_reasons"])
            with self.assertRaises(ValueError):
                y.load_products(path, selected_ids=["999"])
            rows = [dict(product(1), product_key="마그네슘", product_core="마그네슘")]
            path.write_text(json.dumps(rows), encoding="utf-8")
            self.assertIn("common_category_name", y.load_products(path)[0]["generic_reasons"])

    def test_search_uses_product_core_and_ignores_old_done_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            p = product()
            state.mark("search-v1:" + y.fingerprint(p))
            client = Mock()
            client.get.side_effect = [{"items": [{"id": {"videoId": "v"}}]},
                                      {"items": [video(company=False)]}]
            y.collect_search(client, state, p)
            self.assertEqual(client.get.call_args_list[0].kwargs["q"], p["product_core"])
            row = json.loads(state.db.execute("SELECT value FROM results").fetchone()[0])
            self.assertEqual(row["status"], "needs_review")
            self.assertIn("description_preview", row)
            self.assertIn("paidProductPlacementDetails", client.get.call_args_list[1].kwargs["part"])
            state.db.close()

    def test_non_video_search_items_are_ignored(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            client = Mock()
            client.get.side_effect = [{"items": [{"id": {"channelId": "c"}},
                                                   {"id": {"videoId": "v"}}]}, {"items": [video()]}]
            y.collect_search(client, state, product())
            self.assertEqual(client.get.call_args_list[1].kwargs["id"], "v")
            self.assertTrue(state.found(product()))
            state.db.close()

    def test_rejected_pairs_reported_but_not_exported(self):
        with tempfile.TemporaryDirectory() as directory:
            state = y.State(directory)
            state.add(product(), video("good"), "search")
            state.add(product(), video("review", company=False), "search")
            state.add(product(), video("bad", duration="PT61S"), "search")
            report = state.report(Path(directory) / "report.json", [1])
            self.assertEqual(report, {"confirmed": 1, "needs_review": 1, "rejected": 1})
            self.assertEqual(state.export(Path(directory) / "output.json"), 2)
            state.db.close()


if __name__ == "__main__":
    unittest.main()
