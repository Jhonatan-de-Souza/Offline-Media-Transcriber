"""Service for managing transcription operations."""
import threading
import time
from typing import Optional, Callable
from model_manager import ModelManager
from performance_profiler import PerformanceProfiler
from audio_handler import AudioHandler
from video_converter import VideoConverter
from resource_manager import ResourceManager


class TranscriptionService:
    """Handles transcription with threading and intelligent time estimation."""
    
    def __init__(self, model_manager: ModelManager, max_cpu_percent: float = 80.0, max_ram_percent: float = 80.0):
        self.model_manager = model_manager
        self.video_converter = VideoConverter()
        self.profiler = PerformanceProfiler(model_manager)
        self.resource_manager = ResourceManager(max_cpu_percent, max_ram_percent)
        self._thread: Optional[threading.Thread] = None
        self._cancel_requested = False
        self._result: Optional[str] = None
        self._error: Optional[str] = None
        self._start_time: Optional[float] = None
        self._estimated_duration: Optional[float] = None
        self._throttle_count = 0
        # GUI-facing progress state (updated from worker thread)
        self._phase: str = "idle"
        self._chunk_done: int = 0
        self._chunk_total: int = 0
    
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
            if self.video_converter.is_video(file_path):
                self._phase = "Converting video..."
            else:
                self._phase = "Loading audio..."
            audio_file = self._prepare_audio(file_path, on_error)
            if not audio_file:
                return
            
            # Load audio and estimate transcription time
            self._phase = "Loading audio..."
            audio, sr = AudioHandler.load_audio(audio_file)
            audio_duration = len(audio) / sr
            
            # Estimate transcription time using profiler
            self._estimated_duration = self.profiler.estimate_transcription_time(audio_duration)
            self._start_time = time.time()
            
            print(f"Audio duration: {audio_duration:.1f}s")
            print(f"Estimated CPU transcription time: {self._estimated_duration:.1f}s")
            print(f"Using CPU Real-Time Factor (RTF): {self.profiler.rtf:.2f}x")
            print(f"Resource limits: CPU ≤ {self.resource_manager.max_cpu_percent}%, RAM ≤ {self.resource_manager.max_ram_percent}%")
            print("")
            
            self._throttle_count = 0
            
            # Transcribe with resource monitoring
            self._phase = "Transcribing..."
            print("Starting transcription...")
            self._result = self._transcribe_with_monitoring(audio, sr)
            
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
            self._phase = "idle"
    
    def _transcribe_with_monitoring(self, audio, sr: int) -> str:
        """Transcribe audio with chunking, resource monitoring, and progress reporting."""
        result_container: dict = {'text': None, 'error': None}
        # Shared progress state updated by the per-chunk callback
        progress: dict = {'done': 0, 'total': 0}

        def on_chunk_done(idx: int, total: int, partial: str) -> None:
            progress['done'] = idx
            progress['total'] = total
            # Expose to GUI polling
            self._chunk_done = idx
            self._chunk_total = total

        def transcribe_thread():
            try:
                result_container['text'] = self.model_manager.transcribe_long(
                    audio, sr,
                    on_chunk_done=on_chunk_done,
                    cancel_check=lambda: self._cancel_requested,
                )
            except Exception as e:
                result_container['error'] = e

        transcription_thread = threading.Thread(target=transcribe_thread, daemon=True)
        transcription_thread.start()

        check_interval = 0.5
        last_bar = ""

        while transcription_thread.is_alive():
            # Resource throttling
            was_throttled = self.resource_manager.check_and_throttle()
            if was_throttled:
                self._throttle_count += 1

            # Build progress line: prefer chunk-based, fall back to time-based
            done = progress['done']
            total = progress['total']
            if total > 0:
                pct = min(int((done / total) * 100), 99)
                bar = _progress_bar(pct)
                line = f"  [Transcribing] {bar} {pct:3d}%  (chunk {done}/{total})"
            elif self._start_time and self._estimated_duration and self._estimated_duration > 0:
                elapsed = time.time() - self._start_time
                pct = min(int((elapsed / self._estimated_duration) * 100), 99)
                remaining = max(0, self._estimated_duration - elapsed)
                bar = _progress_bar(pct)
                line = f"  [Transcribing] {bar} {pct:3d}%  (~{_format_time(remaining)} remaining)"
            else:
                line = "  [Transcribing] waiting for first chunk..."

            if line != last_bar:
                print(line, end="\r", flush=True)
                last_bar = line

            time.sleep(check_interval)

        # Clear the progress line
        done = progress['total']
        print(f"  [Transcribing] {'█' * 20} 100%  ({done}/{done} chunks done)          ")

        if result_container['error']:
            raise result_container['error']

        return result_container['text']
    
    def _prepare_audio(
        self,
        file_path: str,
        on_error: Optional[Callable],
    ) -> Optional[str]:
        """Convert video to audio if needed. Returns audio file path."""
        if self.video_converter.is_video(file_path):
            try:
                # Pass resource manager for monitoring during video conversion
                return self.video_converter.extract_audio(file_path, self.resource_manager)
            except Exception as e:
                self._error = f"Video conversion error: {str(e)}"
                if on_error:
                    on_error(self._error)
                return None
        return file_path
    
    def get_gui_progress(self) -> tuple[str, float, str]:
        """
        Return (phase_label, fraction_0_to_1, detail_text) for the GUI progress bar.
        fraction is -1.0 while in an indeterminate phase.
        """
        phase = self._phase
        if phase == "idle":
            return "idle", 0.0, ""
        if phase == "Converting video...":
            # Indeterminate — we can't easily get ffmpeg % into the GUI
            return phase, -1.0, "Please wait..."
        if phase == "Loading audio...":
            return phase, -1.0, "Please wait..."
        if phase == "Transcribing...":
            done = self._chunk_done
            total = self._chunk_total
            if total > 0:
                frac = done / total
                pct = int(frac * 100)
                return phase, frac, f"{pct}%"
            # Fall back to time-based before first chunk comes in
            if self._start_time and self._estimated_duration and self._estimated_duration > 0:
                elapsed = time.time() - self._start_time
                frac = min(elapsed / self._estimated_duration, 0.99)
                remaining = max(0, self._estimated_duration - elapsed)
                mins, secs = divmod(int(remaining), 60)
                detail = f"~{mins}m {secs:02d}s remaining"
                return phase, frac, detail
            return phase, -1.0, "Starting..."
        return phase, -1.0, ""

    def cancel(self) -> None:
        """Stop transcription immediately: kill ffmpeg and abort chunk loop."""
        self._cancel_requested = True
        self.video_converter.kill()
    
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
