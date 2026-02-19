# AudioTranscriber

Convert audio and video files to text with ease. This tool uses **Whisper AI** for accurate transcription.

## Features

- 🎵 Transcribe audio files (MP3, WAV, etc.)
- 🎬 Extract audio from video files (MP4, MKV, etc.)
- ⚡ GPU acceleration support (NVIDIA CUDA on Windows)
- 🖥️ Simple desktop interface (PyQt5)
- 🔒 **100% Free & Local** — No cloud uploads, all processing runs on your PC

## Requirements

- **Python 3.12+**
- **FFmpeg** (for video processing)
- **Windows 64-bit OS**
- **NVIDIA GPU** (optional, for faster transcription)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Jhonatan-de-Souza/AudioTranscriber.git
   cd AudioTranscriber
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **GPU Setup (Windows with NVIDIA GPU)**
   ```powershell
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
   ```

4. **Run the app**
   ```bash
   python main.py
   ```

## Verify GPU Support (Windows)

```bash
python -c "import torch; print(torch.__version__, 'cuda:', torch.cuda.is_available(), 'cuda_version:', torch.version.cuda)"
```

## Privacy

All transcription runs **locally on your machine**. No data is sent to the cloud — your audio and video files never leave your PC.

## License

MIT