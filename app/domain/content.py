"""Проверка, что байты файла совпадают с заявленным форматом."""

import zipfile
from io import BytesIO

from app.domain.entities import DocumentFormat
from app.domain.exceptions import InvalidDocumentError

_OLE = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
_MAX_DECLARED_BYTES = 30 * 1024 * 1024


def assert_content_matches(document_format: DocumentFormat, content: bytes) -> None:
    """Отклоняет файл, если сигнатура не совпадает с расширением."""
    if document_format is DocumentFormat.PDF and not content.startswith(b"%PDF-"):
        raise InvalidDocumentError("Содержимое файла не является PDF.")
    if document_format is DocumentFormat.JPEG and not content.startswith(b"\xff\xd8\xff"):
        raise InvalidDocumentError("Содержимое файла не является JPEG.")
    if document_format is DocumentFormat.WEBP and not _is_webp(content):
        raise InvalidDocumentError("Содержимое файла не является WebP.")
    if document_format is DocumentFormat.XLSX:
        _assert_xlsx(content)
    if document_format is DocumentFormat.XLS and not content.startswith(_OLE):
        raise InvalidDocumentError("Содержимое файла не является Excel .xls.")


def _is_webp(content: bytes) -> bool:
    return len(content) >= 12 and content.startswith(b"RIFF") and content[8:12] == b"WEBP"


def _assert_xlsx(content: bytes) -> None:
    if not content.startswith(b"PK\x03\x04"):
        raise InvalidDocumentError("Содержимое файла не является Excel .xlsx.")
    try:
        with zipfile.ZipFile(BytesIO(content)) as archive:
            names = archive.namelist()
            declared = sum(item.file_size for item in archive.infolist())
    except zipfile.BadZipFile as exc:
        raise InvalidDocumentError("Файл Excel повреждён.") from exc
    if not any(name.startswith("xl/") for name in names):
        raise InvalidDocumentError("В архиве нет книги Excel.")
    if declared > _MAX_DECLARED_BYTES:
        raise InvalidDocumentError("Таблица Excel слишком большая.")
