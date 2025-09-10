# ZAKOTU Windows to Linux Migration Guide

This guide helps you migrate your ZAKOTU installation from Windows to Linux while preserving your data and configuration.

## Quick Migration (Recommended)

### Step 1: Backup Your Windows Data

```bash
# On Windows, backup these folders:
# - output/ (your generated content)
# - data/models/ (downloaded AI models)  
# - .env (your API keys)
# - config/ (your custom prompts)
```

### Step 2: Linux Setup

```bash
# Clone or copy the project to Linux
git clone https://github.com/yourusername/zakotu-linux.git
cd zakotu-linux

# Run automated setup
chmod +x setup_linux.sh
./setup_linux.sh
```

### Step 3: Restore Your Data

```bash
# Copy your backed up files:
cp /path/to/backup/.env .
cp -r /path/to/backup/output/* output/
cp -r /path/to/backup/data/models/* data/models/
cp -r /path/to/backup/config/* config/
```

### Step 4: Test Installation

```bash
chmod +x test_linux.sh
./test_linux.sh
```

## Detailed Migration Steps

### Prerequisites Comparison

| Component | Windows | Linux |
|-----------|---------|-------|
| Python | 3.10+ from python.org | `python3-venv python3-pip` |
| FFmpeg | Manual download | `apt install ffmpeg` |
| ImageMagick | Manual download | `apt install imagemagick` |
| Visual C++ | Required | `build-essential` |

### Environment Setup

#### Windows Virtual Environment
```cmd
python -m venv venv
.\venv\Scripts\activate
```

#### Linux Virtual Environment  
```bash
python3 -m venv venv
source venv/bin/activate
```

### Path Differences

| Windows Path | Linux Path |
|--------------|------------|
| `C:\Program Files\ImageMagick\magick.exe` | `/usr/bin/convert` |
| `.\venv\Scripts\activate` | `source venv/bin/activate` |
| `output\generatedVideo\` | `output/generatedVideo/` |

### Configuration Changes

#### .env File
- ✅ **No changes needed** - same format on both platforms

#### Font Paths
- **Windows**: Uses system fonts automatically
- **Linux**: Uses `/usr/share/fonts/` or fonts in `assets/fonts/`

#### ImageMagick Policy
- **Windows**: Usually works out of the box
- **Linux**: May need policy adjustment (handled by setup script)

### Common Issues & Solutions

#### Issue 1: Import Errors
```bash
# Windows error: "DLL load failed"
# Linux solution: Install system libraries
sudo apt-get install libsndfile1 libsndfile1-dev
```

#### Issue 2: Font Rendering
```bash
# Linux: Install additional fonts
sudo apt-get install fonts-liberation fonts-dejavu-core
```

#### Issue 3: Audio Output
```bash
# Linux: Install audio libraries
sudo apt-get install libasound2-dev pulseaudio-dev
```

#### Issue 4: GPU Acceleration
```bash
# Windows: Uses DirectML if available
# Linux: Uses CUDA if available, fallback to CPU
# Both: CPU mode works fine for most use cases
```

### Performance Comparison

| Aspect | Windows | Linux |
|--------|---------|-------|
| Model Loading | Good | Excellent |
| Video Processing | Good | Excellent |
| Memory Usage | Higher | Lower |
| Startup Time | Slower | Faster |
| Container Support | WSL2 | Native |

### Feature Compatibility

| Feature | Windows | Linux | Notes |
|---------|---------|-------|-------|
| Story Generation | ✅ | ✅ | Identical |
| Voice Synthesis | ✅ | ✅ | Better performance on Linux |
| Image Generation | ✅ | ✅ | Identical |
| Video Creation | ✅ | ✅ | Better on Linux |
| Thumbnail Generation | ✅ | ✅ | Identical |
| Docker Support | ✅ | ✅ | Native on Linux |

## Advanced Migration

### Custom Model Locations

If you have custom models or modified configurations:

```bash
# Windows model path
C:\Users\YourName\zakotu\data\models\

# Linux equivalent  
/home/username/zakotu/data/models/

# Update any hardcoded paths in your scripts
```

### Docker Migration

#### From Windows Docker Desktop to Linux Docker

```bash
# Export Windows container (if you have customizations)
docker save zakotu-app > zakotu-windows.tar

# On Linux, load and update
docker load < zakotu-windows.tar
docker-compose -f docker-compose-linux.yml up --build
```

### Performance Optimization

#### Linux-Specific Optimizations

```bash
# Enable all CPU cores
echo "OMP_NUM_THREADS=$(nproc)" >> .env

# Optimize memory usage
echo "MALLOC_MMAP_THRESHOLD_=65536" >> .env
echo "MALLOC_TRIM_THRESHOLD_=131072" >> .env

# GPU optimization (if available)
echo "CUDA_VISIBLE_DEVICES=0" >> .env
```

### Development Environment

#### IDE Setup
- **Windows**: VS Code, PyCharm
- **Linux**: Same IDEs available, often better performance

#### Debugging
```bash
# Linux has better debugging tools
gdb python
valgrind --tool=memcheck python src/main.py
```

## Troubleshooting Migration Issues

### Package Installation Fails

```bash
# Update package lists
sudo apt-get update

# Install build dependencies
sudo apt-get install build-essential python3-dev

# Try installing packages individually
pip install --verbose package-name
```

### Permission Errors

```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/zakotu

# Fix permissions
chmod -R 755 data/ output/ logs/
chmod +x *.sh
```

### Model Download Issues

```bash
# Manual model download
cd data/models
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

### Audio/Video Issues

```bash
# Test multimedia stack
ffmpeg -version
convert -version
python3 -c "import soundfile; print('Audio OK')"
```

## Migration Checklist

- [ ] Backup Windows data
- [ ] Install Linux prerequisites  
- [ ] Set up Python virtual environment
- [ ] Install Python packages
- [ ] Copy configuration files
- [ ] Copy AI models
- [ ] Test basic functionality
- [ ] Run full generation test
- [ ] Verify output quality
- [ ] Update any scripts/automation

## Post-Migration

### Advantages of Linux Setup
- **Better performance** for AI workloads
- **Lower memory usage**
- **More stable** long-running processes  
- **Better Docker integration**
- **Easier automation** and scripting
- **Lower resource costs** for cloud deployment

### Maintenance

```bash
# Regular updates
sudo apt-get update && sudo apt-get upgrade
pip install --upgrade -r requirements-linux.txt

# Clean up
docker system prune
pip cache purge
```

### Backup Strategy

```bash
# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf "zakotu-backup-$DATE.tar.gz" \
    .env config/ output/ data/models/
```

## Support

If you encounter issues during migration:

1. **Check logs**: `tail -f logs/ZAKUTO.log`
2. **Run tests**: `./test_linux.sh`
3. **Check system**: `./setup_linux.sh` (safe to re-run)
4. **Community**: GitHub Issues/Discussions

The Linux version offers significant performance and stability improvements over the Windows version, making the migration worthwhile for production use.
