# 🐳 Docker Quick Start - Run bitHuman Agent

Since you already have Docker Desktop, this is the easiest way to run the bitHuman agent!

## Prerequisites

✅ Docker Desktop installed (you have this)
✅ Docker Desktop is running

## Step 1: Make Sure Docker is Running

1. Open **Docker Desktop**
2. Wait for it to say "Docker Desktop is running"

## Step 2: Build and Run the Agent

Open PowerShell in your project directory:

```powershell
cd C:\Users\carlo\Documents\GitHub\agent-starter-react\agent
.\run-docker.ps1
```

Or manually:

```powershell
cd C:\Users\carlo\Documents\GitHub\agent-starter-react\agent

# Build the Docker image
docker-compose build

# Run the agent
docker-compose up
```

You should see:
```
INFO:voice-agent:Connecting to room voice_assistant_room_XXXX
INFO:voice-agent:Starting bitHuman avatar...
INFO:voice-agent:Agent is ready and waiting for participants
```

## Step 3: Run the Frontend (New Terminal)

**Keep the Docker container running**, then open a **new PowerShell window**:

```powershell
cd C:\Users\carlo\Documents\GitHub\agent-starter-react
pnpm dev
```

## Step 4: Test It!

1. Open http://localhost:3000
2. Click "Start call"
3. Allow microphone
4. **See your bitHuman avatar!**
5. Start talking!

## Managing the Agent

### Stop the Agent
Press `Ctrl+C` in the PowerShell window running Docker

Or:
```powershell
docker-compose down
```

### View Logs
```powershell
docker-compose logs -f
```

### Restart the Agent
```powershell
docker-compose restart
```

### Rebuild After Code Changes
```powershell
docker-compose build
docker-compose up
```

## How It Works

```
┌─────────────────┐
│ Docker Desktop  │
│   (Windows)     │
│                 │
│  ┌───────────┐  │         ┌──────────────┐         ┌─────────────┐
│  │  Linux    │  │ ◄─────► │   LiveKit    │ ◄─────► │   Browser   │
│  │ Container │  │         │    Server    │         │  (Frontend) │
│  │           │  │         └──────────────┘         └─────────────┘
│  │ bitHuman  │  │
│  │  Agent    │  │
│  └───────────┘  │
└─────────────────┘
```

- Docker runs a Linux container on Windows
- The `bithuman` SDK works inside the Linux container
- Agent connects to LiveKit
- Frontend runs normally in Windows
- Everything communicates over the network

## Troubleshooting

### "Docker is not running"
Start Docker Desktop and wait for it to fully start

### "Failed to build"
Make sure you're in the `agent` directory:
```powershell
cd C:\Users\carlo\Documents\GitHub\agent-starter-react\agent
```

### Port already in use
Stop any other agents running:
```powershell
docker-compose down
```

### Can't connect from frontend
Make sure both agent (Docker) and frontend are running

### Need to update code
After changing `agent.py`:
```powershell
docker-compose restart
```

After changing `requirements.txt`:
```powershell
docker-compose build
docker-compose up
```

## Advantages of Docker

- ✅ Works on Windows without WSL2
- ✅ Clean, isolated environment
- ✅ Easy to start/stop
- ✅ Same environment as production
- ✅ No Python installation needed on Windows

## Environment Variables

Docker automatically reads from your `.env` file with all the configured values:
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `LIVEKIT_URL`
- `BITHUMAN_API_SECRET`
- `BITHUMAN_AVATAR_ID`
- `OPENAI_API_KEY`

## Next Steps

Once it's working:
1. Customize the agent in `agent.py`
2. Try different avatars from bitHuman console
3. Deploy to production (Docker makes this easy!)

---

**Total setup time: 2 minutes** ⚡

Your agent will run in a Linux container via Docker, giving you full bitHuman support on Windows!
