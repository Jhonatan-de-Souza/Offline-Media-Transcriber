"""Splash screen for model downloading progress."""
import customtkinter as ctk
from tkinter import font as tkfont


class DownloadSplash(ctk.CTkToplevel):
    """Splash screen showing model download progress."""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Downloading Models")
        self.geometry("500x300")
        self.resizable(False, False)
        self.configure(fg_color="#f6f7f8")
        
        # Remove window decorations for cleaner look
        # self.attributes('-topmost', True)
        
        # Center on screen
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (250)
        y = (screen_height // 2) - (150)
        self.geometry(f"500x300+{x}+{y}")
        
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="#f6f7f8")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="🎤 Audio Transcriber",
            font=("Helvetica", 24, "bold"),
            text_color="#0079d3"
        )
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Downloading AI Models",
            font=("Helvetica", 14),
            text_color="#818384"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # File name label
        self.file_label = ctk.CTkLabel(
            main_frame,
            text="Initializing...",
            font=("Helvetica", 11),
            text_color="#1a1a1b"
        )
        self.file_label.pack(pady=(0, 10))
        
        # Progress bar
        self.progress = ctk.CTkProgressBar(main_frame, height=20)
        self.progress.set(0)
        self.progress.pack(fill="x", pady=(0, 15))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Please wait...",
            font=("Helvetica", 10),
            text_color="#818384"
        )
        self.status_label.pack(pady=(0, 10))
        
        # Info label
        info_label = ctk.CTkLabel(
            main_frame,
            text="(This only happens on first run)",
            font=("Helvetica", 9),
            text_color="#ccc"
        )
        info_label.pack()
        
        self.grab_set()
        self.transient(parent)
    
    def update_file(self, filename: str) -> None:
        """Update the current file being downloaded."""
        self.file_label.configure(text=f"📥 {filename}")
        self.update()
    
    def update_status(self, status: str) -> None:
        """Update the status message."""
        self.status_label.configure(text=status)
        self.update()
    
    def set_progress(self, value: float) -> None:
        """Set progress bar value (0.0 to 1.0)."""
        self.progress.set(value)
        self.update()
    
    def close(self) -> None:
        """Close the splash screen."""
        self.destroy()
