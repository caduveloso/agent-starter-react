# Multi-Agent System Setup Guide

This guide explains how to set up and run a multi-agent conversation system with 2 AI agents and 1 human user using LiveKit and BitHuman avatars.

## Overview

The multi-agent system allows:
- **2 AI Agents** with different BitHuman avatars to participate in discussions
- **1 Human User** to lead and participate in the conversation
- **Turn-taking logic** to manage who speaks when
- **Consensus detection** to identify when agreement is reached
- **Extensible framework** for future decision-making and voting logic

## Architecture

### Files Created

1. **[agent/multi_agent.py](agent/multi_agent.py)** - Basic multi-agent implementation
   - Two agents with separate avatars
   - Simple turn management
   - Conversation history tracking

2. **[agent/multi_agent_advanced.py](agent/multi_agent_advanced.py)** - Advanced implementation
   - Turn-based conversation with phases (Introduction → Discussion → Consensus → Decision → Conclusion)
   - Automatic consensus detection
   - Round tracking and agreement counting
   - Moderator system messages
   - Context-aware agent prompts

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                     LiveKit Room                             │
│                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │   User      │    │  Agent 1    │    │  Agent 2    │    │
│  │  (Human)    │    │ (Analyst)   │    │ (Creative)  │    │
│  │             │    │             │    │             │    │
│  │  Audio ─────┼───►│  Audio      │    │  Audio      │    │
│  │             │    │  STT        │    │  STT        │    │
│  │             │    │  LLM        │    │  LLM        │    │
│  │             │    │  TTS        │    │  TTS        │    │
│  │             │    │  Avatar 1   │    │  Avatar 2   │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Turn Manager (Coordinator)                    │  │
│  │  - Tracks current speaker                            │  │
│  │  - Manages turn order: User → Agent1 → Agent2        │  │
│  │  - Detects consensus                                 │  │
│  │  - Records conversation history                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Setup Instructions

### Step 1: Create a Second BitHuman Avatar

You need two different BitHuman avatars for the two agents:

