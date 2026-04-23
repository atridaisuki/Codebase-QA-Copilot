import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import ErrorResponse

logger = logging.getLogger("codebase_qa")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            "http error status=%s path=%s detail=%s request_id=%s",
            exc.status_code,
            request.url.path,
            exc.detail,
            request_id,
        )
        payload = ErrorResponse(detail=str(exc.detail), request_id=request_id)
        return JSONResponse(status_code=exc.status_code, content=payload.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.warning(
            "validation error path=%s errors=%s request_id=%s",
            request.url.path,
            exc.errors(),
            request_id,
        )
        payload = ErrorResponse(detail="Request validation failed.", request_id=request_id)
        return JSONResponse(status_code=422, content=payload.model_dump())

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.exception(
            "unhandled error path=%s request_id=%s",
            request.url.path,
            request_id,
            exc_info=exc,
        )
        payload = ErrorResponse(detail="Internal server error.", request_id=request_id)
        return JSONResponse(status_code=500, content=payload.model_dump())
