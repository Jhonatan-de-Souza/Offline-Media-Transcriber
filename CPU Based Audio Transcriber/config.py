"""Configuration for Audio Transcriber with auto-download support."""
from pathlib import Path
from huggingface_hub import hf_hub_download

# Get the directory where this config file is located
CONFIG_DIR = Path(__file__).parent
MODELS_DIR = CONFIG_DIR / "models"

# Create models directory if it doesn't exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Hugging Face repo info
HF_REPO_ID = "csukuangfj/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
HF_REPO_REVISION = "main"

# Model file names
MODEL_FILES = {
    "encoder": "encoder.int8.onnx",
    "decoder": "decoder.int8.onnx",
    "joiner": "joiner.int8.onnx",
    "tokens": "tokens.txt",
}


def download_models_if_needed(
    on_file_start=None,
    on_progress=None,
    on_status=None,
) -> bool:
    """
    Download model files from Hugging Face if they don't exist locally.
    This runs once at app startup.
    
    Args:
        on_file_start: Callback function(filename: str) called when starting to download a file
        on_progress: Callback function(value: float) called with progress 0.0-1.0
        on_status: Callback function(status: str) called with status messages
    
    Returns:
        bool: True if all models are available, False if download failed.
    """
    def report_status(msg: str) -> None:
        print(msg)
        if on_status:
            on_status(msg)
    
    report_status("Checking for model files...")
    
    # Check which files are missing
    missing_files = []
    for name, filename in MODEL_FILES.items():
        local_path = MODELS_DIR / filename
        if not local_path.exists():
            missing_files.append((name, filename))
        else:
            report_status(f"  ✓ {filename}")
    
    # If all files exist, we're done
    if not missing_files:
        report_status("✓ All model files found locally")
        return True
    
    # Download missing files
    report_status(f"\nDownloading {len(missing_files)} model file(s) from Hugging Face...")
    report_status("(This may take a few minutes on first run)\n")
    
    try:
        for idx, (name, filename) in enumerate(missing_files):
            report_status(f"Downloading {filename}...")
            
            if on_file_start:
                on_file_start(filename)
            
            hf_hub_download(
                repo_id=HF_REPO_ID,
                filename=filename,
                repo_type="model",
                revision=HF_REPO_REVISION,
                local_dir=str(MODELS_DIR),
                local_dir_use_symlinks=False,
            )
            
            # Update progress
            if on_progress:
                progress = (idx + 1.0) / len(missing_files)
                on_progress(progress)
            
            report_status(f"  ✓ {filename} downloaded")
        
        report_status("\n✓ All models downloaded successfully!")
        return True
        
    except Exception as e:
        report_status(f"\n✗ Failed to download models: {e}")
        report_status("Please download manually from:")
        report_status(f"  https://huggingface.co/{HF_REPO_ID}/tree/{HF_REPO_REVISION}")
        return False


MODEL_CONFIG = {
    "encoder_path": str(MODELS_DIR / MODEL_FILES["encoder"]),
    "decoder_path": str(MODELS_DIR / MODEL_FILES["decoder"]),
    "joiner_path": str(MODELS_DIR / MODEL_FILES["joiner"]),
    "tokens_path": str(MODELS_DIR / MODEL_FILES["tokens"]),
}
