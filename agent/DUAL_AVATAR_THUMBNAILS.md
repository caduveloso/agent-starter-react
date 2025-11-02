# Dual Avatar Thumbnails Setup

## What This Does

Creates **two separate avatar video thumbnails** side-by-side in your UI:

```
┌──────────────────────────────────────┐
│                                      │
│   ┌────────────┐  ┌────────────┐   │
│   │  Agent 1   │  │  Agent 2   │   │
│   │  Analyst   │  │  Creative  │   │
│   │ 🔍         │  │ 💡         │   │
│   └────────────┘  └────────────┘   │
│                                      │
└──────────────────────────────────────┘
```

## Features

✅ **Two visible avatar thumbnails** (left = Analyst, right = Creative)
✅ **Color-coded labels** (blue for Agent 1, purple for Agent 2)
✅ **Role badges** (🔍 Analytical, 💡 Creative)
✅ **Pulsing indicators** when active
✅ **Different voices** (alloy vs echo)
✅ **Both agents listen and respond**

## How to Run

### 1. Update Your .env (Optional)

If you created two different BitHuman avatars:

```bash
BITHUMAN_AVATAR_ID_1=A48QHJ6779      # First avatar
BITHUMAN_AVATAR_ID_2=B12XYZ3456      # Second avatar (different visual)
```

If you're using the same avatar ID for both (they'll look the same but have different labels):
```bash
# Just keep your existing:
BITHUMAN_AVATAR_ID=A48QHJ6779
```

### 2. Stop Current Agents

```bash
cd agent
docker compose down
```

### 3. Start Dual Avatar System

The docker-compose.yml is already configured:

```bash
docker compose up
```

### 4. Open Frontend

In another terminal:
```bash
pnpm dev
```

Open http://localhost:3000

## What You'll See

### In the Logs:
```
Creating Agent 1 (The Analyst)...
Creating Agent 2 (The Creative)...
Creating BitHuman avatar for Agent 1...
Creating BitHuman avatar for Agent 2...
Starting Agent 1 avatar and session...
Starting Agent 2 avatar and session...
🤖🤖  Dual-Avatar System Ready!
```

### In the Browser:

**Before speaking:**
- Two avatar thumbnails side by side
- Agent 1 (Analyst) on the left with blue label and 🔍
- Agent 2 (Creative) on the right with purple label and 💡

**After you speak:**
- Both agents listen
- Both agents respond (may overlap initially)
- Labels show which agent is which

## Visual Design

### Full Screen (Chat Closed):
- Both avatars are large, side by side
- Max width 400px each
- Role badges in top-right corner
- Colored labels at bottom

### Chat Open:
- Both avatars shrink to 90x90px thumbnails
- Still side by side
- Labels remain visible

## Avatar IDs

### Same Avatar ID:
- Both thumbnails show the SAME avatar face
- Different labels/colors distinguish them
- They still have different voices and personalities

### Different Avatar IDs:
- Each thumbnail shows a DIFFERENT avatar face
- Visual distinction + label distinction
- Different voices and personalities

## Technical Details

### Backend ([multi_agent_dual_avatars.py](multi_agent_dual_avatars.py)):
- Creates 2 separate `AgentSession` instances
- Creates 2 separate `bithuman.AvatarSession` instances
- Each publishes its own video track to the room
- 1-second delay between starting them (helps avoid conflicts)

### Frontend ([tile-layout.tsx](../components/app/tile-layout.tsx)):
- Detects multiple avatar video tracks
- Renders them side-by-side with `flex gap-4`
- Adds colored labels and role badges
- Animates them smoothly

## Potential Issues

### Only One Avatar Appears:
**Cause:** Both BitHuman sessions might be using the same participant identity

**Solution:** This is a known limitation. The backend tries to work around it with timing delays. If you still see only one avatar, the identities are colliding.

**Workaround:** Use `multi_agent_simple.py` instead (one avatar, both agents speak through it)

### Avatars Talk Over Each Other:
**Cause:** Both agents respond independently without coordination

**Solution:** This is expected in the current version. Both agents hear you and respond.

**Future Fix:** Add turn coordination (complex, needs agent state management)

### Different Avatar Faces Not Showing:
**Check:**
1. Do you have two different avatar IDs in `.env`?
2. Are both BitHuman avatars created on the BitHuman dashboard?
3. Check logs - do both avatar sessions start successfully?

## Comparison

| Version | Avatars Visible | Turn Taking | Complexity |
|---------|----------------|-------------|------------|
| **multi_agent_dual_avatars.py** (this) | 2 thumbnails | ❌ May overlap | Medium |
| multi_agent_simple.py | 1 shared | ✅ Perfect | Low |
| multi_agent_advanced.py | 1 shared | ⚠️ Complex | High |

## Next Steps

To add proper turn coordination to this dual-avatar setup:

1. **Option A:** Add turn logic in agent instructions:
   ```python
   instructions="Wait for Agent 2 to finish before responding..."
   ```

2. **Option B:** Use LiveKit data messages to coordinate:
   ```python
   # Agent 1 publishes "my_turn_done"
   # Agent 2 waits for that signal before responding
   ```

3. **Option C:** Use a moderator agent that calls on each agent:
   ```python
   # Moderator: "Agent 1, what do you think?"
   # Agent 1 responds
   # Moderator: "Agent 2, your thoughts?"
   # Agent 2 responds
   ```

## Recommendation

**If you want visual distinction:** Use this dual avatar version

**If you want perfect turn-taking:** Use `multi_agent_simple.py`

**Best of both worlds:** This version + add turn coordination logic later

Try it now!
```bash
docker compose up
```

Then open http://localhost:3000 and see both avatar thumbnails! 🎉
