# 🎬 ZAKOTU: AI Video Story Generator

[![Docker Build](https://img.shields.io/badge/docker-supported-blue)](https://docker.com)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-green)](https://python.org)
[![Linux Compatible](https://img.shields.io/badge/linux-compatible-orange)](https://www.linux.org/)

**ZAKOTU** is an automated AI-powered video creation tool that generates creative stories using Google Gemini AI, converts them to natural speech with Kokoro TTS, and creates engaging videos with dynamic captions and thumbnails.

## ✨ Features

- 🤖 **AI Story Generation** - Creates original stories using Google Gemini AI
- 🗣️ **Voice Synthesis** - Converts text to natural-sounding speech using Kokoro TTS
- 🎥 **Video Creation** - Combines voice, background videos, music, and dynamic captions
- 🖼️ **Thumbnail Generation** - Creates social media-style thumbnails
- 🐳 **Docker Support** - Easy deployment in containerized environments
- 🐧 **Linux Optimized** - Full Linux compatibility with automated setup scripts
- 🔄 **Fallback System** - Works even when API quotas are exceeded

## 🚀 Quick Start with Docker (Recommended)

### Prerequisites
- [Docker](https://www.docker.com/products/docker-desktop/)
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Setup Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/zakotu.git
   cd zakotu
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.template .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Create or edit the story prompt:**
   ```bash
   # Edit config/prompt.txt with your story idea
   nano config/prompt.txt
   ```

4. **Build and run with Docker:**
   ```bash
   docker compose up --build
   ```

5. **Access the output:**
   - Generated content will be in the `output/` folder
   - Logs will be in the `logs/` folder

## 🖥️ Local Installation (Linux)

### Automated Setup (Ubuntu/Debian/RHEL/Arch)

```bash
# Make setup script executable
chmod +x setup_linux.sh

# Run automated installation
./setup_linux.sh

# Test the installation
chmod +x test_linux.sh
./test_linux.sh
```

### Manual Setup

1. **Install system dependencies:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install -y ffmpeg imagemagick libsndfile1 python3-pip python3-venv

   # RHEL/CentOS/Fedora
   sudo dnf install -y ffmpeg ImageMagick libsndfile-devel python3-pip python3-virtualenv

   # Arch Linux
   sudo pacman -S ffmpeg imagemagick libsndfile python-pip python-virtualenv
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements-linux.txt
   ```

4. **Install Playwright browsers:**
   ```bash
   playwright install --with-deps chromium
   ```

5. **Download required models:**
   ```bash
   python x.py
   ```

6. **Set up environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your API key
   ```

7. **Run the application:**
   ```bash
   python src/main.py
   ```

## 📁 Project Structure

```
zakotu/
├── src/                          # Main application code
│   ├── main.py                   # Main entry point
│   ├── story_generator.py        # Gemini AI story generation
│   ├── voice_generator.py        # Kokoro TTS integration  
│   ├── video_generator.py        # Video creation with captions
│   ├── thumbnail_generator.py    # Social media thumbnails
│   ├── gen_short.py             # Short-form video generator
│   └── utils/                    # Utility modules
├── config/                       # Configuration and prompts
├── data/                         # AI models and temporary data
├── output/                       # Generated content
├── assets/                       # Stock videos, music, fonts
├── docker-compose.yml           # Docker orchestration
├── Dockerfile                   # Container configuration
├── requirements.txt             # Python dependencies
├── setup_linux.sh              # Linux installation script
└── .env.template               # Environment variables template
```

## 🔧 Configuration

### Environment Variables
Copy `.env.template` to `.env` and configure:

```env
# Required: Google Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Telegram notifications  
# TELEGRAM_BOT_TOKEN=your_telegram_bot_token
# TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### Story Prompts
Edit `config/prompt.txt` to customize story generation:

```text
You are a professional scriptwriter for viral AI and tech short-form videos...
```

### Background Assets
Place your media files in:
- `assets/stock/videos/` - Background videos
- `assets/stock/music/` - Background music
- `assets/fonts/` - Custom fonts

## 🎯 Usage Workflow

1. **Configure** your story prompt in `config/prompt.txt`
2. **Set** your Gemini API key in `.env`
3. **Run** the application via Docker or locally
4. **Wait** for AI story generation and voice synthesis
5. **Collect** your generated video from `output/generatedVideo/`

## 🛠️ Technical Stack

- **AI:** Google Gemini API for story generation
- **TTS:** Kokoro ONNX for voice synthesis  
- **Video:** MoviePy, FFmpeg for video processing
- **Image:** Pillow, ImageMagick for graphics
- **Audio:** SoundFile, Vosk for audio processing
- **Web:** Playwright for thumbnail generation
- **Container:** Docker with Linux optimization

## 🐛 Troubleshooting

### Common Issues

**API Quota Exceeded:**
```
Error: 429 You exceeded your current quota
```
- **Solution:** Wait for quota reset or upgrade your Gemini API plan
- **Fallback:** The system automatically uses pre-written stories when quota is exceeded

**Docker Build Fails:**
```bash
# Clean rebuild
docker compose down
docker compose build --no-cache
docker compose up
```

**ImageMagick Errors:**
```bash
# Check ImageMagick installation
convert -version

# For Docker, ImageMagick is automatically configured
```

**Missing Models:**
```bash
# Re-download models
python x.py
```

**GPU Acceleration (Optional):**
- For NVIDIA GPUs: Install CUDA drivers and nvidia-docker2
- For CPU-only: Default configuration works out of the box

## 📊 Performance

- **Story Generation:** ~2-5 seconds (depends on Gemini API)
- **Voice Synthesis:** ~10-30 seconds (depends on text length)
- **Video Creation:** ~30-120 seconds (depends on content length and hardware)
- **Total Process:** ~1-3 minutes per video

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for sensitive data
- The included `.gitignore` protects sensitive files
- Regenerate exposed API keys immediately

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support

- 📧 **Issues:** [GitHub Issues](https://github.com/yourusername/zakotu/issues)
- 📖 **Documentation:** Check the `docs/` folder
- 💬 **Discussions:** [GitHub Discussions](https://github.com/yourusername/zakotu/discussions)

---

**Made with ❤️ for content creators and AI enthusiasts**
