#!/bin/bash
# Quick Google Cloud Shell compatibility test

echo "🌩️ Testing ZAKOTU on Google Cloud Shell..."
echo

# Check if we're in Cloud Shell
if [[ "$DEVSHELL_PROJECT_ID" != "" ]]; then
    echo "✅ Google Cloud Shell detected"
    echo "   Project: $DEVSHELL_PROJECT_ID"
    echo "   User: $DEVSHELL_GCLOUD_CONFIG"
else
    echo "⚠️  Not running in Google Cloud Shell"
fi

# Check Cloud Shell specifics
echo
echo "🔍 Cloud Shell Environment:"
echo "   HOME: $HOME"
echo "   PWD: $PWD"
echo "   Python: $(python3 --version)"
echo "   Disk space: $(df -h $HOME | tail -1 | awk '{print $4}') available"
echo "   Memory: $(free -h | grep Mem | awk '{print $4}') available"

# Check pre-installed tools
echo
echo "🛠️ Pre-installed tools:"

if command -v ffmpeg >/dev/null 2>&1; then
    echo "   ✅ FFmpeg: $(ffmpeg -version 2>/dev/null | head -1 | cut -d' ' -f3)"
else
    echo "   ❌ FFmpeg not found"
fi

if command -v git >/dev/null 2>&1; then
    echo "   ✅ Git: $(git --version | cut -d' ' -f3)"
else
    echo "   ❌ Git not found"
fi

if command -v docker >/dev/null 2>&1; then
    echo "   ✅ Docker: $(docker --version | cut -d' ' -f3 | cut -d',' -f1)"
else
    echo "   ❌ Docker not found"
fi

# Check if virtual environment exists
echo
echo "🐍 Python Environment:"
if [ -d "venv" ]; then
    echo "   ✅ Virtual environment exists"
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "   ✅ Virtual environment active: $VIRTUAL_ENV"
    else
        echo "   ⚠️  Virtual environment not active"
        echo "   Run: source venv/bin/activate"
    fi
else
    echo "   ❌ Virtual environment not found"
    echo "   Run: ./setup_cloudshell.sh"
fi

# Test ZAKOTU specific files
echo
echo "📁 ZAKOTU Files:"
files=("src/main.py" "src/gen_short.py" ".env" "config/prompt.txt")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file missing"
    fi
done

# Test data directories
echo
echo "📂 Data Directories:"
dirs=("data/models" "output" "logs")
for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir ($(ls -1 $dir 2>/dev/null | wc -l) items)"
    else
        echo "   ❌ $dir missing"
    fi
done

# Test API configuration
echo
echo "🔑 Configuration:"
if [ -f ".env" ]; then
    if grep -q "your_gemini_api_key_here" .env 2>/dev/null; then
        echo "   ⚠️  Gemini API key not configured (still placeholder)"
        echo "   Edit: cloudshell edit .env"
    elif grep -q "GEMINI_API_KEY=" .env 2>/dev/null; then
        echo "   ✅ Gemini API key configured"
    else
        echo "   ❌ Gemini API key not found in .env"
    fi
else
    echo "   ❌ .env file not found"
fi

# Check Internet connectivity
echo
echo "🌐 Network Test:"
if curl -s --max-time 5 https://api.google.com >/dev/null; then
    echo "   ✅ Internet connectivity working"
else
    echo "   ❌ Internet connectivity issues"
fi

# Final recommendations
echo
echo "📋 Next Steps:"
if [ ! -d "venv" ]; then
    echo "   1. Run setup: ./setup_cloudshell.sh"
elif [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "   1. Activate environment: source venv/bin/activate"
fi

if [ -f ".env" ] && grep -q "your_gemini_api_key_here" .env 2>/dev/null; then
    echo "   2. Configure API key: cloudshell edit .env"
fi

echo "   3. Test generation: python src/gen_short.py"
echo "   4. View results: cloudshell download output/generatedVideo/short_video.mp4"

echo
echo "💡 Cloud Shell Tips:"
echo "   - Sessions timeout after 20 min idle"
echo "   - Use 'tmux' for long-running tasks"
echo "   - 5GB persistent storage in $HOME"
echo "   - Use Web Preview to view videos"

echo
echo "🎬 Ready to generate AI videos in the cloud!"
