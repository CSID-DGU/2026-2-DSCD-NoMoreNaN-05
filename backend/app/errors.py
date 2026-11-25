from fastapi.responses import JSONResponse

ERRORS = {
    "COMMON_400": (400, "잘못된 요청입니다."),
    "COMMON_404": (404, "요청한 데이터를 찾을 수 없습니다."),
    "COMMON_500": (500, "서버 내부 오류가 발생했습니다."),
    "URL_001": (400, "영상 주소가 아니에요. YouTube · Instagram · TikTok 영상 주소를 넣어 주세요."),
    "URL_002": (400, "비공개이거나 삭제된 영상이에요. 공개된 영상 주소를 넣어 주세요."),
    "JOB_001": (500, "검증을 시작하지 못했어요. 잠시 후 다시 눌러 주세요."),
    "JOB_002": (404, "검증 기록을 찾을 수 없어요. 영상 주소를 다시 넣어 주세요."),
    "JOB_003": (404, "영상을 아직 가져오지 못했어요."),
    "JOB_004": (409, "검증이 아직 끝나지 않았어요."),
    "JOB_005": (409, "검증을 멈춘 작업이라 결과가 없어요."),
}


class ApiError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code
        self.status = ERRORS[code][0]


def ok(data, code=200) -> dict:
    return {"success": True, "code": code, "message": "요청 성공", "data": data}


def fail(code: str) -> JSONResponse:
    status, message = ERRORS[code]
    return _error(status, message, code)


def _error(status: int, message: str, code: str) -> JSONResponse:
    body = {"success": False, "code": status, "message": message, "error": {"code": code}, "data": None}
    return JSONResponse(body, status_code=status)


async def api_error(request, exc: ApiError):
    return fail(exc.code)


async def validation_error(request, exc):
    return fail("COMMON_400")


async def http_error(request, exc):
    code = f"COMMON_{exc.status_code}"
    if code in ERRORS:
        return fail(code)
    return _error(exc.status_code, exc.detail, code)


async def server_error(request, exc):
    return fail("COMMON_500")
