"""Разбор текста модели в словарь. Логика совпадает с исходным скриптом."""

import ast
import json
import re

from app.domain.exceptions import InvalidModelResponseError

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def parse_model_json(raw: str) -> dict:
    """Снимает markdown-ограждение и читает JSON-объект."""
    cleaned = _FENCE.sub("", raw.strip())
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            data = ast.literal_eval(cleaned)
        except (ValueError, SyntaxError) as exc:
            raise InvalidModelResponseError("Ответ модели не является JSON.") from exc
    if not isinstance(data, dict):
        raise InvalidModelResponseError("Ответ модели не является JSON-объектом.")
    return data
