# ⚡ WSL2 Quick Start - Get bitHuman Working in 5 Minutes

## Why WSL2?

The `bithuman` Python package is **only available for Linux/macOS**, not Windows.
WSL2 (Windows Subsystem for Linux) lets you run Linux on Windows easily.

## Step 1: Install WSL2 (One-Time Setup - 2 minutes)

Open PowerShell as Administrator and run:

```powershell
wsl --install -d Ubuntu
```

**Restart your computer** when prompted.

## Step 2: First Time Ubuntu Setup (1 minute)

After restart, Ubuntu will open automatically:

1. Create a username (e.g., `carlo`)
2. Create a password
3. Done!

## Step 3: Navigate to Your Project (30 seconds)

In the Ubuntu terminal:

```bash
cd /mnt/c/Users/carlo/Documents/GitHub/agent-starter-react/agent
```

> **Note**: Windows drives are mounted at `/mnt/c/`, `/mnt/d/`, etc.

## Step 4: Install Python & Dependencies (2 minutes)

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

This will install everything including the `bithuman` SDK (which works on Linux).

## Step 5: Run the Agent (5 seconds)

```bash
python agent.py dev
```

You should see:
```
INFO:voice-agent:Connecting to room voice_assistant_room_XXXX
INFO:voice-agent:Starting bitHuman avatar...
INFO:voice-agent:Agent is ready and waiting for participants
```

## Step 6: Run Frontend in Windows (Separate Terminal)

**Open a NEW PowerShell window** (keep Ubuntu running):

```powershell
cd C:\Users\carlo\Documents\GitHub\agent-starter-react
pnpm dev
```

## Step 7: Test It! (10 seconds)

1. Open http://localhost:3000
2. Click "Start call"
3. Allow microphone
4. **See your bitHuman avatar!**
5. Start talking!

## 🎉 Done!

Your bitHuman avatar is now working!

---

## Tips & Tricks

### Access WSL2 Anytime

Just search for "Ubuntu" in Windows Start menu

### Stop the Agent

In Ubuntu terminal: Press `Ctrl+C`

### Run Again Later

```bash
# In Ubuntu terminal:
cd /mnt/c/Users/carlo/Documents/GitHub/agent-starter-react/agent
source venv/bin/activate
python agent.py dev
```

### Edit Files

You can still use VS Code in Windows! WSL2 shares the same files.

### Check if Agent is Running

Look for "Agent is ready and waiting for participants" message

## Troubleshooting

### "command not found: python3"

Run: `sudo apt install python3 python3-pip python3-venv`

### "No module named X"

Make sure you activated venv: `source venv/bin/activate`

Then: `pip install -r requirements.txt`

### Can't find project folder

The path is: `/mnt/c/Users/carlo/Documents/GitHub/agent-starter-react/agent`

### Agent won't start

1. Check `.env` has all API keys set
2. Verify `OPENAI_API_KEY` is set
3. Check `BITHUMAN_API_SECRET` is correct

## Why This Works

- ✅ WSL2 = Real Linux on Windows
- ✅ `bithuman` package available for Linux
- ✅ Frontend still runs in Windows
- ✅ They communicate via LiveKit (network)
- ✅ No Docker, no VM, just works!

## Next Steps

Once it's working, you might want to:
- Customize agent personality in `agent.py`
- Try different avatar models from bitHuman console
- Deploy to production Linux server

---

**Total time: ~5 minutes** ⚡

The agent setup is perfect - it just needs Linux to run, and WSL2 gives you that instantly!
