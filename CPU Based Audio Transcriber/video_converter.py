"""Video to audio conversion utility."""
import subprocess
import tempfile
import os
import re
import time
import threading
from pathlib import Path
from typing import Optional


class VideoConverter:
    """Convert video files to audio format with resource monitoring."""
    
    SUPPORTED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv", ".wmv"}
    SUPPORTED_AUDIO_FORMATS = {".wav", ".mp3", ".ogg", ".flac", ".aac"}
    
    def __init__(self):
        self._current_process: Optional[subprocess.Popen] = None
    
    def kill(self) -> None:
        """Kill the running ffmpeg process immediately, if any."""
        proc = self._current_process
        if proc and proc.poll() is None:
            proc.kill()

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
    def _parse_ffmpeg_time(time_str: str) -> float:
        """Parse ffmpeg time string HH:MM:SS.xx into seconds."""
        try:
            parts = time_str.strip().split(":")
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        except:
            return 0.0
    
    def extract_audio(self, video_path: str, resource_manager: Optional[object] = None) -> str:
        """
        Extract audio from video file with real-time progress reporting.
        Returns path to temporary WAV file.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name
        
        try:
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-af", "aformat=s16:16000",
                "-ar", "16000",
                "-ac", "1",
                "-y",
                output_path
            ]
            
            print(f"Converting video to audio: {Path(video_path).name}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace"
            )
            self._current_process = process
            
            # State shared between stderr reader thread and main loop
            state = {
                "total_duration": 0.0,
                "current_time": 0.0,
                "stderr_lines": [],
            }

            # Read stderr in a background thread to prevent pipe buffer deadlock
            def read_stderr():
                for line in process.stderr:
                    state["stderr_lines"].append(line)
                    # Parse total duration from ffmpeg header
                    if state["total_duration"] == 0.0:
                        m = re.search(r"Duration:\s*(\d+:\d+:\d+\.\d+)", line)
                        if m:
                            state["total_duration"] = VideoConverter._parse_ffmpeg_time(m.group(1))
                    # Parse current encode position
                    m = re.search(r"time=(\d+:\d+:\d+\.\d+)", line)
                    if m:
                        state["current_time"] = VideoConverter._parse_ffmpeg_time(m.group(1))
            
            stderr_thread = threading.Thread(target=read_stderr, daemon=True)
            stderr_thread.start()
            
            last_progress_report = -1
            
            while process.poll() is None:
                # Only check resources - no periodic printing
                if resource_manager:
                    resource_manager.check_and_throttle()
                
                # Show progress only when it advances by at least 1%
                total = state["total_duration"]
                current = state["current_time"]
                if total > 0:
                    pct = min(int((current / total) * 100), 99)
                    if pct != last_progress_report:
                        elapsed_str = _format_time(current)
                        total_str = _format_time(total)
                        bar = _progress_bar(pct)
                        print(f"  [Converting] {bar} {pct:3d}%  ({elapsed_str} / {total_str})",
                              end="\r", flush=True)
                        last_progress_report = pct
                
                time.sleep(0.2)
            
            stderr_thread.join(timeout=2)
            self._current_process = None
            
            if process.returncode not in (0, None) and process.returncode != -9:
                # returncode -9 / 1 on Windows means killed intentionally
                stderr_output = "".join(state["stderr_lines"][-20:])
                if os.path.exists(output_path):
                    os.unlink(output_path)
                raise RuntimeError(f"FFmpeg error: {stderr_output}")
            
            if process.returncode != 0:
                # Killed (cancelled)
                if os.path.exists(output_path):
                    os.unlink(output_path)
                return ""
            
            print(f"  [Converting] {'█' * 20} 100%  complete          ")
            print("✓ Video conversion complete")
            return output_path
        
        except FileNotFoundError:
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise RuntimeError(
                "FFmpeg not found. Download from https://ffmpeg.org/download.html "
                "and add it to your PATH."
            )
        except Exception:
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise


def _format_time(seconds: float) -> str:
    """Format seconds as MM:SS or HH:MM:SS."""
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def _progress_bar(pct: int, width: int = 20) -> str:
    """Return a simple ASCII progress bar."""
    filled = int(width * pct / 100)
    return "█" * filled + "░" * (width - filled)

