from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    # Device settings
    device: str = "auto"  # auto|cpu|cuda
    model_default: str = "musicgen-small"
    
    # Generation limits
    max_duration: int = 30
    output_dir: str = os.getenv("OUTPUT_DIR", str(Path(__file__).parent.parent.parent / "data" / "outputs"))
    
    # Rate limiting
    rate_limit_per_hour: int = 20
    
    # CORS
    allow_origins: str = "http://localhost:3000"
    
    # Audio format
    audio_format: str = "wav"  # wav|mp3
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Hugging Face authentication
    huggingface_token: Optional[str] = None
    huggingface_offline: bool = False  # Use only local cache, no online checks
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_origins_list(self) -> list[str]:
        """Parse comma-separated origins into list"""
        return [origin.strip() for origin in self.allow_origins.split(",") if origin.strip()]


settings = Settings()

