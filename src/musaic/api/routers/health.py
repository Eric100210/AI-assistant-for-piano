"""Route de santé : vérifie que l'API répond."""

from fastapi import APIRouter

router = APIRouter(tags=["système"])


@router.get("/health")
def health() -> dict[str, str]:
    """Renvoie ``{"status": "ok"}`` si le serveur fonctionne."""
    return {"status": "ok"}
