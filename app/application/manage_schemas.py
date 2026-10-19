"""Сценарии списка, сохранения и удаления схем извлечения."""

from app.application.ports import SchemaRepository
from app.domain.entities import ExtractionSchema
from app.domain.exceptions import InvalidSchemaError

_MAX_NAME_LENGTH = 120
_MAX_PROMPT_LENGTH = 50_000


class ListSchemas:
    """Возвращает встроенные и сохранённые схемы."""

    def __init__(self, schemas: SchemaRepository) -> None:
        self._schemas = schemas

    def execute(self) -> list[ExtractionSchema]:
        """Список схем для выбора в интерфейсе и API."""
        return self._schemas.list_schemas()


class SaveSchema:
    """Сохраняет пользовательскую схему под новым идентификатором."""

    def __init__(self, schemas: SchemaRepository) -> None:
        self._schemas = schemas

    def execute(self, name: str, prompt: str) -> ExtractionSchema:
        """Проверяет имя и текст, затем передаёт их в хранилище."""
        clean_name = name.strip()
        clean_prompt = prompt.strip()
        if not clean_name:
            raise InvalidSchemaError("Укажите имя схемы.")
        if len(clean_name) > _MAX_NAME_LENGTH:
            raise InvalidSchemaError(f"Имя схемы длиннее {_MAX_NAME_LENGTH} символов.")
        if not clean_prompt:
            raise InvalidSchemaError("Текст схемы пустой.")
        if len(clean_prompt) > _MAX_PROMPT_LENGTH:
            raise InvalidSchemaError(f"Текст схемы длиннее {_MAX_PROMPT_LENGTH} символов.")
        return self._schemas.add(clean_name, clean_prompt)


class DeleteSchema:
    """Удаляет только пользовательскую схему."""

    def __init__(self, schemas: SchemaRepository) -> None:
        self._schemas = schemas

    def execute(self, schema_id: str) -> None:
        """Встроенная схема завершает вызов ошибкой BuiltinSchemaError."""
        self._schemas.delete(schema_id.strip())
