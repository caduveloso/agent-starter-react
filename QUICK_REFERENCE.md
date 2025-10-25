# 🚀 Quick Reference - bitHuman Avatar Agent

## ⚡ Fastest Way to Test

### Windows (Voice-Only - No Avatar)
```powershell
cd agent
.\run_voice_only.ps1
# In new terminal:
pnpm dev
```
Open http://localhost:3000

### Windows (With Avatar - Use WSL2)
```bash
# One-time: Install WSL2
wsl --install -d Ubuntu
# Restart computer

# In WSL2 Ubuntu:
cd /mnt/c/Users/carlo/Documents/GitHub/agent-starter-react/agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python agent.py dev
```
```powershell
# In Windows PowerShell:
pnpm dev
```
Open http://localhost:3000

### Linux/macOS (With Avatar)
```bash
# Terminal 1:
cd agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python agent.py dev

# Terminal 2:
pnpm dev
```
Open http://localhost:3000

## 📁 Key Files

- **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Complete overview ⭐
- **[agent/SETUP_INSTRUCTIONS.md](agent/SETUP_INSTRUCTIONS.md)** - Detailed setup
- **[WINDOWS_LIMITATION.md](WINDOWS_LIMITATION.md)** - Windows/WSL2 guide
- **[agent/agent.py](agent/agent.py)** - Main agent code
- **[.env](.env)** - Configuration (already set up)

## 🔑 Environment Variables (Already Configured)

```env
LIVEKIT_API_KEY=APIVpppzX9SPf56
LIVEKIT_API_SECRET=7WG2eAP43QefJ72zedJuHiDHFj6BIbKe4i1860es4IGB
LIVEKIT_URL=wss://avatar1-zm1yrt0z.livekit.cloud
BITHUMAN_API_SECRET=mXPLZYb1B6EkX1nuypI2qvSyt2xLjL3hSiVJkXuSsA25bT1CuNlEtEusxkxxl7CQb
BITHUMAN_AVATAR_ID=A48QHJ6779
OPENAI_API_KEY=sk-proj-...
```

## ⚠️ Platform Support

- ✅ Linux
- ✅ macOS
- ⚠️ Windows (must use WSL2 for avatar)

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| `No module named 'bithuman'` | Windows: Use WSL2<br>Linux/macOS: Run `pip install -r requirements.txt` |
| Avatar not appearing | Check BITHUMAN_API_SECRET and avatar ID |
| Connection failed | Verify LiveKit credentials, ensure both agent and frontend running |
| OpenAI errors | Check OPENAI_API_KEY is set correctly |

## 📞 What to Expect

1. Start agent → See "Agent is ready"
2. Start frontend → Opens http://localhost:3000
3. Click "Start call" → Allow microphone
4. **With avatar**: See bitHuman avatar render
5. **Voice-only**: No video, just voice interaction
6. Speak → Avatar/agent responds with voice

## 📚 Full Documentation

Read [FINAL_SUMMARY.md](FINAL_SUMMARY.md) for complete information.
