# Backend Dockerfile - CPU version
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsndfile1 \
    pkg-config \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libswresample-dev \
    libavfilter-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU first (without CUDA) - specific version matching audiocraft
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.1.0+cpu torchaudio==2.1.0+cpu

# Install PyAV with patch for FFmpeg compatibility
RUN pip download av==11.0.0 && \
    tar -xzf av-11.0.0.tar.gz && \
    cd av-11.0.0 && \
    find . -name "*.c" -exec sed -i 's/AV_OPT_TYPE_CHANNEL_LAYOUT/AV_OPT_TYPE_CHLAYOUT/g' {} \; && \
    pip install --no-cache-dir . && \
    cd .. && rm -rf av-11.0.0* || \
    (pip install --no-cache-dir "av>=12.0.0" || \
     pip install --no-cache-dir "av==11.2.0" || \
     pip install --no-cache-dir "av==11.1.0" || true)

# Copy requirements without audiocraft
COPY requirements.txt .
RUN sed -i '/^audiocraft/d' requirements.txt

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Install audiocraft without dependencies to avoid conflicts with PyAV
RUN pip install --no-cache-dir --no-deps audiocraft>=1.3.0 || true

# Install essential audiocraft dependencies
RUN pip install --no-cache-dir \
    einops \
    encodec \
    flashy>=0.0.1 \
    hydra-core>=1.1 \
    hydra_colorlog \
    librosa \
    sentencepiece \
    torchmetrics \
    num2words \
    spacy>=3.6.1 \
    protobuf \
    dora_search \
    colorlog \
    lightning-utilities \
    lazy_loader \
    numba \
    audioread \
    decorator \
    joblib \
    msgpack \
    pooch \
    scikit-learn \
    soxr \
    "huggingface_hub<1.0,>=0.19.3" \
    "regex!=2019.12.17" \
    safetensors \
    "tokenizers>=0.14,<0.19" || true

# Force reinstall torch CPU to override any CUDA versions that audiocraft may have installed
# Also ensure NumPy is <2.0.0 for compatibility with torch
RUN pip install --no-cache-dir --force-reinstall --no-index --find-links https://download.pytorch.org/whl/cpu torch==2.1.0+cpu torchaudio==2.1.0+cpu && \
    pip install --no-cache-dir "numpy<2.0.0,>=1.24.0" --force-reinstall || \
    (pip install --no-cache-dir --force-reinstall torch==2.1.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu && \
     pip install --no-cache-dir "numpy<2.0.0,>=1.24.0" --force-reinstall)

# Ensure compatible versions after all installations (spacy may upgrade numpy)
# Install xformers for AudioGen support - try multiple versions for compatibility
# Force correct tokenizers version for AudioGen compatibility
RUN pip install --no-cache-dir "numpy<2.0.0,>=1.24.0" "transformers>=4.31.0,<4.40.0" --force-reinstall && \
    pip install --no-cache-dir --force-reinstall "tokenizers>=0.14,<0.19" && \
    (pip install --no-cache-dir "xformers==0.0.22.post7" || \
     pip install --no-cache-dir "xformers==0.0.23.post1" || \
     pip install --no-cache-dir "xformers>=0.0.23,<0.0.24" || \
     echo "Warning: xformers installation failed, AudioGen may not work") && \
    pip install --no-cache-dir "numpy<2.0.0,>=1.24.0" --force-reinstall

# Copy application code
COPY . .

# Create output directory
RUN mkdir -p /data/outputs

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

