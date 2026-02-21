"""Audio file handling utilities."""
import soundfile as sf
import os
from typing import Tuple
import numpy as np


class AudioHandler:
    """Handles audio file operations."""
    
    @staticmethod
    def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file. Returns (audio_data, sample_rate)."""
        audio, sr = sf.read(file_path, dtype="float32", always_2d=True)
        audio = audio[:, 0]
        return audio, sr
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Delete temporary file if it exists."""
        if file_path and "tmp" in file_path and os.path.exists(file_path):
            os.remove(file_path)
