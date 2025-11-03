# Professional Multi-Agent System with LiveKit Handoffs

## Overview

This implementation uses **LiveKit's native agent handoff workflow** - the professional approach for coordinated multi-agent conversations. Instead of both agents listening simultaneously and trying to coordinate through timing or instructions, agents explicitly pass control to each other using LiveKit's handoff API.

## How It Works

### Architecture

```
User speaks
    ↓
Agent 1 (Analyst) responds
    ↓
Agent 1 calls hand_off_to_creative tool
    ↓
[LiveKit transfers control]
    ↓
Agent 2 (Creative) receives full conversation context
    ↓
Agent 2 responds (aware of what Agent 1 said)
    ↓
Agent 2 calls pass_back_to_analyst tool
    ↓
[LiveKit transfers control back]
    ↓
Repeat cycle...
```

### Key Features

1. **Turn Coordination**: One agent speaks, finishes completely, then explicitly hands off
2. **Context Awareness**: Each agent receives the full conversation history
3. **State Management**: Shared `ConversationState` tracks round numbers and progress
4. **Consensus Detection**: Built-in tools for agents to declare consensus
5. **Dual Avatars**: Both BitHuman avatars visible as thumbnails throughout

## Implementation Details

### Agent Handoff Pattern

```python
@function_tool()
async def hand_off_to_creative(self, context: RunContext) -> tuple[Agent, str]:
    """Hand off control to Agent 2"""
    return creative_agent, "Handing off to the creative agent"
```

When Agent 1 calls this tool:
- LiveKit completes Agent 1's current response
- Transfers control to `creative_agent`
- Agent 2's `on_enter()` method is called
- Agent 2 receives full conversation context
- Agent 2 can now respond

### Shared Session

Both agents share a single `AgentSession`:
```python
session = AgentSession(
    vad=silero.VAD.load(),
    stt=openai.STT(),
    llm=openai.LLM(),
    tts=openai.TTS(),
)
session.userdata = conversation_state  # Shared state
```

### Dual Avatar Display

Both BitHuman avatars are started with unique identities:
```python
avatar1 = bithuman.AvatarSession(
    avatar_participant_identity="agent-1-analyst",
    avatar_participant_name="Agent 1 - Analyst",
)
avatar2 = bithuman.AvatarSession(
    avatar_participant_identity="agent-2-creative",
    avatar_participant_name="Agent 2 - Creative",
)
```

Both avatars remain visible as thumbnails in the frontend.

## Why This Approach?

### Professional Benefits

1. **LiveKit Native**: Uses LiveKit's built-in features, not workarounds
2. **Reliable**: No race conditions or timing dependencies
3. **Scalable**: Easy to add more agents or complex workflows
4. **Future-Proof**: Built on documented LiveKit patterns
5. **Context Preservation**: Full conversation history maintained automatically

### vs. Previous Approaches

| Approach | Issue |
|----------|-------|
| Timing delays | Unpredictable, agents still overlap |
| Instructions only | LLMs don't reliably follow turn-taking rules |
| Event hooks | Events we needed don't exist in SDK |
| Data messages | More complex, lower-level coordination |
| **Handoffs** ✅ | **Professional, native, reliable** |

## Testing

1. Start the system: `docker compose up`
2. Connect via the web interface
3. Ask a question about "the future of AI" (or your configured topic)
4. Observe:
   - Agent 1 responds first with analytical perspective
   - Agent 1 completes fully before Agent 2 starts
   - Agent 2 references Agent 1's specific points
   - Both avatars remain visible as thumbnails
   - Clean handoff with no overlap

## Future Enhancements

- **Rounds**: Track multi-round debates with state
- **Consensus**: Detect when agents reach agreement
- **Decision Making**: Implement voting or combined recommendations
- **More Agents**: Add specialized agents (mediator, fact-checker, etc.)
- **Phases**: Move through structured discussion phases

## References

- [LiveKit Workflows Documentation](https://docs.livekit.io/agents/build/workflows/)
- [LiveKit Agent Handoffs](https://docs.livekit.io/agents/build/tools/)
- [BitHuman Avatar Integration](https://docs.livekit.io/agents/integrations/avatar/bithuman/)
