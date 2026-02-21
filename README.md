# Audio Transcriber

Convert any audio or video file to text—completely offline and private. Choose between CPU-optimized (recommended) or GPU-accelerated depending on your hardware.

![CPU-Based Transcriber](./CPU%20Based%20Audio%20Transcriber//assets/cpu_audio_transcriber.png)

## Why Audio Transcriber?

✅ **Works offline** — No cloud uploads, no account needed  
✅ **Fast and accurate** — Powered by advanced AI models  
✅ **Free and open** — No subscriptions or usage limits  
✅ **Cross-platform** — Windows, macOS, and Linux supported  
✅ **Choose your tool** — CPU-based is significantly faster for single files; GPU-based better for batch processing  

---

## ⚡ Quick Comparison

| Feature | CPU-Based | GPU-Based |
|---------|-----------|-----------|
| **Best for** | Single files, laptops | Batch processing |
| **Engine** | Parakeet V3 (ONNX) | Whisper AI (PyTorch) |
| **Speed** | 13.8x real-time | 2.91x real-time |
| **Setup** | Simple | Requires CUDA setup |
| **GPU needed** | No | Yes (NVIDIA) |
| **Model size** | ~671MB | ~1GB |

**Test Results (1:14 min, 1MB audio file):**
- CPU: **5.36 seconds** (13.8x real-time, 0.07 RTF)
- GPU: **25.45 seconds** (2.91x real-time, 0.34 RTF)
- **CPU is 4.75x faster for single files**

**→ Recommended: Start with CPU-based for single transcriptions. Use GPU for batch processing 50+ files.**

---

## 🚀 CPU-Based Transcriber (Recommended)

This is the easiest option. It works on any computer without requiring a GPU.

### Installation

**Step 1: Navigate to the CPU folder**

```bash
cd "CPU Based Audio Transcriber"
```

**Step 2: Create a virtual environment**

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

Windows (Command Prompt):

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4 (Optional): Install FFmpeg for video support**

macOS:

```bash
brew install ffmpeg
```

Ubuntu / Debian:

```bash
sudo apt-get install ffmpeg
```

Windows:

```bash
choco install ffmpeg
```

### Quick Start

Launch the app:

```bash
python app.py
```

**On first run:**
1. **Download splash screen** — App automatically downloads AI models from Hugging Face (~671MB)
2. **Progress indicator** — Shows download status
3. **Main window** — Ready to transcribe

**Subsequent runs:**
1. **No splash screen** — Models are cached locally, app starts instantly
2. **Loading screen** — App loads the model into memory
3. **Main window** — Ready to transcribe

Then:
1. Click **Browse** and select an audio or video file
2. Click **Transcribe**
3. Watch the countdown timer
4. Results appear automatically

### Supported File Types

**Audio:** MP3, WAV, M4A, FLAC, OGG, AIFF, AU, and more  
**Video:** MP4, MKV, AVI, MOV, WEBM, FLV, WMV, etc. (auto-converted)

### How It Works

- **Smart time estimation** — App measures your CPU performance on startup
- **Accurate countdown** — Timer shows real remaining time, not guesses
- **Responsive UI** — Never freezes; cancel anytime
- **No language selection** — Model auto-detects what you're speaking

### What Happens Behind the Scenes

```
1. Select file
  ↓
2. App measures CPU speed (5-second benchmark)
  ↓
3. Calculate: estimated_time = file_duration × your_cpu_speed
  ↓
4. Transcribe with accurate countdown
  ↓
5. Show results
```

### Project Files

```
CPU Based Audio Transcriber/
├── app.py                      # Main interface (start here)
├── config.py                   # Model auto-download configuration
├── download_splash.py          # Download progress splash screen
├── model_manager.py            # Parakeet V3 model loader
├── transcription_service.py    # Transcription engine
├── performance_profiler.py     # CPU benchmarking
├── video_converter.py          # Video-to-audio conversion
├── audio_handler.py            # Audio file loading
├── requirements.txt            # Dependencies list
│
├── models/                     # ONNX model files (auto-downloaded on first run)
│   ├── encoder.int8.onnx
│   ├── decoder.int8.onnx
│   ├── joiner.int8.onnx
│   └── tokens.txt
```

**Note:** Model files are automatically downloaded from Hugging Face on first run (~671MB). Subsequent runs use the cached models.
│
└── assets/                     # UI resources
```

### System Requirements

- **Python:** 3.14+
- **RAM:** 2GB minimum (4GB recommended)
- **Disk:** 300MB for models
- **OS:** Windows, macOS (Intel/Apple Silicon), Linux

### Dependencies

- `sherpa-onnx>=1.9.0` — ONNX runtime for Parakeet V3
- `soundfile>=0.12.1` — Audio file reading
- `customtkinter>=5.0.0` — Modern graphical interface
- `numpy>=1.21.0` — Audio processing

---

## 🎮 GPU-Based Transcriber

Use this if you have an NVIDIA GPU for batch processing.

![GPU-Based Transcriber - Before](./GPU%20Based%20Audio%20Transcriber/modules/assets/before1.jpeg)
![GPU-Based Transcriber - After](./GPU%20Based%20Audio%20Transcriber/modules/assets/after2.jpeg)

### Installation

**Step 1: Navigate to the GPU folder**

```bash
cd "GPU Based Audio Transcriber"
```

**Step 2: Create a virtual environment**

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

**Step 4: Install PyTorch with CUDA support**

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

**Step 5: Verify GPU detection**

```bash
python -c "import torch; print('GPU available:', torch.cuda.is_available())"
```

If `True` appears, your GPU is ready. If `False`, see [GPU troubleshooting](#gpu-not-detected).

### Quick Start

```bash
python main.py
```

**On first run:**
1. **Download splash screen** — App automatically downloads Whisper AI model from Hugging Face (~1GB)
2. **Progress indicator** — Shows download status
3. **Splash screen** — Model loads into memory
4. **Main window** — Two columns for single/batch transcription

**Subsequent runs:**
1. **No download** — Models are cached, app loads model directly
2. **Splash screen** — Model loads into memory
3. **Main window** — Ready to transcribe

Choose **Single File Transcription** or **Batch Processing**:

**Single File:**
1. Click **Browse File**
2. Select language
3. Click **Transcribe**

**Batch Processing:**
1. Click **Select Folder**
2. Choose output folder
3. Click **Start Batch**

### Features

- 🌐 **Multi-language** — Supports multiple languages
- 📁 **Batch processing** — Transcribe entire folders automatically
- 💾 **Auto-save** — Results saved to text files
- ⏱️ **Real-time feedback** — Monitor transcription progress

### Dependencies

- `torch>=2.0.0` — PyTorch with CUDA support
- `openai-whisper>=20230314` — Whisper speech recognition
- `pydub>=0.25.0` — Audio handling
- `PyQt5>=5.0.0` — Professional interface

**Note:** AI models are automatically downloaded from Hugging Face on first run (~1GB). Subsequent runs use the cached models.

---

## 📖 Detailed Usage Guide

### CPU Version: Full Workflow

**Example: Transcribe a podcast episode**

```
1. Start app: python app.py

2. App benchmarks your CPU (watch progress):
  "⏳ Starting CPU benchmark..."
  "✓ CPU benchmark complete (RTF: 1.2x)"

3. Click "Browse" → Select "podcast.mp4"

4. Click "Transcribe"
  Status: "⏱️ 15.2s remaining"
  (countdown updates every 0.5 seconds)

5. Wait for transcription
  Status: "✓ Ready"

6. Results appear in text box
  (Select all + copy, or save to file)
```

### GPU Version: Batch Processing

**Example: Transcribe 10 MP4 files**

```
1. Start app: python main.py
  (Splash screen shows model loading progress)

2. Click "Select Folder with Files"
  → Choose folder with 10 MP4s

3. Shows "✓ 10 file(s) found"

4. Click "Start Batch"
  → Choose output folder

5. Watch real-time progress:
  "Processing 3/10: meeting-notes.mp4"
  "⏱️ Est. Time: 2:45"

6. Results saved:
  ✓ meeting-notes.txt
  ✓ Q1-summary.txt
  ...
```

---

## 🔧 Troubleshooting

### CPU Version

#### "Module not found: sherpa_onnx"

**Cause:** Dependencies not installed in virtual environment  
**Solution:**

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### "FFmpeg not found" (video files not working)

**Cause:** FFmpeg not installed on your system  
**Solution:**

macOS:

```bash
# Install Homebrew first if needed: https://brew.sh
brew install ffmpeg
```

Ubuntu / Debian:

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

Windows:

```bash
# Option 1: Using Chocolatey (requires admin)
choco install ffmpeg

# Option 2: Manual download
# 1. Visit https://ffmpeg.org/download.html
# 2. Download Windows build
# 3. Extract to C:\ffmpeg
# 4. Add C:\ffmpeg\bin to PATH
```

#### "Model files not found"

**Cause:** Models are missing or in wrong location  
**Solution:**

```bash
# Check if models exist
ls models/

# Should show:
# encoder.int8.onnx
# decoder.int8.onnx
# joiner.int8.onnx
# tokens.txt

# If missing, you may need to re-clone the repository
```

#### Countdown timer seems wrong

**Cause:** CPU performance measurement may vary between runs  
**Solution:** Subsequent runs will provide better accuracy as the app learns your system performance.

### GPU Version

#### GPU not detected

**Cause:** Either no NVIDIA GPU, or CUDA not installed  
**Solution:**

```bash
# Check if you have an NVIDIA GPU
nvidia-smi

# If command not found, you need NVIDIA drivers
# Download from: https://www.nvidia.com/Download/driverDetails.aspx

# After installing drivers, reinstall PyTorch
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
```

#### "CUDA out of memory"

**Cause:** Your GPU doesn't have enough VRAM  
**Solution:** Switch to CPU-based version or reduce batch size

```bash
# Use CPU instead
cd ../CPU\ Based\ Audio\ Transcriber
python app.py
```

#### Model loading hangs

**Cause:** First download taking too long (Whisper model needs to download)  
**Solution:** Be patient. Check internet connection. It's a one-time download.

```bash
# Check if it's downloading (on Windows, check Task Manager)
# Check if it's downloading (on Mac, check Activity Monitor)
# Check if it's downloading (on Linux, run: watch -n 1 'du -sh ~/.cache/huggingface/hub/')
```

---

## ⚙️ Advanced Configuration

### CPU Version: Change Model Path

Edit `config.py`:

```python
MODEL_CONFIG = {
   "encoder_path": "./models/encoder.int8.onnx",  # ← Path to encoder
   "decoder_path": "./models/decoder.int8.onnx",
   "joiner_path": "./models/joiner.int8.onnx",
   "tokens_path": "./models/tokens.txt",
}
```

### Performance Analysis

**Real-World Test Results** (1:14 min podcast segment, 1MB file):

| Metric | CPU-Based | GPU-Based |
|--------|-----------|-----------|
| Transcription time | 5.36 sec | 25.45 sec |
| Real-Time Factor (RTF) | 0.07 | 0.34 |
| Speed multiplier | 13.8x real-time | 2.91x real-time |
| **Performance advantage** | **4.75x faster** | Better for batch jobs |

**Why CPU is faster for single files:**
- No GPU memory transfer overhead
- Lightweight ONNX runtime (vs PyTorch)
- Efficient CPU-optimized model
- Minimal initialization time

**GPU-Based advantages emerge when:**
- Processing 50+ files in batch
- Parallelizing multiple transcriptions
- Working with very long audio (>1 hour)

### Performance Tuning

**CPU Version:**
- Close other applications for 5-10% speed improvement
- System load affects transcription speed (watch Task Manager)
- Already optimized; no configuration needed

**GPU Version:**
- Best suited for batch processing multiple files
- Requires CUDA drivers and PyTorch setup
- GPU memory matters (8GB+ recommended)

---

## 🎯 Which Version Should I Choose?

**Choose CPU-Based if:** ← **Recommended for most users**
- ✅ You want the fastest single-file transcription (4.75x faster in tests)
- ✅ You want the simplest setup (no GPU required)
- ✅ You don't have an NVIDIA GPU
- ✅ You transcribe 1-50 files per session
- ✅ You're on a laptop or limited hardware

**Benchmark (1:14 min audio): CPU = 5.36s vs GPU = 25.45s**

**Choose GPU-Based if:**
- ✅ You transcribe 50+ files per session (batch processing)
- ✅ You have an NVIDIA GPU with 8GB+ VRAM
- ✅ You're willing to set up CUDA and PyTorch
- ✅ You process very long audio files (>1 hour consistently)

---

## Privacy & Security

✅ **100% Offline** — All processing happens on your computer  
✅ **No Cloud** — Audio never leaves your device  
✅ **No Account** — No login, email, or registration required  
✅ **No Tracking** — No analytics, no telemetry, no ads  
✅ **Open Source** — Inspect the code anytime  

---

## 📝 License

MIT — Free to use, modify, and distribute

---

## ❓ FAQ

**Q: Can I use this without internet?**  
A: Yes! After you run the app once (models download), you can work completely offline.

**Q: Is there a file size limit?**  
A: No. Very large files will just take longer to transcribe.

**Q: Does it work on Mac with Apple Silicon?**  
A: Yes, the CPU version works on Apple Silicon (M1/M2/M3).

**Q: Can I batch transcribe with CPU version?**  
A: Not in the UI, but you can run multiple instances.

**Q: Can I improve transcription accuracy?**  
A: Use clear audio and minimize background noise for best results.

---

## 🤝 Contributing

Found a bug? Want to improve something?

1. Check existing [GitHub issues](https://github.com/Jhonatan-de-Souza/AudioTranscriber/issues)
2. Create a new issue with clear description
3. Submit a pull request with improvements

---
