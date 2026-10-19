"""Сборка зависимостей: сценарии получают адаптеры инфраструктуры."""

from functools import lru_cache

from app.application.manage_schemas import DeleteSchema, ListSchemas, SaveSchema
from app.application.recognize_document import RecognizeDocument
from app.infrastructure.config import AppSettings, resolve_path
from app.infrastructure.document_preparer import FileDocumentPreparer
from app.infrastructure.gigachat_recognizer import GigaChatRecognizer
from app.infrastructure.schema_store import JsonSchemaRepository


@lru_cache
def get_settings() -> AppSettings:
    """Читает настройки один раз на процесс."""
    return AppSettings()


@lru_cache
def get_schema_repository() -> JsonSchemaRepository:
    """Общее хранилище схем для API и страницы."""
    return JsonSchemaRepository(resolve_path(get_settings().schemas_path))


@lru_cache
def get_recognizer() -> GigaChatRecognizer:
    """Один асинхронный клиент GigaChat на процесс: токен переиспользуется библиотекой."""
    return GigaChatRecognizer(get_settings())


def get_recognize_document() -> RecognizeDocument:
    """Сценарий распознавания с подготовкой файла и разбором JSON."""
    return RecognizeDocument(
        schemas=get_schema_repository(),
        preparer=FileDocumentPreparer(),
        recognizer=get_recognizer(),
        max_upload_bytes=get_settings().max_upload_bytes,
    )


def get_list_schemas() -> ListSchemas:
    """Сценарий списка схем."""
    return ListSchemas(get_schema_repository())


def get_save_schema() -> SaveSchema:
    """Сценарий сохранения пользовательской схемы."""
    return SaveSchema(get_schema_repository())


def get_delete_schema() -> DeleteSchema:
    """Сценарий удаления пользовательской схемы."""
    return DeleteSchema(get_schema_repository())
