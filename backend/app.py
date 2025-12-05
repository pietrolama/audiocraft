from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from core.settings import settings
from core.jobs import job_manager
from ml.generate import generate_audio
from api.routes_generate import router as generate_router
from api.routes_jobs import router as jobs_router
from api.routes_files import router as files_router
from api.routes_models import router as models_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AudioCraft Text-to-Audio API",
    description="Generate audio from text prompts using Meta AudioCraft",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(generate_router)
app.include_router(jobs_router)
app.include_router(files_router)
app.include_router(models_router)


async def process_job(job, progress_callback):
    """Process a generation job"""
    params = job.params
    
    # Run generation in executor to avoid blocking
    loop = asyncio.get_event_loop()
    result_path = await loop.run_in_executor(
        None,
        lambda: generate_audio(
            model_name=params.get("model", "musicgen-small"),
            prompt=params["prompt"],
            duration=params.get("duration", 10),
            seed=params.get("seed"),
            temperature=params.get("temperature", 1.0),
            top_k=params.get("top_k", 250),
            top_p=params.get("top_p", 0.0),
            cfg_coef=params.get("cfg_coef", 3.0),
            stereo=params.get("stereo", True),
            sample_rate=params.get("sample_rate", 32000),
            progress_callback=progress_callback,
        )
    )
    
    # Extract filename and create URL
    import os
    filename = os.path.basename(result_path)
    return f"/api/files/{filename}"


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting AudioCraft API server...")
    logger.info(f"Device: {settings.device}")
    logger.info(f"Output directory: {settings.output_dir}")
    logger.info(f"Max duration: {settings.max_duration}s")
    
    # Configure Hugging Face offline mode if requested
    if settings.huggingface_offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        logger.info("Hugging Face offline mode enabled - using local cache only")
    
    # Configure Hugging Face authentication if token is provided
    if settings.huggingface_token:
        try:
            from huggingface_hub import login
            login(token=settings.huggingface_token, add_to_git_credential=False)
            logger.info("Hugging Face authentication configured")
        except Exception as e:
            logger.warning(f"Failed to configure Hugging Face authentication: {e}")
    else:
        if not settings.huggingface_offline:
            logger.info("No Hugging Face token provided - using public access only")
    
    # Start job worker
    job_manager.start_worker(process_job)
    logger.info("Job worker started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "AudioCraft Text-to-Audio API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check with more details"""
    from ml.models import get_device
    import torch
    
    device = get_device()
    
    health_info = {
        "status": "healthy",
        "device": str(device),
        "device_type": device.type,
        "cuda_available": torch.cuda.is_available() if hasattr(torch, 'cuda') else False,
    }
    
    # Aggiungi info XPU se disponibile
    if device.type == "xpu":
        try:
            import intel_extension_for_pytorch as ipex
            health_info["xpu_available"] = True
            health_info["xpu_device_name"] = ipex.xpu.get_device_name(0)
            health_info["xpu_device_count"] = ipex.xpu.device_count()
        except (ImportError, OSError, Exception):
            health_info["xpu_available"] = False
    else:
        try:
            import intel_extension_for_pytorch as ipex
            health_info["xpu_available"] = ipex.xpu.is_available() if hasattr(ipex, 'xpu') else False
        except (ImportError, OSError, Exception):
            health_info["xpu_available"] = False
    
    return health_info

