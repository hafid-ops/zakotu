#!/bin/bash
set -e

# Try to install Playwright browser
echo "Installing Playwright browser..."
if ! playwright install --with-deps chromium; then
    echo "Failed to install browser with dependencies, trying alternative method..."
    apt-get update && apt-get install -y wget
    playwright install chromium
fi

# Download Kokoro model files if they don't exist
echo "Checking for Kokoro model files..."
if [ ! -f "/app/data/models/kokoro-v1.0.onnx" ]; then
    echo "Downloading Kokoro ONNX model..."
    mkdir -p /app/data/models
    wget -O /app/data/models/kokoro-v1.0.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
fi

if [ ! -f "/app/data/models/voices-v1.0.bin" ]; then
    echo "Downloading Kokoro voices file..."
    mkdir -p /app/data/models
    wget -O /app/data/models/voices-v1.0.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
fi

echo "Setup complete. Starting application..."

# Execute the command passed to docker run
exec "$@"
