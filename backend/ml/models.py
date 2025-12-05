import os
import torch
import logging
from typing import Optional, Dict, Any
from core.settings import settings

# Configure Hugging Face token if available
if settings.huggingface_token:
    os.environ["HUGGING_FACE_HUB_TOKEN"] = settings.huggingface_token

logger = logging.getLogger(__name__)

# Global model cache
_model_cache: Dict[str, Any] = {}
_device: Optional[torch.device] = None



def get_device() -> torch.device:
    """Get the appropriate device (GPU or CPU)"""
    global _device
    
    if _device is not None:
        return _device
    
    if settings.device == "cpu":
        _device = torch.device("cpu")
        logger.info("Using CPU device")
    elif settings.device == "cuda" and torch.cuda.is_available():
        _device = torch.device("cuda:0")
        logger.info(f"Using CUDA device: {torch.cuda.get_device_name(0)}")
    elif settings.device == "auto":
        if torch.cuda.is_available():
            _device = torch.device("cuda:0")
            logger.info(f"Auto-detected CUDA: {torch.cuda.get_device_name(0)}")
        else:
            _device = torch.device("cpu")
            logger.info("Auto-detected CPU")
    else:
        _device = torch.device("cpu")
        logger.info("Using CPU device (CUDA requested but not available)")
    
    return _device


def load_model(model_name: str, device: Optional[torch.device] = None) -> Any:
    """
    Load an AudioCraft model with caching
    Supports: musicgen-small, musicgen-medium, audiogen-medium
    """
    if device is None:
        device = get_device()
    
    cache_key = f"{model_name}:{device}"
    
    if cache_key in _model_cache:
        logger.info(f"Using cached model: {model_name}")
        return _model_cache[cache_key]
    
    try:
        logger.info(f"Loading model: {model_name} on {device}")
        
        if model_name.startswith("musicgen"):
            from audiocraft.models import MusicGen
            
            # Map model names to pretrained model identifiers
            model_map = {
                "musicgen-small": "facebook/musicgen-small",
                "musicgen-medium": "facebook/musicgen-medium",
                "musicgen-large": "facebook/musicgen-large",
            }
            
            pretrained_name = model_map.get(model_name, "facebook/musicgen-small")
            model = MusicGen.get_pretrained(pretrained_name, device=device)
            
        elif model_name.startswith("audiogen"):
            try:
                from audiocraft.models import AudioGen
                
                model_map = {
                    "audiogen-medium": "facebook/audiogen-medium",
                    "audiogen-small": "facebook/audiogen-small",
                }
                
                pretrained_name = model_map.get(model_name, "facebook/audiogen-medium")
                
                # Try loading model - first attempt without auth (may work if cached)
                try:
                    # Try without forcing auth first - might work with local cache
                    model = AudioGen.get_pretrained(pretrained_name, device=device)
                except Exception as first_error:
                    error_str = str(first_error)
                    
                    # If it's an auth error and we have a token, try with token
                    if ("401" in error_str or "unauthorized" in error_str.lower()) and settings.huggingface_token:
                        logger.info(f"Authentication required for {pretrained_name}, using token...")
                        # Token should be set in environment from app startup
                        model = AudioGen.get_pretrained(pretrained_name, device=device)
                    # If it's an auth error without token, try to use local cache only
                    elif "401" in error_str or "unauthorized" in error_str.lower():
                        logger.warning(f"Auth error, trying to use local cache only for {pretrained_name}...")
                        # Try with offline mode to use only cached files
                        import huggingface_hub
                        old_offline = os.environ.get("HF_HUB_OFFLINE", "0")
                        try:
                            os.environ["HF_HUB_OFFLINE"] = "1"
                            model = AudioGen.get_pretrained(pretrained_name, device=device)
                            logger.info(f"Successfully loaded {pretrained_name} from local cache")
                        except Exception as cache_error:
                            # Cache doesn't have the files, need auth
                            os.environ["HF_HUB_OFFLINE"] = old_offline
                            raise ValueError(
                                f"AudioGen model {model_name} requires Hugging Face authentication. "
                                f"The model is not in local cache. Please set HUGGINGFACE_TOKEN environment variable. "
                                f"Get your token from: https://huggingface.co/settings/tokens"
                            )
                        finally:
                            os.environ["HF_HUB_OFFLINE"] = old_offline
                    else:
                        raise
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"AudioGen not available: {e}")
                
                # Provide helpful error message if auth is the issue
                if "401" in error_msg or "unauthorized" in error_msg.lower():
                    raise ValueError(
                        f"AudioGen model {model_name} requires Hugging Face authentication. "
                        f"Please set HUGGINGFACE_TOKEN environment variable. "
                        f"Get your token from: https://huggingface.co/settings/tokens"
                    )
                raise ValueError(f"AudioGen model {model_name} is not available: {error_msg}")
        
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Cache the model
        _model_cache[cache_key] = model
        logger.info(f"Model {model_name} loaded and cached")
        
        return model
    
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}", exc_info=True)
        raise


def get_available_models() -> list[Dict[str, Any]]:
    """Get list of available models with metadata"""
    device = get_device()
    is_cuda = device.type == "cuda"
    
    models = [
        {
            "id": "musicgen-small",
            "name": "MusicGen Small",
            "type": "music",
            "description": "Fast generation, low VRAM (~2GB)",
            "supports_stereo": True,
            "sample_rate": 32000,
            "requires_gpu": False,
        },
        {
            "id": "musicgen-medium",
            "name": "MusicGen Medium",
            "type": "music",
            "description": "Better quality, higher VRAM (~4GB GPU recommended)",
            "supports_stereo": True,
            "sample_rate": 32000,
            "requires_gpu": True,
        },
        {
            "id": "musicgen-large",
            "name": "MusicGen Large",
            "type": "music",
            "description": "Best quality, requires high VRAM (~8GB GPU recommended)",
            "supports_stereo": True,
            "sample_rate": 32000,
            "requires_gpu": True,
        },
    ]
    
    # Try to add AudioGen if available
    try:
        from audiocraft.models import AudioGen
        logger.info("AudioGen is available, adding models")
        
        models.append({
            "id": "audiogen-small",
            "name": "AudioGen Small (Raccomandato per CPU)",
            "type": "sfx",
            "description": "Sound effects (small, fast - 1-3 min for 10s on CPU)",
            "supports_stereo": False,
            "sample_rate": 16000,
            "requires_gpu": False,
        })
        
        models.append({
            "id": "audiogen-medium",
            "name": "AudioGen Medium",
            "type": "sfx",
            "description": "Sound effects and ambient audio (SLOW on CPU - 10-20+ min for 10s)",
            "supports_stereo": False,
            "sample_rate": 16000,
            "requires_gpu": False,
        })
        logger.info(f"Successfully added {len([m for m in models if m['id'].startswith('audiogen')])} AudioGen model(s)")
    except ImportError as e:
        logger.warning(f"AudioGen not available (ImportError): {e}")
        logger.info("This is normal if xformers is not properly configured")
    except Exception as e:
        logger.error(f"AudioGen not available (Error): {e}", exc_info=True)
        logger.info("AudioGen models will not be shown in the UI")
    
    # Filter models based on device if needed
    if not is_cuda:
        # Still show but mark GPU requirement
        pass
    
    return models

