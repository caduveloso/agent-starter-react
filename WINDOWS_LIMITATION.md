# ⚠️ Windows Limitation - bitHuman SDK

## Issue Discovered

The **bitHuman Python SDK is not available for Windows**.

According to the [official documentation](https://bithuman.mintlify.app/api-reference/sdk/quick-start):

### Supported Operating Systems:
- ✅ Linux (x86_64 and arm64)
- ✅ macOS (Apple Silicon)
- ❌ **Windows** (NOT supported)

This means the bitHuman avatar integration **cannot run natively on Windows**.

## Solutions

### Option 1: Use WSL2 (Windows Subsystem for Linux) - Recommended

Run the agent in WSL2 Ubuntu:

1. **Install WSL2** (if not already installed):
   ```powershell
   wsl --install
   ```

2. **Open Ubuntu terminal** and navigate to your project:
   ```bash
   cd /mnt/c/Users/carlo/Documents/GitHub/agent-starter-react
   ```

3. **Set up Python environment in WSL**:
   ```bash
   cd agent
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install bithuman
   ```

4. **Run the agent**:
   ```bash
   python agent.py dev
   ```

5. **Keep frontend running in Windows**:
   ```powershell
   # In Windows PowerShell
   pnpm dev
   ```

### Option 2: Use Docker

Create a Linux container to run the agent:

1. **Create Dockerfile** (I can help with this)
2. **Build and run** the agent in Docker
3. **Frontend runs in Windows** as normal

### Option 3: Deploy to Linux Server

Run the agent on:
- A Linux VPS (DigitalOcean, AWS EC2, etc.)
- Your LiveKit Cloud infrastructure
- A Linux machine on your network

### Option 4: Use Voice-Only Mode (Windows Compatible)

The voice-only agent works perfectly on Windows:

```powershell
cd agent
.\run_voice_only.ps1
```

This gives you:
- ✅ Voice interaction
- ✅ OpenAI STT/LLM/TTS
- ✅ Works on Windows
- ❌ No avatar rendering

## Recommended Path Forward

### For Development/Testing:
**Use WSL2** - It's the easiest way to run Linux apps on Windows

### For Production:
**Deploy to Linux server** - Better performance and reliability

##  Quick WSL2 Setup Guide

### 1. Install WSL2
```powershell
# In PowerShell (Admin)
wsl --install -d Ubuntu
```

Restart your computer.

### 2. Set up the agent in WSL2
```bash
# In WSL2 Ubuntu terminal
cd /mnt/c/Users/carlo/Documents/GitHub/agent-starter-react/agent

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install livekit livekit-agents[openai,silero] python-dotenv opencv-python loguru
pip install bithuman

# Run the agent
python agent.py dev
```

### 3. Run frontend in Windows
```powershell
# In Windows PowerShell (separate terminal)
pnpm dev
```

### 4. Test
Open http://localhost:3000

## Why This Happens

bitHuman uses native libraries (like opencv, ffmpeg, etc.) that are compiled for specific platforms. They've prioritized Linux and macOS for their SDK, which is common for AI/ML tools.

## Current Status

- ✅ All code is ready
- ✅ Configuration is complete
- ✅ Voice-only works on Windows
- ⚠️ Avatar needs Linux/macOS/WSL2

## Need Help?

Let me know if you'd like me to:
1. Create a Docker setup
2. Help with WSL2 installation
3. Create deployment scripts for Linux
4. Set up a cloud deployment

The good news: Everything is configured correctly, it's just an OS compatibility issue!
