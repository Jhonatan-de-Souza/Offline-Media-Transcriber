"""
Audio Transcriber - Convert audio and video files to text using Whisper AI.

Main entry point for the application.
Import torch before other libraries to avoid Windows DLL initialization issues.
"""

# Import torch FIRST (Windows DLL initialization fix for c10.dll)
import torch

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from modules.ui import TranscriberApp
from modules.splash import SplashScreen
from modules.transcriber import ModelLoaderThread


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI"))
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    
    # Create and setup the main window (but don't show it yet)
    window = TranscriberApp()
    
    # Create model loader thread
    loader_thread = ModelLoaderThread()
    
    def on_model_loaded(model):
        """Called when model finishes loading."""
        window.model = model
        splash.stop_animation()
        window.show()
    
    def on_loader_error(error_msg):
        """Called if model loading fails."""
        splash.stop_animation()
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(splash, "Error", f"Failed to load model: {error_msg}")
        sys.exit(1)
    
    def on_status_changed(status):
        """Update splash screen status."""
        splash.set_status(status)
    
    # Connect signals
    loader_thread.finished.connect(on_model_loaded)
    loader_thread.error.connect(on_loader_error)
    loader_thread.status_changed.connect(on_status_changed)
    
    # Start loading the model
    loader_thread.start()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

