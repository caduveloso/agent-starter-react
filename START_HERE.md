# 🚀 START HERE - Run Your bitHuman Avatar Agent

You have Docker Desktop installed! This is the **easiest way** to run the bitHuman agent on Windows.

## Quick Start (3 Steps)

### Step 1: Start Docker Desktop (1 minute)

1. Press **Windows Key**
2. Type "Docker Desktop"
3. Click to open it
4. Wait for the whale icon in the system tray to stop animating
5. You'll see "Docker Desktop is running"

### Step 2: Run the Agent (30 seconds)

Open PowerShell and run:

```powershell
cd C:\Users\carlo\Documents\GitHub\agent-starter-react\agent
docker-compose build
docker-compose up
```

You should see:
```
INFO:voice-agent:Starting bitHuman avatar...
INFO:voice-agent:Agent is ready and waiting for participants
```

**Keep this terminal running!**

### Step 3: Run the Frontend (30 seconds)

Open a **NEW PowerShell window**:

```powershell
cd C:\Users\carlo\Documents\GitHub\agent-starter-react
pnpm dev
```

### Step 4: Test It! (10 seconds)

1. Open http://localhost:3000
2. Click "Start call"
3. Allow microphone access
4. **Your bitHuman avatar appears!**
5. Start talking!

---

## 🎉 That's It!

Your bitHuman avatar agent is now running in a Linux Docker container on Windows.

## Detailed Guides

- **[DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md)** - Complete Docker guide
- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Technical overview
- **[README_IMPORTANT.md](README_IMPORTANT.md)** - Why Docker/WSL2 is needed

## Commands Reference

### Start the agent:
```powershell
cd agent
docker-compose up
```

### Stop the agent:
Press `Ctrl+C` or in another terminal:
```powershell
docker-compose down
```

### Rebuild after code changes:
```powershell
docker-compose build
docker-compose up
```

### View logs:
```powershell
docker-compose logs -f
```

## Troubleshooting

### "Docker is not running"
→ Start Docker Desktop from the Start menu

### "Port already in use"
→ Run: `docker-compose down`

### "Build failed"
→ Make sure you're in the `agent` directory
→ Check that `.env` file exists in project root

### Avatar not appearing
→ Check BITHUMAN_API_SECRET is correct
→ Verify avatar ID in .env
→ Look at agent logs for errors

## Why Docker?

- ✅ **Works on Windows** - No WSL2 needed
- ✅ **Linux environment** - bitHuman SDK runs perfectly
- ✅ **Isolated** - Doesn't affect your system
- ✅ **Production-ready** - Same setup for deployment
- ✅ **Easy** - One command to start/stop

## Architecture

```
Your Computer (Windows)
├── Docker Desktop
│   └── Linux Container
│       └── bitHuman Agent (Python)
│           └── Connects to LiveKit
├── PowerShell
│   └── Frontend (Next.js)
│       └── Connects to LiveKit
└── Browser
    └── Shows Avatar + Voice Chat
```

## Next Steps

Once it's working:
1. Customize agent personality in `agent.py`
2. Try different avatars from [bitHuman Console](https://imaginex.bithuman.ai/)
3. Modify the UI in your React app

---

**Need help?** Check [DOCKER_QUICKSTART.md](DOCKER_QUICKSTART.md) for detailed troubleshooting!
