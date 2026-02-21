import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
from model_manager import ModelManager
from transcription_service import TranscriptionService
from video_converter import VideoConverter
from download_splash import DownloadSplash
from config import MODEL_CONFIG, download_models_if_needed

# Light Reddit-style theme
COLOR_BG = "#f6f7f8"           # Light background
COLOR_FG = "#1a1a1b"           # Dark text
COLOR_PRIMARY = "#0079d3"      # Reddit blue
COLOR_SUCCESS = "#27ae60"      # Green
COLOR_WARNING = "#f39c12"      # Orange
COLOR_DANGER = "#e74c3c"       # Red
COLOR_CARD = "#ffffff"         # White cards
COLOR_BORDER = "#ccc"          # Light gray border
COLOR_TEXT_LIGHT = "#818384"   # Light gray text

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class AudioTranscriberApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Window setup
        self.title("Fast Audio Transcriber")
        self.geometry("900x750")
        self.configure(fg_color=COLOR_BG)
        self._center_window()
        
        # Hide main window during model download
        self.withdraw()
        
        # Create and show splash screen for model download
        splash = DownloadSplash(self)
        
        # Download models if needed (must happen before ModelManager)
        success = download_models_if_needed(
            on_file_start=splash.update_file,
            on_progress=splash.set_progress,
            on_status=splash.update_status,
        )
        
        splash.close()
        
        if not success:
            messagebox.showerror(
                "Error", 
                "Could not download model files. Please check your internet connection.\n"
                "You can download them manually from:\n"
                "https://huggingface.co/csukuangfj/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
            )
            self.destroy()
            return
        
        # Show main window
        self.deiconify()
        
        # State
        self.audio_file: str | None = None
        self.is_transcribing = False
        
        # Services
        self.model_manager = ModelManager(**MODEL_CONFIG)
        self.transcription_service = TranscriptionService(self.model_manager)
        
        # UI Setup
        self._setup_ui()
        self._load_model_async()
    
    def _center_window(self) -> None:
        """Center window on screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _setup_ui(self) -> None:
        """Initialize UI components following separation of concerns."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._create_header(main_frame)
        
        # File selection section
        self._create_file_section(main_frame)
        
        # Output section
        self._create_output_section(main_frame)
        
        # Status bar
        self._create_status_bar(main_frame)
    
    def _create_header(self, parent: ctk.CTkFrame) -> None:
        """Create header with title."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            header_frame,
            text="🎤 Fast Audio Transcriber",
            font=("Helvetica", 28, "bold"),
            text_color=COLOR_PRIMARY
        )
        title.pack(side="left")
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Powered by Parakeet V3",
            font=("Helvetica", 12),
            text_color=COLOR_TEXT_LIGHT
        )
        subtitle.pack(side="left", padx=(10, 0))
    
    def _create_file_section(self, parent: ctk.CTkFrame) -> None:
        """Create file selection UI."""
        section_frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=10)
        section_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            section_frame,
            text="📁 Select Audio or Video File",
            font=("Helvetica", 12, "bold"),
            text_color=COLOR_PRIMARY
        ).pack(anchor="w", padx=15, pady=(15, 8))
        
        self.file_label = ctk.CTkLabel(
            section_frame,
            text="No file selected",
            font=("Helvetica", 10),
            text_color=COLOR_TEXT_LIGHT
        )
        self.file_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        button_frame = ctk.CTkFrame(section_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        self.select_btn = ctk.CTkButton(
            button_frame,
            text="Choose File",
            command=self.choose_file,
            fg_color=COLOR_PRIMARY,
            hover_color="#0056a8",
            text_color=COLOR_CARD,
            font=("Helvetica", 11, "bold"),
            height=35
        )
        self.select_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        self.transcribe_btn = ctk.CTkButton(
            button_frame,
            text="✨ Transcribe",
            command=self.start_transcription,
            fg_color=COLOR_SUCCESS,
            hover_color="#1f8c47",
            text_color=COLOR_CARD,
            font=("Helvetica", 11, "bold"),
            height=35
        )
        self.transcribe_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
        
        self.cancel_btn = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self.cancel_transcription,
            fg_color=COLOR_DANGER,
            hover_color="#c0392b",
            text_color=COLOR_CARD,
            font=("Helvetica", 11, "bold"),
            height=35,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", fill="x", expand=True)
    
    def _create_output_section(self, parent: ctk.CTkFrame) -> None:
        """Create transcription output UI."""
        output_frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=10)
        output_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Output header with status and timer
        header = ctk.CTkFrame(output_frame, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(15, 0))
        
        ctk.CTkLabel(
            header,
            text="📝 Transcription Result",
            font=("Helvetica", 13, "bold"),
            text_color=COLOR_PRIMARY
        ).pack(side="left")
        
        self.status_label = ctk.CTkLabel(
            header,
            text="",
            font=("Helvetica", 10),
            text_color=COLOR_WARNING
        )
        self.status_label.pack(side="right")
        
        # Output textbox
        self.output_text = ctk.CTkTextbox(
            output_frame,
            fg_color=COLOR_CARD,
            text_color=COLOR_FG,
            border_color=COLOR_BORDER,
            border_width=1,
            font=("Menlo", 11)
        )
        self.output_text.pack(fill="both", expand=True, padx=15, pady=15)
        self.output_text.insert("0.0", "Transcription results will appear here...\n")
    
    def _create_status_bar(self, parent: ctk.CTkFrame) -> None:
        """Create status bar at bottom."""
        status_frame = ctk.CTkFrame(parent, fg_color=COLOR_CARD, corner_radius=8)
        status_frame.pack(fill="x")
        
        ctk.CTkLabel(
            status_frame,
            text="Status:",
            font=("Helvetica", 10, "bold"),
            text_color=COLOR_PRIMARY
        ).pack(side="left", padx=12, pady=10)
        
        self.app_status = ctk.CTkLabel(
            status_frame,
            text="Loading model...",
            font=("Helvetica", 10),
            text_color=COLOR_SUCCESS
        )
        self.app_status.pack(side="left", padx=(0, 12), pady=10)
    
    def _load_model_async(self) -> None:
        """Load model in background."""
        import threading
        self.app_status.configure(text="Loading model...", text_color=COLOR_WARNING)
        threading.Thread(target=self._load_model, daemon=True).start()
    
    def _load_model(self) -> None:
        """Load model and profile CPU-only performance."""
        if self.model_manager.load():
            self.app_status.configure(text="Benchmarking CPU...", text_color=COLOR_WARNING)
            self.update()
            
            # Profile CPU performance (Parakeet V3 uses CPU only)
            self.transcription_service.profiler.profile()
            
            self.app_status.configure(text="Ready", text_color=COLOR_SUCCESS)
        else:
            messagebox.showerror("Error", "Failed to load model")
            self.app_status.configure(text="Error loading model", text_color=COLOR_DANGER)
    
    def choose_file(self) -> None:
        """Handle file selection."""
        supported_formats = (
            ("Audio & Video Files", "*.wav *.mp3 *.ogg *.flac *.mp4 *.avi *.mov *.mkv"),
            ("Audio Files", "*.wav *.mp3 *.ogg *.flac"),
            ("Video Files", "*.mp4 *.avi *.mov *.mkv *.webm *.flv *.wmv"),
            ("All Files", "*.*"),
        )
        
        file_path = filedialog.askopenfilename(filetypes=supported_formats)
        if file_path:
            self.audio_file = file_path
            filename = Path(file_path).name
            self.file_label.configure(text=f"Selected: {filename}")
            self.output_text.delete("0.0", "end")
            self.output_text.insert("0.0", "")
            self.status_label.configure(text="")
    
    def start_transcription(self) -> None:
        """Start transcription process."""
        if not self.audio_file:
            messagebox.showwarning("Warning", "Please select an audio or video file first.")
            return
        
        if not self.model_manager.model:
            messagebox.showwarning("Warning", "Model is not loaded yet.")
            return
        
        if self.is_transcribing:
            messagebox.showinfo("Info", "Transcription is already running.")
            return
        
        self.is_transcribing = True
        self._update_ui_for_transcription(True)
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", "Transcribing...\n")
        
        self.transcription_service.transcribe_async(
            self.audio_file,
            on_progress=self._on_transcription_progress,
            on_complete=self._on_transcription_complete,
            on_error=self._on_transcription_error,
        )
        
        self._update_timer()
    
    def _on_transcription_progress(self, elapsed: float, total: float) -> None:
        """Update progress during transcription."""
        if total > 0:
            remaining = total - elapsed
            self.status_label.configure(
                text=f"⏱️ {remaining:.1f}s remaining"
            )
    
    def _on_transcription_complete(self, result: str) -> None:
        """Handle completed transcription."""
        self.output_text.delete("0.0", "end")
        self.output_text.insert("0.0", result)
        self.status_label.configure(text="✓ Complete", text_color=COLOR_SUCCESS)
        self.app_status.configure(text="Transcription complete", text_color=COLOR_SUCCESS)
        self._finish_transcription()
    
    def _on_transcription_error(self, error: str) -> None:
        """Handle transcription error."""
        messagebox.showerror("Transcription Error", error)
        self.status_label.configure(text="✗ Error", text_color=COLOR_DANGER)
        self.app_status.configure(text="Transcription failed", text_color=COLOR_DANGER)
        self._finish_transcription()
    
    def cancel_transcription(self) -> None:
        """Cancel ongoing transcription."""
        self.transcription_service.cancel()
        self._finish_transcription()
        self.app_status.configure(text="Transcription cancelled", text_color=COLOR_WARNING)
    
    def _update_ui_for_transcription(self, is_running: bool) -> None:
        """Enable/disable buttons based on transcription state."""
        state = "disabled" if is_running else "normal"
        self.select_btn.configure(state=state)
        self.transcribe_btn.configure(state=state)
        self.cancel_btn.configure(state="normal" if is_running else "disabled")
    
    def _finish_transcription(self) -> None:
        """Cleanup after transcription."""
        self.is_transcribing = False
        self._update_ui_for_transcription(False)
    
    def _update_timer(self) -> None:
        """Update countdown timer."""
        if self.is_transcribing and self.transcription_service.is_running():
            elapsed, estimated_total = self.transcription_service.get_progress()
            
            if estimated_total > 0:
                remaining = max(0, estimated_total - elapsed)
                self.status_label.configure(
                    text=f"⏱️ {remaining:.1f}s remaining"
                )
            
            self.after(500, self._update_timer)
    
    def __del__(self) -> None:
        """Cleanup on exit."""
        try:
            self.transcription_service.cancel()
        except Exception:
            pass


if __name__ == "__main__":
    app = AudioTranscriberApp()
    app.mainloop()

