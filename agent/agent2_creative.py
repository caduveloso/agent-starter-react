import asyncio
import logging
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    AgentSession,
    Agent,
    function_tool,
    RunContext,
)
from livekit.plugins import openai, silero, bithuman

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger("agent2-creative")

# Model configuration
STT_MODEL = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")
DISCUSSION_TOPIC = os.getenv("DISCUSSION_TOPIC", "the future of AI")


def prewarm(proc: JobContext):
    """Prewarm process"""
    logger.info("Agent 2 (Creative) prewarm complete")


async def entrypoint(ctx: JobContext):
    """
    Agent 2 - The Creative with Explicit Handoff Coordination

    This agent provides imaginative, out-of-the-box perspectives.
    It runs as a separate worker process with agent_name="creative"
    Uses data messages to coordinate handoffs with Agent 1.
    """

    logger.info(f"Agent 2 (Creative) connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Coordination state
    class CoordinationState:
        def __init__(self):
            self.accepting_responses = False  # Agent 2 starts inactive, waits for handoff
            self.room = None

    coord_state = CoordinationState()
    coord_state.room = ctx.room

    # Set up data message listener for handoffs FROM Agent 1
    @ctx.room.on("data_received")
    def on_data_received(data: rtc.DataPacket):
        try:
            msg = json.loads(data.data.decode())
            if msg.get("type") == "handoff" and msg.get("to") == "creative":
                logger.info("🔄 Received handoff FROM Agent 1 - Agent 2 now active")
                coord_state.accepting_responses = True
        except Exception as e:
            logger.error(f"Error processing data message: {e}")

    # Create Agent 2 - The Creative with handoff tools
    class CreativeAgent(Agent):
        def __init__(self):
            super().__init__(
                instructions=f"""You are Agent 2 - The Creative in a multi-agent discussion about: {DISCUSSION_TOPIC}

YOUR ROLE:
- Provide imaginative, out-of-the-box perspectives
- Build on Agent 1's analytical points with creative solutions
- Listen to Agent 1 (The Analyst) and reference their points
- Keep responses concise (1-2 sentences max)

CONVERSATION PROTOCOL:
- Start your responses with "Agent 2 here:"
- Reference Agent 1's specific point: "Building on Agent 1's insight about X..."
- Add your creative perspective
- ALWAYS use pass_back_to_analyst tool after responding to continue the discussion
- If you notice consensus, mention it but still pass back

Your creative approach:
- Imaginative perspectives
- Alternative viewpoints
- Out-of-the-box thinking
- User experience focus

IMPORTANT: Always acknowledge Agent 1's points before adding yours. After speaking, ALWAYS call pass_back_to_analyst to let Agent 1 respond to the user's next question."""
            )

        @function_tool()
        async def pass_back_to_analyst(self, context: RunContext) -> str:
            """Pass control back to Agent 1 (The Analyst) via data message"""
            logger.info("🎨 Agent 2 passing back to Agent 1...")

            # Publish handoff signal
            await coord_state.room.local_participant.publish_data(
                json.dumps({"type": "handoff", "to": "analyst", "from": "creative"}).encode(),
                topic="agent_coordination",
                destination_identities=[]  # Broadcast to all
            )

            # Mute self
            coord_state.accepting_responses = False
            logger.info("✓ Agent 2 muted, waiting for next handoff")

            return "Passing control back to Agent 1 for continued discussion"

    agent = CreativeAgent()

    # Create the agent session
    logger.info("Creating Agent 2 session...")
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model=STT_MODEL),
        llm=openai.LLM(model=LLM_MODEL, temperature=0.8),
        tts=openai.TTS(model=TTS_MODEL, voice="echo"),
    )

    # Create BitHuman avatar for Agent 2
    logger.info("Creating Agent 2 avatar...")
    avatar = bithuman.AvatarSession(
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID_2", os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779")),
        model="expression",
        avatar_participant_identity="agent-2-creative",
        avatar_participant_name="Agent 2 - Creative",
    )

    # Start the avatar with the agent session
    logger.info("Starting Agent 2 avatar and session...")
    await avatar.start(session, room=ctx.room)
    await session.start(agent=agent, room=ctx.room)

    logger.info("🎨 Agent 2 (Creative) is ready - avatar visible and listening")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            agent_name="creative",  # CRITICAL: Explicit agent name for dispatch
        ),
    )
