# 🌐 ZAKOTU Google Cloud Shell Setup Guide

## 🚀 **Quick Start in Google Cloud Shell**

### **Step 1: Clone Your Repository**
```bash
# Clone your GitHub repository
git clone https://github.com/hafid-ops/zakotu.git
cd zakotu
```

### **Step 2: Set Up Environment**
```bash
# Copy the environment template
cp .env.template .env

# Edit the .env file to add your API key
nano .env
# Add your GEMINI_API_KEY="your_actual_api_key_here"
```

### **Step 3: Option A - Docker Setup (Recommended)**
```bash
# Build and run with Docker (easiest)
docker compose up --build

# Or run in detached mode
docker compose up --build -d

# View logs
docker compose logs -f
```

### **Step 4: Option B - Native Linux Setup**
```bash
# Make setup script executable
chmod +x setup_linux.sh

# Run automated setup
./setup_linux.sh

# Download required models
python3 x.py

# Run the application
python3 src/main.py
```

## 🔧 **Google Cloud Shell Specific Configuration**

### **Enable Required APIs**
```bash
# Enable necessary Google Cloud APIs
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
```

### **Increase Cloud Shell Resource Limits**
```bash
# Cloud Shell has limited resources by default
# For better performance, consider using:
# - Compute Engine VM with more resources
# - Cloud Run for containerized deployment
# - GKE for Kubernetes deployment
```

### **Persistent Storage Setup**
```bash
# Your home directory persists between sessions
# Store your project and data there
cd $HOME
git clone https://github.com/hafid-ops/zakotu.git
cd zakotu
```

## 📁 **File Structure in Cloud Shell**
```
$HOME/zakotu/
├── .env                    # Your API keys (never commit!)
├── docker-compose.yml      # Docker orchestration
├── output/                 # Generated videos will be here
├── data/models/           # AI models (downloaded automatically)
└── logs/                  # Application logs
```

## 🎥 **Accessing Generated Content**

### **Download Files from Cloud Shell**
```bash
# Download generated videos to your local machine
# Method 1: Use Cloud Shell Editor
# - Navigate to output/generatedVideo/
# - Right-click files → Download

# Method 2: Use gcloud command
gcloud alpha cloud-shell get-mount-command $HOME/zakotu/output

# Method 3: Upload to Google Cloud Storage
gsutil cp -r output/generatedVideo gs://your-bucket-name/
```

### **View Files in Cloud Shell**
```bash
# List generated content
ls -la output/generatedVideo/
ls -la output/generatedVoice/
ls -la output/generatedThumbnail/

# View logs
tail -f logs/ZAKUTO.log
```

## 🚀 **Advanced Cloud Deployment Options**

### **Option 1: Cloud Run (Serverless)**
```bash
# Build for Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/zakotu

# Deploy to Cloud Run
gcloud run deploy zakotu \
  --image gcr.io/PROJECT_ID/zakotu \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### **Option 2: Compute Engine VM**
```bash
# Create a VM with Docker
gcloud compute instances create zakotu-vm \
  --image-family ubuntu-2004-lts \
  --image-project ubuntu-os-cloud \
  --machine-type e2-standard-2 \
  --boot-disk-size 50GB \
  --tags http-server,https-server

# SSH into the VM
gcloud compute ssh zakotu-vm
```

### **Option 3: Google Kubernetes Engine**
```bash
# Create GKE cluster
gcloud container clusters create zakotu-cluster \
  --num-nodes=2 \
  --machine-type=e2-standard-2

# Deploy your application
kubectl apply -f k8s-deployment.yaml
```

## ⚡ **Performance Optimization**

### **Resource Requirements**
- **CPU:** 2+ cores recommended
- **Memory:** 4GB+ recommended  
- **Storage:** 10GB+ for models and output
- **Network:** Good bandwidth for AI API calls

### **Cloud Shell Limitations**
- **CPU:** Limited compute power
- **Memory:** ~3.75GB available
- **Storage:** 5GB persistent home directory
- **Session:** Auto-hibernates after inactivity

### **Recommended for Production**
```bash
# Use Compute Engine for better performance
gcloud compute instances create zakotu-production \
  --machine-type n1-standard-4 \
  --boot-disk-size 100GB \
  --image-family ubuntu-2004-lts \
  --image-project ubuntu-os-cloud
```

## 🔐 **Security Best Practices**

### **API Key Management**
```bash
# Use Google Secret Manager (recommended)
gcloud secrets create gemini-api-key --data-file=-
# Then reference in your application

# Or use environment variables
export GEMINI_API_KEY="your_key_here"
```

### **Network Security**
```bash
# Create firewall rules if needed
gcloud compute firewall-rules create allow-zakotu \
  --allow tcp:8080 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow access to Zakotu app"
```

## 🐛 **Troubleshooting**

### **Common Issues**
```bash
# If Docker build fails due to memory
docker system prune -a
docker compose build --no-cache

# If models fail to download
python3 x.py --force-download

# If API quota exceeded
# Check your Gemini API quotas and billing
```

### **Cloud Shell Specific**
```bash
# Restart Cloud Shell if stuck
# Use the restart button in Cloud Shell interface

# Check available space
df -h

# Monitor resource usage
top
free -h
```

## 📊 **Monitoring and Logs**

### **Application Logs**
```bash
# Real-time log monitoring
tail -f logs/ZAKUTO.log

# Docker logs
docker compose logs -f

# System logs
journalctl -f
```

### **Resource Monitoring**
```bash
# Monitor Docker containers
docker stats

# System resources
htop
iostat 1
```

## 🎯 **Quick Commands Summary**

```bash
# Complete setup in one go:
git clone https://github.com/hafid-ops/zakotu.git
cd zakotu
cp .env.template .env
nano .env  # Add your API key
docker compose up --build

# Check status:
docker compose ps
docker compose logs

# Stop:
docker compose down
```

## 📞 **Support**

- **Cloud Shell Docs:** https://cloud.google.com/shell/docs
- **Docker Issues:** Check container logs with `docker compose logs`
- **API Issues:** Verify your Gemini API key and quotas
- **Storage Issues:** Use `df -h` to check available space

---

**Ready to generate AI videos in the cloud! 🎬☁️**
