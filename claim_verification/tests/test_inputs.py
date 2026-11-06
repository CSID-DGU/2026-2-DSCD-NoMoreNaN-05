import copy
import json
from pathlib import Path

import pytest

from claim_verification.inputs import InputError, validate_video, validate_videos

# 평가 입력. 로컬에만 있다.
EVAL_INPUT = Path(__file__).resolve().parents[2] / "data/eval/claims_with_db_1554/claims_with_db_test.json"


def video(status="confirmed", db=None, **claim_overrides):
    claim = {"claim_id": "c01", "product_ref": "p01", "text": "건강기능식품", "claim_type": ["CERTIFICATION"]}
    claim.update(claim_overrides)
    product = {"product_ref": "p01", "product_name": "제품", "match": {"status": status},
               "DB": {"CERTIFICATION": {}} if db is None else db}
    return {"video_id": "v1", "url": None, "db_version": "x", "products": [product], "claims": [claim]}


def test_valid_video_passes():
    validate_video(video())
    validate_video(video(claim_type="EFFECT"))
    validate_video(video(product_ref=None))


def test_unknown_match_status():
    with pytest.raises(InputError, match="알 수 없는 status 'matched'"):
        validate_video(video(status="matched"))


def test_confirmed_needs_db():
    with pytest.raises(InputError, match="v1/p01: confirmed인데 DB가 없음"):
        validate_video(video(db=False))


@pytest.mark.parametrize("status", ["unresolved", "not_found"])
def test_unconfirmed_may_have_no_db(status):
    data = video(status=status)
    data["products"][0]["DB"] = None
    validate_video(data)


def test_missing_claim_field_names_location():
    data = video()
    del data["claims"][0]["claim_type"]
    with pytest.raises(InputError, match=r"v1/c01: 필드 없음 \['claim_type'\]"):
        validate_video(data)


@pytest.mark.parametrize("claim_type", [None, 3, ["EFFECT", 1]])
def test_claim_type_must_be_text(claim_type):
    with pytest.raises(InputError, match="claim_type"):
        validate_video(video(claim_type=claim_type))


def test_claim_ref_must_be_in_video():
    with pytest.raises(InputError, match="영상에 없는 product_ref 'p09'"):
        validate_video(video(product_ref="p09"))


def test_duplicates_are_rejected():
    data = video()
    data["claims"].append(dict(data["claims"][0]))
    with pytest.raises(InputError, match="claim_id 중복"):
        validate_video(data)
    data = video()
    data["products"].append(dict(data["products"][0]))
    with pytest.raises(InputError, match="product_ref 중복"):
        validate_video(data)
    with pytest.raises(InputError, match="video_id 중복"):
        validate_videos([video(), copy.deepcopy(video())])


def test_videos_must_be_list():
    with pytest.raises(InputError, match="영상 목록"):
        validate_videos(video())


@pytest.mark.skipif(not EVAL_INPUT.exists(), reason="로컬 평가 입력 없음")
def test_eval_input_matches_format():
    validate_videos(json.loads(EVAL_INPUT.read_text(encoding="utf-8")))
