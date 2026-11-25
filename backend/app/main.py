from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS

from . import cache, errors, jobs, llm, worker
from .routes import router


@asynccontextmanager
async def lifespan(_):
    cache.open()
    jobs.restore(jobs.now())
    llm.start()
    worker.start()
    yield
    worker.stop()
    llm.stop()
    cache.close()


api = FastAPI(title="TRUEAD API", lifespan=lifespan)
api.add_exception_handler(errors.ApiError, errors.api_error)
api.add_exception_handler(RequestValidationError, errors.validation_error)
api.add_exception_handler(StarletteHTTPException, errors.http_error)
api.add_exception_handler(Exception, errors.server_error)
api.include_router(router)

app = CORSMiddleware(api, allow_origins=CORS_ORIGINS, allow_methods=["GET", "POST"],
                     allow_headers=["Content-Type", "Range"], expose_headers=["Content-Range", "Accept-Ranges"])
