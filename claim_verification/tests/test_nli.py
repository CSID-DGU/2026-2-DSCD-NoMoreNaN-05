import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from claim_verification.nli import NEUTRAL_SCORES, FakeNLI, NLIError, ServerNLI, get_nli

HIGH = {"entailment": 0.9, "neutral": 0.08, "contradiction": 0.02}


def test_fake_table_rule_and_default():
    nli = FakeNLI(table={("a", "x"): HIGH}, rule=lambda p, h: HIGH if p == "b" else None)
    assert nli.score([("a", "x"), ("b", "y"), ("c", "z")]) == [HIGH, HIGH, NEUTRAL_SCORES]
    assert nli.calls == [[("a", "x"), ("b", "y"), ("c", "z")]]


def test_get_nli_reads_env(monkeypatch):
    monkeypatch.delenv("CLAIM_NLI_URL", raising=False)
    assert get_nli() is None
    monkeypatch.setenv("CLAIM_NLI_URL", "http://nli.example/score")
    assert isinstance(get_nli(), ServerNLI)


def test_server_parse_keeps_request_order():
    data = {"model": "klue-nli-v1", "results": [
        {"id": "1", "entailment": 0.1, "neutral": 0.8, "contradiction": 0.1},
        {"id": "0", **HIGH},
    ]}
    nli = ServerNLI("http://unused")
    assert nli._parse(data, 2) == [HIGH, {"entailment": 0.1, "neutral": 0.8, "contradiction": 0.1}]
    assert nli.model_id == "klue-nli-v1"


def test_server_parse_rejects_missing_scores():
    with pytest.raises(NLIError, match="id 1"):
        ServerNLI("http://unused")._parse({"results": [{"id": "0", **HIGH}]}, 2)


@pytest.fixture
def server():
    received = []

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            received.append(body)
            results = [{"id": p["id"], **HIGH} for p in body["pairs"]]
            payload = json.dumps({"model": "test-model", "results": results}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, *args):
            pass

    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_port}/score", received
    httpd.shutdown()


def test_server_round_trip_in_batches(server):
    url, received = server
    nli = ServerNLI(url, batch_size=2)
    pairs = [("감기예방", "가설1"), ("감기예방", "가설2"), ("치매예방", "가설3")]
    assert nli.score(pairs) == [HIGH, HIGH, HIGH]
    assert [len(b["pairs"]) for b in received] == [2, 1]
    assert received[0]["pairs"][0] == {"id": "0", "premise": "감기예방", "hypothesis": "가설1"}
    assert nli.model_id == "test-model"
