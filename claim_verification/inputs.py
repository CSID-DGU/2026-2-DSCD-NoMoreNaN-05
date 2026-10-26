"""DB 담당의 evidence handoff(광고 영상 한 편)를 확인한다.

    {"video_id", "products": [...], "claims": [{..., "evidences": [...]}]}

서비스에서는 validate_video(dict)만 쓴다. load_handoff(path)는 로컬 파일로 돌릴 때만 쓴다.
필수 필드는 판정에서 실제로 쓰는 것만 둔다. 나머지 필드는 고치지 않고 그대로 넘긴다.
"""

import json
from pathlib import Path

VIDEO_FIELDS = ("video_id", "products", "claims")
CLAIM_FIELDS = ("claim_id", "text", "evidences")
EVIDENCE_FIELDS = ("source_ref", "text", "source")


class HandoffError(ValueError):
    """handoff 형식이 맞지 않을 때. 메시지에 위치(video_id/claim_id)를 담는다."""


def load_handoff(path: str | Path) -> dict:
    video = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_video(video)
    return video


def validate_video(video: dict) -> None:
    _require(video, VIDEO_FIELDS, "video")
    vid = video["video_id"]
    # 영상 하나에 제품 하나(DB 담당이 정제해서 넘김). judge는 이 제품 하나를 모든 클레임에 쓴다.
    # 그래서 판정에는 product_ref가 필요 없다(있으면 결과에 그대로 넘긴다).
    if len(video["products"]) != 1:
        raise HandoffError(f"{vid}: products는 1개여야 함 (현재 {len(video['products'])}개)")
    for claim in video["claims"]:
        where = f"{vid}/{claim.get('claim_id', '?')}"
        _require(claim, CLAIM_FIELDS, where)
        for i, ev in enumerate(claim["evidences"]):
            _require(ev, EVIDENCE_FIELDS, f"{where}/evidences[{i}]")


def _require(obj: dict, fields: tuple[str, ...], where: str) -> None:
    missing = [f for f in fields if f not in obj]
    if missing:
        raise HandoffError(f"{where}: 필드 없음 {missing}")
