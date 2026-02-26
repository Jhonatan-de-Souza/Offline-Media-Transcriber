"""Resource monitoring and limiting for the transcriber."""
import psutil
import time
from typing import Optional


class ResourceManager:
    """Monitor and manage system resources with caps on CPU and RAM usage."""
    
    def __init__(self, max_cpu_percent: float = 80.0, max_ram_percent: float = 80.0):
        """
        Initialize resource manager.
        
        Args:
            max_cpu_percent: Maximum CPU usage percentage (0-100)
            max_ram_percent: Maximum RAM usage percentage (0-100)
        """
        self.max_cpu_percent = max_cpu_percent
        self.max_ram_percent = max_ram_percent
        self.process = psutil.Process()
        self._throttle_active = False
        # Warm up cpu_percent so interval=None returns real values immediately
        psutil.cpu_percent(interval=None)
    
    def get_current_usage(self) -> dict:
        """Get current system resource usage (non-blocking)."""
        try:
            # interval=None returns cached value from last call - non-blocking
            cpu_percent = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            return {
                'cpu_percent': cpu_percent,
                'ram_percent': ram.percent,
                'ram_used_mb': ram.used / (1024 * 1024),
                'ram_total_mb': ram.total / (1024 * 1024),
            }
        except Exception as e:
            print(f"Error getting resource usage: {e}")
            return {
                'cpu_percent': 0,
                'ram_percent': 0,
                'ram_used_mb': 0,
                'ram_total_mb': 0,
            }
    
    def check_and_throttle(self) -> bool:
        """
        Check resource usage and throttle if necessary.
        Returns True if throttling was applied.
        """
        usage = self.get_current_usage()
        
        if usage['cpu_percent'] > self.max_cpu_percent or usage['ram_percent'] > self.max_ram_percent:
            if not self._throttle_active:
                print(f"⚠️  Resource limit reached. Throttling...")
                print(f"   CPU: {usage['cpu_percent']:.1f}% (max: {self.max_cpu_percent}%)")
                print(f"   RAM: {usage['ram_percent']:.1f}% (max: {self.max_ram_percent}%)")
                self._throttle_active = True
            
            # Brief sleep to throttle processing
            time.sleep(0.1)
            return True
        
        if self._throttle_active:
            print("✓ Resources back to normal levels")
            self._throttle_active = False
        
        return False
    
    def print_status(self) -> None:
        """Print current resource usage status."""
        usage = self.get_current_usage()
        print(f"📊 Resources - CPU: {usage['cpu_percent']:.1f}% | RAM: {usage['ram_percent']:.1f}% ({usage['ram_used_mb']:.0f}MB / {usage['ram_total_mb']:.0f}MB)")
