"""
TRUEAD 근거 문장 전처리 (NLI 전제 만들기)

products.main_functionality / intake_precautions, evidence.evidence_text 원문을
NLI에 넣을 수 있는 "기능성 1개 = 문장 1개" 형태로 정리한다.

정리 결과(core)에는 주어가 없다. 주어는 광고 주장의 target에 맞춰
실행할 때 make_premise(subject, core)로 붙인다. (주의사항은 주어를 붙이지 않는다)

정리 규칙
  1) 원료 묶음 나누기: [비타민C]① ... / - 비타민 D : ... / * 아연
  2) 항목 나누기: ①② ⑴⑵ (1) 1. (가) 줄바꿈, 서술어 뒤의 쉼표·마침표·'/'
  3) 서술어가 빠진 항목은 같은 묶음 마지막 서술어를 빌려 붙임 (없으면 기본 서술어, inferred=1)
  4) "A·B·C에 도움" → A, B, C 각각에 서술어를 붙여 나눔
  5) 등급 표기·영문 번역·따옴표 제거, 문장 끝 통일 ("~수 있음"→"~수 있다", "~에 필요"→"~에 필요하다")
  6) 주의사항은 명령형을 평서문으로 ("~할 것" → "~해야 한다")

사용법
    python evidence_prep.py products_func.csv evidence.csv  [출력폴더]
출력
    premises_product.csv   제품 단위 전제 (기능성·주의사항)
    premises_ingredient.csv 원료 단위 전제 (evidence 테이블)
    prep_report.txt         정리 통계
"""
import re
import sys
import csv
from collections import Counter

# ─────────────────────────────────────────────────────────────
# 1. 공통 정리
# ─────────────────────────────────────────────────────────────
CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳"
PAREN_NUM = "⑴⑵⑶⑷⑸⑹⑺⑻⑼⑽⑾⑿⒀⒁⒂⒃⒄⒅⒆⒇"
FUNC_WORDS = r"(도움|필요|개선|증진|억제|건강|원활|감소|유지|보호|형성|생성|흡수|대사|발달|적응|이용|운반|분열|응고|촉진|완화|조절|보충|작용)"
PRED = r"(도움|필요|관여)"     # 문장이 '완결'됐다고 볼 핵심 서술어

GRADE_TAG = re.compile(r"[\(（]\s*(기타|생리\s*활성|질병\s*발생)[^)）]*[\)）]")


def normalize_text(s):
    if not isinstance(s, str):
        return ""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("･", "·").replace("ㆍ", "·").replace("‧", "·").replace("․", "·").replace("⋅", "·")
    s = s.replace("\u3000", " ").replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


def hangul_ratio(s):
    letters = [c for c in s if c.isalpha()]
    if not letters:
        return 0.0
    return sum("가" <= c <= "힣" for c in letters) / len(letters)


# ─────────────────────────────────────────────────────────────
# 2. 원료 묶음(헤더) 나누기
#    [비타민C]① ... / - 비타민 D : ... / * 아연\n① ...
# ─────────────────────────────────────────────────────────────
def clean_label(label):
    label = re.sub(r"^\s*[\(（]?\d+[\)）.]\s*", "", label)      # "2) 비타민B1" → "비타민B1"
    label = re.sub(r"[\(（]\s*원료성\s*[\)）]|원료성", "", label)
    label = re.sub(r"[\(（][^)）]*[\)）]", "", label)              # "셀레늄(또는 셀렌)" → "셀레늄"
    label = re.sub(r"\s*제품\s*$", "", label)
    label = label.strip(" -*•○:：")
    if not label or re.search(r"기능성\s*내용|국문|영문|주원료|기능성|[“”\"]", label):
        return None
    if re.search(PRED, label):                                     # 헤더가 아니라 문장
        return None
    return label


