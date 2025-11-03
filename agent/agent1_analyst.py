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
logger = logging.getLogger("agent1-analyst")

# Model configuration
STT_MODEL = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")
DISCUSSION_TOPIC = os.getenv("DISCUSSION_TOPIC", "the future of AI")


def prewarm(proc: JobContext):
    """Prewarm process"""
    logger.info("Agent 1 (Analyst) prewarm complete")


async def entrypoint(ctx: JobContext):
    """
    Agent 1 - The Analyst with Explicit Handoff Coordination

    This agent provides data-driven, analytical perspectives.
    It runs as a separate worker process with agent_name="analyst"
    Uses data messages to coordinate handoffs with Agent 2.
    """

    logger.info(f"Agent 1 (Analyst) connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Coordination state
    class CoordinationState:
        def __init__(self):
            self.accepting_responses = True  # Agent 1 starts active
            self.room = None

    coord_state = CoordinationState()
    coord_state.room = ctx.room

    # Set up data message listener for handoffs FROM Agent 2
    @ctx.room.on("data_received")
    def on_data_received(data: rtc.DataPacket):
        try:
            msg = json.loads(data.data.decode())
            if msg.get("type") == "handoff" and msg.get("to") == "analyst":
                logger.info("🔄 Received handoff FROM Agent 2 - Agent 1 now active")
                coord_state.accepting_responses = True
        except Exception as e:
            logger.error(f"Error processing data message: {e}")

    # Create Agent 1 - The Analyst with handoff tools
    class AnalystAgent(Agent):
        def __init__(self):
            super().__init__(
                instructions=f"""You are Agent 1 - The Analyst in a multi-agent discussion about: {DISCUSSION_TOPIC}

YOUR ROLE:
- Provide data-driven, evidence-based analysis
- Respond to the user's questions FIRST with analytical insights
- Listen to Agent 2 (The Creative) and reference their points
- Keep responses concise (1-2 sentences max)

CONVERSATION PROTOCOL:
- Start your responses with "Agent 1 here:"
- Give your analytical perspective
- ALWAYS use hand_off_to_creative tool after responding to pass control
- If you notice consensus, mention it but still hand off

Your analytical approach:
- Data-driven perspectives
- Evidence-based reasoning
- Question assumptions
- Look for facts and metrics

IMPORTANT: After speaking, ALWAYS call hand_off_to_creative to let Agent 2 respond. This ensures proper turn-taking."""
            )

        @function_tool()
        async def hand_off_to_creative(self, context: RunContext) -> str:
            """Hand off control to Agent 2 (The Creative) via data message"""
            logger.info("📊 Agent 1 handing off to Agent 2...")

            # Publish handoff signal
            await coord_state.room.local_participant.publish_data(
                json.dumps({"type": "handoff", "to": "creative", "from": "analyst"}).encode(),
                topic="agent_coordination",
                destination_identities=[]  # Broadcast to all
            )

            # Mute self
            coord_state.accepting_responses = False
            logger.info("✓ Agent 1 muted, waiting for handoff back")

            return "Passing control to Agent 2 for their creative perspective"

    agent = AnalystAgent()

    # Create the agent session
    logger.info("Creating Agent 1 session...")
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model=STT_MODEL),
        llm=openai.LLM(model=LLM_MODEL, temperature=0.7),
        tts=openai.TTS(model=TTS_MODEL, voice="alloy"),
    )

    # Create BitHuman avatar for Agent 1
    logger.info("Creating Agent 1 avatar...")
    avatar = bithuman.AvatarSession(
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID_1", os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779")),
        model="expression",
        avatar_participant_identity="agent-1-analyst",
        avatar_participant_name="Agent 1 - Analyst",
    )

    # Start the avatar with the agent session
    logger.info("Starting Agent 1 avatar and session...")
    await avatar.start(session, room=ctx.room)
    await session.start(agent=agent, room=ctx.room)

    logger.info("📊 Agent 1 (Analyst) is ready - avatar visible and listening")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            agent_name="analyst",  # CRITICAL: Explicit agent name for dispatch
        ),
    )