1. **Go to BitHuman Dashboard**: https://bithuman.ai/dashboard
2. **Create First Avatar** (if you haven't already):
   - Click "Create Avatar"
   - Choose your preferred avatar style
   - Name it "Agent 1 - Analyst" (or similar)
   - Copy the Avatar ID (e.g., `A48QHJ6779`)

3. **Create Second Avatar**:
   - Click "Create Avatar" again
   - Choose a different avatar style to distinguish it visually
   - Name it "Agent 2 - Creative" (or similar)
   - Copy the Avatar ID (e.g., `B12XYZ3456`)

### Step 2: Update Environment Variables

Edit your [.env](.env) file with the avatar IDs:

```bash
# BitHuman API credentials (shared by both avatars)
BITHUMAN_API_SECRET=your_api_secret_here
BITHUMAN_AVATAR_ID=A48QHJ6779  # Original avatar (fallback)

# Multi-agent configuration
BITHUMAN_AVATAR_ID_1=A48QHJ6779  # First agent avatar ID
BITHUMAN_AVATAR_ID_2=B12XYZ3456  # Second agent avatar ID (CHANGE THIS!)

# Optional: Set discussion topic
DISCUSSION_TOPIC=the future of AI
```

### Step 3: Choose Your Implementation

**Option A: Basic Multi-Agent** (`multi_agent.py`)
- Simpler implementation
- Good for getting started
- Passive turn management

**Option B: Advanced Multi-Agent** (`multi_agent_advanced.py`)
- Full turn management with phases
- Consensus detection
- Better for structured discussions

### Step 4: Run the Multi-Agent System

#### Using Docker Compose (Recommended - Same as Before!)

Just like you've been doing with the single agent:

1. **Navigate to the agent directory**:
```bash
cd agent
```

2. **Edit docker-compose.yml** and uncomment the version you want:

```yaml
services:
  bithuman-agent:
    # ... other config ...
    # Change the command to run different agent versions:
    # Default: Single agent
    command: ["python", "agent.py", "dev"]
    # Multi-agent basic: uncomment the line below
    # command: ["python", "multi_agent.py", "dev"]
    # Multi-agent advanced: uncomment the line below (RECOMMENDED)
    # command: ["python", "multi_agent_advanced.py", "dev"]
```

3. **Run it**:
```bash
docker compose up
```

**That's it!** Same workflow as before, just change which Python file to run.

#### Alternative: Using WSL2 or Linux Directly

If you prefer to run without Docker:

1. **Install dependencies**:
```bash
cd agent
pip install -r requirements.txt
```

2. **Run the basic version**:
```bash
python multi_agent.py dev
```

3. **Or run the advanced version**:
```bash
python multi_agent_advanced.py dev
```

### Step 5: Start the Frontend

In a separate terminal:

```bash
pnpm dev
```

Open http://localhost:3000 in your browser.

### Step 6: Test the System

1. **Join the room** from the web interface
2. **Start speaking** - You'll see/hear both agents listening
3. **Agents will respond** in turn order:
   - User speaks first
   - Agent 1 (Analyst) responds
   - Agent 2 (Creative) adds perspective
   - Cycle repeats

## Turn Management Logic

### Basic Version
- Simple round-robin: User → Agent 1 → Agent 2 → User...
- Time limits per turn (30 seconds default)
- Conversation history tracking

### Advanced Version

#### Conversation Phases:
1. **Introduction** - Initial thoughts sharing
2. **Discussion** - Deep dive into the topic
3. **Consensus** - Finding agreement
4. **Decision** - Finalizing the conclusion
5. **Conclusion** - Wrapping up

#### Turn Control:
```python
# Turn order
[USER, AGENT_1, AGENT_2] → repeats

# Each turn has:
- Max duration (30s default)
- Context from previous turns
- Phase-specific instructions
```

#### Consensus Detection:
The system looks for agreement keywords:
- "agree"
- "consensus"
- "yes"
- "correct"
- "exactly"

When 2+ agreements detected after 1+ complete rounds → moves to conclusion phase.

## Customization

### Change Turn Order

Edit the `turn_order` in either file:

```python
self.turn_manager = TurnManager(
    turn_order=[
        SpeakerRole.AGENT_1,   # Agent 1 starts
        SpeakerRole.AGENT_2,   # Agent 2 next
        SpeakerRole.USER,      # User last
    ],
    topic=self.discussion_topic
)
```

### Modify Agent Personalities

Edit the agent instructions in the `create_agent` calls:

```python
# Make Agent 1 more skeptical
instructions="""You are a skeptical analyst.
Always question assumptions and ask for evidence.
Play devil's advocate to test ideas."""

# Make Agent 2 more supportive
instructions="""You are a supportive creative thinker.
Build on others' ideas and find connections.
Encourage collaboration and synthesis."""
```

### Adjust Turn Duration

```python
@dataclass
class TurnState:
    max_turn_duration: float = 45.0  # Increase to 45 seconds
```

### Change TTS Voices

Available OpenAI voices: `alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`

```python
tts_voice="nova"  # Try different voices
```

## Future Enhancements

### 1. Voting System
```python
class VoteManager:
    def __init__(self):
        self.votes = {}

    async def call_vote(self, proposal: str):
        # Each agent votes
        agent1_vote = await self.get_agent_vote(AGENT_1, proposal)
        agent2_vote = await self.get_agent_vote(AGENT_2, proposal)
        # Tally results
```

### 2. Debate Mode
```python
# Assign opposing positions
agent1_instructions = "Argue FOR the proposal"
agent2_instructions = "Argue AGAINST the proposal"
# User acts as judge
```

### 3. Expert Panel
```python
# 3+ agents with different expertise
agents = [
    ("Technical Expert", technical_instructions),
    ("Business Analyst", business_instructions),
    ("User Advocate", ux_instructions),
]
```

### 4. Consensus Metrics
```python
def calculate_consensus_score():
    # Analyze sentiment similarity
    # Check for repeated themes
    # Measure agreement percentage
    return score
```

## Troubleshooting

### Issue: Both agents have the same voice
**Solution**: Check that you're using different `tts_voice` values in the `create_agent` calls.

### Issue: Both agents have the same avatar
**Solution**: Verify you've set different avatar IDs in `.env`:
```bash
BITHUMAN_AVATAR_ID_1=A48QHJ6779
BITHUMAN_AVATAR_ID_2=B12XYZ3456  # Must be different!
```

### Issue: Agents don't take turns
**Solution**: The basic version doesn't enforce strict turns - they respond to audio. Use the advanced version for stricter turn management.

### Issue: Agents talk over each other
**Solution**: This is expected in the basic version. The advanced version has better turn control but may need tuning.

### Issue: No audio from agents
**Solution**:
1. Check OpenAI API key is valid
2. Verify both agents are initialized (check logs)
3. Ensure browser has microphone permissions

## LiveKit Configuration

### Do You Need Multiple Agent Workers?

**No!** A single agent worker process can run multiple agents. Both Agent 1 and Agent 2 are created within the same `multi_agent.py` process.

**Each room connection** runs its own multi-agent system with 2 agents + 1 user.

### If You Want Separate Worker Processes

You can run agents as separate workers:

1. **Create separate agent files**:
   - `agent1_worker.py` - Runs only Agent 1
   - `agent2_worker.py` - Runs only Agent 2

2. **Start multiple workers**:
```bash
python agent1_worker.py dev &
python agent2_worker.py dev &
```

But this is **not necessary** for your use case!

## Testing Scenarios

### Scenario 1: Simple Discussion
Topic: "What should we have for lunch?"
- User: "I'm thinking pizza or sushi"
- Agent 1: Analyzes nutrition, cost, delivery time
- Agent 2: Suggests creative fusion options
- Result: Consensus on sushi

### Scenario 2: Decision Making
Topic: "Should we implement feature X?"
- User: Presents the feature idea
- Agent 1: Analyzes technical feasibility
- Agent 2: Explores user experience impact
- System detects consensus or disagreement
- Result: Go/no-go decision

### Scenario 3: Brainstorming
Topic: "How can we improve our product?"
- Set phase to DISCUSSION
- Longer turn times (60s)
- Less strict consensus requirements
- Result: List of creative ideas

## Next Steps

1. **Create your second BitHuman avatar** ✅
2. **Update `.env` with both avatar IDs** ✅
3. **Choose basic or advanced version** ✅
4. **Run the system and test** ✅
5. **Customize agent personalities** (optional)
6. **Implement voting/consensus logic** (future)
7. **Add decision-making workflows** (future)

## Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents)
- [BitHuman Integration](https://docs.livekit.io/agents/integrations/avatar/bithuman/)
- [OpenAI TTS Voices](https://platform.openai.com/docs/guides/text-to-speech)
- [LiveKit Python SDK](https://docs.livekit.io/realtime/client-sdks/python/)

## Questions?

Check the logs for debugging:
- Look for "Creating agent_1..." and "Creating agent_2..."
- Verify "All agents are ready!"
- Watch for turn transitions in the log

Happy multi-agent conversing! 🤖🤝🤖
