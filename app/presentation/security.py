"""Проверка ключа доступа, локального адреса и частоты запросов."""

import hashlib
import secrets
import time
from collections import defaultdict

from fastapi import Depends, HTTPException, Request

from app.infrastructure.config import AppSettings
from app.presentation.dependencies import get_settings

_LOOPBACK = {"127.0.0.1", "::1", "localhost", "testclient"}
_limiter_hits: dict[str, list[float]] = defaultdict(list)


def client_host(request: Request) -> str:
    """Возвращает адрес сокета, не заголовок, который может подделать клиент."""
    if request.client is None:
        return ""
    return request.client.host


def token_matches(provided: str, expected: str) -> bool:
    """Сравнивает ключи по хешу, чтобы длина ключа не отличалась по времени ответа."""
    provided_hash = hashlib.sha256(provided.encode()).digest()
    expected_hash = hashlib.sha256(expected.encode()).digest()
    return secrets.compare_digest(provided_hash, expected_hash)


def _bearer_token(request: Request) -> str:
    header = request.headers.get("authorization", "")
    scheme, _, value = header.partition(" ")
    if scheme.lower() != "bearer":
        return ""
    return value.strip()


async def _allow_rate(key: str, limit: int, window_seconds: float) -> bool:
    now = time.monotonic()
    hits = [stamp for stamp in _limiter_hits[key] if now - stamp < window_seconds]
    if len(hits) >= limit:
        _limiter_hits[key] = hits
        return False
    hits.append(now)
    _limiter_hits[key] = hits
    return True


async def require_access(
    request: Request,
    settings: AppSettings = Depends(get_settings),
) -> None:
    """Пускает запрос только с ключом и в пределах частоты."""
    host = client_host(request)
    if not settings.allow_remote and host not in _LOOPBACK:
        raise HTTPException(status_code=403, detail="Доступ только с этого компьютера.")
    expected = settings.app_token.strip()
    if not expected:
        raise HTTPException(status_code=503, detail="Ключ доступа не настроен.")
    if not token_matches(_bearer_token(request), expected):
        raise HTTPException(status_code=401, detail="Нужен ключ доступа.")
    limit = settings.recognize_per_minute if request.url.path == "/api/recognize" else settings.api_per_minute
    allowed = await _allow_rate(f"{host}:{request.url.path}", limit, settings.rate_window_seconds)
    if not allowed:
        raise HTTPException(status_code=429, detail="Слишком много запросов. Подождите минуту.")
