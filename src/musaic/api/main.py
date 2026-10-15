"""Application FastAPI de MusAIc.

Assemble l'application : création de l'app, CORS, inclusion des routers.

Lancement en développement :
    uvicorn musaic.api.main:app --reload --port 8000

    # ou, si installé avec l'extra [api] :  pip install -e ".[api]"
    musaic-api

Documentation interactive (générée automatiquement) : http://localhost:8000/docs
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from musaic.api.routers import analyze, chat, health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Origines autorisées à appeler l'API depuis un navigateur.
# Ici : le serveur de développement Vite (le front React).
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def create_app() -> FastAPI:
    """Construit et configure l'application FastAPI."""
    app = FastAPI(
        title="MusAIc API",
        version="0.1.0",
        description=(
            "Analyse audio et suggestions d'accords pour l'improvisation au piano."
        ),
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Tout est préfixé par /api : le front appelle /api/analyze, /api/chat…
    app.include_router(health.router, prefix="/api")
    app.include_router(analyze.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")

    return app


app = create_app()


def run() -> None:
    """Point d'entrée de la commande ``musaic-api`` (raccourci pour uvicorn)."""
    import uvicorn

    uvicorn.run("musaic.api.main:app", host="127.0.0.1", port=8000, reload=True)
