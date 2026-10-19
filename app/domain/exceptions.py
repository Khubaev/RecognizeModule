"""Ошибки предметной области. Слои выше переводят их в ответы API."""


class DomainError(Exception):
    """Базовая ошибка предметной области."""


class InvalidDocumentError(DomainError):
    """Файл пустой, слишком большой или его формат не поддерживается."""


class SchemaNotFoundError(DomainError):
    """Схема с указанным идентификатором отсутствует."""


class SchemaSelectionError(DomainError):
    """Не выбрана сохранённая схема и не передан разовый текст схемы."""


class InvalidSchemaError(DomainError):
    """Имя или текст пользовательской схемы не проходят проверку."""


class BuiltinSchemaError(DomainError):
    """Встроенную схему нельзя изменить или удалить."""


class InvalidModelResponseError(DomainError):
    """Ответ модели не удалось разобрать как JSON-объект."""


class RecognitionFailedError(DomainError):
    """Внешний распознаватель не смог обработать документ."""