def split_blocks(text):
    """원문 → [(원료이름 또는 None, 그 원료의 텍스트), ...]"""
    t = normalize_text(text)
    t = re.sub(r"\[([^\]\n]{1,60})\]", lambda m: f"\n§H§{m.group(1)}§\n", t)
    t = re.sub(r"(필요|있음|줌|있습니다)\s+([^\s:：\n]{2,20})\s*[:：]", r"\1\n\2 :", t)
    t = re.sub(r"(?m)^\s*(?:[-*•○]\s*)?((?:[\(（]?\d+[\)）.]\s*)?[^:：\n§]{1,30}?)\s*[:：]\s*",
               lambda m: f"§H§{m.group(1)}§\n", t)
    blocks, label, buf = [], None, []

    def flush():
        body = "\n".join(buf).strip()
        if body:
            blocks.append((label, body))

    for line in t.split("\n"):
        line = line.strip()
        if not line:
            continue
        m = re.fullmatch(r"§H§(.*?)§", line)
        if m:
            flush(); buf = []
            label = clean_label(m.group(1))
            continue
        bare = re.fullmatch(r"[*•○■◆]\s*(.{1,25})", line)       # "* 아연" 같은 헤더 줄
        if bare and not re.search(PRED, bare.group(1)):
            flush(); buf = []
            label = clean_label(bare.group(1))
            continue
        buf.append(line)
    flush()
    return blocks


# ─────────────────────────────────────────────────────────────
# 3. 묶음 → 항목 나누기
# ─────────────────────────────────────────────────────────────
MARKERS = [
    rf"[{CIRCLED}{PAREN_NUM}]",
    r"(?:(?<=^)|(?<=\s))[\(（]\s*\d{1,2}\s*[\)）]",               # (1)
    r"(?:(?<=^)|(?<=\s))\d{1,2}[\.\)](?!\d)",                    # 1.  1)
    r"[\(（]\s*[가-하]\s*[\)）]",                                 # (가)
    r"(?m)^\s*[-*•○■◆▶·]\s*",                                    # 줄 앞 기호
]


def split_items(block, kind):
    t = block
    for pat in MARKERS:
        t = re.sub(pat, "\n", t)
    if kind == "func":
        # 서술어로 끝난 뒤 오는 쉼표·마침표에서만 자른다 ("지방, 탄수화물, 단백질 대사..."는 안 자름)
        t = re.sub(rf"((?:{PRED})(?:을|를)?(?:\s*줄\s*수\s*있(?:음|습니다|다))?|도움을\s*줌)\s*[,，./／;]\s*", r"\1\n", t)
        t = re.sub(r"\s+[/／]\s+", "\n", t)
    else:
        t = re.sub(r"(것|십시오|바랍니다|있음|있습니다|한다|주의)\s*[,，.]\s*", r"\1\n", t)
    items = []
    for line in t.split("\n"):
        line = re.split(r"[\(（]\s*영문\s*[\)）]", line)[0]           # 같은 줄의 영문 번역 버림
        line = line.strip(" ,，.;")
        line = re.sub(r"^[\(（]?\s*(국문|영문)\s*[\)）]?\s*", "", line)
        if len(line) < 3 or hangul_ratio(line) < 0.3:              # 영어 번역 줄, 찌꺼기 제거
            continue
        items.append(line)
    return items


def expand_dots(item):
    """'면역력 증진·피로개선에 도움을 줄 수 있음' → 두 항목 (뒤 서술어를 나눠 붙임)"""
    item = re.sub(r"(?<=[가-힣])\s*[/／]\s*(?=[가-힣])", "·", item)      # "증진/피로개선"도 같은 방식
    parts = [x.strip() for x in re.split(r"\s*·\s*", item) if x.strip()]
    # "혈중 콜레스테롤 개선, 식후 혈당상승 억제에 도움"처럼 쉼표로 이어진 기능성 이름도 나눔
    # ("지방, 탄수화물, 단백질 대사"처럼 기능성 이름이 아닌 쉼표는 그대로 둠)
    NOMINAL = r"(개선|억제|원활|증진|감소|증식|건강|보호|유지|형성|흡수|촉진|완화)$"
    expanded = []
    for x in parts:
        sub = [y.strip() for y in re.split(r"\s*[,，]\s*", x) if y.strip()]
        if len(sub) > 1 and all(re.search(NOMINAL, y) for y in sub[:-1]):
            expanded.extend(sub)
        else:
            expanded.append(x)
    parts = expanded
    if len(parts) == 1:
        return parts
    if any(len(x) <= 2 for x in parts[:-1]):
        return [item]                      # "산화·환원 효소"처럼 한 단어인 경우
    tail_m = re.search(r"((?:에|데)\s*(?:도움|필요|관여).*)$", parts[-1])
    if not tail_m:
        return [item]                      # 서술어를 못 찾으면 나누지 않음
    tail = tail_m.group(1)
    out = []
    for x in parts:
        out.append(x if re.search(PRED, x) else f"{x}{tail}")
    return out


