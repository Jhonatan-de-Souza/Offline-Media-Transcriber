"""Video to audio conversion utility."""
import subprocess
import tempfile
import os
from pathlib import Path


class VideoConverter:
    """Convert video files to audio format."""
    
    SUPPORTED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"}
    SUPPORTED_AUDIO_FORMATS = {".wav", ".mp3", ".ogg", ".flac", ".aac"}
    
    @staticmethod
    def is_video(file_path: str) -> bool:
        """Check if file is a video format."""
        ext = Path(file_path).suffix.lower()
        return ext in VideoConverter.SUPPORTED_VIDEO_FORMATS
    
    @staticmethod
    def is_audio(file_path: str) -> bool:
        """Check if file is an audio format."""
        ext = Path(file_path).suffix.lower()
        return ext in VideoConverter.SUPPORTED_AUDIO_FORMATS
    
    @staticmethod
    def extract_audio(video_path: str) -> str:
        """
        Extract audio from video file.
        Returns path to temporary WAV file.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name
        
        try:
            # Use ffmpeg to extract audio
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-af", "aformat=s16:16000",
                "-ar", "16000",
                "-ac", "1",
                "-y",  # Overwrite output
                output_path
            ]
            
            subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                timeout=300  # 5 minute timeout
            )
            
            return output_path
        
        except subprocess.TimeoutExpired:
            os.unlink(output_path)
            raise RuntimeError("Video conversion timed out")
        except subprocess.CalledProcessError as e:
            os.unlink(output_path)
            raise RuntimeError(f"FFmpeg error: {e.stderr.decode()}")
        except FileNotFoundError:
            os.unlink(output_path)
            raise RuntimeError(
                "FFmpeg not found. Install it with: brew install ffmpeg"
            )
