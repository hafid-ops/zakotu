#!/bin/bash
# ZAKOTU Linux Setup Script

set -e

echo "🚀 Setting up ZAKOTU for Linux..."
echo

# Check if Python 3.10+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.10"

if (( $(echo "$python_version < $required_version" | bc -l) )); then
    echo "❌ Python 3.10+ is required. Current version: $python_version"
    echo "Please install Python 3.10 or later and try again."
    exit 1
fi

echo "✅ Python version $python_version found"

# Function to install system dependencies based on distribution
install_system_deps() {
    if command -v apt-get >/dev/null 2>&1; then
        # Ubuntu/Debian
        echo "📦 Installing system dependencies (Ubuntu/Debian)..."
        sudo apt-get update
        sudo apt-get install -y \
            ffmpeg \
            imagemagick \
            libsndfile1 \
            espeak-ng \
            espeak-ng-data \
            libespeak-ng1 \
            fonts-liberation \
            fonts-dejavu-core \
            libnss3 \
            libnspr4 \
            libatk1.0-0 \
            libatk-bridge2.0-0 \
            libcups2 \
            libatspi2.0-0 \
            libxcomposite1 \
            libxdamage1 \
            libxrandr2 \
            libxss1 \
            libgtk-3-0 \
            libgbm-dev \
            wget \
            curl \
            ca-certificates \
            git \
            build-essential \
            python3-venv \
            python3-pip \
            bc
    elif command -v yum >/dev/null 2>&1; then
        # RHEL/CentOS/Fedora
        echo "📦 Installing system dependencies (RHEL/CentOS/Fedora)..."
        sudo yum install -y \
            ffmpeg \
            ImageMagick \
            libsndfile \
            espeak-ng \
            liberation-fonts \
            dejavu-fonts-common \
            nss \
            nspr \
            atk \
            at-spi2-atk \
            cups-libs \
            at-spi2-core \
            libXcomposite \
            libXdamage \
            libXrandr \
            libXss \
            gtk3 \
            wget \
            curl \
            ca-certificates \
            git \
            gcc \
            gcc-c++ \
            make \
            python3-venv \
            python3-pip \
            bc
    elif command -v pacman >/dev/null 2>&1; then
        # Arch Linux
        echo "📦 Installing system dependencies (Arch Linux)..."
        sudo pacman -S --noconfirm \
            ffmpeg \
            imagemagick \
            libsndfile \
            espeak-ng \
            ttf-liberation \
            ttf-dejavu \
            nss \
            nspr \
            atk \
            at-spi2-atk \
            libcups \
            at-spi2-core \
            libxcomposite \
            libxdamage \
            libxrandr \
            libxss \
            gtk3 \
            wget \
            curl \
            ca-certificates \
            git \
            base-devel \
            python \
            python-pip \
            bc
    else
        echo "⚠️  Could not detect package manager. Please install the following manually:"
        echo "   - FFmpeg"
        echo "   - ImageMagick"
        echo "   - libsndfile"
        echo "   - espeak-ng"
        echo "   - Python 3.10+"
        echo "   - Git"
        echo "   - Build tools (gcc, make)"
        echo
        read -p "Press Enter to continue after installing dependencies..."
    fi
}

# Install system dependencies
install_system_deps

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python dependencies..."

# Install numpy first (compatibility)
pip install "numpy<2.0"

# Install core dependencies
pip install python-dotenv requests tqdm

# Install audio/video processing
pip install soundfile vosk pysbd
pip install ffmpeg-python

# Install image processing
pip install "Pillow>=9.5.0,<10.0"

# Install ML/AI dependencies
pip install torch==2.0.1 torchaudio==2.0.2 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu
pip install onnxruntime==1.20.1
pip install kokoro_onnx==0.4.9

# Install video processing
pip install moviepy==1.0.3

# Install AI/generation dependencies
pip install transformers==4.33.3
pip install diffusers==0.23.0
pip install google-generativeai==0.6.0

# Install web automation
pip install playwright==1.42.0

# Install utilities
pip install pydantic==2.5.2
pip install "setuptools<81"

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install --with-deps chromium

# Fix ImageMagick policy for PDF/video processing
echo "🎨 Configuring ImageMagick..."
if [ -f "/etc/ImageMagick-6/policy.xml" ]; then
    sudo cp /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.backup
    sudo tee /etc/ImageMagick-6/policy.xml > /dev/null <<EOF
<policymap>
  <policy domain="resource" name="memory" value="256MiB"/>
  <policy domain="resource" name="disk" value="1GiB"/>
  <policy domain="resource" name="time" value="120"/>
  <policy domain="coder" rights="read|write" pattern="PDF" />
  <policy domain="coder" rights="read|write" pattern="LABEL" />
  <policy domain="path" rights="read|write" pattern="@*" />
</policymap>
EOF
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/models data/temp data/audio
mkdir -p generatedVoice generatedVideo 
mkdir -p output/generatedStory output/generatedImage output/generatedThumbnail
mkdir -p output/generatedVideo output/generatedVoice logs

# Download required models
echo "⬇️  Downloading AI models..."
python3 x.py

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file template..."
    cat > .env << EOF
# ZAKOTU Environment Configuration

# Required: Google Gemini API key - Get from https://aistudio.google.com/app/apikey
GEMINI_API_KEY="your_gemini_api_key_here"

# Optional: Telegram notification settings (if enabled in the code)
# TELEGRAM_BOT_TOKEN=your_telegram_bot_token
# TELEGRAM_CHAT_ID=your_telegram_chat_id
EOF
    echo "⚠️  Please edit .env file and add your Gemini API key!"
fi

# Create default prompt if it doesn't exist
if [ ! -f "config/prompt.txt" ]; then
    echo "📝 Creating default prompt file..."
    mkdir -p config
    echo "Write a captivating 3-sentence horror story that is both unsettling and memorable." > config/prompt.txt
fi

echo
echo "🎉 Setup complete!"
echo
echo "Next steps:"
echo "1. Edit .env file and add your Gemini API key"
echo "2. Optionally edit config/prompt.txt with your story prompt"
echo "3. Run the application:"
echo "   source venv/bin/activate  # Activate virtual environment"
echo "   python src/main.py       # Generate full video"
echo "   # OR"
echo "   python src/gen_short.py  # Generate short video"
echo
echo "🐳 For Docker usage:"
echo "   docker-compose up --build"
echo
