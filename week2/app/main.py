from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db, close_connection
from .routers import action_items, notes
from .services.extract import OllamaServiceError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    close_connection()


app = FastAPI(title="Action Item Extractor", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
    return html_path.read_text(encoding="utf-8")


app.include_router(notes.router)
app.include_router(action_items.router)


@app.exception_handler(OllamaServiceError)
async def ollama_service_error_handler(request: Request, exc: OllamaServiceError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


static_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")