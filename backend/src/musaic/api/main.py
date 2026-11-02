"""MusAIc FastAPI application.

Assembles the application: app creation, CORS, router registration.

Development:
    uvicorn musaic.api.main:app --reload --port 8000

    # or, if installed with the [api] extra from the repository root:
    # pip install -e "backend[api]"
    musaic-api

Interactive documentation (generated automatically): http://localhost:8000/docs
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from musaic.api.routers import analyze, chat, health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Origins allowed to call the API from a browser.
# Here: the Vite development server (the React frontend).
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title="MusAIc API",
        version="0.1.0",
        description=(
            "Audio analysis and chord suggestions for piano improvisation."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Everything is prefixed with /api: the frontend calls /api/analyze, /api/chat…
    app.include_router(health.router, prefix="/api")
    app.include_router(analyze.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")

    return app


app = create_app()


def run() -> None:
    """Entry point for the ``musaic-api`` command (uvicorn shortcut)."""
    import uvicorn

    uvicorn.run("musaic.api.main:app", host="127.0.0.1", port=8000, reload=True)
