"""최종 결과(final_results.json의 results)와 정답 파일(gold_label이 있는 영상 목록)을 클레임마다 붙인다.

    키: video_id + product_ref + claim_id

한쪽에만 있는 클레임, 키 중복, gold_label이 없는 클레임은 오류다. 평가 건수가 조용히 줄면 안 되기 때문이다.
"""

GOLD = "gold_label"


class JoinError(ValueError):
    """최종 결과와 정답을 붙일 수 없을 때. 메시지에 문제 클레임 키를 담는다."""


def _key(video_id: str, claim: dict) -> tuple:
    return video_id, claim.get("product_ref"), claim["claim_id"]


def gold_index(videos: list[dict]) -> dict[tuple, dict]:
    out = {}
    for video in videos:
        for claim in video["claims"]:
            k = _key(video["video_id"], claim)
            if GOLD not in claim:
                raise JoinError(f"정답 라벨 없음: {k}")
            if k in out:
                raise JoinError(f"정답 키 중복: {k}")
            out[k] = claim
    return out


def join(results: list[dict], gold_videos: list[dict]) -> list[dict]:
    """최종 결과 순서대로 [{video_id, product_ref, claim_id, claim_type, text, gold, pred, decided_by, A, B, skipped_reason}]."""
    gold = gold_index(gold_videos)
    rows, seen = [], set()
    for r in results:
        k = _key(r["video_id"], r)
        if k in seen:
            raise JoinError(f"최종 결과 키 중복: {k}")
        seen.add(k)
        if k not in gold:
            raise JoinError(f"정답에 없는 클레임: {k}")
        rows.append({"video_id": r["video_id"], "product_ref": r.get("product_ref"), "claim_id": r["claim_id"],
                     "claim_type": r.get("claim_type"), "text": r.get("text"), "gold": gold[k][GOLD],
                     "pred": r["final_label"], "decided_by": r.get("decided_by", []), "A": r.get("A"), "B": r.get("B"),
                     "skipped_reason": r.get("skipped_reason")})
    missing = sorted(set(gold) - seen, key=str)
    if missing:
        raise JoinError(f"최종 결과에 없는 클레임 {len(missing)}건: {missing[:5]}")
    return rows