def normalize_ending(s):
    s = re.split(r"[\(（]?\s*영문\s*[\)）]?", s)[0]                  # 영문 번역 버림
    s = re.sub(r"[\s(（]*[A-Za-z][A-Za-z0-9 ,.'\-()]{12,}[)）]?\s*$", "", s)  # 끝에 붙은 영어 문장
    s = GRADE_TAG.sub("", s)
    s = re.sub(r"[\(（]?\s*국문\s*[\)）]?\s*", "", s)
    s = re.sub(r"(있)으나,?\s*인체\s*적용\s*시험이\s*미흡함?", r"\1음", s)   # 옛 3등급 문구의 단서 제거
    s = re.sub(r"^([^\s]{1,15})\s+-\s+(?=.*(?:도움|필요))", "", s)        # "비타민E - 항산화..."
    if re.search(r"[:：]", s):                                         # "기능성 : 함량 정보" / "원료명 : 기능성"
        left, right = re.split(r"\s*[:：]\s*", s, maxsplit=1)
        if re.search(PRED, left):
            s = left
        elif re.search(PRED, right):
            s = right
    s = s.strip(" \"'“”‘’「」『』[]()（）:：")
    s = re.sub(r"[.。]+$", "", s).strip()
    s = re.sub(r"도움을\s*줄\s*수\s*있(?:음|습니다)$", "도움을 줄 수 있다", s)
    s = re.sub(r"도움을\s*줌$", "도움을 준다", s)
    s = re.sub(r"(에|데)\s*도움$", r"\1 도움을 줄 수 있다", s)
    s = re.sub(r"필요$", "필요하다", s)
    s = re.sub(r"관여$", "관여한다", s)
    s = re.sub(r"있습니다$", "있다", s)
    s = re.sub(r"(됨|됩니다)$", "된다", s)
    s = re.sub(r"줍니다$", "준다", s)
    s = re.sub(r"있음$", "있다", s)
    return re.sub(r"\s+", " ", s).strip()


STATED_SUBJ = re.compile(r"^(.{2,45}?)(은|는)\s+(?=.*(?:도움|필요))")


def split_stated_subject(s):
    """'식물스타놀 에스테르는 ...' → ('식물스타놀 에스테르', '...')"""
    m = STATED_SUBJ.match(s)
    if m and not re.search(FUNC_WORDS, m.group(1)) \
            and not re.search(r"(시|하|되|있|없|또)$|[이가]\s|[“”\"]", m.group(1)):   # "걱정되시는 분" 같은 수식어 제외
        return m.group(1).strip(), s[m.end():]
    return None, s


