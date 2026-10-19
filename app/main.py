"""Точка входа FastAPI. Собирает сценарии, API и страницу."""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.presentation.api.routes_documents import router as documents_router
from app.presentation.api.routes_schemas import router as schemas_router
from app.presentation.dependencies import get_recognizer
from app.presentation.errors import register_error_handlers
from app.presentation.security import require_access
from app.presentation.web.routes import router as web_router

_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
    "Content-Security-Policy": (
        "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; "
        "base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
    ),
}


class _SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Добавляет заголовки, которые мешают подмене типа ответа и встраиванию страницы."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers.update(_SECURITY_HEADERS)
        return response


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Закрывает клиент GigaChat при остановке процесса."""
    yield
    await get_recognizer().aclose()


def create_app() -> FastAPI:
    """Создаёт приложение: страница, распознавание и схемы."""
    logging.basicConfig(level=logging.INFO)
    app = FastAPI(
        title="Распознавание документов",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.add_middleware(_SecurityHeadersMiddleware)
    register_error_handlers(app)
    app.include_router(web_router)
    app.include_router(documents_router, dependencies=[Depends(require_access)])
    app.include_router(schemas_router, dependencies=[Depends(require_access)])
    return app


app = create_app()
