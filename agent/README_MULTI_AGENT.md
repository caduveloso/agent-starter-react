# Multi-Agent System - Quick Reference

## Quick Start

### 1. Create Second Avatar on BitHuman
- Go to https://bithuman.ai/dashboard
- Create a new avatar (different from your first one)
- Copy the Avatar ID

### 2. Update .env
```bash
BITHUMAN_AVATAR_ID_1=A48QHJ6779      # Your first avatar
BITHUMAN_AVATAR_ID_2=YOUR_NEW_ID     # Your second avatar
DISCUSSION_TOPIC=the future of AI     # Optional topic
```

### 3. Run Multi-Agent System

**Basic Version** (simpler, good for testing):
```bash
python multi_agent.py dev
```

**Advanced Version** (full turn management & consensus):
```bash
python multi_agent_advanced.py dev
```

### 4. Start Frontend
```bash
pnpm dev
```

Open http://localhost:3000

## File Overview

| File | Purpose |
|------|---------|
| `multi_agent.py` | Basic multi-agent implementation with simple turn tracking |
| `multi_agent_advanced.py` | Advanced version with phases, consensus detection, and structured turns |
| `agent.py` | Original single-agent implementation (reference) |

## Architecture Differences

### Single Agent (agent.py)
```
User ←→ 1 Agent (with avatar)
```

### Multi-Agent (multi_agent.py, multi_agent_advanced.py)
```
        ┌─────────────────┐
        │   Turn Manager   │
        └────────┬─────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
  User      Agent 1      Agent 2
 (Human)   (Avatar 1)  (Avatar 2)
```

## Turn Order

Default turn order: **User → Agent 1 → Agent 2** (repeats)

All participants can hear each other!

## Key Classes

### TurnManager
- Tracks who speaks when
- Records conversation history
- Detects consensus (advanced version)
- Manages conversation phases (advanced version)

### MultiAgentCoordinator
- Creates and manages both agents
- Starts avatar sessions
- Coordinates turn-taking
- Handles room events

### SpeakerRole (Enum)
- `USER` - The human participant
- `AGENT_1` - First AI agent (Analyst role)
- `AGENT_2` - Second AI agent (Creative role)

### ConversationPhase (advanced only)
- `INTRODUCTION` - Initial thoughts
- `DISCUSSION` - Deep exploration
- `CONSENSUS` - Finding agreement
- `DECISION` - Making choice
- `CONCLUSION` - Wrapping up

## Customization Examples

### Change Turn Duration
```python
# In TurnState dataclass
max_turn_duration: float = 45.0  # seconds
```

### Modify Agent Personality
```python
# In create_agent call
instructions="""Your custom instructions here.
Make the agent behave however you want."""
```

### Change TTS Voice
```python
# In create_agent call
tts_voice="nova"  # Options: alloy, echo, fable, onyx, nova, shimmer
```

### Adjust Turn Order
```python
# In MultiAgentCoordinator.__init__
self.turn_manager = TurnManager([
    SpeakerRole.AGENT_1,   # Agent 1 first
    SpeakerRole.AGENT_2,   # Agent 2 second
    SpeakerRole.USER,      # User last
])
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Both agents have same voice | Set different `tts_voice` values |
| Both agents have same avatar | Use different avatar IDs in `.env` |
| Agents don't wait for turns | Use `multi_agent_advanced.py` |
| Can't hear agents | Check OpenAI API key, verify logs show "All agents are ready!" |
| Import errors | Run `pip install -r requirements.txt` |

## Logs to Watch For

**Successful startup:**
```
Creating agent_1...
Creating agent_2...
Starting agent 1 avatar and session...
Starting agent 2 avatar and session...
All agents are ready!
Turn management active
```

**During conversation:**
```
Turn 1: user is speaking
[user]: What do you think about AI?
Turn 2: agent_1 is speaking
[agent_1]: AI has tremendous potential...
Turn 3: agent_2 is speaking
[agent_2]: I agree, and I'd add that...
```

**Consensus detected (advanced version):**
```
Agreement detected! Count: 2
Round 1 completed
Consensus appears to be reached!
```

## Development Roadmap

### Current Features ✅
- 2 agents + 1 user in same room
- Turn tracking and history
- Consensus detection (advanced)
- Phase management (advanced)
- Context-aware agent prompts

### Future Enhancements 🚀
- [ ] Voting system
- [ ] Debate mode (agents argue opposing sides)
- [ ] 3+ agent support
- [ ] Custom consensus thresholds
- [ ] Sentiment analysis
- [ ] Meeting minutes generation
- [ ] Decision documentation

## Testing Checklist

Before deploying, verify:
- [ ] Two different BitHuman avatars created
- [ ] Both avatar IDs in `.env` file
- [ ] OpenAI API key valid
- [ ] LiveKit credentials configured
- [ ] Both agents start successfully (check logs)
- [ ] User can join room from browser
- [ ] User audio is heard by both agents
- [ ] Both agents respond in turn
- [ ] Turn order is respected (advanced version)

## Performance Notes

- **Latency**: ~2-5 seconds response time per agent
- **Concurrent rooms**: Each room gets its own agent pair
- **Resource usage**: 2x agents = 2x API calls per turn
- **Cost**: OpenAI costs multiply by 2 (STT, LLM, TTS for each agent)

## API Costs Estimate

Per conversation turn (all 3 speakers):
- STT: $0.006 per minute audio (3 speakers)
- LLM: $0.15 per 1M tokens (depends on length)
- TTS: $0.015 per 1K characters (2 agents speaking)

Example 10-minute conversation (~30 turns):
- STT: ~$0.06
- LLM: ~$0.50
- TTS: ~$0.30
- **Total**: ~$0.86

## Next Steps

1. ✅ Create second BitHuman avatar
2. ✅ Update `.env` with avatar IDs
3. ✅ Run `python multi_agent_advanced.py dev`
4. ✅ Test conversation flow
5. 🎯 Customize for your use case
6. 🚀 Build consensus/voting logic
7. 📊 Add decision tracking

## Need Help?

Check the full guide: [MULTI_AGENT_SETUP.md](../MULTI_AGENT_SETUP.md)

## Credits

Built on:
- [LiveKit Agents](https://docs.livekit.io/agents)
- [BitHuman Avatars](https://bithuman.ai)
- [OpenAI APIs](https://platform.openai.com)
