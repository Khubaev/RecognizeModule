"""Файловое хранилище пользовательских схем. Встроенная схема в файл не пишется."""

import json
import threading
import uuid
from pathlib import Path

from app.domain.entities import ExtractionSchema
from app.domain.exceptions import BuiltinSchemaError, InvalidSchemaError, SchemaNotFoundError
from app.infrastructure.prompts.invoice import INVOICE_PROMPT
from app.infrastructure.prompts.invoice_schema import INVOICE_JSON_SCHEMA

_BUILTIN = ExtractionSchema(
    id="invoice",
    name="Счёт на оплату",
    prompt=INVOICE_PROMPT,
    builtin=True,
    json_schema=INVOICE_JSON_SCHEMA,
)


class JsonSchemaRepository:
    """Список схем: встроенный счёт плюс записи из JSON-файла."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = threading.Lock()

    def list_schemas(self) -> list[ExtractionSchema]:
        """Встроенная схема первая, затем пользовательские в порядке сохранения."""
        with self._lock:
            custom = self._read()
        return [_BUILTIN, *custom]

    def get(self, schema_id: str) -> ExtractionSchema:
        """Ищет схему по идентификатору."""
        if schema_id == _BUILTIN.id:
            return _BUILTIN
        with self._lock:
            for schema in self._read():
                if schema.id == schema_id:
                    return schema
        raise SchemaNotFoundError(f"Схема «{schema_id}» не найдена.")

    def add(self, name: str, prompt: str) -> ExtractionSchema:
        """Добавляет схему с новым идентификатором, не затирая встроенную."""
        schema = ExtractionSchema(
            id=f"custom-{uuid.uuid4().hex[:12]}",
            name=name,
            prompt=prompt,
            builtin=False,
        )
        with self._lock:
            stored = self._read()
            stored.append(schema)
            self._write(stored)
        return schema

    def delete(self, schema_id: str) -> None:
        """Удаляет пользовательскую схему. Попытка удалить встроенную запрещена."""
        if schema_id == _BUILTIN.id:
            raise BuiltinSchemaError("Встроенную схему «Счёт на оплату» удалить нельзя.")
        with self._lock:
            stored = self._read()
            remaining = [item for item in stored if item.id != schema_id]
            if len(remaining) == len(stored):
                raise SchemaNotFoundError(f"Схема «{schema_id}» не найдена.")
            self._write(remaining)

    def _read(self) -> list[ExtractionSchema]:
        if not self._path.is_file():
            return []
        raw = self._path.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        try:
            payload = json.loads(raw)
            return [
                ExtractionSchema(
                    id=item["id"],
                    name=item["name"],
                    prompt=item["prompt"],
                    builtin=False,
                )
                for item in payload.get("schemas", [])
            ]
        except (json.JSONDecodeError, AttributeError, KeyError, TypeError) as exc:
            raise InvalidSchemaError(f"Файл схем повреждён: {self._path}") from exc

    def _write(self, schemas: list[ExtractionSchema]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schemas": [
                {"id": item.id, "name": item.name, "prompt": item.prompt}
                for item in schemas
            ]
        }
        self._path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
