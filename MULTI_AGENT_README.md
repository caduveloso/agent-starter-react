# Multi-Agent System with Dual Avatars

## What This Is

A LiveKit-based multi-agent discussion system featuring:
- ✅ **Two AI agents** with distinct personalities and voices
- ✅ **Two separate avatar videos** displayed side-by-side
- ✅ **Turn-taking coordination** to prevent overlap
- ✅ **Real-time voice interaction** with a human user

## Features

### Visual Display
- **Agent 1 (Analyst)**: Blue label, 🔍 Analytical badge, "alloy" voice
- **Agent 2 (Creative)**: Purple label, 💡 Creative badge, "echo" voice
- Both avatars visible simultaneously with custom labels

### Agent Personalities
- **Agent 1**: Analytical, data-driven, evidence-based, asks for facts
- **Agent 2**: Creative, imaginative, thinks outside the box

### Turn Management
- Agent 1 speaks first (2-second delay after user)
- Agent 2 speaks second (5-second delay, after Agent 1)
- Both keep responses brief (1 sentence)
- Agents only respond to USER, not to each other

## Quick Start

### 1. Setup Environment

Make sure your `.env` file has:
```bash
# LiveKit credentials
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
LIVEKIT_URL=your_livekit_url

# BitHuman credentials
BITHUMAN_API_SECRET=your_bithuman_secret

# Avatar IDs (can be same or different)
BITHUMAN_AVATAR_ID_1=A48QHJ6779
BITHUMAN_AVATAR_ID_2=B12XYZ3456  # Use different ID for visual distinction

# OpenAI
OPENAI_API_KEY=your_openai_key

# Optional: Discussion topic
DISCUSSION_TOPIC=the future of AI
```

### 2. Run the System

```bash
cd agent
docker compose up
```

### 3. Start Frontend

In another terminal:
```bash
pnpm dev
```

Open http://localhost:3000

## How It Works

### Key Innovation: Custom Participant Identities

The breakthrough was using `avatar_participant_identity`:

```python
avatar1 = bithuman.AvatarSession(
    avatar_id="AVATAR_ID_1",
    avatar_participant_identity="agent-1-analyst-avatar",  # Unique!
    avatar_participant_name="Agent 1 - Analyst",
)

avatar2 = bithuman.AvatarSession(
    avatar_id="AVATAR_ID_2",
    avatar_participant_identity="agent-2-creative-avatar",  # Different!
    avatar_participant_name="Agent 2 - Creative",
)
```

This creates **two separate video participants** in the LiveKit room instead of one.

### Turn Coordination

Agents coordinate through:
1. **Timing delays** (`min_endpointing_delay`)
   - Agent 1: 2 seconds
   - Agent 2: 5 seconds
2. **Clear instructions** to only respond to USER
3. **Brief responses** (1 sentence each)

## Files

### Active Files
- `agent/multi_agent_dual_avatars.py` - Main agent code
- `agent/docker-compose.yml` - Docker configuration
- `agent/Dockerfile` - Container setup
- `agent/requirements.txt` - Python dependencies
- `agent/README.md` - Agent-specific docs

### Removed Files
All experimental and outdated approaches have been cleaned up:
- ❌ `multi_agent_simple.py` - Single personality approach
- ❌ `multi_agent_advanced.py` - Complex turn management
- ❌ `agent1.py` / `agent2.py` - Separate worker attempts
- ❌ Various outdated documentation files

## Configuration

### Change Agent Personalities

Edit in `multi_agent_dual_avatars.py`:

```python
agent1 = Agent(
    instructions="""Your custom Agent 1 instructions here..."""
)

agent2 = Agent(
    instructions="""Your custom Agent 2 instructions here..."""
)
```

### Adjust Turn Timing

```python
session1 = AgentSession(
    ...
    min_endpointing_delay=2.0,  # Agent 1 waits 2 seconds
)

session2 = AgentSession(
    ...
    min_endpointing_delay=5.0,  # Agent 2 waits 5 seconds
)
```

### Change Voices

Available OpenAI TTS voices: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

```python
tts=openai.TTS(model=TTS_MODEL, voice="nova"),  # Change here
```

## Usage Example

**User:** "What do you think about AI in education?"

**Agent 1 (Analyst):** "Agent 1 here. Studies show AI tutoring can improve test scores by 15-20% on average."

**Agent 2 (Creative):** "Agent 2 here. Imagine learning that adapts to each student's curiosity in real-time, not just performance."

## Frontend Integration

The frontend ([components/app/tile-layout.tsx](components/app/tile-layout.tsx)) automatically:
- Detects multiple avatar video tracks
- Renders them side-by-side
- Adds colored labels and role badges
- Handles responsive layout (full screen vs chat mode)

## Future Enhancements

### Consensus Detection
Add logic to detect when agents reach agreement:
```python
if "agree" in agent1_response and "agree" in agent2_response:
    announce_consensus()
```

### Voting System
Let agents vote on proposals:
```python
vote1 = agent1.vote(proposal)
vote2 = agent2.vote(proposal)
decision = tally_votes([vote1, vote2])
```

### Round Management
Track discussion rounds and phases:
```python
phases = [INTRODUCTION, DISCUSSION, CONSENSUS, DECISION]
current_phase = advance_phase()
```

## Troubleshooting

### Only One Avatar Appears
- Check logs for participant identities
- Ensure both avatars use DIFFERENT `avatar_participant_identity`
- Verify both BitHuman avatars are created on dashboard

### Agents Talk Over Each Other
- Increase `min_endpointing_delay` values
- Make instructions more explicit about waiting
- Reduce response length requirements

### No Audio from Agents
- Verify OpenAI API key is valid
- Check browser microphone permissions
- Ensure both agents show "ready" in logs

## Cost Considerations

Per user conversation (10 minutes, ~30 total utterances):
- **STT**: ~$0.06 (3 speakers: user + 2 agents hearing each other)
- **LLM**: ~$1.00 (2 agents processing separately)
- **TTS**: ~$0.30 (2 agents speaking)
- **Total**: ~$1.36 per 10-minute conversation

## Credits

Built with:
- [LiveKit Agents](https://docs.livekit.io/agents)
- [BitHuman Avatars](https://bithuman.ai)
- [OpenAI APIs](https://platform.openai.com)
- [LiveKit Components React](https://github.com/livekit/components-js)

## Success! 🎉

You now have a working multi-agent system with:
- Two distinct AI personalities
- Two separate avatar videos
- Coordinated turn-taking
- Professional UI with labels and badges

The key breakthrough was discovering the `avatar_participant_identity` parameter!
