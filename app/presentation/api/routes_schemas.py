"""Список, сохранение и удаление схем извлечения."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.application.manage_schemas import DeleteSchema, ListSchemas, SaveSchema
from app.domain.entities import ExtractionSchema
from app.presentation.dependencies import get_delete_schema, get_list_schemas, get_save_schema

router = APIRouter(prefix="/api")


class SchemaBody(BaseModel):
    """Тело запроса на сохранение пользовательской схемы."""

    name: str
    prompt: str


class SchemaResponse(BaseModel):
    """Схема в ответе API."""

    id: str
    name: str
    prompt: str
    builtin: bool


def _response(schema: ExtractionSchema) -> SchemaResponse:
    return SchemaResponse(
        id=schema.id,
        name=schema.name,
        prompt=schema.prompt,
        builtin=schema.builtin,
    )


@router.get("/schemas", response_model=list[SchemaResponse])
def list_schemas(use_case: ListSchemas = Depends(get_list_schemas)) -> list[SchemaResponse]:
    """Возвращает встроенную схему счёта и сохранённые схемы."""
    return [_response(item) for item in use_case.execute()]


@router.post("/schemas", response_model=SchemaResponse, status_code=201)
def save_schema(
    body: SchemaBody,
    use_case: SaveSchema = Depends(get_save_schema),
) -> SchemaResponse:
    """Сохраняет новую схему. Встроенную схему этот вызов не заменяет."""
    return _response(use_case.execute(body.name, body.prompt))


@router.delete("/schemas/{schema_id}", status_code=204)
def delete_schema(
    schema_id: str,
    use_case: DeleteSchema = Depends(get_delete_schema),
) -> None:
    """Удаляет пользовательскую схему. Встроенная схема остаётся."""
    use_case.execute(schema_id)
