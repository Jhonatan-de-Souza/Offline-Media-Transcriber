import sherpa_onnx
from typing import Optional, Callable
import os
import numpy as np

class ModelManager:
    """Handles loading and inference with Parakeet V3 model."""
    
    # Parakeet V3 encoder uses 10ms hop features; its attention layers have a
    # hard maximum of 4112 feature frames (~41 seconds).  Stay well below that.
    SAFE_CHUNK_SECONDS = 30
    OVERLAP_SECONDS = 0.5   # half-second crossfade to avoid clipping words at boundaries
    
    def __init__(self, encoder_path: str, decoder_path: str, joiner_path: str, tokens_path: str):
        self.encoder_path = encoder_path
        self.decoder_path = decoder_path
        self.joiner_path = joiner_path
        self.tokens_path = tokens_path
        self.model: Optional[sherpa_onnx.OfflineRecognizer] = None
    
    def load(self) -> bool:
        """Load the model. Returns True if successful."""
        try:
            # Check if files exist
            files = {
                "encoder": self.encoder_path,
                "decoder": self.decoder_path,
                "joiner": self.joiner_path,
                "tokens": self.tokens_path,
            }
            
            print(f"Current working directory: {os.getcwd()}")
            print("Checking model files...")
            for name, path in files.items():
                exists = os.path.exists(path)
                print(f"  {name}: {path} - {'EXISTS' if exists else 'NOT FOUND'}")
            
            self.model = sherpa_onnx.OfflineRecognizer.from_transducer(
                encoder=self.encoder_path,
                decoder=self.decoder_path,
                joiner=self.joiner_path,
                tokens=self.tokens_path,
                num_threads=4,
                provider="cpu",
                debug=False,
                decoding_method="greedy_search",
                model_type="nemo_transducer"
            )
            print("Model loaded successfully!")
            return True
        except Exception as e:
            print(f"Model load error: {str(e)}")
            return False
    
    def transcribe(self, audio_data, sample_rate: int) -> str:
        """Transcribe a single audio chunk. Must be ≤ SAFE_CHUNK_SECONDS long."""
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        stream = self.model.create_stream()
        stream.accept_waveform(sample_rate, audio_data)
        self.model.decode_stream(stream)
        return stream.result.text
    
    def transcribe_long(
        self,
        audio_data: np.ndarray,
        sample_rate: int,
        on_chunk_done: Optional[Callable[[int, int, str], None]] = None,
        cancel_check: Optional[Callable[[], bool]] = None,
    ) -> str:
        """
        Transcribe arbitrarily long audio by splitting it into safe-sized chunks.

        Args:
            audio_data:    1-D float32 numpy array at `sample_rate` Hz.
            sample_rate:   Samples per second (should be 16000).
            on_chunk_done: Optional callback(chunk_index, total_chunks, partial_text)
                           called after each chunk is transcribed.
            cancel_check:  Optional callable that returns True when cancelled.

        Returns:
            Full transcription text with chunks joined by spaces.
        """
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        chunk_samples = int(self.SAFE_CHUNK_SECONDS * sample_rate)
        overlap_samples = int(self.OVERLAP_SECONDS * sample_rate)
        total_samples = len(audio_data)
        
        # If audio fits in one chunk, skip all chunking logic
        if total_samples <= chunk_samples:
            text = self.transcribe(audio_data, sample_rate)
            if on_chunk_done:
                on_chunk_done(1, 1, text)
            return text
        
        # Build chunk start positions (no overlap on first chunk)
        starts = list(range(0, total_samples, chunk_samples - overlap_samples))
        total_chunks = len(starts)
        parts: list[str] = []
        
        print(f"  Audio split into {total_chunks} chunks of {self.SAFE_CHUNK_SECONDS}s each")
        
        for idx, start in enumerate(starts, 1):
            if cancel_check and cancel_check():
                print("  Transcription cancelled.")
                break
            end = min(start + chunk_samples, total_samples)
            chunk = audio_data[start:end]
            
            chunk_text = self.transcribe(chunk, sample_rate)
            parts.append(chunk_text.strip())
            
            if on_chunk_done:
                on_chunk_done(idx, total_chunks, chunk_text)
        
        return " ".join(p for p in parts if p)
