"""Configuration for Audio Transcriber."""
from pathlib import Path

# Get the directory where this config file is located
CONFIG_DIR = Path(__file__).parent

MODEL_CONFIG = {
    "encoder_path": str(CONFIG_DIR / "models" / "encoder.int8.onnx"),
    "decoder_path": str(CONFIG_DIR / "models" / "decoder.int8.onnx"),
    "joiner_path": str(CONFIG_DIR / "models" / "joiner.int8.onnx"),
    "tokens_path": str(CONFIG_DIR / "models" / "tokens.txt"),
}
