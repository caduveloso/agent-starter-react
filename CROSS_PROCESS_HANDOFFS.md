# Cross-Process Handoffs with Separate Avatars

## Overview

This system combines the **best of both worlds**:
- ✅ **Separate workers** (dual avatars, each controls its own video)
- ✅ **Explicit handoff workflow** (deterministic turn-taking via data messages)

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       LiveKit Room                            │
│                                                                │
│  ┌──────────────────────┐      ┌──────────────────────┐      │
│  │  Worker 1: Analyst   │      │  Worker 2: Creative  │      │
│  │  agent_name="analyst"│      │  agent_name="creative"│     │
│  ├──────────────────────┤      ├──────────────────────┤      │
│  │ AgentSession 1       │      │ AgentSession 2       │      │
│  │ Avatar 1 (Left)      │      │ Avatar 2 (Right)     │      │
│  │ accepting=TRUE       │      │ accepting=FALSE      │      │
│  └──────────────────────┘      └──────────────────────┘      │
│           │                              │                    │
│           └─────── Data Messages ────────┘                    │
│                                                                │
│   Handoff Flow via Data Messages:                             │
│   Agent 1: hand_off_to_creative() → publish_data()           │
│   Agent 2: receives data → accepting_responses = True         │
└──────────────────────────────────────────────────────────────┘
```

## How It Works

### Coordination State

Each agent tracks whether it should respond:

**Agent 1 (Analyst)**:
```python
coord_state.accepting_responses = True  # Starts ACTIVE
```

**Agent 2 (Creative)**:
```python
coord_state.accepting_responses = False  # Starts INACTIVE
```

### Handoff Mechanism

#### Agent 1 Hands Off to Agent 2

```python
@function_tool()
async def hand_off_to_creative(self, context: RunContext) -> str:
    # Publish data message
    await room.local_participant.publish_data(
        json.dumps({"type": "handoff", "to": "creative", "from": "analyst"}).encode(),
        topic="agent_coordination"
    )

    # Mute self
    coord_state.accepting_responses = False

    return "Passing control to Agent 2..."
```

#### Agent 2 Receives Handoff

```python
@room.on("data_received")
def on_data_received(data: rtc.DataPacket):
    msg = json.loads(data.data.decode())
    if msg.get("type") == "handoff" and msg.get("to") == "creative":
        # Unmute self
        coord_state.accepting_responses = True
```

#### Agent 2 Passes Back to Agent 1

```python
@function_tool()
async def pass_back_to_analyst(self, context: RunContext) -> str:
    # Publish data message
    await room.local_participant.publish_data(
        json.dumps({"type": "handoff", "to": "analyst", "from": "creative"}).encode(),
        topic="agent_coordination"
    )

    # Mute self
    coord_state.accepting_responses = False

    return "Passing control back to Agent 1..."
```

## Complete Conversation Flow

```
1. User connects → Both agents join room
   Agent 1: accepting_responses = TRUE (active)
   Agent 2: accepting_responses = FALSE (inactive)

2. User: "What do you think about AI?"
   ↓

3. Agent 1 (active) responds:
   "Agent 1 here: AI shows 40% productivity gains..."
   LEFT avatar animates 📊
   ↓

4. Agent 1 calls hand_off_to_creative tool
   ↓

5. Data message published:
   {"type": "handoff", "to": "creative", "from": "analyst"}
   ↓

6. Agent 2 receives data message:
   coord_state.accepting_responses = TRUE
   Agent 1: accepting_responses = FALSE
   ↓

7. Agent 2 (now active) responds:
   "Agent 2 here: Building on Agent 1's productivity insight..."
   RIGHT avatar animates 🎨
   ↓

8. Agent 2 calls pass_back_to_analyst tool
   ↓

9. Data message published:
   {"type": "handoff", "to": "analyst", "from": "creative"}
   ↓

10. Agent 1 receives data message:
    coord_state.accepting_responses = TRUE
    Agent 2: accepting_responses = FALSE
    ↓

11. Ready for user's next question → repeat cycle
```

## Key Files

### [agent1_analyst.py](agent/agent1_analyst.py)

**Handoff Tool** (Lines 97-113):
```python
@function_tool()
async def hand_off_to_creative(self, context: RunContext) -> str:
    """Hand off control to Agent 2 via data message"""
    await coord_state.room.local_participant.publish_data(...)
    coord_state.accepting_responses = False
    return "Passing control to Agent 2..."
```

**Data Listener** (Lines 60-68):
```python
@ctx.room.on("data_received")
def on_data_received(data: rtc.DataPacket):
    msg = json.loads(data.data.decode())
    if msg.get("type") == "handoff" and msg.get("to") == "analyst":
        coord_state.accepting_responses = True
