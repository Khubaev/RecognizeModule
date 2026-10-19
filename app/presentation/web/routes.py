"""HTML-страница загрузки документа."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


@router.get("/")
def index(request: Request):
    """Отдаёт страницу выбора файла и схемы."""
    return templates.TemplateResponse(request, "index.html")
