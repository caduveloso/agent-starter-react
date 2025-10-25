# bitHuman Avatar Agent - Complete Setup Instructions

Based on the [official bitHuman SDK examples](https://github.com/bithuman-ai/sdk-examples-python/tree/main/livekit_agent).

## ⚠️ Important: Platform Requirements

The bitHuman SDK **only supports**:
- ✅ Linux (x86_64, arm64)
- ✅ macOS (Apple Silicon)
- ❌ Windows (NOT supported - must use WSL2)

## Option 1: Windows Users - Use WSL2 (Recommended)

### 1. Install WSL2

```powershell
# In PowerShell (Admin)
wsl --install -d Ubuntu
```

Restart your computer after installation.

### 2. Access your project in WSL2

```bash
# In WSL2 Ubuntu terminal
cd /mnt/c/Users/carlo/Documents/GitHub/agent-starter-react/agent
```

### 3. Install dependencies in WSL2

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

This will install:
- `livekit` - LiveKit Python SDK
- `livekit-agents` with OpenAI and Silero plugins
- `livekit-plugins-bithuman` - bitHuman plugin
- `bithuman` - bitHuman SDK (Linux/macOS only)
- `python-dotenv` - Environment variable management
- `opencv-python` - Video processing
- `loguru` - Logging

### 4. Run the agent in WSL2

```bash
python agent.py dev
```

### 5. Run frontend in Windows (separate terminal)

```powershell
# In Windows PowerShell
cd C:\Users\carlo\Documents\GitHub\agent-starter-react
pnpm dev
```

## Option 2: Linux/macOS Users

### 1. Navigate to agent directory

```bash
cd agent
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the agent

```bash
python agent.py dev
```

### 5. Run frontend (separate terminal)

```bash
cd ..
pnpm dev
```

## Environment Variables

All required environment variables are already set in `.env`:

```env
# LiveKit credentials
LIVEKIT_API_KEY=APIVpppzX9SPf56
LIVEKIT_API_SECRET=7WG2eAP43QefJ72zedJuHiDHFj6BIbKe4i1860es4IGB
LIVEKIT_URL=wss://avatar1-zm1yrt0z.livekit.cloud

# bitHuman credentials
BITHUMAN_API_SECRET=mXPLZYb1B6EkX1nuypI2qvSyt2xLjL3hSiVJkXuSsA25bT1CuNlEtEusxkxxl7CQb
BITHUMAN_AVATAR_ID=A48QHJ6779

# OpenAI API Key
OPENAI_API_KEY=sk-proj-...
```

## Testing the Setup

### 1. Agent should start successfully

You should see:
```
INFO:voice-agent:Connecting to room voice_assistant_room_XXXX
INFO:voice-agent:Starting bitHuman avatar...
INFO:voice-agent:Starting agent session...
INFO:voice-agent:Agent is ready and waiting for participants
```

### 2. Open the frontend

Navigate to http://localhost:3000

### 3. Start a call

1. Click "Start call"
2. Allow microphone access
3. Your bitHuman avatar should appear
4. Start talking!

## Troubleshooting

### "ModuleNotFoundError: No module named 'bithuman'"

**Windows**: You must use WSL2. The bitHuman SDK doesn't support Windows natively.

**Linux/macOS**: Make sure you ran `pip install -r requirements.txt`

### "OPENAI_API_KEY not set"

Check that your `.env` file has the `OPENAI_API_KEY` set correctly.

### Avatar not appearing

1. Check that BITHUMAN_API_SECRET is correct
2. Verify avatar ID `A48QHJ6779` exists in your bitHuman account
3. Check agent logs for errors

### Connection issues

1. Verify LIVEKIT_URL is accessible
2. Check LIVEKIT_API_KEY and LIVEKIT_API_SECRET are correct
3. Make sure both agent and frontend are running

## Alternative: Voice-Only Mode (Windows Compatible)

If you can't use WSL2, test with voice-only mode:

```powershell
cd agent
.\run_voice_only.ps1
```

This works on Windows but doesn't include the avatar.

## Resources

- [bitHuman SDK Examples](https://github.com/bithuman-ai/sdk-examples-python)
- [bitHuman Documentation](https://sdk.docs.bithuman.ai/)
- [LiveKit Agents Docs](https://docs.livekit.io/agents/)
- [bitHuman Console](https://imaginex.bithuman.ai/)

## Need Help?

1. **WSL2 Issues**: See [WINDOWS_LIMITATION.md](../WINDOWS_LIMITATION.md)
2. **Agent Issues**: Check agent logs for specific errors
3. **Frontend Issues**: Check browser console for errors
