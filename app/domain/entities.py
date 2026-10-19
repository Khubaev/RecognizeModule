"""Сущности документа, схемы извлечения и результата распознавания."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from app.domain.exceptions import InvalidDocumentError


class DocumentFormat(str, Enum):
    """Форматы, которые принимает сценарий распознавания."""

    PDF = "pdf"
    XLSX = "xlsx"
    XLS = "xls"
    JPEG = "jpeg"
    WEBP = "webp"


_EXTENSIONS = {
    ".pdf": DocumentFormat.PDF,
    ".xlsx": DocumentFormat.XLSX,
    ".xls": DocumentFormat.XLS,
    ".jpg": DocumentFormat.JPEG,
    ".jpeg": DocumentFormat.JPEG,
    ".webp": DocumentFormat.WEBP,
}


def detect_format(filename: str) -> DocumentFormat:
    """Определяет формат по расширению имени файла."""
    suffix = Path(filename).suffix.lower()
    try:
        return _EXTENSIONS[suffix]
    except KeyError as exc:
        allowed = ", ".join(sorted({item.value for item in DocumentFormat}))
        raise InvalidDocumentError(
            f"Формат «{suffix or 'без расширения'}» не поддерживается. Допустимо: {allowed}."
        ) from exc


@dataclass(frozen=True)
class SourceDocument:
    """Исходный файл, как его передал пользователь."""

    filename: str
    content: bytes
    format: DocumentFormat


@dataclass(frozen=True)
class PreparedDocument:
    """Файл, приведённый к виду, который можно отправить в распознаватель."""

    filename: str
    content: bytes
    media_type: str


@dataclass(frozen=True)
class ExtractionSchema:
    """Инструкция модели: имя типа документа, текст промпта и необязательная JSON Schema."""

    id: str
    name: str
    prompt: str
    builtin: bool
    json_schema: dict | None = None


@dataclass(frozen=True)
class RecognizerOutput:
    """Текст ответа модели и имя модели, которая его дала."""

    text: str
    model: str


@dataclass(frozen=True)
class RecognitionResult:
    """Разобранный JSON, исходный текст ответа и имя модели."""

    schema_id: str
    schema_name: str
    data: dict
    raw_text: str
    model: str
