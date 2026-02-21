import sherpa_onnx
from typing import Optional
import os

class ModelManager:
    """Handles loading and inference with Parakeet V3 model."""
    
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
        """Transcribe audio. Returns transcription text."""
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        stream = self.model.create_stream()
        stream.accept_waveform(sample_rate, audio_data)
        self.model.decode_stream(stream)
        return stream.result.text