def parse_functionality(text):
    rows = []
    for label, block in split_blocks(text):
        raw_items = split_items(block, "func")
        # 묶음 안의 마지막 서술어 꼬리 ("에 도움을 줄 수 있음")를 찾아 둔다
        tail = None
        for it in reversed(raw_items):
            m = re.search(r"((?:에|데)\s*(?:도움|필요|관여).*)$", it)
            if m:
                tail = m.group(1)
                break
        for it in raw_items:
            inferred = False
            if not re.search(PRED, it):                    # 서술어가 빠진 항목은 꼬리를 빌려 붙인다
                if not re.search(FUNC_WORDS, it):
                    continue                               # 기능성 문장이 아님
                it = f"{it}{tail}" if tail else f"{it}에 도움을 줄 수 있음"
                inferred = tail is None
            for piece in expand_dots(it):                  # "A·B에 도움" → "A에 도움", "B에 도움"
                core = normalize_ending(piece)
                if re.fullmatch(r"인체에서의\s*확인이\s*필요함?", core):   # 기능성이 아니라 단서 문구
                    continue
                subj, core = split_stated_subject(core)
                status = "OK"
                if len(core) > 90 or re.search(rf"[{CIRCLED}{PAREN_NUM}:：/／]", core):
                    status = "CHECK"
                rows.append({"ingredient_label": label or subj, "core": core, "raw": piece,
                             "inferred_predicate": inferred, "status": status})
    return dedupe(rows)


def normalize_precaution(s):
    """명령형 주의사항을 평서문으로: '섭취를 피할 것' → '섭취를 피해야 한다'"""
    s = re.sub(r"\s+", " ", s.strip(" \"'“”")).strip()
    s = re.sub(r"[.。]+$", "", s)
    s = re.sub(r"하(?:십시오|십시요|시요|시기\s*바랍니다|세요)$", "해야 한다", s)
    s = re.sub(r"말\s*것$", "말아야 한다", s)
    s = re.sub(r"할\s*것$", "해야 한다", s)
    s = re.sub(r"주의$", "주의해야 한다", s)
    return s


def parse_precautions(text):
    rows = []
    for label, block in split_blocks(text):
        for it in split_items(block, "prec"):
            core = normalize_precaution(it)
            if len(core) < 4:
                continue
            rows.append({"ingredient_label": label, "core": core, "raw": it,
                         "inferred_predicate": False, "status": "OK" if len(core) <= 120 else "CHECK"})
    return dedupe(rows)


def dedupe(rows):
    seen, out = set(), []
    for r in rows:
        key = re.sub(r"\s+", "", r["core"])
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out


# ─────────────────────────────────────────────────────────────
# 4. 실행할 때 쓰는 함수: 주어 붙이기, NLI 쌍 만들기
# ─────────────────────────────────────────────────────────────
DIGIT_BATCHIM = {"0": True, "1": True, "2": False, "3": True, "4": False,
                 "5": False, "6": True, "7": True, "8": True, "9": False}
LATIN_BATCHIM = set("LMNRlmnr")          # 엘, 엠, 엔, 알


def topic_particle(word):
    """받침에 맞춰 '은/는'을 고른다. 홍삼→은, 비타민C→는, 코엔자임Q10→은"""
    w = re.sub(r"[\s\)）\]]+$", "", word)
    w = re.sub(r"[\(（][^)）]*$", "", w).strip() or word.strip()
    ch = w[-1]
    if "가" <= ch <= "힣":
        return "은" if (ord(ch) - 0xAC00) % 28 else "는"
    if ch.isdigit():
        return "은" if DIGIT_BATCHIM[ch] else "는"
    if ch.isalpha():
        return "은" if ch in LATIN_BATCHIM else "는"
    return "은(는)"


def make_premise(subject, core):
    """주어 + 정리된 문장 → NLI 전제 문장"""
    return f"{subject}{topic_particle(subject)} {core}"


def build_pairs(claim, premises, subject):
    """
    claim:    {"claim_id", "hypothesis"}  (가설 문장은 주어가 이미 맞춰진 상태)
    premises: parse_functionality / parse_precautions 결과(또는 CSV 행) 목록
    subject:  전제에 붙일 주어 (광고 주장의 target)
    반환:     [{"claim_id", "premise_ref", "premise", "hypothesis"}, ...]
    """
    pairs = []
    for i, p in enumerate(premises):
        etype = p.get("evidence_type", "")
        # 주의사항은 "임산부는 ~" 처럼 자기 주어가 있어서 제품 주어를 붙이지 않는다
        premise = p["core"] if "PRECAUTION" in etype else make_premise(subject, p["core"])
        pairs.append({
            "claim_id": claim["claim_id"],
            "premise_ref": p.get("ref", i),
            "evidence_type": etype,
            "premise": premise,
            "hypothesis": claim["hypothesis"],
        })
    return pairs