```

### [agent2_creative.py](agent/agent2_creative.py)

**Handoff Tool** (Lines 98-114):
```python
@function_tool()
async def pass_back_to_analyst(self, context: RunContext) -> str:
    """Pass control back to Agent 1 via data message"""
    await coord_state.room.local_participant.publish_data(...)
    coord_state.accepting_responses = False
    return "Passing control back to Agent 1..."
```

**Data Listener** (Lines 60-68):
```python
@ctx.room.on("data_received")
def on_data_received(data: rtc.DataPacket):
    msg = json.loads(data.data.decode())
    if msg.get("type") == "handoff" and msg.get("to") == "creative":
        coord_state.accepting_responses = True
```

## Benefits

### vs. Instruction-Only Coordination

| Feature | Instruction-Only | Cross-Process Handoffs |
|---------|-----------------|----------------------|
| Turn-taking reliability | ⚠️ Depends on LLM | ✅ Explicit control |
| Separate avatars | ✅ Yes | ✅ Yes |
| Handoff visibility | ❌ Implicit | ✅ Explicit (logs) |
| Debugging | ⚠️ Hard to trace | ✅ Clear data flow |
| Scalability | ⚠️ Complex with 3+ agents | ✅ Easy to add more |

### vs. Single-Worker Handoffs

| Feature | Single-Worker | Cross-Process |
|---------|--------------|--------------|
| Handoff API | ✅ Native | ✅ Via data messages |
| Separate avatars | ❌ Conflict | ✅ Yes |
| BitHuman compatibility | ❌ Single session issue | ✅ Separate sessions |
| Scalability | ⚠️ All in one process | ✅ Distributed |

## Testing

### Expected Behavior

1. **Connect** - See both avatar thumbnails
2. **Ask a question** - Agent 1 responds first (left avatar)
3. **Watch handoff** - Agent 1 finishes, data message sent
4. **Agent 2 responds** - Right avatar animates
5. **Watch handoff back** - Agent 2 finishes, passes back
6. **No overlap** - Clean turn-taking

### Logs to Watch For

**Successful handoff FROM Agent 1:**
```
agent1-analyst-1   | 📊 Agent 1 handing off to Agent 2...
agent1-analyst-1   | ✓ Agent 1 muted, waiting for handoff back
agent2-creative-1  | 🔄 Received handoff FROM Agent 1 - Agent 2 now active
```

**Successful handoff TO Agent 1:**
```
agent2-creative-1  | 🎨 Agent 2 passing back to Agent 1...
agent2-creative-1  | ✓ Agent 2 muted, waiting for next handoff
agent1-analyst-1   | 🔄 Received handoff FROM Agent 2 - Agent 1 now active
```

### Monitor Logs

```bash
cd agent
docker compose logs -f
```

Look for handoff coordination messages showing the explicit control transfer.

## Advanced: Adding Agent 3

To add a third agent (e.g., "Mediator"):

1. **Create `agent3_mediator.py`**:
```python
@function_tool()
async def hand_off_to_analyst(self, context: RunContext) -> str:
    await room.publish_data({"type": "handoff", "to": "analyst"})

@function_tool()
async def hand_off_to_creative(self, context: RunContext) -> str:
    await room.publish_data({"type": "handoff", "to": "creative"})
```

2. **Update docker-compose.yml**:
```yaml
agent3-mediator:
  command: ["python", "agent3_mediator.py", "dev"]
```

3. **Update route.ts**:
```typescript
agents: [
  { agentName: 'analyst' },
  { agentName: 'creative' },
  { agentName: 'mediator' },
]
```

4. **Update handoff logic**:
- Agent 1 → Mediator → Agent 2 → Agent 1
- Or custom orchestration based on topic

## Troubleshooting

**Issue: Agents still talk over each other**
- Check logs for handoff messages
- Verify `accepting_responses` state changes
- Ensure data messages are being published/received

**Issue: Agent 2 never responds**
- Verify Agent 2 starts with `accepting_responses = False`
- Check Agent 1 is calling `hand_off_to_creative` tool
- Verify data listener is registered before session starts

**Issue: Data messages not received**
- Check room connection established before registering listeners
- Verify `topic="agent_coordination"` matches (though optional)
- Check for errors in data_received callback

## Future Enhancements

- **Round tracking**: Count handoff cycles
- **Consensus detection**: Detect when agents agree
- **Dynamic routing**: Route to different agents based on topic
- **State sharing**: Pass conversation context in handoff messages
- **Timeout handling**: Auto-handoff if agent doesn't respond

## References

- [LiveKit Data Messages](https://docs.livekit.io/realtime/client/data-messages/)
- [LiveKit Room Events](https://docs.livekit.io/realtime/client/events/)
- [Agent Function Tools](https://docs.livekit.io/agents/build/tools/)
