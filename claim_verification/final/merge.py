"""A 결과와 B 결과를 클레임마다 최종 라벨 하나로 합친다.

입력 클레임 전체가 기준이다. 결과는 입력 순서대로 클레임마다 한 건이다.
    키: video_id + product_ref + claim_id

라벨 우선순위(B 담당 설정과 같음): DISCLAIMER 먼저, 나머지는 VIOLATION > OVERCLAIM > UNCLEAR > SUPPORTED > OUT_OF_SCOPE.
    A와 B가 모두 결과를 냈으면 우선순위가 앞선 라벨을 쓴다. 면책 문구는 A를 먼저 따른다.
    OVERCLAIM은 B만 낸다.

오류로 멈추는 경우(조용히 틀린 결과를 내지 않기 위해):
    EFFECT가 붙은 클레임인데 B 결과가 없음 / EFFECT가 없는 클레임에 B 결과가 있음
    입력에 없는 클레임의 B 결과 / B 결과 키 중복 / 알 수 없는 B 라벨

A가 제품 미확정으로 건너뛴 클레임(skipped)은 근거가 없으므로 UNCLEAR로 두고 사유를 남긴다.

결과 행에는 최종 라벨 하나와 함께 판정 근거를 담는다(결과 페이지용).
    A.checks: 원료·수치 하나마다 판정한 결과
"""

from ..claim_types.result import OUT_OF_SCOPE
from ..claim_types.tags import EFFECT, claim_types, types_of
from ..disclaimer import DISCLAIMER
from ..finding import OVERCLAIM, SUPPORTED, UNCLEAR, VIOLATION

LABEL_ORDER = (VIOLATION, OVERCLAIM, UNCLEAR, SUPPORTED, OUT_OF_SCOPE)
LABELS = (DISCLAIMER, *LABEL_ORDER)

A, B = "A", "B"
B_FIELDS = ("video_id", "product_ref", "claim_id", "label")


class MergeError(ValueError):
    """A·B 결과를 합칠 수 없을 때. 메시지에 문제 클레임 키를 담는다."""


def key(video_id: str, claim: dict) -> tuple:
    return video_id, claim.get("product_ref"), claim["claim_id"]


def index_b(records: list[dict]) -> dict[tuple, dict]:
    out = {}
    for r in records:
        missing = [f for f in B_FIELDS if f not in r]
        if missing:
            raise MergeError(f"B 결과에 필드 없음 {missing}: {r.get('video_id')}/{r.get('claim_id')}")
        if r["label"] not in LABELS:
            raise MergeError(f"알 수 없는 B 라벨 {r['label']!r}: {r['video_id']}/{r['claim_id']}")
        k = key(r["video_id"], r)
        if k in out:
            raise MergeError(f"B 결과 키 중복: {k}")
        out[k] = r
    return out


def final_label(a_label: str | None, b_label: str | None) -> tuple[str, list[str]]:
    """(최종 라벨, 그 라벨을 낸 쪽)."""
    labels = {A: a_label, B: b_label}
    if a_label == DISCLAIMER:
        return DISCLAIMER, [A] + ([B] if b_label == DISCLAIMER else [])
    if b_label == DISCLAIMER:
        return DISCLAIMER, [B]
    for label in LABEL_ORDER:
        by = [side for side, value in labels.items() if value == label]
        if by:
            return label, by
    raise MergeError("A·B 라벨이 모두 없음")


def _a_part(claim: dict) -> dict:
    """A 라벨과 항목별 판정(원료·수치 하나마다 status, reason, 대조한 DB 값)."""
    return {"label": claim["label"], "reason_codes": claim["reason_codes"], "checks": claim.get("checks", [])}


def _b_part(record: dict) -> dict:
    return {k: record.get(k) for k in ("label", "reason_code", "reason", "evidence_text")}


def merge_video(video: dict, a_result: dict, b_index: dict[tuple, dict], used: set) -> list[dict]:
    vid = video["video_id"]
    a_claims = {c["claim_id"]: c for c in a_result["claims"]}
    skipped = {s["claim_id"]: s["reason"] for s in a_result["skipped"]}
    out = []
    for claim in video["claims"]:
        k = key(vid, claim)
        cid = claim["claim_id"]
        b = b_index.get(k)
        has_effect = EFFECT in claim_types(claim)
        if b is not None:
            used.add(k)
            if not has_effect:
                raise MergeError(f"EFFECT가 없는 클레임에 B 결과가 있음: {k}")
        row = {"video_id": vid, "product_ref": claim.get("product_ref"), "claim_id": cid,
               "claim_type": types_of(claim), "text": claim["text"]}
        if cid in skipped:
            row.update(final_label=UNCLEAR, decided_by=[], skipped_reason=skipped[cid], A=None,
                       B=_b_part(b) if b else None)
            out.append(row)
            continue
        if has_effect and b is None:
            raise MergeError(f"EFFECT 클레임인데 B 결과가 없음: {k}")
        a = a_claims.get(cid)
        if a is None and b is None:
            raise MergeError(f"A·B 결과가 모두 없음: {k}")
        label, by = final_label(a["label"] if a else None, b["label"] if b else None)
        row.update(final_label=label, decided_by=by, skipped_reason=None,
                   A=_a_part(a) if a else None, B=_b_part(b) if b else None)
        out.append(row)
    return out


def merge(videos: list[dict], a_results: list[dict], b_records: list[dict]) -> list[dict]:
    if [v["video_id"] for v in videos] != [r["video_id"] for r in a_results]:
        raise MergeError("입력 영상과 A 결과의 영상 순서가 다름")
    b_index = index_b(b_records)
    used: set = set()
    rows = [row for video, a in zip(videos, a_results) for row in merge_video(video, a, b_index, used)]
    extra = sorted(set(b_index) - used, key=str)
    if extra:
        raise MergeError(f"입력에 없는 클레임의 B 결과 {len(extra)}건: {extra[:5]}")
    return rows
