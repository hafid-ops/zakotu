FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# System packages (ffmpeg is required by moviepy/ffmpeg-python)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    git \
    curl \
    ca-certificates \
    imagemagick \
    build-essential \
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
    && rm -rf /var/lib/apt/lists/*

# Fix ImageMagick policy (the path is version-dependent)
RUN mkdir -p /etc/ImageMagick-6 && \
    echo '<policymap>' > /etc/ImageMagick-6/policy.xml && \
    echo '  <policy domain="resource" name="memory" value="256MiB"/>' >> /etc/ImageMagick-6/policy.xml && \
    echo '  <policy domain="resource" name="disk" value="1GiB"/>' >> /etc/ImageMagick-6/policy.xml && \
    echo '  <policy domain="resource" name="time" value="120"/>' >> /etc/ImageMagick-6/policy.xml && \
    echo '  <policy domain="coder" rights="read|write" pattern="PDF" />' >> /etc/ImageMagick-6/policy.xml && \
    echo '</policymap>' >> /etc/ImageMagick-6/policy.xml

WORKDIR /app

# Install Python dependencies first (layer cache)
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    # Install dependencies one by one to better handle errors
    pip install --no-cache-dir numpy tqdm typing-extensions && \
    pip install --no-cache-dir python-dotenv requests && \
    pip install --no-cache-dir Pillow ffmpeg-python && \
    pip install --no-cache-dir soundfile vosk && \
    pip install --no-cache-dir pysbd && \
    pip install --no-cache-dir torch==2.0.1 torchaudio==2.0.2 torchvision==0.15.2 && \
    pip install --no-cache-dir onnxruntime==1.20.1 && \
    pip install --no-cache-dir kokoro_onnx==0.4.9 && \
    pip install --no-cache-dir transformers==4.33.3 diffusers==0.23.0 && \
    pip install --no-cache-dir google-generativeai==0.6.0 && \
    pip install --no-cache-dir moviepy==1.0.3 && \
    pip install --no-cache-dir playwright==1.42.0 && \
    pip install --no-cache-dir pydantic==2.5.2 && \
    pip install --no-cache-dir setuptools

# Copy the rest of the project
COPY . .

# Create necessary directories
RUN mkdir -p data/models data/temp data/audio \
    generatedVoice generatedVideo output/generatedStory \
    output/generatedImage output/generatedThumbnail \
    output/generatedVideo output/generatedVoice logs

# Configure MoviePy to use ImageMagick
RUN echo "from moviepy.config import change_settings; change_settings({'IMAGEMAGICK_BINARY': 'convert'})" > set_moviepy_config.py && \
    python set_moviepy_config.py

# Set proper permissions
RUN chmod -R 755 /app

# Set a health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import os; exit(0 if os.path.exists('/app/logs/ZAKUTO.log') else 1)"

# Make the entrypoint script executable
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Set entrypoint to our custom script
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

# Default command
CMD ["python", "src/main.py"]
