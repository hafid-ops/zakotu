#!/bin/bash
# ZAKOTU Google Cloud Shell Setup Script

set -e

echo "🌩️ Setting up ZAKOTU for Google Cloud Shell..."
echo

# Check if we're in Cloud Shell
if [[ "$DEVSHELL_PROJECT_ID" != "" ]]; then
    echo "✅ Google Cloud Shell environment detected"
    echo "Project ID: $DEVSHELL_PROJECT_ID"
else
    echo "⚠️  Not running in Google Cloud Shell, proceeding anyway..."
fi

# Cloud Shell already has Python 3.9+, ffmpeg, git, curl, wget
echo "✅ Using pre-installed Cloud Shell tools"

# Install additional packages needed for ZAKOTU
echo "📦 Installing additional system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    imagemagick \
    libsndfile1 \
    libsndfile1-dev \
    espeak-ng \
    espeak-ng-data \
    libespeak-ng1 \
    fonts-liberation \
    fonts-dejavu-core \
    bc

# Configure ImageMagick for Cloud Shell
echo "🎨 Configuring ImageMagick for Cloud Shell..."
if [ -f "/etc/ImageMagick-6/policy.xml" ]; then
    sudo cp /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.backup
    sudo tee /etc/ImageMagick-6/policy.xml > /dev/null <<EOF
<policymap>
  <policy domain="resource" name="memory" value="512MiB"/>
  <policy domain="resource" name="disk" value="2GiB"/>
  <policy domain="resource" name="time" value="120"/>
  <policy domain="coder" rights="read|write" pattern="PDF" />
  <policy domain="coder" rights="read|write" pattern="LABEL" />
  <policy domain="path" rights="read|write" pattern="@*" />
</policymap>
EOF
fi

# Create virtual environment (Cloud Shell recommended practice)
echo "🐍 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip --quiet

# Install Python dependencies optimized for Cloud Shell
echo "📚 Installing Python dependencies (optimized for Cloud Shell)..."

# Install core dependencies
pip install --quiet python-dotenv requests tqdm

# Install numpy with Cloud Shell optimization
pip install --quiet "numpy>=1.24.0,<2.0"

# Install audio/video processing
pip install --quiet soundfile vosk pysbd ffmpeg-python

# Install image processing
pip install --quiet "Pillow>=9.5.0,<10.0"

# Install video processing
pip install --quiet moviepy==1.0.3

# Install ML/AI dependencies (CPU versions for Cloud Shell)
echo "🤖 Installing AI/ML dependencies..."
pip install --quiet torch==2.0.1 torchaudio==2.0.2 torchvision==0.15.2 --index-url https://download.pytorch.org/whl/cpu
pip install --quiet onnxruntime>=1.15.0
pip install --quiet kokoro_onnx==0.4.9

# Install generation dependencies
pip install --quiet transformers==4.33.3 diffusers==0.23.0
pip install --quiet google-generativeai==0.6.0

# Install web automation
pip install --quiet "playwright>=1.40.0"

# Install utilities
pip install --quiet "pydantic>=2.0.0,<3.0.0"
pip install --quiet scikit-image

# Install Playwright browsers (optimized for Cloud Shell)
echo "🌐 Installing Playwright browsers..."
playwright install --with-deps chromium

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/models data/temp data/audio
mkdir -p generatedVoice generatedVideo 
mkdir -p output/generatedStory output/generatedImage/short output/generatedThumbnail
mkdir -p output/generatedVideo output/generatedVoice logs

# Download required models
echo "⬇️  Downloading AI models..."
python3 x.py

# Create .env file template if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file template..."
    cat > .env << EOF
# ZAKOTU Environment Configuration for Google Cloud Shell

# Required: Google Gemini API key - Get from https://aistudio.google.com/app/apikey
GEMINI_API_KEY="your_gemini_api_key_here"

# Cloud Shell specific optimizations
OMP_NUM_THREADS=2
MKL_NUM_THREADS=2
IMAGEMAGICK_BINARY=convert

# Optional: Telegram notification settings
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

# Set Cloud Shell specific permissions
chmod -R 755 data/ output/ logs/
chmod +x *.sh

# Cloud Shell session persistence tip
echo "💡 Adding activation to .bashrc for session persistence..."
if ! grep -q "source.*venv/bin/activate" ~/.bashrc; then
    echo "# Auto-activate ZAKOTU environment" >> ~/.bashrc
    echo "if [ -f ~/zakotu-linux/venv/bin/activate ]; then" >> ~/.bashrc
    echo "    source ~/zakotu-linux/venv/bin/activate" >> ~/.bashrc
    echo "    cd ~/zakotu-linux" >> ~/.bashrc
    echo "fi" >> ~/.bashrc
fi

echo
echo "🎉 Google Cloud Shell setup complete!"
echo
echo "🌩️ Cloud Shell Specific Notes:"
echo "- Your home directory has 5GB persistent storage"
echo "- Sessions timeout after 20 minutes of inactivity"
echo "- Use 'cloudshell edit' for file editing"
echo "- Use Web Preview to view generated content"
echo
echo "Next steps:"
echo "1. Edit .env file: cloudshell edit .env"
echo "2. Add your Gemini API key to the .env file"
echo "3. Test installation: ./test_linux.sh"
echo "4. Generate your first video: python src/gen_short.py"
echo
echo "🔗 To access generated videos:"
echo "   Use Cloud Shell's Web Preview or download files"
echo
