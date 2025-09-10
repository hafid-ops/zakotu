#!/bin/bash
# Quick Linux compatibility test for ZAKOTU

echo "🧪 Testing ZAKOTU Linux compatibility..."
echo

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  Virtual environment not detected. Activating..."
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ No virtual environment found. Run setup_linux.sh first."
        exit 1
    fi
fi

# Test Python imports
echo "🐍 Testing Python imports..."

python3 -c "
import sys
print(f'Python version: {sys.version}')

# Test core imports
try:
    import numpy as np
    print('✅ NumPy:', np.__version__)
except ImportError as e:
    print('❌ NumPy:', e)

try:
    import moviepy
    print('✅ MoviePy:', moviepy.__version__)
except ImportError as e:
    print('❌ MoviePy:', e)

try:
    from moviepy.editor import TextClip
    print('✅ MoviePy TextClip import successful')
except ImportError as e:
    print('❌ MoviePy TextClip:', e)

try:
    import onnxruntime as ort
    providers = ort.get_available_providers()
    print('✅ ONNX Runtime providers:', providers)
except ImportError as e:
    print('❌ ONNX Runtime:', e)

try:
    from kokoro_onnx import Kokoro
    print('✅ Kokoro ONNX import successful')
except ImportError as e:
    print('❌ Kokoro ONNX:', e)

try:
    import google.generativeai as genai
    print('✅ Google Generative AI import successful')
except ImportError as e:
    print('❌ Google Generative AI:', e)

try:
    import vosk
    print('✅ Vosk import successful')
except ImportError as e:
    print('❌ Vosk:', e)

try:
    import playwright
    print('✅ Playwright import successful')
except ImportError as e:
    print('❌ Playwright:', e)
"

# Test system commands
echo
echo "🔧 Testing system dependencies..."

# Test ImageMagick
if command -v convert >/dev/null 2>&1; then
    echo "✅ ImageMagick: $(convert -version | head -1)"
else
    echo "❌ ImageMagick not found"
fi

# Test FFmpeg
if command -v ffmpeg >/dev/null 2>&1; then
    echo "✅ FFmpeg: $(ffmpeg -version | head -1 | cut -d' ' -f3)"
else
    echo "❌ FFmpeg not found"
fi

# Test directories
echo
echo "📁 Testing directory structure..."

directories=("data/models" "output" "logs" "config")
for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ Directory exists: $dir"
    else
        echo "⚠️  Creating directory: $dir"
        mkdir -p "$dir"
    fi
done

# Test .env file
echo
echo "🔑 Testing configuration..."

if [ -f ".env" ]; then
    echo "✅ .env file exists"
    if grep -q "GEMINI_API_KEY" .env; then
        if grep -q "your_gemini_api_key_here" .env; then
            echo "⚠️  .env contains placeholder API key - please update it"
        else
            echo "✅ Gemini API key configured"
        fi
    else
        echo "❌ No GEMINI_API_KEY found in .env"
    fi
else
    echo "❌ .env file not found"
fi

# Test model files
echo
echo "🤖 Testing AI models..."

if [ -f "data/models/kokoro-v1.0.onnx" ]; then
    echo "✅ Kokoro model found"
else
    echo "⚠️  Kokoro model not found - will be downloaded on first run"
fi

if [ -d "data/models/vosk-model-small-en-us-0.15" ]; then
    echo "✅ Vosk model found"
else
    echo "⚠️  Vosk model not found - run 'python x.py' to download"
fi

# Quick functionality test
echo
echo "🚀 Running quick functionality test..."

if python3 -c "
import os
import sys
sys.path.insert(0, 'src')

# Test ImageMagick setup
try:
    from gen_short import setup_imagemagick
    setup_imagemagick()
    print('✅ ImageMagick setup successful')
except Exception as e:
    print(f'❌ ImageMagick setup failed: {e}')

# Test story generator fallback
try:
    from story_generator import get_fallback_stories
    stories = get_fallback_stories()
    print(f'✅ Story fallback system: {len(stories)} stories available')
except Exception as e:
    print(f'❌ Story fallback system failed: {e}')
"; then
    echo "✅ Basic functionality test passed"
else
    echo "❌ Basic functionality test failed"
fi

echo
echo "📋 Test complete!"
echo
echo "Next steps:"
echo "1. If any tests failed, run: ./setup_linux.sh"
echo "2. Update your .env file with a valid Gemini API key"
echo "3. Run: python src/gen_short.py"
echo
