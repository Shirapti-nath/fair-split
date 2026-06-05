"""Fair Split API."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes.split import router as split_router

load_dotenv()

app = FastAPI(title="Fair Split API", version="1.0.0")

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(split_router)

STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@app.get("/health")
def health() -> dict[str, str]:
    from api.services.offline import has_valid_api_key

    return {
        "status": "ok",
        "mode": "online" if has_valid_api_key() else "offline-demo",
        "version": "2",
    }


if STATIC_DIR.is_dir():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    def serve_frontend() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")