# ─────────────────────────────────────────────────────────────
# 5. 일괄 처리
# ─────────────────────────────────────────────────────────────
def clean_evidence_text(t):
    t = normalize_text(t)
    t = re.split(r"[\(（]\s*영문\s*[\)）]", t)[0]                  # 영문 번역 부분 버림
    return t


def main(prod_path, evid_path, out_dir="."):
    csv.field_size_limit(10**8)
    report = []
    # 제품 단위
    n_prod = n_func_prod = n_raw = 0
    endings = Counter()
    status_cnt = Counter()
    per_prod = []
    with open(prod_path, encoding="utf-8-sig") as f, \
         open(f"{out_dir}/premises_product.csv", "w", newline="", encoding="utf-8-sig") as g:
        w = csv.writer(g)
        w.writerow(["ref", "product_id", "evidence_type", "ingredient_label", "core",
                    "inferred_predicate", "status", "is_raw_material", "raw"])
        for row in csv.DictReader(f):
            n_prod += 1
            pid = row["product_id"]
            raw_mat = "원료로 사용" in (row.get("intake_method") or "")
            n_raw += raw_mat
            funcs = parse_functionality(row.get("main_functionality"))
            precs = parse_precautions(row.get("intake_precautions"))
            per_prod.append(len(funcs))
            n_func_prod += bool(funcs)
            for kind, items in (("FUNCTIONALITY", funcs), ("PRECAUTION", precs)):
                for k, it in enumerate(items):
                    if kind == "FUNCTIONALITY":
                        endings[re.search(r"(도움을 줄 수 있다|도움을 준다|필요하다)$", it["core"]).group(1)
                                if re.search(r"(도움을 줄 수 있다|도움을 준다|필요하다)$", it["core"]) else "기타"] += 1
                        status_cnt[it["status"]] += 1
                    w.writerow([f"product:{pid}:{kind[0]}{k}", pid, kind, it["ingredient_label"] or "",
                                it["core"], int(it["inferred_predicate"]), it["status"], int(raw_mat), it["raw"]])
    # 원료 단위
    n_ev = 0
    with open(evid_path, encoding="utf-8-sig") as f, \
         open(f"{out_dir}/premises_ingredient.csv", "w", newline="", encoding="utf-8-sig") as g:
        w = csv.writer(g)
        w.writerow(["ref", "ingredient_id", "evidence_id", "evidence_type", "stated_subject", "core", "status", "raw"])
        for row in csv.DictReader(f):
            et = row["evidence_type"]
            if et not in ("OFFICIAL_FUNCTIONALITY", "OFFICIAL_PRECAUTION"):
                continue
            text = clean_evidence_text(row["evidence_text"])
            items = parse_functionality(text) if et == "OFFICIAL_FUNCTIONALITY" else parse_precautions(text)
            for k, it in enumerate(items):
                n_ev += 1
                w.writerow([f"evidence:{row['evidence_id']}:{k}", row["ingredient_id"], row["evidence_id"], et,
                            it["ingredient_label"] or "", it["core"], it["status"], it["raw"]])

    s = sorted(per_prod)
    report += [
        f"제품 수: {n_prod}",
        f"기능성 문장이 1개 이상 나온 제품: {n_func_prod} ({n_func_prod / n_prod:.1%})",
        f"원료 제품(섭취방법 '원료로 사용'): {n_raw}",
        f"제품당 기능성 문장 수: 평균 {sum(s) / len(s):.1f}, 중앙값 {s[len(s) // 2]}, 최대 {s[-1]}",
        f"기능성 문장 끝 형태: {dict(endings)}",
        f"상태: {dict(status_cnt)}  (CHECK = 너무 길거나 나누기 기호가 남아 있어 사람이 확인할 것)",
        f"원료 단위 전제 문장 수: {n_ev}",
    ]
    with open(f"{out_dir}/prep_report.txt", "w", encoding="utf-8") as g:
        g.write("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ".")
