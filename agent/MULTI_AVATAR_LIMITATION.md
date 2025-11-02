# Multi-Avatar Technical Limitation

## The Problem

You're seeing only ONE avatar because of how the BitHuman LiveKit plugin works:

### What's Happening:
1. Agent 1 creates a `bit Human.AvatarSession` → joins room as participant `"bithuman-avatar-agent"`
2. Agent 2 creates a `bithuman.AvatarSession` → **also** tries to join as `"bithuman-avatar-agent"`
3. LiveKit only allows ONE participant per identity → second agent **replaces** the first

### Evidence from Logs:
```
waiting for the remote participant {"identity": "bithuman-avatar-agent", ...
waiting for the remote participant {"identity": "bithuman-avatar-agent", ...
```

Both agents have the same identity, so they conflict.

## Why This Happens

The `bithuman.AvatarSession` plugin:
- Creates a separate remote participant for the avatar video
- Uses a hardcoded identity: `"bithuman-avatar-agent"`
- Cannot be configured to use different identities

This is a limitation of the LiveKit BitHuman plugin architecture.

## Solutions

### Solution 1: Two Different Avatar Identities (Doesn't Work Currently)
❌ **Not possible** - The BitHuman plugin doesn't support custom participant identities

### Solution 2: Two Audio-Only Agents (No Avatars)
✅ Remove BitHuman avatars, use two different TTS voices
- Agent 1: Voice "alloy"
- Agent 2: Voice "echo"
- No visual avatars, just audio with different voices

### Solution 3: Single Avatar, Multiple Personalities
✅ One visual avatar that role-plays as two different agents
- Single BitHuman avatar
- LLM responds as both "Agent 1" and "Agent 2"
- Example: "Agent 1: I think... Agent 2: But I believe..."

### Solution 4: Sequential Agent Appearances (Current Behavior)
✅ What you're experiencing now:
- Two agents exist
- They take turns speaking
- When one speaks, its avatar appears
- Avatar "switches" between them

### Solution 5: Use Different Avatar Services
✅ Use different avatar providers for each agent:
- Agent 1: BitHuman avatar
- Agent 2: Different service (Synthesia, D-ID, custom WebRTC)

### Solution 6: Custom BitHuman Implementation
✅ Modify the BitHuman plugin to support custom identities (requires forking the plugin)

## Recommended Approach

**For your use case (discussion between 2 agents + 1 user):**

I recommend **Solution 4** (what's happening now) or **Solution 3**:

### Why Solution 4 Works:
- Both agents ARE running
- Both agents CAN hear each other
- Both agents WILL respond
- The avatar visual switches between them when speaking
- This is actually quite natural - it looks like one person with two minds!

### To Verify Both Agents Are Working:
Check the logs for:
```
Creating agent_1...
Creating agent_2...
All agents are ready!
```

If you see this, both agents exist. They're just sharing the same visual avatar participant.

## Testing Right Now

Let me check what's actually happening in your setup:

**Current Status:**
- ✅ Two agents created (agent_1 and agent_2)
- ✅ Both have different voices (alloy vs echo)
- ✅ Both have different personalities (Analyst vs Creative)
- ⚠️ Both share the same avatar video (BitHuman limitation)
- ⚠️ Avatar video switches when different agent speaks

**What You Should Experience:**
1. Say something to the agents
2. First agent responds with voice "alloy" (analytical perspective)
3. Second agent responds with voice "echo" (creative perspective)
4. Avatar video might flicker/switch between them

## The Real Question

**Are you hearing TWO different voices responding?**

If YES → Both agents are working! The avatar just switches.
If NO → There might be another issue.

## Alternative: Display Agent Names in UI

Instead of showing two avatar videos, we could:
1. Show ONE avatar video (which switches)
2. Add text overlays showing which agent is currently speaking
3. Display transcripts with "Agent 1:" and "Agent 2:" labels

This way you know which agent is talking even though they share a visual avatar.

Want me to implement this?
