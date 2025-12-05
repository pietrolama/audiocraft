from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from core.jobs import job_manager
from core.ratelimit import IPRateLimiter
from core.settings import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["generate"])

# Initialize rate limiter
rate_limiter = IPRateLimiter(requests_per_hour=settings.rate_limit_per_hour)


def get_client_ip(request: Request) -> str:
    """Extract client IP address"""
    # Try X-Forwarded-For header first (for proxies)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    # Fallback to direct client
    return request.client.host if request.client else "unknown"


class GenerateRequest(BaseModel):
    model: str = Field(default="musicgen-small", description="Model to use")
    prompt: str = Field(..., min_length=1, max_length=500, description="Text prompt")
    duration: int = Field(default=10, ge=1, le=60, description="Duration in seconds")
    seed: Optional[int] = Field(default=None, ge=-1, description="Random seed (-1 for random)")
    temperature: float = Field(default=1.0, ge=0.0, le=3.0)
    top_k: int = Field(default=250, ge=0, le=500)
    top_p: float = Field(default=0.0, ge=0.0, le=1.0)
    cfg_coef: float = Field(default=3.0, ge=0.0, le=10.0, description="Classifier-Free Guidance")
    stereo: bool = Field(default=True)
    sample_rate: int = Field(default=32000, description="Sample rate (16000 or 32000)")
    format: str = Field(default="wav", description="Output format (wav or mp3)")
    
    @field_validator("sample_rate")
    @classmethod
    def validate_sample_rate(cls, v):
        if v not in [16000, 32000, 44100, 48000]:
            raise ValueError("Sample rate must be 16000, 32000, 44100, or 48000")
        return v
    
    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v):
        if v > settings.max_duration:
            raise ValueError(f"Duration exceeds maximum of {settings.max_duration} seconds")
        return v


@router.post("/generate", status_code=201)
async def create_generation(
    request: GenerateRequest,
    http_request: Request
):
    """Create a new audio generation job"""
    
    # Rate limiting
    client_ip = get_client_ip(http_request)
    allowed, remaining = rate_limiter.is_allowed(client_ip)
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Maximum {settings.rate_limit_per_hour} requests per hour."
        )
    
    # Validate model
    from ml.models import get_available_models
    available_models = [m["id"] for m in get_available_models()]
    
    if request.model not in available_models:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{request.model}' not available. Available: {available_models}"
        )
    
    # Create job
    params = request.model_dump()
    job = job_manager.create_job(params)
    
    # Estimate time (rough: ~2s per second of audio for small model)
    estimated_seconds = request.duration * 2
    
    return {
        "job_id": job.job_id,
        "status": job.status,
        "estimated_seconds": estimated_seconds,
        "rate_limit_remaining": remaining
    }

