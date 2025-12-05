from fastapi import APIRouter
from ml.models import get_available_models

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models")
async def list_models():
    """List available models with metadata"""
    models = get_available_models()
    return {"models": models}

