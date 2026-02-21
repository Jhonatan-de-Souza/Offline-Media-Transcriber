"""CPU performance profiling for accurate transcription time estimation.

Parakeet V3 uses CPU-only inference. This profiler measures CPU performance
to accurately estimate transcription times.
"""
import time
import numpy as np
from typing import Optional
from model_manager import ModelManager


class PerformanceProfiler:
    """Measures CPU performance for accurate transcription time estimation.
    
    Parakeet V3 operates on CPU only. This profiler benchmarks your CPU
    to calculate the Real-Time Factor (RTF) - how fast your CPU can
    transcribe audio relative to the audio's duration.
    """
    
    def __init__(self, model_manager: ModelManager):
        """
        Initialize profiler for CPU-only performance measurement.
        
        Args:
            model_manager: ModelManager instance (must be CPU-only)
        """
        self.model_manager = model_manager
        self.rtf: Optional[float] = None  # Real-Time Factor
        self.is_profiled = False
    
    def profile(self) -> float:
        """
        Run CPU-only performance benchmark.
        
        Creates a short synthetic audio segment and measures how long
        the CPU takes to transcribe it. This gives us the Real-Time Factor.
        
        Returns:
            RTF (Real-Time Factor) - CPU transcription speed:
            - 0.5 = CPU is 2x faster than real-time (fast CPU)
            - 1.0 = CPU matches real-time (average CPU)
            - 2.0 = CPU is 2x slower than real-time (slow/old CPU)
        """
        if self.is_profiled and self.rtf is not None:
            return self.rtf
        
        print("🔍 Benchmarking CPU performance (Parakeet V3 - CPU only)...")
        
        try:
            # Create synthetic audio: 5 seconds of silence at 16kHz
            # This is enough time for accurate measurement without being too slow
            sample_rate = 16000
            duration_seconds = 5
            audio_data = np.zeros(sample_rate * duration_seconds, dtype=np.float32)
            
            print(f"  Testing with {duration_seconds}s of audio...")
            
            # Measure transcription time on CPU
            start_time = time.time()
            _ = self.model_manager.transcribe(audio_data, sample_rate)
            elapsed_time = time.time() - start_time
            
            # Calculate Real-Time Factor (RTF)
            # RTF = time_to_transcribe / audio_duration
            audio_duration = len(audio_data) / sample_rate
            self.rtf = elapsed_time / audio_duration
            
            print(f"✓ CPU Benchmark complete:")
            print(f"  Audio duration: {audio_duration:.1f}s")
            print(f"  CPU transcription time: {elapsed_time:.1f}s")
            print(f"  Real-Time Factor (RTF): {self.rtf:.2f}x")
            print(f"  Performance: {1/self.rtf:.2f}x real-time speed" if self.rtf > 0 else "  Performance: N/A")
            
            self.is_profiled = True
            return self.rtf
        
        except Exception as e:
            print(f"⚠️ CPU Benchmark failed: {str(e)}")
            print("  Using conservative estimate (RTF = 1.5x)")
            self.rtf = 1.5
            self.is_profiled = True
            return self.rtf
    
    def estimate_transcription_time(self, audio_duration: float) -> float:
        """
        Estimate CPU transcription time based on audio duration.
        
        Formula: estimated_time = audio_duration * RTF
        
        Args:
            audio_duration: Duration of audio file in seconds
        
        Returns:
            Estimated transcription time in seconds (CPU only)
        """
        if self.rtf is None:
            # Default conservative estimate if profiling not done
            # Assumes average CPU performance
            rtf = 1.5
        else:
            rtf = self.rtf
        
        estimated_time = audio_duration * rtf
        return estimated_time
