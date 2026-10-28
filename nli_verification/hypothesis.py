"""
TRUEAD 가설 문장 만들기
추출된 광고 원문 조각(span)을 NLI 가설로 쓸 수 있게 "주어 + 완결된 문장"으로 바꾼다.

    make_hypothesis("혈류 흐름을 원활하게 해주고", "베르베린")
    → "베르베린은 혈류 흐름을 원활하게 해 준다"

실험(4단계)에서 전제와 가설의 주어가 다르거나 한쪽에만 있으면
뜻이 같아도 NLI가 Neutral로 판단하는 것이 확인되어 만든 모듈이다.
전제 쪽은 evidence_prep.make_premise(target, core)로 같은 주어를 붙인다.
"""
import re
from evidence_prep import topic_particle

# "이 제품은", "이거", "얘는" 같은 지시어 주어
DEMONSTRATIVE = re.compile(
    r"^(?:바로\s*)?(?:이\s*제품|이\s*영양제|요\s*제품|이것|이거|이건|얘|요거|요것)\s*(?:은|는|이|가|도|만)?\s+")

# 문장 끝 바꾸기 규칙 (위에서부터 처음 맞는 것 하나만 적용)
ENDINGS = [
    (r"(해|해서|하여)?(\s*)(주고|줘서|주는데|주며|주면서|줍니다|줘요|주는|줌)$",
     lambda m: ("해 " if m.group(1) else m.group(2)) + "준다"),
    (r"(잡아|높여|낮춰|지켜|도와|채워|풀어|만들어|바꿔|살려|빼|올려|내려)\s*(주고|줘서|주는데|줍니다|줘요|주는|버립니다|버려요|버리고)$",
     lambda m: f"{m.group(1)} 준다" if "버" not in m.group(2) else f"{m.group(1)} 버린다"),
    (r"(됩니다|돼요|되고|되어|돼서|되는데|되며)$", lambda m: "된다"),
    (r"(합니다|해요|하고|하며|해서|하여|하는데|해)$", lambda m: "한다"),
    (r"(있습니다|있어요|있고|있어서|있는데|있음)$", lambda m: "있다"),
    (r"(없습니다|없어요|없고|없어서|없는데|없음)$", lambda m: "없다"),
    (r"(입니다|이에요|예요|이고|이며)$", lambda m: "이다"),
    (r"지고$|져요$|집니다$|져서$", lambda m: "진다"),
    (r"려요$|립니다$|리고$", lambda m: "린다"),
    (r"습니다$", lambda m: "다"),
]


def _bpnida_to_plain(s):
    """'낮춥니다' → '낮춘다' 처럼 'ㅂ니다'를 'ㄴ다'로 (받침 ㅂ 음절 + 니다)"""
    m = re.search(r"([가-힣])니다$", s)
    if not m:
        return s
    ch = m.group(1)
    code = ord(ch) - 0xAC00
    if code < 0 or code % 28 != 17:          # 받침이 ㅂ이 아니면 그대로
        return s
    base = chr(0xAC00 + code - 17 + 4)       # ㅂ 받침 → ㄴ 받침
    return s[:m.start(1)] + base + "다"


def normalize_claim_ending(s):
    """광고체 문장 끝을 평서문으로. 바뀌었으면 (문장, True)"""
    s0 = s
    for pat, rep in ENDINGS:
        if re.search(pat, s):
            s = re.sub(pat, rep, s, count=1)
            break
    else:
        s = _bpnida_to_plain(s)
    return s, s != s0


def make_hypothesis(span, target, fix_ending=True):
    """
    span:   추출된 광고 원문 조각
    target: 주장의 대상 (제품명 또는 원료명). 전제에도 똑같이 쓴다.
    fix_ending: False면 주어만 맞추고 문장 끝은 그대로 둔다 (비교 실험용)
    반환:   {"hypothesis", "is_question", "ending_changed", "subject_added"}
    """
    s = re.sub(r"\s+", " ", span).strip(" \"'“”‘’")
    is_question = s.endswith("?") or bool(re.search(r"(까요|나요|ㄹ까|을까|는가)\??$", s))
    s = re.sub(r"[.!~…\s]+$", "", s).rstrip("?")
    s = re.sub(r"(인데요|는데요|거든요|답니다)$", "", s).strip() or s

    subject_added = False
    t = re.escape(target)
    m = DEMONSTRATIVE.match(s)
    if m and re.search(r"(은|는|이|가|도|만)\s+$", m.group(0)):  # "이 제품은 ~" → "target은 ~"
        s = DEMONSTRATIVE.sub(f"{target}{topic_particle(target)} ", s, count=1)
    elif m:                                                      # "이거 하나면 ~" → "target 하나면 ~"
        s = DEMONSTRATIVE.sub(f"{target} ", s, count=1)
    elif re.match(rf"^{t}\s*(은|는|이|가)\s", s):                # target이 이미 주어 → 조사만 통일
        s = re.sub(rf"^{t}\s*(은|는|이|가)\s", f"{target}{topic_particle(target)} ", s, count=1)
    elif not re.match(rf"^{t}", s):                              # 주어 없음 → 붙이기
        s = f"{target}{topic_particle(target)} {s}"
        subject_added = True

    s, changed = normalize_claim_ending(s) if fix_ending else (s, False)
    return {"hypothesis": s, "is_question": is_question,
            "ending_changed": changed, "subject_added": subject_added}


if __name__ == "__main__":
    samples = [
        ("혈류 흐름을 원활하게 해주고", "베르베린"),
        ("베르베린이 정맥 기능을 개선해", "베르베린"),
        ("손상된 혈관 내벽을 보호해 주는데", "베르베린"),
        ("염증이랑 혈액 정체까지 잡아줘서", "베르베린"),
        ("정맥 자체를 건강하게 만들어 버립니다", "베르베린"),
        ("복용 한 달 차에는 다리 붓기와 저림이 깨끗이 사라지고", "혈행톡"),
        ("이 제품은 면역력을 높여 줍니다", "홍삼"),
        ("이거 하나면 피로가 싹 풀려요", "홍삼"),
        ("체지방을 줄이는 데 도움을 줘요", "가르시니아"),
        ("혈당을 낮춥니다", "바나바잎 추출물"),
        ("알파아이가 당뇨를 치료할까요?", "알파아이"),
    ]
    for span, target in samples:
        r = make_hypothesis(span, target)
        q = " [질문]" if r["is_question"] else ""
        print(f"{span:<36} → {r['hypothesis']}{q}")


# ─────────────────────────────────────────────────────────────
# 동의어 바꾸기 (⑤)
# 광고의 쉬운 말을 식약처 공식 용어로 바꾼 '추가 가설'을 만든다.
# 원래 가설은 그대로 두고, 두 가설 중 더 높은 E를 쓰는 용도다.
# 원칙: 확실히 같은 뜻만 넣는다. 과장 표현("확", "싹", "100%")은 절대 지우지 않는다.
# ─────────────────────────────────────────────────────────────
SYNONYMS = [
    (r"혈류\s*흐름", "혈행"),
    (r"혈액\s*순환", "혈행"),
    (r"피\s*순환", "혈행"),
    (r"피가\s*잘\s*돌", "혈행이 개선되"),
    (r"눈\s*피로", "눈의 피로도"),
    # 실제 광고에서 실패 사례가 모이면 여기에 추가
]


def synonym_variant(hypothesis):
    """동의어를 공식 용어로 바꾼 문장. 바뀐 게 없으면 None"""
    s = hypothesis
    for pat, rep in SYNONYMS:
        s = re.sub(pat, rep, s)
    return s if s != hypothesis else None
