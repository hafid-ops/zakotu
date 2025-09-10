# ZAKOTU on Google Cloud Shell

This guide helps you run ZAKOTU AI Video Generator on Google Cloud Shell with optimized settings.

## 🌩️ Why Google Cloud Shell?

- **Free tier**: 50 hours per week
- **Pre-installed tools**: Python, FFmpeg, Git, Docker
- **5GB persistent storage**: Keeps your models and data
- **No setup required**: Ready-to-use Linux environment
- **Web-based access**: Works from any browser

## 🚀 Quick Start (3 Minutes)

### Step 1: Open Cloud Shell
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the **Cloud Shell** icon (⧉) in the top toolbar
3. Wait for initialization (30 seconds)

### Step 2: Get ZAKOTU
```bash
# Option A: Clone from repository
git clone https://github.com/yourusername/zakotu-linux.git
cd zakotu-linux

# Option B: Upload your files
# Use the "Upload file" button in Cloud Shell
```

### Step 3: Automated Setup
```bash
# Make script executable and run
chmod +x setup_cloudshell.sh
./setup_cloudshell.sh
```

### Step 4: Configure API Key
```bash
# Edit environment file
cloudshell edit .env

# Add your Gemini API key:
# GEMINI_API_KEY="your_actual_api_key_here"
```

### Step 5: Generate Your First Video
```bash
# Test installation
./test_linux.sh

# Generate a short video (3-5 minutes)
python src/gen_short.py

# Generate a full video (5-10 minutes)  
python src/main.py
```

## 📋 Detailed Setup Instructions

### System Requirements (Auto-handled)
Google Cloud Shell provides:
- ✅ **Ubuntu 20.04 LTS**
- ✅ **Python 3.9+**
- ✅ **FFmpeg** (pre-installed)
- ✅ **Git** (pre-installed)
- ✅ **Docker** (pre-installed)
- ✅ **2 vCPUs, 8GB RAM**
- ✅ **5GB persistent storage**

### Manual Installation (If Needed)

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y imagemagick libsndfile1 espeak-ng fonts-liberation

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install Python packages
pip install -r requirements-linux.txt

# 4. Install browser for image generation
playwright install --with-deps chromium

# 5. Download AI models
python x.py
```

## 🔧 Cloud Shell Optimizations

### Performance Settings
```bash
# Add to .env file for optimal Cloud Shell performance
OMP_NUM_THREADS=2
MKL_NUM_THREADS=2
IMAGEMAGICK_BINARY=convert
```

### Memory Management
```bash
# For larger videos, use these settings:
echo "PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256" >> .env
echo "OMP_NUM_THREADS=1" >> .env
```

### Session Persistence
Cloud Shell sessions timeout after 20 minutes of inactivity. The setup script automatically adds environment activation to your `.bashrc`:

```bash
# Your environment will auto-activate on each session
# Files in $HOME persist between sessions
# Generated content stays in ~/zakotu-linux/output/
```

## 📁 File Management

### Accessing Generated Content

**Option 1: Web Preview**
```bash
# Start a simple web server
cd output/generatedVideo
python3 -m http.server 8080

# Click "Web Preview" button and select port 8080
```

**Option 2: Download Files**
```bash
# Download individual files
cloudshell download output/generatedVideo/short_video.mp4

