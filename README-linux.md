# ZAKOTU: AI Video Story Generator (Linux Edition)

This project automatically generates creative stories using Google Gemini AI, converts them to speech with the Kokoro voice model, and creates engaging videos with dynamic captions and visual elements. **Optimized for Linux environments.**

## Features

- **AI Story Generation**: Creates original stories using Google Gemini AI
- **Voice Synthesis**: Converts text to natural-sounding speech using Kokoro
- **Video Creation**: Combines voice, visuals, and dynamic captions
- **Thumbnail Generation**: Creates social media style thumbnails
- **Cross-Platform Support**: Runs on Linux, Docker, and Windows
- **Fallback Mechanisms**: Works even when API quotas are exceeded

## Quick Start (Linux)

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/zakotu-linux.git
cd zakotu-linux

# Make setup script executable and run it
chmod +x setup_linux.sh
./setup_linux.sh

# Edit your API key
nano .env  # Add your Gemini API key

# Run the application
source venv/bin/activate
python src/main.py
```

### Manual Linux Installation

#### Prerequisites

- **Python 3.10+**
- **System packages**: Install via package manager

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg imagemagick libsndfile1 espeak-ng \
    fonts-liberation python3-venv python3-pip build-essential \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libatspi2.0-0 libxcomposite1 libxdamage1 libxrandr2 libxss1 \
    libgtk-3-0 libgbm-dev wget curl ca-certificates git bc
```

**RHEL/CentOS/Fedora:**
```bash
sudo yum install -y ffmpeg ImageMagick libsndfile espeak-ng \
    liberation-fonts python3-venv python3-pip gcc gcc-c++ make \
    nss nspr atk at-spi2-atk cups-libs at-spi2-core \
    libXcomposite libXdamage libXrandr libXss gtk3 \
    wget curl ca-certificates git bc
```

**Arch Linux:**
```bash
sudo pacman -S --noconfirm ffmpeg imagemagick libsndfile espeak-ng \
    ttf-liberation python python-pip base-devel nss nspr atk \
    at-spi2-atk libcups at-spi2-core libxcomposite libxdamage \
    libxrandr libxss gtk3 wget curl ca-certificates git bc
```

#### Setup Steps

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements-linux.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install --with-deps chromium
   ```

4. **Configure ImageMagick (if needed):**
   ```bash
   # Fix ImageMagick policy for video generation
   sudo cp /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.backup
   sudo tee /etc/ImageMagick-6/policy.xml > /dev/null <<EOF
   <policymap>
     <policy domain="resource" name="memory" value="256MiB"/>
     <policy domain="resource" name="disk" value="1GiB"/>
     <policy domain="resource" name="time" value="120"/>
     <policy domain="coder" rights="read|write" pattern="PDF" />
     <policy domain="coder" rights="read|write" pattern="LABEL" />
   </policymap>
   EOF
   ```

5. **Download AI models:**
   ```bash
   python x.py
   ```

6. **Set up environment:**
   ```bash
   # Create .env file
   echo 'GEMINI_API_KEY="your_gemini_api_key_here"' > .env
   
   # Create story prompt
   mkdir -p config
   echo "Write a captivating 3-sentence horror story." > config/prompt.txt
   ```

7. **Run the application:**
   ```bash
   python src/main.py       # Full video generation
   python src/gen_short.py  # Short video generation
   ```

## Docker Setup (Cross-Platform)

### Quick Docker Start

```bash
# Create .env file with your API key
echo 'GEMINI_API_KEY="your_key_here"' > .env

# Run with Docker Compose
docker-compose up --build
```

### Manual Docker Commands

```bash
# Build the image
docker build -t zakotu-app .

# Run the container
docker run --rm \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/logs:/app/logs" \
  --env-file .env \
  zakotu-app
```

## Project Structure

```
zakotu-linux/
├── src/                    # Main application code
│   ├── main.py            # Main entry point (full videos)
│   ├── gen_short.py       # Short video generator
│   ├── story_generator.py # Gemini AI story generation
│   ├── voice_generator.py # Kokoro TTS
│   ├── video_generator.py # Video creation with captions
│   ├── image_generator.py # Image generation
│   └── utils/             # Utility functions
├── config/                # Configuration and prompts
├── data/                  # AI models and temp files
├── output/                # Generated content
├── logs/                  # Application logs
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Container definition
├── requirements-linux.txt # Linux-optimized dependencies
├── setup_linux.sh        # Automated Linux setup
└── README-linux.md        # This file
```

## Linux-Specific Optimizations

### System Integration
- **Native package manager support** (apt, yum, pacman)
- **Automatic ImageMagick detection** for video text overlays
- **Font handling** with Linux system fonts
- **GPU acceleration** support where available

### Performance Features
- **CPU-optimized** PyTorch and ONNX Runtime
- **Memory-efficient** processing for lower-end systems
- **Automatic fallback** mechanisms for missing dependencies

### File System Compatibility
- **Unix path handling** throughout the codebase
- **Proper permissions** for executable files
- **Symlink support** for shared model files

## Troubleshooting Linux Issues

### Common Problems

1. **ImageMagick Policy Errors:**
   ```bash
   # Run the policy fix from setup script
   sudo ./setup_linux.sh  # Will fix automatically
   # Or manually edit /etc/ImageMagick-6/policy.xml
   ```

2. **Missing System Libraries:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install -f
   
   # RHEL/CentOS
   sudo yum install missing-package-name
   ```

3. **Audio Issues (No Sound Output):**
   ```bash
   # Install PulseAudio/ALSA development packages
   sudo apt-get install libasound2-dev pulseaudio-dev  # Ubuntu
   sudo yum install alsa-lib-devel pulseaudio-libs-devel  # RHEL
   ```

4. **Playwright Browser Issues:**
   ```bash
   # Install browsers with system dependencies
   playwright install --with-deps chromium
   
   # If that fails, install manually:
   sudo apt-get install chromium-browser  # Ubuntu
   ```

5. **Permission Errors:**
   ```bash
   # Fix file permissions
   chmod +x setup_linux.sh
   chmod +x docker-entrypoint.sh
   
   # Fix data directory permissions
   chmod -R 755 data/ output/ logs/
   ```

### Performance Tuning

**For low-memory systems:**
```bash
# Set memory limits in .env
echo "PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512" >> .env
echo "OMP_NUM_THREADS=2" >> .env
```

**For high-performance systems:**
```bash
# Enable all CPU cores
echo "OMP_NUM_THREADS=$(nproc)" >> .env
```

## API Rate Limits & Fallbacks

The system includes intelligent fallback mechanisms:

- **Story Generation**: Falls back to pre-written stories when Gemini API quota is exceeded
- **Image Prompts**: Uses context-aware fallback prompts 
- **Error Recovery**: Continues processing even with partial failures

## Development

### Contributing
1. Fork the repository
2. Create a feature branch
3. Test on multiple Linux distributions
4. Submit a pull request

### Testing on Different Distributions
```bash
# Test with Docker on different base images
docker build -f Dockerfile.ubuntu -t zakotu-ubuntu .
docker build -f Dockerfile.alpine -t zakotu-alpine .
```

## License

MIT License - see LICENSE file for details.

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions  
- **Documentation**: Wiki pages

---

**Note**: This is the Linux-optimized version of ZAKOTU. For Windows-specific instructions, see the original README.md.
