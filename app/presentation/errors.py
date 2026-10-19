"""Перевод доменных ошибок в JSON-ответы HTTP."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    BuiltinSchemaError,
    DomainError,
    InvalidDocumentError,
    InvalidModelResponseError,
    InvalidSchemaError,
    RecognitionFailedError,
    SchemaNotFoundError,
    SchemaSelectionError,
)

_STATUS = {
    InvalidDocumentError: 400,
    InvalidSchemaError: 400,
    SchemaSelectionError: 400,
    BuiltinSchemaError: 400,
    SchemaNotFoundError: 404,
    InvalidModelResponseError: 422,
    RecognitionFailedError: 502,
}


def register_error_handlers(app: FastAPI) -> None:
    """Регистрирует обработчики доменных ошибок на приложении."""

    @app.exception_handler(DomainError)
    async def handle_domain_error(_request: Request, exc: DomainError) -> JSONResponse:
        status = _STATUS.get(type(exc), 400)
        return JSONResponse(status_code=status, content={"detail": str(exc)})
