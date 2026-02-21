"""Service for managing transcription operations."""
import threading
import time
from typing import Optional, Callable
from model_manager import ModelManager
from performance_profiler import PerformanceProfiler
from audio_handler import AudioHandler
from video_converter import VideoConverter


class TranscriptionService:
    """Handles transcription with threading and intelligent time estimation."""
    
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
        self.video_converter = VideoConverter()
        self.profiler = PerformanceProfiler(model_manager)
        self._thread: Optional[threading.Thread] = None
        self._cancel_requested = False
        self._result: Optional[str] = None
        self._error: Optional[str] = None
        self._start_time: Optional[float] = None
        self._estimated_duration: Optional[float] = None
    
    def transcribe_async(
        self,
        file_path: str,
        on_progress: Optional[Callable[[float, float], None]] = None,
        on_complete: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
    ) -> None:
        """
        Start transcription in a background thread.
        
        Args:
            file_path: Path to audio or video file
            on_progress: Callback(elapsed, estimated_total) for progress updates
            on_complete: Callback(result) when done
            on_error: Callback(error_msg) on error
        """
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Transcription already in progress")
        
        self._cancel_requested = False
        self._result = None
        self._error = None
        self._start_time = None
        self._estimated_duration = None
        
        self._thread = threading.Thread(
            target=self._transcribe_worker,
            args=(file_path, on_progress, on_complete, on_error),
            daemon=True
        )
        self._thread.start()
    
    def _transcribe_worker(
        self,
        file_path: str,
        on_progress: Optional[Callable],
        on_complete: Optional[Callable],
        on_error: Optional[Callable],
    ) -> None:
        """Worker thread for transcription."""
        try:
            # Convert video to audio if needed
            audio_file = self._prepare_audio(file_path, on_error)
            if not audio_file:
                return
            
            # Load audio and estimate transcription time
            audio, sr = AudioHandler.load_audio(audio_file)
            audio_duration = len(audio) / sr
            
            # Estimate transcription time using profiler
            self._estimated_duration = self.profiler.estimate_transcription_time(audio_duration)
            self._start_time = time.time()
            
            print(f"Audio duration: {audio_duration:.1f}s")
            print(f"Estimated CPU transcription time: {self._estimated_duration:.1f}s")
            print(f"Using CPU Real-Time Factor (RTF): {self.profiler.rtf:.2f}x")
            
            # Transcribe
            self._result = self.model_manager.transcribe(audio, sr)
            
            # Cleanup
            AudioHandler.cleanup_temp_file(audio_file)
            
            if on_complete:
                on_complete(self._result)
        
        except Exception as e:
            self._error = str(e)
            if on_error:
                on_error(self._error)
        
        finally:
            self._start_time = None
            self._estimated_duration = None
    
    def _prepare_audio(
        self,
        file_path: str,
        on_error: Optional[Callable],
    ) -> Optional[str]:
        """Convert video to audio if needed. Returns audio file path."""
        if self.video_converter.is_video(file_path):
            try:
                return self.video_converter.extract_audio(file_path)
            except Exception as e:
                self._error = f"Video conversion error: {str(e)}"
                if on_error:
                    on_error(self._error)
                return None
        return file_path
    
    def cancel(self) -> None:
        """Request cancellation of ongoing transcription."""
        self._cancel_requested = True
    
    def is_running(self) -> bool:
        """Check if transcription is currently running."""
        return self._thread is not None and self._thread.is_alive()
    
    def get_progress(self) -> tuple[float, float]:
        """
        Get transcription progress.
        
        Returns:
            (elapsed_seconds, estimated_total_seconds)
        """
        if not self._start_time or not self._estimated_duration:
            return 0.0, 0.0
        
        elapsed = time.time() - self._start_time
        return elapsed, self._estimated_duration


