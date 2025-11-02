import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
    AgentSession,
    Agent,
)
from livekit.plugins import openai, silero, bithuman

# Load .env from project root (parent directory)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger("multi-agent-workaround")

# Model configuration
STT_MODEL = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")


def prewarm(proc: JobContext):
    """Prewarm process to load models before handling requests"""
    logger.info("Prewarm complete")


async def entrypoint(ctx: JobContext):
    """
    WORKAROUND: Multi-agent system with single avatar.

    Since BitHuman's AvatarSession creates a single participant with a fixed identity,
    we can't have two separate avatar participants simultaneously.

    Instead, this creates two AI agents that share the same avatar video stream.
    The agents alternate speaking but use the same visual avatar.
    """

    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create a single unified agent that switches between two personalities
    logger.info("Creating multi-personality agent...")

    agent = Agent(
        instructions="""You are a multi-agent discussion facilitator with two distinct personalities:

**Agent 1 (The Analyst)**: Analytical, data-driven, skeptical, asks for evidence
**Agent 2 (The Creative)**: Creative, big-picture thinker, explores possibilities

When responding:
1. First, respond as Agent 1 (analytical perspective)
2. Then, respond as Agent 2 (creative perspective)

Format your responses like:
"Agent 1: [analytical response]
Agent 2: [creative response]"

Keep each agent's response to 1-2 sentences. Make sure both perspectives are heard.
""")

    # Create the agent session
    logger.info("Creating agent session...")
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model=STT_MODEL),
        llm=openai.LLM(model=LLM_MODEL),
        tts=openai.TTS(model=TTS_MODEL, voice="alloy"),
    )

    # Create ONE bitHuman avatar session
    logger.info("Creating bitHuman avatar session...")
    avatar = bithuman.AvatarSession(
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779"),
        model="expression",
    )

    # Start the avatar with the agent session
    logger.info("Starting bitHuman avatar with agent session...")
    await avatar.start(session, room=ctx.room)

    # Start the agent session
    logger.info("Starting agent session...")
    await session.start(agent=agent, room=ctx.room)

    logger.info("Multi-personality agent is ready!")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
