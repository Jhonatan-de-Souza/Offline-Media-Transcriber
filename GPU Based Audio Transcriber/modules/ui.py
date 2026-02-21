"""
PyQt5 user interface for the Audio Transcriber application.
"""
import os
import time
from pathlib import Path
import torch
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog,
    QLabel, QMessageBox, QComboBox, QDesktopWidget
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QLoggingCategory, QTimer
from .transcriber import TranscribeThread, BatchTranscribeThread, load_whisper_model

# Silence noisy font enumeration warnings from Qt
QLoggingCategory.setFilterRules("qt.qpa.fonts=false")

LANGUAGES = [
    ("English", "en"),
    ("Spanish", "es"),
    ("French", "fr"),
    ("German", "de"),
    ("Italian", "it"),
    ("Portuguese", "pt"),
    ("Chinese", "zh"),
    ("Japanese", "ja"),
    ("Korean", "ko"),
    ("Russian", "ru"),
    ("Hindi", "hi"),
    ("Arabic", "ar"),
]


class TranscriberApp(QWidget):
    """Main application window for the Audio Transcriber."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beautiful Audio Transcriber")
        
        # Get icon path relative to this module
        icon_path = Path(__file__).parent / "assets" / "audio-to-text.ico"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.setGeometry(100, 100, 700, 550)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")  # Dark theme
        self.center_on_screen()

        # State
        self.audio_path = None
        self.batch_folder = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        
        # Time tracking for countdown
        self.remaining_time = 0  # Seconds remaining
        self.display_time = 0    # For countdown display
        
        # Model will be set by main.py after loading
        self.model = None
        self.transcribe_thread = None

        # Build UI
        self.init_ui()
    
    def center_on_screen(self):
        """Center the main window on the monitor."""
        screen = QDesktopWidget().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()

        # Title
        title = QLabel("Audio Transcriber")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")  # Bright cyan for title in dark theme
        main_layout.addWidget(title)

        # Language selection
        self.language_label = QLabel("Select Language:")
        self.language_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.language_label.setStyleSheet("color: #ffffff;")
        main_layout.addWidget(self.language_label)

        self.language_combo = QComboBox()
        self.language_combo.setFont(QFont("Segoe UI", 11))
        self.language_combo.setStyleSheet(
            "QComboBox { background-color: #2d2d2d; color: #ffffff; border: 1px solid #444; padding: 5px; }"
            "QComboBox::drop-down { border: none; }"
            "QComboBox QAbstractItemView { background-color: #2d2d2d; color: #ffffff; selection-background-color: #00a8ff; }"
        )
        for name, code in LANGUAGES:
            self.language_combo.addItem(name, code)
        main_layout.addWidget(self.language_combo)

        # Separator
        separator = QLabel("")
        separator.setFixedHeight(10)
        main_layout.addWidget(separator)

        # Two-column layout for single and batch operations
        columns_layout = QHBoxLayout()

        # ===== LEFT COLUMN: SINGLE FILE TRANSCRIPTION =====
        left_layout = QVBoxLayout()
        
        single_title = QLabel("Single File Transcription")
        single_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        single_title.setStyleSheet("color: #00d4ff;")  # Dark theme cyan
        left_layout.addWidget(single_title)

        single_desc = QLabel("Transcribe one audio or video file")
        single_desc.setFont(QFont("Segoe UI", 10))
        single_desc.setStyleSheet("color: #b0b0b0;")  # Light gray for descriptions
        left_layout.addWidget(single_desc)

        self.label = QLabel("No file selected")
        self.label.setFont(QFont("Segoe UI", 11))
        self.label.setStyleSheet("background-color: #2d2d2d; color: #ffffff; padding: 8px; border-radius: 4px; border: 1px solid #444;")
        left_layout.addWidget(self.label)

        self.btn_browse = QPushButton("📁 Browse File")
        self.btn_browse.setFont(QFont("Segoe UI", 11))
        self.btn_browse.setStyleSheet("background-color: #0088cc; color: white; border-radius: 6px; padding: 10px; font-weight: bold; border: none;")
        self.btn_browse.clicked.connect(self.browse_file)
        left_layout.addWidget(self.btn_browse)

        self.btn_transcribe = QPushButton("▶ Transcribe")
        self.btn_transcribe.setFont(QFont("Segoe UI", 11))
        self.btn_transcribe.setStyleSheet("background-color: #7c3aed; color: white; border-radius: 6px; padding: 10px; font-weight: bold; border: none;")
        self.btn_transcribe.clicked.connect(self.transcribe_audio)
        left_layout.addWidget(self.btn_transcribe)

        self.btn_save = QPushButton("💾 Save to Text File")
        self.btn_save.setFont(QFont("Segoe UI", 11))
        self.btn_save.setStyleSheet("background-color: #059669; color: white; border-radius: 6px; padding: 10px; font-weight: bold; border: none;")
        self.btn_save.clicked.connect(self.save_transcription)
        left_layout.addWidget(self.btn_save)

        left_layout.addStretch()

        # ===== RIGHT COLUMN: BATCH TRANSCRIPTION =====
        right_layout = QVBoxLayout()

        batch_title = QLabel("Batch Transcription")
        batch_title.setFont(QFont("Segoe UI", 13, QFont.Bold))
        batch_title.setStyleSheet("color: #ff6b6b;")  # Red for batch in dark theme
        right_layout.addWidget(batch_title)

        batch_desc = QLabel("Transcribe multiple audio or video files at once")
        batch_desc.setFont(QFont("Segoe UI", 10))
        batch_desc.setStyleSheet("color: #b0b0b0;")
        right_layout.addWidget(batch_desc)

        self.batch_label = QLabel("No folder selected")
        self.batch_label.setFont(QFont("Segoe UI", 11))
        self.batch_label.setStyleSheet("background-color: #2d2d2d; color: #ffffff; padding: 8px; border-radius: 4px; border: 1px solid #444;")
        right_layout.addWidget(self.batch_label)

        self.btn_batch_folder = QPushButton("📂 Select Folder with Files")
        self.btn_batch_folder.setFont(QFont("Segoe UI", 11))
        self.btn_batch_folder.setStyleSheet("background-color: #d97706; color: white; border-radius: 6px; padding: 10px; font-weight: bold; border: none;")
        self.btn_batch_folder.clicked.connect(self.browse_batch_folder)
        right_layout.addWidget(self.btn_batch_folder)

        self.btn_batch_transcribe = QPushButton("▶ Start Batch")
        self.btn_batch_transcribe.setFont(QFont("Segoe UI", 11))
        self.btn_batch_transcribe.setStyleSheet("background-color: #dc2626; color: white; border-radius: 6px; padding: 10px; font-weight: bold; border: none;")
        self.btn_batch_transcribe.clicked.connect(self.batch_transcribe)
        self.btn_batch_transcribe.setEnabled(False)
        right_layout.addWidget(self.btn_batch_transcribe)

        right_layout.addStretch()

        # Add both columns to the main layout
        columns_layout.addLayout(left_layout)
        columns_layout.addLayout(right_layout)
        main_layout.addLayout(columns_layout)

        # Time estimate label (replaces progress bar)
        self.time_label = QLabel("")
        self.time_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.time_label.setStyleSheet("color: #00d4ff; padding: 8px;")
        self.time_label.setVisible(False)
        main_layout.addWidget(self.time_label)

        # Output text area
        output_label = QLabel("Transcription Output:")
        output_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        output_label.setStyleSheet("color: #ffffff;")
        main_layout.addWidget(output_label)

        self.text_output = QTextEdit()
        self.text_output.setFont(QFont("Segoe UI", 11))
        self.text_output.setStyleSheet("background-color: #2d2d2d; color: #ffffff; border-radius: 6px; border: 1px solid #444;")
        self.text_output.setPlaceholderText("Transcription results will appear here...")
        self.text_output.setMinimumHeight(150)
        main_layout.addWidget(self.text_output)

        self.setLayout(main_layout)

    def browse_file(self):
        """Open file dialog to select an audio or video file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio/Video File", "", 
            "Audio/Video Files (*.mp3 *.wav *.m4a *.flac *.ogg *.mp4)"
        )
        if file_path:
            self.audio_path = file_path
            self.label.setText(f"✓ {os.path.basename(file_path)}")

    def transcribe_audio(self):
        """Start transcribing the selected audio file."""
        if not self.audio_path:
            QMessageBox.warning(self, "No File", "Please select an audio or video file first.")
            return
        
        language_code = self.language_combo.currentData()
        self.label.setText("⏳ Transcribing...")
        self.time_label.setVisible(True)
        self.text_output.clear()
        self.btn_transcribe.setEnabled(False)
        
        # Start the timer for countdown
        self.start_time = time.time()
        self.timer.start(1000)  # Update every 1 second

        # Start thread
        self.transcribe_thread = TranscribeThread(self.model, self.audio_path, language_code)
        self.transcribe_thread.finished.connect(self.on_transcription_finished)
        self.transcribe_thread.error.connect(self.on_transcription_error)
        self.transcribe_thread.time_estimate.connect(self.on_time_estimate)
        self.transcribe_thread.start()

    def on_transcription_finished(self, text):
        """Handle successful transcription completion."""
        self.timer.stop()
        self.text_output.setPlainText(text)
        try:
            name = os.path.basename(self.audio_path) if self.audio_path else ""
        except Exception:
            name = ""
        self.label.setText(f"✓ {name}")
        self.time_label.setVisible(False)
        self.btn_transcribe.setEnabled(True)

    def on_transcription_error(self, error_msg):
        """Handle transcription error."""
        self.timer.stop()
        self.time_label.setVisible(False)
        
        QMessageBox.critical(self, "Error", f"Failed to transcribe: {error_msg}")
        self.label.setText("No file selected")
        self.btn_transcribe.setEnabled(True)
    
    def on_time_estimate(self, estimated_seconds):
        """Handle time estimate from transcription thread."""
        self.remaining_time = estimated_seconds
        self.display_time = estimated_seconds
        self.update_countdown()
    
    def update_countdown(self):
        """Update the countdown display every second."""
        if self.start_time is None:
            return
        
        elapsed = time.time() - self.start_time
        remaining = self.remaining_time - elapsed
        
        # Auto-extend if countdown reaches zero but still processing
        if remaining <= 0:
            self.remaining_time += self.display_time
            remaining = self.remaining_time - elapsed
        
        # Format time as MM:SS
        minutes = int(remaining) // 60
        seconds = int(remaining) % 60
        
        self.time_label.setText(f"⏱️ Est. Time: {minutes}:{seconds:02d}")

    def browse_batch_folder(self):
        """Open folder dialog to select a folder with MP4 files."""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder with MP4 Files")
        if folder_path:
            self.batch_folder = folder_path
            mp4_count = len([f for f in os.listdir(folder_path) if f.lower().endswith('.mp4')])
            self.batch_label.setText(f"✓ {mp4_count} file(s) found")
            self.btn_batch_transcribe.setEnabled(True)
    
    def batch_transcribe(self):
        """Start batch transcription of all MP4 files in the selected folder."""
        if not self.batch_folder:
            QMessageBox.warning(self, "No Folder", "Please select a folder first.")
            return
        
        # Ask user where to save the transcriptions
        output_folder = QFileDialog.getExistingDirectory(self, "Select Output Folder for Transcriptions")
        if not output_folder:
            return
        
        language_code = self.language_combo.currentData()
        
        # Disable buttons during batch processing
        self.btn_batch_transcribe.setEnabled(False)
        self.btn_transcribe.setEnabled(False)
        self.btn_batch_folder.setEnabled(False)
        self.btn_browse.setEnabled(False)
        
        # Clear output and show time estimate
        self.text_output.clear()
        self.time_label.setVisible(True)
        
        # Start the timer for countdown
        self.start_time = time.time()
        self.timer.start(1000)  # Update every 1 second
        
        # Start batch processing thread
        self.transcribe_thread = BatchTranscribeThread(self.model, self.batch_folder, language_code, output_folder)
        self.transcribe_thread.finished.connect(self.on_batch_finished)
        self.transcribe_thread.error.connect(self.on_batch_error)
        self.transcribe_thread.file_progress.connect(self.on_batch_progress)
        self.transcribe_thread.time_estimate.connect(self.on_time_estimate)
        self.transcribe_thread.file_completed.connect(self.on_file_completed)
        self.transcribe_thread.start()
    
    def on_batch_progress(self, current, total, filename):
        """Update progress during batch processing."""
        self.batch_label.setText(f"Processing {current}/{total}: {filename}")
    
    def on_file_completed(self, filename, transcription):
        """Called when a file is completed."""
        self.text_output.append(f"✓ {filename}\n")
        self.text_output.append(f"{transcription[:100]}...\n\n")  # Show first 100 chars
    
    def on_batch_finished(self):
        """Called when batch processing is complete."""
        self.timer.stop()
        self.batch_label.setText("✓ Batch completed!")
        self.time_label.setVisible(False)
        
        # Re-enable buttons
        self.btn_batch_transcribe.setEnabled(True)
        self.btn_transcribe.setEnabled(True)
        self.btn_batch_folder.setEnabled(True)
        self.btn_browse.setEnabled(True)
        
        QMessageBox.information(self, "Complete", "All files have been transcribed successfully!")
    
    def on_batch_error(self, error_msg):
        """Called when batch processing encounters an error."""
        self.timer.stop()
        self.time_label.setVisible(False)
        
        QMessageBox.critical(self, "Batch Error", f"Batch processing failed: {error_msg}")
        self.batch_label.setText("Error during batch processing")
        
        # Re-enable buttons
        self.btn_batch_transcribe.setEnabled(True)
        self.btn_transcribe.setEnabled(True)
        self.btn_batch_folder.setEnabled(True)
        self.btn_browse.setEnabled(True)

    def save_transcription(self):
        """Save the transcription to a text file."""
        text = self.text_output.toPlainText()
        if not text:
            QMessageBox.warning(self, "No Transcription", "No transcription to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Transcription", "transcription.txt", "Text Files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(self, "Saved", f"Transcription saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save: {e}")
