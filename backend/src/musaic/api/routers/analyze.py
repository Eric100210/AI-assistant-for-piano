"""Audio analysis route."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from musaic.api.schemas import Analysis
from musaic.api.services import analyze_audio

router = APIRouter(tags=["analysis"])

# Formats allowed by the frontend (see UploadPanel.tsx).
ALLOWED_SUFFIXES = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}


@router.post("/analyze", response_model=Analysis)
def analyze(file: UploadFile = File(...)) -> Analysis:
    """Analyze an audio file and return the key, chords and suggestion.

    The frontend sends the file as ``multipart/form-data`` in the ``file`` field.
    """
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported audio format: '{suffix or 'unknown'}'. "
                f"Accepted formats: {', '.join(sorted(ALLOWED_SUFFIXES))}."
            ),
        )

    # ``basic_pitch`` expects a file PATH, not bytes: the upload is therefore
    # written to a temporary file.
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file.file.read())
        tmp_path = Path(tmp.name)

    try:
        return analyze_audio(tmp_path, file_name=file.filename or tmp_path.name)
    finally:
        # Cleanup, even if an error occurs during analysis.
        tmp_path.unlink(missing_ok=True)
