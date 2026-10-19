"""Разбор текста модели в словарь. Принимается только JSON ограниченного размера."""

import json
import re

from app.domain.exceptions import InvalidModelResponseError

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)
_MAX_RESPONSE_CHARS = 500_000


def parse_model_json(raw: str) -> dict:
    """Снимает markdown-ограждение и читает JSON-объект."""
    if len(raw) > _MAX_RESPONSE_CHARS:
        raise InvalidModelResponseError("Ответ модели слишком большой.")
    cleaned = _FENCE.sub("", raw.strip())
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise InvalidModelResponseError("Ответ модели не является JSON.") from exc
    if not isinstance(data, dict):
        raise InvalidModelResponseError("Ответ модели не является JSON-объектом.")
    return data
