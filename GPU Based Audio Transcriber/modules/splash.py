"""
Splash screen with loading animation for the Audio Transcriber application.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QDesktopWidget
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon


class SplashScreen(QWidget):
    """Animated splash screen shown during model loading."""
    
    # Braille animation frames for the loader
    SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧']
    
    def __init__(self):
        super().__init__()
        self.frame_index = 0
        self.init_ui()
        self.center_on_screen()
        
        # Setup animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(100)  # Update every 100ms
    
    def init_ui(self):
        """Initialize the splash screen UI."""
        self.setWindowTitle("Audio Transcriber")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #1e1e1e;")
        
        # Remove window frame for clean splash screen look
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Add stretcher at top
        layout.addStretch()
        
        # Title
        title = QLabel("Audio Transcriber")
        title.setFont(QFont("Segoe UI", 32, QFont.Bold))
        title.setStyleSheet("color: #00d4ff;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Loading spinner label
        self.spinner_label = QLabel()
        self.spinner_label.setFont(QFont("Segoe UI", 28))
        self.spinner_label.setStyleSheet("color: #ffffff;")
        self.spinner_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.spinner_label)
        
        # Loading text label
        self.text_label = QLabel("Loading audio transcription models")
        self.text_label.setFont(QFont("Segoe UI", 14))
        self.text_label.setStyleSheet("color: #b0b0b0;")
        self.text_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.text_label)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet("color: #808080;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # Add stretcher at bottom
        layout.addStretch()
        
        self.setLayout(layout)
    
    def center_on_screen(self):
        """Center the splash screen on the monitor."""
        screen = QDesktopWidget().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def update_animation(self):
        """Update the spinner animation frame."""
        frame = self.SPINNER_FRAMES[self.frame_index]
        self.spinner_label.setText(frame)
        self.frame_index = (self.frame_index + 1) % len(self.SPINNER_FRAMES)
    
    def set_status(self, status_text):
        """Update the status text."""
        self.status_label.setText(status_text)
    
    def stop_animation(self):
        """Stop the animation and remove the splash screen."""
        self.timer.stop()
        self.close()
