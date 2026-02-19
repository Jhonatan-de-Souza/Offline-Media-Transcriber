"""
Audio processing utilities for converting media files to MP3.
"""
import os
import tempfile
import torch
from pydub import AudioSegment


def get_gpu_memory():
    """
    Get available GPU memory in gigabytes.
    
    Returns:
        float: GPU memory in GB, or 0 if no GPU available
    """
    if not torch.cuda.is_available():
        return 0
    
    try:
        gpu_memory_bytes = torch.cuda.get_device_properties(0).total_memory
        gpu_memory_gb = gpu_memory_bytes / (1024 ** 3)
        return gpu_memory_gb
    except Exception:
        return 0


def get_file_duration(file_path):
    """
    Get the duration of an audio or video file in seconds.
    
    Args:
        file_path (str): Path to the audio or video file
        
    Returns:
        float: Duration in seconds
    """
    try:
        if file_path.lower().endswith('.mp4'):
            audio = AudioSegment.from_file(file_path, format="mp4")
        else:
            # Try to detect format from file extension
            ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            audio = AudioSegment.from_file(file_path, format=ext)
        
        duration_ms = len(audio)
        duration_sec = duration_ms / 1000.0
        return duration_sec
    except Exception:
        return 0  # Default to 0 if duration detection fails


def estimate_conversion_time(duration_sec, gpu_vram_gb=None):
    """
    Estimate transcription time based on file duration and GPU memory.
    
    Args:
        duration_sec (float): Duration of the audio/video file in seconds
        gpu_vram_gb (float): GPU memory in GB (None = auto-detect)
        
    Returns:
        float: Estimated transcription time in seconds
    """
    if gpu_vram_gb is None:
        gpu_vram_gb = get_gpu_memory()
    
    # Estimation factors based on GPU memory
    if gpu_vram_gb >= 16:
        # 16GB+ GPU: 40% of file duration
        factor = 0.40
    elif gpu_vram_gb >= 8:
        # 8GB GPU: 80% of file duration
        factor = 0.80
    elif gpu_vram_gb >= 4:
        # 4GB GPU: 120% of file duration
        factor = 1.20
    else:
        # CPU or very limited VRAM: 200% of file duration
        factor = 2.0
    
    estimated_time = duration_sec * factor
    return estimated_time


def convert_mp4_to_mp3(mp4_path):
    """
    Convert MP4 file to MP3 format.
    
    Args:
        mp4_path (str): Path to the MP4 file
        
    Returns:
        str: Path to the temporary MP3 file
    """
    temp_dir = tempfile.gettempdir()
    temp_filename = f"temp_audio_{os.getpid()}.mp3"
    temp_file = os.path.join(temp_dir, temp_filename)
    
    audio = AudioSegment.from_file(mp4_path, format="mp4")
    audio.export(temp_file, format="mp3")
    
    return temp_file


def cleanup_temp_file(temp_file_path):
    """
    Clean up a temporary file if it exists.
    
    Args:
        temp_file_path (str): Path to the temporary file
    """
    if temp_file_path and os.path.exists(temp_file_path):
        try:
            os.remove(temp_file_path)
        except Exception:
            pass  # Ignore cleanup errors

