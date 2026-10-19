"""Асинхронный адаптер GigaChat: загрузка файла и запрос чата с вложением."""

import asyncio

from gigachat import GigaChat
from gigachat.exceptions import BadRequestError, GigaChatException, UnprocessableEntityError
from gigachat.models import Chat, Messages, MessagesRole
from gigachat.models.response_format import JsonSchemaResponseFormat

from app.domain.entities import DocumentFormat, PreparedDocument, RecognizerOutput
from app.domain.exceptions import RecognitionFailedError
from app.infrastructure.config import AppSettings, resolve_path


class GigaChatRecognizer:
    """Загружает подготовленный файл и возвращает текст ответа модели."""

    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings
        self._client: GigaChat | None = None
        self._lock = asyncio.Lock()
        self._slots = asyncio.Semaphore(max(1, settings.gigachat_max_concurrency))

    async def recognize(
        self,
        document: PreparedDocument,
        prompt: str,
        source_format: DocumentFormat,
        json_schema: dict | None = None,
    ) -> RecognizerOutput:
        """Загружает вложение, ждёт ответ выбранной модели и удаляет файл из хранилища."""
        model = self._model_for(source_format)
        async with self._slots:
            client = await self._client_or_raise()
            uploaded_id: str | None = None
            try:
                uploaded = await client.aupload_file(
                    (document.filename, document.content, document.media_type),
                    purpose="general",
                )
                uploaded_id = uploaded.id_
                response = await self._complete(client, prompt, uploaded_id, json_schema, model)
            except GigaChatException as exc:
                raise RecognitionFailedError(f"GigaChat не принял документ: {exc}") from exc
            finally:
                if uploaded_id is not None:
                    await self._delete_uploaded(client, uploaded_id)
        if not response.choices:
            raise RecognitionFailedError("GigaChat вернул пустой ответ.")
        return RecognizerOutput(text=response.choices[0].message.content or "", model=model)

    def _model_for(self, source_format: DocumentFormat) -> str:
        """JPEG распознаёт GigaChat-2-Max, PDF и остальные форматы — GigaChat-2."""
        if source_format is DocumentFormat.JPEG:
            return self._settings.gigachat_jpeg_model
        return self._settings.gigachat_model

    async def _complete(
        self,
        client: GigaChat,
        prompt: str,
        file_id: str,
        json_schema: dict | None,
        model: str,
    ):
        """Запрашивает ответ. Если модель не принимает JSON Schema, повторяет запрос без неё."""
        try:
            return await client.achat(self._chat(prompt, file_id, json_schema, model))
        except (BadRequestError, UnprocessableEntityError):
            if json_schema is None:
                raise
            return await client.achat(self._chat(prompt, file_id, None, model))

    def _chat(self, prompt: str, file_id: str, json_schema: dict | None, model: str) -> Chat:
        """Собирает запрос чата для выбранной модели."""
        chat = Chat(
            model=model,
            messages=[
                Messages(
                    role=MessagesRole.USER,
                    content=prompt,
                    attachments=[file_id],
                )
            ],
        )
        if json_schema is not None:
            chat.response_format = JsonSchemaResponseFormat(schema=json_schema, strict=True)
        return chat

    async def _delete_uploaded(self, client: GigaChat, file_id: str) -> None:
        """Удаляет вложение. Ошибка очистки не заменяет результат распознавания."""
        try:
            await client.adelete_file(file_id)
        except GigaChatException:
            return

    async def aclose(self) -> None:
        """Закрывает HTTP-клиент, если распознавание уже открывало соединение."""
        async with self._lock:
            if self._client is not None:
                await self._client.aclose()
                self._client = None

    async def _client_or_raise(self) -> GigaChat:
        if self._client is not None:
            return self._client
        credentials = self._settings.gigachat_credentials.strip()
        if not credentials:
            raise RecognitionFailedError("Не задан GIGACHAT_CREDENTIALS в окружении или .env.")
        ca_bundle = resolve_path(self._settings.gigachat_ca_bundle)
        if not ca_bundle.is_file():
            raise RecognitionFailedError(f"Не найден CA-сертификат: {ca_bundle}")
        async with self._lock:
            if self._client is None:
                self._client = GigaChat(
                    credentials=credentials,
                    scope=self._settings.gigachat_scope,
                    model=self._settings.gigachat_model,
                    ca_bundle_file=str(ca_bundle),
                    timeout=self._settings.gigachat_timeout,
                    max_retries=self._settings.gigachat_max_retries,
                    verify_ssl_certs=True,
                )
            return self._client
