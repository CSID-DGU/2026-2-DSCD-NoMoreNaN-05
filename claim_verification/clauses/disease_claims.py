"""영별표1-1-가(질병 예방)·나(질병 치료) 표현 판정.

    1. 질병 후보 찾기 (diseases.find). 없으면 이 조항 대상이 아니다.
    2. 질병마다 예방·치료 가설을 만들어 NLI로 함의 점수를 받는다.
    3. 조항(목)마다 가장 높은 함의 점수로 라벨을 정한다.

1-1-가 단서: 건강기능식품이 기능성을 인정받은 사항을 표시하면 예방 표현이어도 위반이 아니다.
질병명이 들어간 인정 기능성은 질병발생위험감소(골다공증·충치)뿐이다. 그 질병의 예방 주장은
제품 인정 기능성과 대조해야 하는데, 대조 함수는 4호 나에서 만든다. 그 전까지는 UNCLEAR로 둔다.
1-1-나(치료)는 단서가 없다.

면책 문구는 judge가 먼저 거르므로 여기 오지 않는다.
"""

from ..diseases import find
from ..finding import UNCLEAR, VIOLATION, Finding
from ..nli import ENTAILMENT, NLI

LAW_PREVENTION = "영별표1-1-가"
LAW_TREATMENT = "영별표1-1-나"

# 함의 점수 → 라벨. NLI 담당자와 dev 세트로 다시 맞춘다.
VIOLATION_AT = 0.8
UNCLEAR_AT = 0.4

# 질병발생위험감소기능이 인정된 질병. 이 질병의 예방 주장만 1-1-가 단서에 걸릴 수 있다.
RISK_REDUCTION_DISEASES = {"골다공증", "충치"}

HYPOTHESES = {
    LAW_PREVENTION: ("이 문장은 {d}{을} 예방할 수 있다고 주장한다.",
                     "이 문장은 {d}에 걸리지 않게 해 준다고 말한다."),
    LAW_TREATMENT: ("이 문장은 {d}{을} 치료할 수 있다고 주장한다.",
                    "이 문장은 {d}{이} 낫거나 증상이 완화된다고 말한다."),
}

# 사유 코드
CLAIM = {LAW_PREVENTION: "DISEASE_PREVENTION_CLAIM", LAW_TREATMENT: "DISEASE_TREATMENT_CLAIM"}
POSSIBLE = {LAW_PREVENTION: "DISEASE_PREVENTION_POSSIBLE", LAW_TREATMENT: "DISEASE_TREATMENT_POSSIBLE"}
NLI_UNAVAILABLE = "NLI_UNAVAILABLE"
EXCEPTION_PENDING = "APPROVED_FUNCTION_CHECK_PENDING"


class DiseaseClaimCheck:
    """check 함수 두 개(가·나)를 내놓는다. 같은 클레임의 NLI 호출은 한 번으로 묶는다."""

    def __init__(self, nli: NLI | None):
        self.nli = nli
        self._last: tuple[str, dict] | None = None

    def checks(self) -> list:
        return [self.prevention, self.treatment]

    def prevention(self, claim: dict, product: dict) -> Finding | None:
        return self._judge(claim, LAW_PREVENTION)

    def treatment(self, claim: dict, product: dict) -> Finding | None:
        return self._judge(claim, LAW_TREATMENT)

    def _judge(self, claim: dict, law: str) -> Finding | None:
        text = claim["text"]
        diseases = _unique_terms(find(text))
        if not diseases:
            return None
        span = ", ".join(diseases)
        if self.nli is None:
            return Finding(UNCLEAR, NLI_UNAVAILABLE, law, span, "질병명이 있으나 NLI가 연결되지 않아 판정 못 함")
        disease, entail, hypothesis = self._scores(text, diseases)[law]
        detail = f"{disease}: 함의 {entail:.2f} / 가설 \"{hypothesis}\" / 모델 {self.nli.model_id}"
        if entail >= VIOLATION_AT:
            if law == LAW_PREVENTION and disease in RISK_REDUCTION_DISEASES:
                return Finding(UNCLEAR, EXCEPTION_PENDING, law, disease,
                               detail + " / 인정 기능성(질병발생위험감소) 대조 전")
            return Finding(VIOLATION, CLAIM[law], law, disease, detail)
        if entail >= UNCLEAR_AT:
            return Finding(UNCLEAR, POSSIBLE[law], law, disease, detail)
        return None

    def _scores(self, text: str, diseases: list[str]) -> dict:
        """{law: (질병, 최고 함의 점수, 그 가설)}. 직전 클레임과 같으면 다시 묻지 않는다."""
        if self._last and self._last[0] == text:
            return self._last[1]
        keys, pairs = [], []
        for law, templates in HYPOTHESES.items():
            for d in diseases:
                for t in templates:
                    keys.append((law, d))
                    pairs.append((text, fill(t, d)))
        best = {}
        for (law, d), (_, h), s in zip(keys, pairs, self.nli.score(pairs)):
            if law not in best or s[ENTAILMENT] > best[law][1]:
                best[law] = (d, s[ENTAILMENT], h)
        self._last = (text, best)
        return best


def fill(template: str, disease: str) -> str:
    """{d}에 질병명을 넣고 {을}·{이}를 받침에 맞춘다."""
    final = _has_final(disease)
    return (template.replace("{d}", disease)
            .replace("{을}", "을" if final else "를")
            .replace("{이}", "이" if final else "가"))


def _has_final(word: str) -> bool:
    ch = word[-1]
    if "가" <= ch <= "힣":
        return (ord(ch) - ord("가")) % 28 != 0
    return False


def _unique_terms(found: list[dict]) -> list[str]:
    return list(dict.fromkeys(f["term"] for f in found))
