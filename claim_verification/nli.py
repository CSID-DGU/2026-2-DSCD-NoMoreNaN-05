"""NLI 점수 매기기. 조항은 이 모듈의 score()만 부른다.

NLI 모델은 담당자 서버에서 돈다. 조항은 법을 알고 가설을 만들고, NLI는 점수만 매긴다.

    nli.score([(전제, 가설), ...]) -> [{"entailment", "neutral", "contradiction"}, ...]  # 같은 순서
    nli.model_id                    -> 결과에 기록할 모델 이름·버전

구현은 둘이다.
- ServerNLI: 담당자 서버에 JSON으로 묻는다. 형식은 docs/nli_handoff.md 3장.
- FakeNLI: 개발·테스트용. 정해 둔 점수를 돌려준다.

get_nli()는 환경변수 CLAIM_NLI_URL이 있으면 ServerNLI를, 없으면 None을 준다.
NLI가 없으면 조항은 판정하지 않고 UNCLEAR를 낸다(부재를 위반으로 바꾸지 않는다).
"""

import json
import os
import urllib.request
from typing import Callable, Protocol

ENTAILMENT, NEUTRAL, CONTRADICTION = "entailment", "neutral", "contradiction"
LABELS = (ENTAILMENT, NEUTRAL, CONTRADICTION)

Pair = tuple[str, str]
Scores = dict[str, float]

NEUTRAL_SCORES: Scores = {ENTAILMENT: 0.0, NEUTRAL: 1.0, CONTRADICTION: 0.0}


class NLIError(RuntimeError):
    """서버 응답이 형식과 맞지 않을 때."""


class NLI(Protocol):
    model_id: str

    def score(self, pairs: list[Pair]) -> list[Scores]: ...


class FakeNLI:
    """table[(전제, 가설)] 또는 rule(전제, 가설)로 점수를 정한다. 둘 다 없으면 중립."""

    def __init__(self, table: dict[Pair, Scores] | None = None,
                 rule: Callable[[str, str], Scores | None] | None = None, model_id: str = "fake"):
        self.table = table or {}
        self.rule = rule
        self.model_id = model_id
        self.calls: list[list[Pair]] = []

    def score(self, pairs: list[Pair]) -> list[Scores]:
        self.calls.append(list(pairs))
        out = []
        for p in pairs:
            s = self.table.get(p) or (self.rule(*p) if self.rule else None)
            out.append(s or NEUTRAL_SCORES)
        return out


class ServerNLI:
    """담당자 서버에 묻는다.

    요청: POST {"pairs": [{"id", "premise", "hypothesis"}, ...]}
    응답: {"model": str, "results": [{"id", "entailment", "neutral", "contradiction"}, ...]}
    """

    def __init__(self, url: str, timeout: float = 30.0, batch_size: int = 64):
        self.url = url
        self.timeout = timeout
        self.batch_size = batch_size
        self.model_id = "unknown"

    def score(self, pairs: list[Pair]) -> list[Scores]:
        out = []
        for i in range(0, len(pairs), self.batch_size):
            out.extend(self._post(pairs[i:i + self.batch_size]))
        return out

    def _post(self, pairs: list[Pair]) -> list[Scores]:
        body = {"pairs": [{"id": str(i), "premise": p, "hypothesis": h} for i, (p, h) in enumerate(pairs)]}
        req = urllib.request.Request(self.url, data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return self._parse(data, len(pairs))

    def _parse(self, data: dict, n: int) -> list[Scores]:
        self.model_id = data.get("model") or self.model_id
        by_id = {r.get("id"): r for r in data.get("results", [])}
        out = []
        for i in range(n):
            r = by_id.get(str(i))
            if r is None or any(not isinstance(r.get(k), (int, float)) for k in LABELS):
                raise NLIError(f"응답에 id {i}의 점수가 없음")
            out.append({k: float(r[k]) for k in LABELS})
        return out


def get_nli() -> NLI | None:
    url = os.environ.get("CLAIM_NLI_URL")
    return ServerNLI(url) if url else None
