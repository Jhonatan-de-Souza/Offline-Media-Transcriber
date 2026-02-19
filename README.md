# Offline Media Transcriber

Convert any audio or video file to text with ease. This desktop application uses **Whisper AI** for fast, accurate transcription—completely local and private.

## Features

- 🎵 **Transcribe Audio** — MP3, WAV, M4A, FLAC, OGG formats
- 🎬 **Extract Audio from Video** — MP4, MKV, and more
- ⚡ **GPU Acceleration** — NVIDIA CUDA support for faster processing
- 🕐 **Smart Time Estimation** — Predicts transcription time based on your GPU/CPU
- 🌙 **Dark Theme UI** — Modern, eye-friendly interface
- 📁 **Batch Processing** — Transcribe multiple files at once
- 🔒 **100% Private & Free** — No cloud uploads, all processing runs locally
- ⚙️ **Animated Loading Screen** — Live status updates while models load

## Requirements

- **Python 3.12+**
- **FFmpeg** (for video/audio processing)
- **Windows 64-bit OS**
- **NVIDIA GPU** (optional, for faster transcription)

## Quick Start

### 1. Clone the Repository
````bash
git clone https://github.com/Jhonatan-de-Souza/AudioTranscriber.git
cd AudioTranscriber
````

### 2. Create Virtual Environment (Recommended)
````bash
python -m venv .venv
.venv\Scripts\activate
````

### 3. Install Dependencies
````bash
pip install -r requirements.txt
````

### 4. GPU Setup (Windows with NVIDIA GPU)
````powershell
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
````

### 5. Run the Application
````bash
python main.py
````

On startup, you'll see an animated loading screen while the Whisper model loads (10-15 seconds). Once ready, the main window opens.

## Verify GPU Support

Check if GPU acceleration is available:
````bash
python -c "import torch; print('GPU Available:', torch.cuda.is_available(), '| CUDA Version:', torch.version.cuda)"
````

## How It Works

1. **Select a file** — Audio or video format
2. **Choose language** — Supports 12+ languages
3. **Start transcription** — See smart time estimate countdown
4. **Save results** — Export transcription as .txt file

### Batch Processing
- Select a folder with multiple MP4 files
- Choose output folder for transcriptions
- App processes them sequentially with time estimates

## Privacy

✓ All transcription runs **locally on your machine**  
✓ No data sent to the cloud  
✓ Your audio/video files never leave your PC  
✓ Works completely offline (after model loads)

## Project Structure

````
AudioTranscriber/
├── main.py                    # Entry point (torch imported first for Windows)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── .gitignore                 # Git ignore rules
├── audio-to-text.ico         # Application icon
└── modules/
    ├── __init__.py           # Package exports
    ├── splash.py             # Animated loading screen with braille spinner
    ├── ui.py                 # PyQt5 GUI with dark theme
    ├── transcriber.py        # Whisper transcription logic + threading
    └── audio_processor.py    # Audio processing & GPU detection utilities
````

## Architecture & Best Practices

### Modular Design
- **Separation of Concerns**: Each module handles one responsibility
  - `splash.py` — UI/Loading animation
  - `ui.py` — Main application interface
  - `transcriber.py` — Transcription logic & threading
  - `audio_processor.py` — Audio utilities & GPU detection

### Threading
- Long-running tasks (model loading, transcription) run on separate threads
- UI remains responsive during processing
- Signals/slots pattern for thread-safe communication

### Smart Time Estimation
- Analyzes file duration + available GPU memory
- Adaptive multipliers for different GPU tiers:
  - 16GB+ GPU: 40% of file duration
  - 8GB GPU: 80% of file duration
  - 4GB GPU: 120% of file duration
  - CPU only: 200% of file duration
- Auto-extends countdown if transcription takes longer

### Error Handling
- Graceful fallbacks (CPU if GPU fails)
- User-friendly error messages
- Cleanup of temporary files

### UI/UX
- Dark theme for reduced eye strain
- Animated loading screen (not frozen)
- Centered windows
- Real-time countdown instead of progress bar
- Status updates during processing

## Tech Stack

| Component | Technology |
|-----------|-----------|
| **GUI Framework** | PyQt5 |
| **Speech Recognition** | OpenAI Whisper |
| **Deep Learning** | PyTorch |
| **Audio Processing** | pydub, FFmpeg |
| **Language** | Python 3.12 |
| **OS** | Windows 64-bit |

## License

MIT
