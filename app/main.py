"""Точка входа FastAPI. Собирает сценарии, API и страницу."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.presentation.api.routes_documents import router as documents_router
from app.presentation.api.routes_schemas import router as schemas_router
from app.presentation.dependencies import get_recognizer
from app.presentation.errors import register_error_handlers
from app.presentation.web.routes import router as web_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Закрывает клиент GigaChat при остановке процесса."""
    yield
    await get_recognizer().aclose()


def create_app() -> FastAPI:
    """Создаёт приложение: страница, распознавание и схемы."""
    app = FastAPI(title="Распознавание документов", version="1.0.0", lifespan=lifespan)
    register_error_handlers(app)
    app.include_router(web_router)
    app.include_router(documents_router)
    app.include_router(schemas_router)
    return app


app = create_app()
