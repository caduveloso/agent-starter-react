# Multi-Agent Quick Start

## TL;DR - Super Simple Steps

### 1. Create Second Avatar
- Go to https://bithuman.ai/dashboard
- Create a new avatar
- Copy the Avatar ID

### 2. Update .env
Edit `.env` in project root:
```bash
BITHUMAN_AVATAR_ID_2=YOUR_NEW_AVATAR_ID  # Line 11
```

### 3. Edit docker-compose.yml
In `agent/docker-compose.yml`, change line 14:

**For advanced multi-agent (recommended):**
```yaml
command: ["python", "multi_agent_advanced.py", "dev"]
```

**For basic multi-agent:**
```yaml
command: ["python", "multi_agent.py", "dev"]
```

**For single agent (original):**
```yaml
command: ["python", "agent.py", "dev"]
```

### 4. Run It
```bash
cd agent
docker compose up
```

### 5. Start Frontend
In another terminal:
```bash
pnpm dev
```

Open http://localhost:3000

## That's It!

You now have:
- 🤖 Agent 1 (Analyst personality)
- 🤖 Agent 2 (Creative personality)
- 👤 You (the user)

All in one room, taking turns talking!

## Turn Order

User → Agent 1 → Agent 2 → (repeat)

Everyone can hear each other!

## Full Documentation

- [Complete Setup Guide](../MULTI_AGENT_SETUP.md)
- [Technical Reference](./README_MULTI_AGENT.md)
