"""판정 입력(claims_with_db 형식, 영상 목록)을 확인한다. 메커니즘 A와 최종 판정이 같은 입력을 쓴다.

    [{"video_id", "url", "db_version",
      "products": [{"product_ref", "product_name", ..., "match": {"status", ...}, "DB": {"QUANTITY": {...}, ...} | null}],
      "claims": [{"claim_id", "product_ref" | null, "text", "claim_type": ["EFFECT", ...] | "EFFECT", ...}]}]

필수 필드는 판정에서 실제로 쓰는 것만 둔다. 나머지 필드는 고치지 않고 그대로 넘긴다.
confirmed 제품은 DB가 있어야 한다(A·B가 DB 값과 대조한다). 다른 상태의 DB는 보지 않는다.
클레임의 product_ref는 비어 있을 수 있지만, 값이 있으면 같은 영상의 제품이어야 한다.
video_id는 목록 안에서, product_ref·claim_id는 영상 안에서 겹치면 안 된다(최종 판정이 이 값으로 결과를 붙인다).
"""

from collections import Counter

VIDEO_FIELDS = ("video_id", "products", "claims")
PRODUCT_FIELDS = ("product_ref", "match")
CLAIM_FIELDS = ("claim_id", "text", "claim_type")

# 광고 제품을 DB에서 특정했는지. 닫힌 목록이다.
CONFIRMED = "confirmed"
UNRESOLVED = "unresolved"
NOT_FOUND = "not_found"
MATCH_STATUSES = (CONFIRMED, UNRESOLVED, NOT_FOUND)


class InputError(ValueError):
    """입력 형식이 맞지 않을 때. 메시지에 위치(video_id/product_ref/claim_id)를 담는다."""


def validate_videos(videos: list[dict]) -> None:
    if not isinstance(videos, list):
        raise InputError("입력은 영상 목록이어야 함")
    for video in videos:
        validate_video(video)
    _unique([v["video_id"] for v in videos], "video_id", "input")


def validate_video(video: dict) -> None:
    _require(video, VIDEO_FIELDS, "video")
    vid = video["video_id"]
    for product in video["products"]:
        _validate_product(product, vid)
    refs = [p["product_ref"] for p in video["products"]]
    _unique(refs, "product_ref", vid)
    for claim in video["claims"]:
        where = f"{vid}/{claim.get('claim_id', '?')}"
        _require(claim, CLAIM_FIELDS, where)
        _validate_claim_type(claim["claim_type"], where)
        ref = claim.get("product_ref")
        if ref is not None and ref not in refs:
            raise InputError(f"{where}: 영상에 없는 product_ref {ref!r}")
    _unique([c["claim_id"] for c in video["claims"]], "claim_id", vid)


def _validate_product(product: dict, vid: str) -> None:
    where = f"{vid}/{product.get('product_ref', '?')}"
    _require(product, PRODUCT_FIELDS, where)
    _require(product["match"], ("status",), f"{where}/match")
    status = product["match"]["status"]
    if status not in MATCH_STATUSES:
        raise InputError(f"{where}/match: 알 수 없는 status {status!r}")
    if status == CONFIRMED and not isinstance(product.get("DB"), dict):
        raise InputError(f"{where}: confirmed인데 DB가 없음")


def _validate_claim_type(value, where: str) -> None:
    values = [value] if isinstance(value, str) else value
    if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
        raise InputError(f"{where}: claim_type은 문자열이나 문자열 배열이어야 함")


def _unique(values: list, name: str, where: str) -> None:
    duplicated = [v for v, n in Counter(values).items() if n > 1]
    if duplicated:
        raise InputError(f"{where}: {name} 중복 {duplicated[:5]}")


def _require(obj: dict, fields: tuple[str, ...], where: str) -> None:
    missing = [f for f in fields if f not in obj]
    if missing:
        raise InputError(f"{where}: 필드 없음 {missing}")
