"""Route d'analyse audio."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from musaic.api.schemas import Analysis
from musaic.api.services import analyze_audio

router = APIRouter(tags=["analyse"])

# Formats que le front autorise (voir UploadPanel.tsx).
ALLOWED_SUFFIXES = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}


@router.post("/analyze", response_model=Analysis)
def analyze(file: UploadFile = File(...)) -> Analysis:
    """Analyse un fichier audio et renvoie tonalité, accords et suggestion.

    Le front envoie le fichier en ``multipart/form-data`` dans le champ ``file``.
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Format audio non supporté : '{suffix or 'inconnu'}'. "
                f"Formats acceptés : {', '.join(sorted(ALLOWED_SUFFIXES))}."
            ),
        )

    # ``basic_pitch`` attend un CHEMIN de fichier, pas des octets :
    # on écrit donc l'upload dans un fichier temporaire.
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = Path(tmp.name)

    try:
        return analyze_audio(tmp_path, file_name=file.filename or tmp_path.name)
    finally:
        # Nettoyage, même en cas d'erreur pendant l'analyse.
        tmp_path.unlink(missing_ok=True)
