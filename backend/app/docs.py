from pathlib import Path

from files import load_json

from .errors import ERRORS

_EX = load_json(Path(__file__).with_name("examples.json"))


def _ok(key) -> dict:
    return {"content": {"application/json": {"example": _EX[key]}}}


def _fail(*codes) -> dict:
    examples = {}
    for code in codes:
        status, message = ERRORS[code]
        body = {"success": False, "code": status, "message": message, "error": {"code": code}, "data": None}
        examples[code] = {"summary": code, "value": body}
    return {"content": {"application/json": {"examples": examples}}}


CREATE_JOB = {201: _ok("create_job"), 400: _fail("COMMON_400", "URL_001", "URL_002"), 500: _fail("JOB_001")}
GET_JOB = {200: _ok("get_job"), 404: _fail("JOB_002")}
GET_VIDEO = {
    200: {"content": {"video/mp4": {"schema": {"type": "string", "format": "binary"}}}},
    404: _fail("JOB_002", "JOB_003"),
}
GET_RESULT = {200: _ok("get_result"), 404: _fail("JOB_002"), 409: _fail("JOB_004", "JOB_005")}