# Create archive for multiple files
tar -czf my_videos.tar.gz output/
cloudshell download my_videos.tar.gz
```

**Option 3: Google Cloud Storage**
```bash
# Upload to Cloud Storage (if you have a project)
gsutil cp output/generatedVideo/*.mp4 gs://your-bucket-name/
```

### Storage Limits
- **Total storage**: 5GB persistent in `$HOME`
- **Temporary space**: 20GB in `/tmp` (session-only)
- **Recommendations**:
  - Keep models in `~/zakotu-linux/data/` (persistent)
  - Generate videos in `~/zakotu-linux/output/` (persistent)
  - Clean up old videos regularly

## 🎬 Generation Examples

### Quick Test (30 seconds)
```bash
# Generate a simple short video
python src/gen_short.py
```

### Custom Story
```bash
# Edit your prompt
echo "Write a funny 2-sentence story about a confused robot." > config/prompt.txt

# Generate video with custom prompt
python src/main.py
```

### Batch Generation
```bash
# Generate multiple videos
for i in {1..3}; do
    echo "Story $i: Write a $i-sentence mystery story." > config/prompt.txt
    python src/gen_short.py
    mv output/generatedVideo/short_video.mp4 output/story_$i.mp4
done
```

## 🐳 Docker Alternative

If you prefer using Docker in Cloud Shell:

```bash
# Build container
docker build -f Dockerfile-linux -t zakotu .

# Run container
docker run --rm \
  -v "$(pwd)/output:/app/output" \
  -v "$(pwd)/data:/app/data" \
  -e GEMINI_API_KEY="your_key_here" \
  zakotu
```

## 🔍 Troubleshooting

### Common Issues

**1. Session Timeout**
```bash
# Sessions auto-timeout after 20 min idle
# Solution: Keep generating content or use tmux
tmux new-session -d 'python src/main.py'
```

**2. Out of Memory**
```bash
# Reduce memory usage
echo "OMP_NUM_THREADS=1" >> .env
echo "PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128" >> .env
```

**3. Storage Full**
```bash
# Clean up old files
rm -rf output/generatedVideo/*.mp4
rm -rf data/temp/*
```

**4. API Rate Limits**
```bash
# ZAKOTU has built-in fallbacks for API limits
# Fallback stories will be used automatically
```

### Performance Tips

**Optimize for Cloud Shell:**
```bash
# Use shorter prompts for faster generation
echo "Write a 1-sentence horror story." > config/prompt.txt

# Generate lower quality for testing
# Edit src/gen_short.py and change resolution to 720p
```

**Monitor Resources:**
```bash
# Check memory usage
free -h

# Check disk usage  
df -h

# Check processes
htop
```

## 📊 Expected Performance

On Google Cloud Shell (2 vCPU, 8GB RAM):

| Task | Duration | Output |
|------|----------|--------|
| **Setup** | 3-5 minutes | One-time installation |
| **Model Download** | 2-3 minutes | One-time download |
| **Short Video** | 3-5 minutes | 30-60 second video |
| **Full Video** | 8-12 minutes | 2-3 minute video |

## 🎯 Production Tips

### For Regular Use
```bash
# Create alias for quick access
echo 'alias zakotu="cd ~/zakotu-linux && source venv/bin/activate"' >> ~/.bashrc

# Auto-cleanup old files
echo '0 2 * * * find ~/zakotu-linux/output -name "*.mp4" -mtime +7 -delete' | crontab -
```

### For Collaboration
```bash
# Share via Cloud Storage
gsutil cp -r output/ gs://your-shared-bucket/

# Or share via git (without large files)
git add src/ config/ .env.example
git commit -m "Updated ZAKOTU configuration"
git push origin main
```

## 🆘 Support & Resources

### Cloud Shell Specific Help
- **Docs**: [Cloud Shell Documentation](https://cloud.google.com/shell/docs)
- **Limits**: 50 hours/week, 5GB storage
- **Pricing**: Free tier available

### ZAKOTU Help
- **Test Script**: `./test_linux.sh`
- **Logs**: `tail -f logs/ZAKUTO.log`
- **Reset**: Re-run `./setup_cloudshell.sh`

### Getting Help
1. **Check logs**: `cat logs/ZAKUTO.log | tail -50`
2. **Test system**: `./test_linux.sh`
3. **Restart session**: Close and reopen Cloud Shell
4. **Clean install**: `rm -rf venv && ./setup_cloudshell.sh`

## 🎉 Success!

Once setup is complete, you can generate AI videos directly in your browser using Google Cloud Shell. The environment persists your models and configuration, making subsequent generations much faster.

**Happy video generating! 🎬✨**
