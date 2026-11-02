"""Health route: checks that the API is responding."""

from fastapi import APIRouter

router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    """Return ``{"status": "ok"}`` when the server is running."""
    return {"status": "ok"}
