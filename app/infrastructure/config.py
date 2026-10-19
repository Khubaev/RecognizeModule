"""Настройки приложения. Секреты читаются из окружения и файла .env."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


class AppSettings(BaseSettings):
    """Параметры GigaChat, лимит загрузки и путь к файлу пользовательских схем."""

    gigachat_credentials: str = ""
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_model: str = "GigaChat-2"
    gigachat_jpeg_model: str = "GigaChat-2-Max"
    gigachat_ca_bundle: str = "certs/russian_trusted_root_ca.pem"
    gigachat_timeout: float = 300.0
    gigachat_max_retries: int = 2
    gigachat_max_concurrency: int = 2
    max_upload_bytes: int = 15 * 1024 * 1024
    schemas_path: str = "data/schemas.json"

    model_config = SettingsConfigDict(
        env_file=str(_PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


def resolve_path(path: str) -> Path:
    """Возвращает абсолютный путь: как есть, если файл уже есть, иначе от корня проекта."""
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    from_cwd = Path.cwd() / candidate
    if from_cwd.exists():
        return from_cwd
    return _PROJECT_ROOT / candidate
