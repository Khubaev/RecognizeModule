"""Загрузка документа и запуск распознавания."""

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.application.recognize_document import RecognizeDocument
from app.domain.exceptions import InvalidDocumentError
from app.infrastructure.config import AppSettings
from app.presentation.dependencies import get_recognize_document, get_settings

router = APIRouter(prefix="/api")
_READ_CHUNK = 1024 * 1024


async def _read_limited(upload: UploadFile, limit: int) -> bytes:
    """Читает файл частями и останавливается, как только размер превысил лимит."""
    chunks: list[bytes] = []
    total = 0
    while True:
        block = await upload.read(_READ_CHUNK)
        if not block:
            break
        total += len(block)
        if total > limit:
            limit_mb = limit / (1024 * 1024)
            raise InvalidDocumentError(f"Файл больше допустимого размера {limit_mb:.0f} МБ.")
        chunks.append(block)
    return b"".join(chunks)


@router.post("/recognize")
async def recognize_document(
    file: UploadFile = File(...),
    schema_id: str | None = Form(default=None),
    prompt: str | None = Form(default=None),
    settings: AppSettings = Depends(get_settings),
    use_case: RecognizeDocument = Depends(get_recognize_document),
) -> dict:
    """Принимает файл и schema_id либо разовый prompt. Непустой prompt не сохраняется."""
    content = await _read_limited(file, settings.max_upload_bytes)
    result = await use_case.execute(
        filename=file.filename or "document",
        content=content,
        schema_id=schema_id,
        prompt=prompt,
    )
    return {
        "schema_id": result.schema_id,
        "schema_name": result.schema_name,
        "model": result.model,
        "data": result.data,
        "raw_text": result.raw_text,
    }
