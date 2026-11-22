"""Audio analysis route."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from musaic.api.schemas import Analysis
from musaic.api.services import analyze_audio
from musaic.audio.transcriber import AudioDecodeError

router = APIRouter(tags=["analysis"])

# Formats allowed by the frontend (see UploadPanel.tsx).
ALLOWED_SUFFIXES = {".mp3", ".wav", ".m4a", ".flac", ".ogg"}
MAX_UPLOAD_BYTES = 25_000_000
COPY_CHUNK_BYTES = 1024 * 1024
UPLOAD_LIMIT_DETAIL = "Audio files must be 25 MB or smaller."


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

    if file.size is not None and file.size > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail=UPLOAD_LIMIT_DETAIL)

    # Basic Pitch takes a path. Keep the copy scoped to this request.
    with tempfile.TemporaryDirectory() as directory:
        audio_path = Path(directory) / f"recording{suffix}"
        size = 0
        with audio_path.open("wb") as output:
            while chunk := file.file.read(COPY_CHUNK_BYTES):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail=UPLOAD_LIMIT_DETAIL)
                output.write(chunk)

        if size == 0:
            raise HTTPException(status_code=422, detail="The audio file is empty.")
        try:
            return analyze_audio(audio_path, file_name=file.filename or audio_path.name)
        except AudioDecodeError as error:
            raise HTTPException(status_code=422, detail=str(error)) from error
