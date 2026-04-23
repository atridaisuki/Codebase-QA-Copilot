import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.responses import Response

logger = logging.getLogger("codebase_qa")


def configure_logging() -> None:
    if logger.handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    started_at = time.perf_counter()

    response = await call_next(request)

    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "request completed method=%s path=%s status=%s duration_ms=%s request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )
    return response
