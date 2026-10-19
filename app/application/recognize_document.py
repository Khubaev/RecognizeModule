"""Сценарий распознавания одного документа по выбранной или разовой схеме."""

import asyncio
from pathlib import Path

from app.application.parse_model_json import parse_model_json
from app.application.ports import DocumentPreparer, DocumentRecognizer, SchemaRepository
from app.domain.entities import ExtractionSchema, RecognitionResult, SourceDocument
from app.domain.entities import detect_format
from app.domain.exceptions import InvalidDocumentError, SchemaSelectionError

_ADHOC_ID = "adhoc"
_ADHOC_NAME = "Разовая схема"


class RecognizeDocument:
    """Проверяет файл, готовит вложение, вызывает распознаватель и разбирает JSON."""

    def __init__(
        self,
        schemas: SchemaRepository,
        preparer: DocumentPreparer,
        recognizer: DocumentRecognizer,
        max_upload_bytes: int,
    ) -> None:
        self._schemas = schemas
        self._preparer = preparer
        self._recognizer = recognizer
        self._max_upload_bytes = max_upload_bytes

    async def execute(
        self,
        filename: str,
        content: bytes,
        schema_id: str | None = None,
        prompt: str | None = None,
    ) -> RecognitionResult:
        """Распознаёт документ. Непустой prompt используется как разовая схема и не сохраняется."""
        source = self._source_document(filename, content)
        schema = await asyncio.to_thread(self._schema, schema_id, prompt)
        prepared = await asyncio.to_thread(self._preparer.prepare, source)
        completed = await self._recognizer.recognize(
            prepared,
            schema.prompt,
            source.format,
            schema.json_schema,
        )
        data = parse_model_json(completed.text)
        return RecognitionResult(
            schema_id=schema.id,
            schema_name=schema.name,
            data=data,
            raw_text=completed.text,
            model=completed.model,
        )

    def _source_document(self, filename: str, content: bytes) -> SourceDocument:
        safe_name = Path(filename).name.strip() or "document"
        if not content:
            raise InvalidDocumentError("Файл пустой.")
        if len(content) > self._max_upload_bytes:
            limit_mb = self._max_upload_bytes / (1024 * 1024)
            raise InvalidDocumentError(f"Файл больше допустимого размера {limit_mb:.0f} МБ.")
        return SourceDocument(filename=safe_name, content=content, format=detect_format(safe_name))

    def _schema(self, schema_id: str | None, prompt: str | None) -> ExtractionSchema:
        prompt_text = (prompt or "").strip()
        if prompt_text:
            return ExtractionSchema(
                id=_ADHOC_ID,
                name=_ADHOC_NAME,
                prompt=prompt_text,
                builtin=False,
            )
        schema_key = (schema_id or "").strip()
        if not schema_key:
            raise SchemaSelectionError("Укажите schema_id или текст схемы.")
        return self._schemas.get(schema_key)
