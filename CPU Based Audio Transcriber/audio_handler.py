"""Audio file handling utilities."""
import soundfile as sf
import os
from typing import Tuple, Generator, Optional
import numpy as np


class AudioHandler:
    """Handles audio file operations with support for streaming large files."""
    
    # Default chunk size: 30 seconds of audio at 16kHz = 480,000 samples
    DEFAULT_CHUNK_SIZE = 480000
    
    @staticmethod
    def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file. Returns (audio_data, sample_rate)."""
        audio, sr = sf.read(file_path, dtype="float32", always_2d=True)
        audio = audio[:, 0]
        return audio, sr
    
    @staticmethod
    def stream_audio_chunks(
        file_path: str,
        chunk_size: Optional[int] = None,
        overlap_samples: int = 0
    ) -> Generator[Tuple[np.ndarray, int, float], None, None]:
        """
        Stream audio file in chunks to reduce memory usage.
        
        Args:
            file_path: Path to audio file
            chunk_size: Number of samples per chunk (default: 30 seconds at 16kHz)
            overlap_samples: Number of samples to overlap between chunks (default: 0)
        
        Yields:
            Tuple of (audio_chunk, sample_rate, progress_ratio)
        """
        if chunk_size is None:
            chunk_size = AudioHandler.DEFAULT_CHUNK_SIZE
        
        # Get file info without loading entire file
        with sf.SoundFile(file_path) as f:
            sr = f.samplerate
            total_frames = len(f)
            
            # Calculate overlap in frames
            overlap = max(0, overlap_samples)
            position = 0
            
            while position < total_frames:
                # Read chunk
                f.seek(position)
                read_size = min(chunk_size, total_frames - position)
                chunk = f.read(read_size, dtype="float32", always_2d=True)
                
                if chunk.shape[0] == 0:
                    break
                
                # Convert to mono if stereo
                if chunk.ndim == 2 and chunk.shape[1] > 1:
                    chunk = chunk[:, 0]
                elif chunk.ndim == 2:
                    chunk = chunk[:, 0]
                
                progress = (position + read_size) / total_frames
                yield chunk, sr, progress
                
                # Move position for next chunk (accounting for overlap)
                position += read_size - overlap
    
    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        """Get audio duration in seconds."""
        try:
            with sf.SoundFile(file_path) as f:
                return len(f) / f.samplerate
        except Exception as e:
            print(f"Error getting audio duration: {e}")
            return 0.0
    
    @staticmethod
    def cleanup_temp_file(file_path: str) -> None:
        """Delete temporary file if it exists."""
        if file_path and "tmp" in file_path and os.path.exists(file_path):
            os.remove(file_path)
