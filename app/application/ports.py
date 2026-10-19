"""Порты, которые реализует инфраструктура. Сценарии зависят только от них."""

from typing import Protocol

from app.domain.entities import DocumentFormat, ExtractionSchema, PreparedDocument, RecognizerOutput, SourceDocument


class SchemaRepository(Protocol):
    """Хранение встроенных и пользовательских схем извлечения."""

    def list_schemas(self) -> list[ExtractionSchema]:
        """Возвращает все схемы: сначала встроенные, затем сохранённые."""

    def get(self, schema_id: str) -> ExtractionSchema:
        """Возвращает схему или возбуждает SchemaNotFoundError."""

    def add(self, name: str, prompt: str) -> ExtractionSchema:
        """Сохраняет пользовательскую схему и возвращает её."""

    def delete(self, schema_id: str) -> None:
        """Удаляет пользовательскую схему. Встроенную удалить нельзя."""


class DocumentPreparer(Protocol):
    """Приводит исходный файл к вложению, которое принимает распознаватель."""

    def prepare(self, document: SourceDocument) -> PreparedDocument:
        """WebP конвертирует в JPEG, Excel — в текст. PDF и JPEG оставляет как есть."""


class DocumentRecognizer(Protocol):
    """Отправляет подготовленный файл и промпт, возвращает сырой текст модели."""

    async def recognize(
        self,
        document: PreparedDocument,
        prompt: str,
        source_format: DocumentFormat,
        json_schema: dict | None = None,
    ) -> RecognizerOutput:
        """Ждёт текст ответа. JPEG уходит в отдельную модель."""
