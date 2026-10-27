"""DB 담당의 handoff(광고 영상 한 편)를 확인한다.

    {"video_id", "db_version",
     "product": {"match": {"status", "method", "note"},
                 "evi_product": {"product_id", ..., "main_functionality"} | null},
     "claims": [{"claim_id", "text", ...}]}

서비스에서는 validate_video(dict)만 쓴다. load_handoff(path)는 로컬 파일로 돌릴 때만 쓴다.
필수 필드는 판정에서 실제로 쓰는 것만 둔다. 나머지 필드는 고치지 않고 그대로 넘긴다.
"""

import json
from pathlib import Path

VIDEO_FIELDS = ("video_id", "product", "claims")
PRODUCT_FIELDS = ("match", "evi_product")
CLAIM_FIELDS = ("claim_id", "text")

# 광고 제품을 DB에서 특정했는지. 닫힌 목록이다.
CONFIRMED = "confirmed"
UNRESOLVED = "unresolved"
NOT_FOUND = "not_found"
MATCH_STATUSES = (CONFIRMED, UNRESOLVED, NOT_FOUND)


class HandoffError(ValueError):
    """handoff 형식이 맞지 않을 때. 메시지에 위치(video_id/claim_id)를 담는다."""


def load_handoff(path: str | Path) -> dict:
    video = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_video(video)
    return video


def validate_video(video: dict) -> None:
    _require(video, VIDEO_FIELDS, "video")
    vid = video["video_id"]
    _validate_product(video["product"], f"{vid}/product")
    for claim in video["claims"]:
        _require(claim, CLAIM_FIELDS, f"{vid}/{claim.get('claim_id', '?')}")


def _validate_product(product: dict, where: str) -> None:
    _require(product, PRODUCT_FIELDS, where)
    _require(product["match"], ("status",), f"{where}/match")
    status = product["match"]["status"]
    if status not in MATCH_STATUSES:
        raise HandoffError(f"{where}/match: 알 수 없는 status {status!r}")
    evi = product["evi_product"]
    # 제품을 못 찾았으면 근거가 없어야 하고, 찾았으면(확정이든 후보든) 기능성 원문이 있어야 한다.
    if status == NOT_FOUND:
        if evi is not None:
            raise HandoffError(f"{where}: not_found인데 evi_product가 있음")
    elif evi is None:
        raise HandoffError(f"{where}: {status}인데 evi_product가 없음")
    else:
        _require(evi, ("main_functionality",), f"{where}/evi_product")


def _require(obj: dict, fields: tuple[str, ...], where: str) -> None:
    missing = [f for f in fields if f not in obj]
    if missing:
        raise HandoffError(f"{where}: 필드 없음 {missing}")
