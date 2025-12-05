from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from core.settings import settings
import os

router = APIRouter(prefix="/api", tags=["files"])


@router.get("/files/{filename}")
async def get_audio_file(filename: str):
    """Serve generated audio file"""
    # Security: prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    filepath = Path(settings.output_dir) / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine content type
    if filename.endswith(".wav"):
        media_type = "audio/wav"
    elif filename.endswith(".mp3"):
        media_type = "audio/mpeg"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=str(filepath),
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

