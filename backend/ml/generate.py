import os
import uuid
import torch
import logging
from pathlib import Path
from typing import Callable, Optional, Dict, Any
from core.settings import settings
from ml.models import load_model, get_device

logger = logging.getLogger(__name__)


def generate_audio(
    model_name: str,
    prompt: str,
    duration: int = 10,
    seed: Optional[int] = None,
    temperature: float = 1.0,
    top_k: int = 250,
    top_p: float = 0.0,
    cfg_coef: float = 3.0,
    stereo: bool = True,
    sample_rate: int = 32000,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> str:
    """
    Generate audio from text prompt
    
    Returns path to generated audio file
    """
    device = get_device()
    
    # Progress: 0-10% - Loading model
    if progress_callback:
        progress_callback(5, "Loading model...")
    
    model = load_model(model_name, device)
    
    # Progress: 10-15% - Setting generation parameters
    if progress_callback:
        progress_callback(10, "Preparing generation...")
    
    # Set generation parameters - AudioGen has different API than MusicGen
    is_audiogen = model_name.startswith("audiogen")
    
    if is_audiogen:
        # AudioGen has fixed sample rate of 16000 and doesn't support all MusicGen params
        # Build params dict conditionally to avoid passing None values
        audiogen_params = {
            "duration": duration,
            "temperature": temperature,
            "top_k": top_k,
            "cfg_coef": cfg_coef,
        }
        # Only add top_p if it's > 0
        if top_p > 0:
            audiogen_params["top_p"] = top_p
        
        try:
            model.set_generation_params(**audiogen_params)
            # AudioGen uses 16kHz sample rate by default
            audio_sample_rate = 16000
        except Exception as e:
            logger.warning(f"Some AudioGen params not supported: {e}")
            # Minimal fallback for AudioGen
            try:
                model.set_generation_params(
                    duration=duration,
                    temperature=temperature,
                    cfg_coef=cfg_coef,
                )
                audio_sample_rate = 16000
            except Exception as e2:
                logger.error(f"Failed to set AudioGen params: {e2}")
                audio_sample_rate = 16000
    else:
        # MusicGen supports more parameters including sample_rate
        try:
            model.set_generation_params(
                duration=duration,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p if top_p > 0 else None,
                cfg_coef=cfg_coef,
                two_step_cfg=False,
                use_sampling=True,
                sample_rate=sample_rate,
            )
            audio_sample_rate = sample_rate
        except Exception as e:
            logger.warning(f"Some params not supported, using defaults: {e}")
            # Fallback to basic params
            try:
                model.set_generation_params(
                    duration=duration,
                    temperature=temperature,
                    cfg_coef=cfg_coef,
                    sample_rate=sample_rate,
                )
                audio_sample_rate = sample_rate
            except Exception as e:
                logger.warning(f"Using minimal params: {e}")
                audio_sample_rate = sample_rate
    
    # Set seed if provided
    if seed is not None and seed >= 0:
        torch.manual_seed(seed)
        if device.type == "cuda":
            torch.cuda.manual_seed_all(seed)
        elif device.type == "xpu":
            # Intel GPU seed handling
            import intel_extension_for_pytorch as ipex
            ipex.xpu.manual_seed_all(seed)
    else:
        # Generate random seed
        seed = torch.randint(0, 2**32, (1,)).item()
        torch.manual_seed(seed)
        if device.type == "cuda":
            torch.cuda.manual_seed_all(seed)
        elif device.type == "xpu":
            # Intel GPU seed handling
            import intel_extension_for_pytorch as ipex
            ipex.xpu.manual_seed_all(seed)
    
    # Progress: 15-20% - Generating
    if progress_callback:
        progress_callback(15, "Generating audio...")
    
    # Simple progress tracking wrapper
    generation_progress = {"step": 15}
    
    def update_progress(delta: int, message: str):
        if progress_callback:
            generation_progress["step"] = min(95, generation_progress["step"] + delta)
            progress_callback(generation_progress["step"], message)
    
    try:
        # Generate audio
        # Note: AudioCraft doesn't expose fine-grained progress, so we simulate
        update_progress(5, "Sampling audio...")
        
        with torch.no_grad():
            wav = model.generate(
                descriptions=[prompt],
                progress=True if progress_callback else False
            )
        
        update_progress(10, "Processing output...")
        
        # Convert to numpy and handle stereo
        import numpy as np
        
        if isinstance(wav, torch.Tensor):
            wav = wav.cpu().numpy()
        
        # Handle shape: (batch, channels, samples) -> (samples, channels)
        if len(wav.shape) == 3:
            wav = wav[0]  # Take first batch item
            if wav.shape[0] == 1:  # Mono
                wav = wav[0]
            elif wav.shape[0] == 2:  # Stereo
                wav = wav.T  # Transpose to (samples, channels)
        
        # Ensure output is stereo if requested
        # AudioGen generates mono, MusicGen can generate stereo
        if stereo and len(wav.shape) == 1:
            # Duplicate mono to stereo
            wav = np.stack([wav, wav], axis=1)
        elif not stereo and len(wav.shape) == 2:
            # Convert stereo to mono (average channels)
            wav = wav.mean(axis=1)
        
        # AudioGen always outputs mono at 16kHz, so force mono if it's AudioGen
        if is_audiogen and len(wav.shape) == 2:
            # If somehow we got stereo from AudioGen, convert to mono
            wav = wav.mean(axis=1) if wav.shape[1] == 2 else wav
            # Then duplicate to stereo if requested
            if stereo:
                wav = np.stack([wav, wav], axis=1)
        
        # Progress: 85-95% - Saving file
        if progress_callback:
            progress_callback(90, "Saving audio file...")
        
        # Ensure output directory exists
        output_dir = Path(settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        file_id = str(uuid.uuid4())
        if settings.audio_format == "mp3":
            filename = f"{file_id}.wav"  # Save as WAV first, convert to MP3
        else:
            filename = f"{file_id}.wav"
        
        filepath = output_dir / filename
        
        # Save as WAV using torchaudio or scipy
        try:
            import torchaudio
            # Convert to tensor with correct shape
            if len(wav.shape) == 1:
                wav_tensor = torch.from_numpy(wav).unsqueeze(0)  # (1, samples)
            else:
                wav_tensor = torch.from_numpy(wav).T  # (channels, samples)
            
            torchaudio.save(str(filepath), wav_tensor, audio_sample_rate)
            
        except Exception as e:
            logger.warning(f"torchaudio save failed: {e}, using scipy")
            from scipy.io import wavfile
            wavfile.write(str(filepath), audio_sample_rate, wav)
        
        # Convert to MP3 if requested
        if settings.audio_format == "mp3":
            try:
                from pydub import AudioSegment
                mp3_path = output_dir / f"{file_id}.mp3"
                audio = AudioSegment.from_wav(str(filepath))
                audio.export(str(mp3_path), format="mp3")
                os.remove(filepath)  # Remove WAV file
                filepath = mp3_path
                
            except Exception as e:
                logger.warning(f"MP3 conversion failed: {e}, keeping WAV")
        
        if progress_callback:
            progress_callback(100, "Complete!")
        
        return str(filepath)
    
    except torch.cuda.OutOfMemoryError as e:
        error_msg = f"Out of memory. Try a smaller model or shorter duration."
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    except RuntimeError as e:
        error_str = str(e)
        # Gestisci OutOfMemoryError anche per XPU
        if "out of memory" in error_str.lower() or "out_of_memory" in error_str.lower():
            error_msg = f"Out of memory on {device.type}. Try a smaller model or shorter duration."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        raise
    except Exception as e:
        logger.error(f"Generation failed: {e}", exc_info=True)
        raise RuntimeError(f"Audio generation failed: {str(e)}")

