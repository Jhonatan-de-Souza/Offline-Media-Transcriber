"""
Audio transcription using OpenAI Whisper.
"""
import os
import time
import torch
from PyQt5.QtCore import QThread, pyqtSignal
import whisper
from .audio_processor import (
    convert_mp4_to_mp3, cleanup_temp_file, get_file_duration, 
    estimate_conversion_time, get_gpu_memory
)


class ModelLoaderThread(QThread):
    """Thread for loading the Whisper model asynchronously."""
    finished = pyqtSignal(object)  # Emits the loaded model
    error = pyqtSignal(str)
    status_changed = pyqtSignal(str)  # Status updates
    
    def __init__(self, device=None):
        super().__init__()
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
    
    def run(self):
        try:
            self.status_changed.emit("Detecting device...")
            
            if self.device == "cuda":
                self.status_changed.emit("Loading model to GPU...")
            else:
                self.status_changed.emit("Loading model to CPU...")
            
            # Load model
            model = load_whisper_model(self.device)
            
            self.status_changed.emit("Ready!")
            self.finished.emit(model)
        except Exception as e:
            self.error.emit(str(e))


class TranscribeThread(QThread):
    """Thread for transcribing a single audio file."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    time_estimate = pyqtSignal(float)  # Estimated seconds remaining
    
    def __init__(self, model, audio_path, language):
        super().__init__()
        self.model = model
        self.audio_path = audio_path
        self.language = language
        self.temp_file = None
        self.start_time = None
    
    def run(self):
        try:
            # Get file duration and estimate conversion time
            duration = get_file_duration(self.audio_path)
            gpu_memory = get_gpu_memory()
            estimated_time = estimate_conversion_time(duration, gpu_memory)
            self.time_estimate.emit(estimated_time)
            
            # Track elapsed time for auto-extension
            self.start_time = time.time()
            extended_count = 0
            
            # Convert MP4 to MP3 if needed
            working_path = self.audio_path
            if self.audio_path.lower().endswith('.mp4'):
                self.temp_file = convert_mp4_to_mp3(self.audio_path)
                working_path = self.temp_file
            
            # Transcribe
            result = self.model.transcribe(working_path, language=self.language)
            self.finished.emit(result["text"])
            
        except Exception as e:
            self.error.emit(str(e))
        finally:
            cleanup_temp_file(self.temp_file)
    
    def update_time_estimate(self):
        """Update time estimate based on elapsed time (for auto-extension)."""
        if self.start_time is None:
            return
        
        elapsed = time.time() - self.start_time
        # Get original estimates
        duration = get_file_duration(self.audio_path)
        gpu_memory = get_gpu_memory()
        original_estimate = estimate_conversion_time(duration, gpu_memory)
        
        # If elapsed time exceeds estimate, extend by another estimate period
        if elapsed > original_estimate:
            remaining = original_estimate  # Add another full estimate
            self.time_estimate.emit(remaining)


class BatchTranscribeThread(QThread):
    """Thread for transcribing multiple audio files."""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    time_estimate = pyqtSignal(float)  # Estimated seconds remaining for current file
    file_progress = pyqtSignal(int, int, str)  # current file index, total files, current filename
    file_completed = pyqtSignal(str, str)  # filename, transcription text
    
    def __init__(self, model, folder_path, language, output_folder):
        super().__init__()
        self.model = model
        self.folder_path = folder_path
        self.language = language
        self.output_folder = output_folder
        self.temp_files = []
        self.start_time = None
    
    def run(self):
        try:
            # Find all MP4 files in the folder
            mp4_files = [f for f in os.listdir(self.folder_path) 
                        if f.lower().endswith('.mp4')]
            
            if not mp4_files:
                self.error.emit("No MP4 files found in the selected folder.")
                return
            
            total_files = len(mp4_files)
            gpu_memory = get_gpu_memory()
            
            for idx, filename in enumerate(mp4_files, 1):
                file_path = os.path.join(self.folder_path, filename)
                self.file_progress.emit(idx, total_files, filename)
                
                # Estimate time for this file
                duration = get_file_duration(file_path)
                estimated_time = estimate_conversion_time(duration, gpu_memory)
                self.time_estimate.emit(estimated_time)
                
                # Convert MP4 to MP3
                temp_file = convert_mp4_to_mp3(file_path)
                self.temp_files.append(temp_file)
                
                # Transcribe
                result = self.model.transcribe(temp_file, language=self.language)
                transcription = result["text"]
                
                # Save transcription to file
                base_name = os.path.splitext(filename)[0]
                output_file = os.path.join(self.output_folder, f"{base_name}.txt")
                
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(transcription)
                
                self.file_completed.emit(filename, transcription)
            
            self.finished.emit()
            
        except Exception as e:
            self.error.emit(str(e))
        finally:
            # Clean up all temporary files
            for temp_file in self.temp_files:
                cleanup_temp_file(temp_file)


def load_whisper_model(device=None):
    """
    Load Whisper model on the specified device.
    
    Args:
        device (str): Device to load model on ('cuda' or 'cpu'). If None, auto-detect.
        
    Returns:
        whisper.Whisper: Loaded model
    """
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    
    try:
        model = whisper.load_model("medium", device=device)
    except TypeError:
        # Fallback if load_model doesn't accept device
        model = whisper.load_model("medium")
        try:
            if hasattr(model, "to"):
                model.to(device)
        except Exception:
            pass  # Continue with CPU model
    
    return model
