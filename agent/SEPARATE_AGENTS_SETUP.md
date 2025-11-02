# Running Two Separate Agent Workers

## The Solution

Instead of running both agents in one Python process, we run **two separate agent worker processes**. Each worker:
- Connects to LiveKit independently
- Has its own BitHuman avatar participant
- Listens to the room and responds independently

This way, LiveKit sees them as **two different agent workers** that happen to join the same room.

## Files Created

1. **[agent1.py](agent1.py)** - Agent 1 (The Analyst) worker
2. **[agent2.py](agent2.py)** - Agent 2 (The Creative) worker
3. **[docker-compose.separate-agents.yml](docker-compose.separate-agents.yml)** - Runs both agents

## How to Run

### Stop Current Agent

```bash
cd agent
docker compose down
```

### Run Both Agents as Separate Workers

```bash
docker compose -f docker-compose.separate-agents.yml up
```

This will start:
- **Container 1**: agent-1-analyst (running agent1.py)
- **Container 2**: agent-2-creative (running agent2.py)

Both will connect to the same LiveKit room when a user joins!

## What You'll See

### In the Logs:
```
agent-1-analyst     | Agent 1 connecting to room...
agent-1-analyst     | Agent 1 is ready and listening!

agent-2-creative    | Agent 2 connecting to room...
agent-2-creative    | Agent 2 is ready and listening!
```

### In the Browser:
- Two separate avatar videos (if using different avatar IDs)
- OR two audio agents with different voices (if using same avatar ID)

## Expected Behavior

1. **User speaks**: Both agents hear you
2. **Agents respond**: They both respond (might talk over each other initially)
3. **Different voices**: Agent 1 = "alloy", Agent 2 = "echo"
4. **Different personalities**: Analyst vs Creative

## Important Notes

### Will They Take Turns?

❌ **No automatic turn-taking** with this approach. Both agents will respond independently when they detect speech.

If you want turn-taking, you need to use the `multi_agent_advanced.py` version, but that has the avatar limitation.

### Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| **Separate Workers** (this approach) | • Two distinct agents<br>• Can have different avatars<br>• True multi-agent | • No turn management<br>• Might talk over each other |
| **Single Process** (multi_agent_advanced.py) | • Turn management<br>• Organized discussion<br>• Consensus detection | • Share same avatar video<br>• One avatar identity |

## Testing

1. Run the separate agents
2. Open http://localhost:3000
3. Join the room
4. Say: "What do you both think about AI?"
5. Listen for both responses (different voices)

## Troubleshooting

### Only one agent responds
- Check logs - both should show "ready and listening"
- Make sure both containers are running: `docker ps`

### Agents talk at the same time
- This is expected! They're independent workers
- To fix: Use the single-process version with turn management

### Still only see one avatar
- Check if you have different avatar IDs in `.env`:
  ```
  BITHUMAN_AVATAR_ID_1=A48QHJ6779
  BITHUMAN_AVATAR_ID_2=YOUR_SECOND_AVATAR_ID
  ```
- If same ID: You'll hear different voices but see one avatar

## Recommendation

For your use case (structured discussion), I recommend:

**Option 1**: Use separate workers + add turn-taking logic to each agent's instructions:
```python
instructions="""You are Agent 1. Wait for Agent 2 to finish before responding."""
```

**Option 2**: Use the single-process multi_agent_advanced.py (accept that avatars share video)

**Option 3**: Remove avatars entirely, use voice-only with clear agent identification

Which do you prefer?
