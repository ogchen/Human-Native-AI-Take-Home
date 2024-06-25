import logging
import time
from fastapi import FastAPI
from fastapi import Request
from typing import Any
from typing import Callable

from app.routers import report

logger = logging.getLogger("uvicorn")
report_app = FastAPI()
report_app.include_router(report.router)

@report_app.middleware("http")
async def log_processing_time(request: Request, call_next: Callable[[Request], Any]):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
