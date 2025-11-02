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
logger = logging.getLogger("agent-2")

# Model configuration
STT_MODEL = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")


def prewarm(proc: JobContext):
    """Prewarm process to load models before handling requests"""
    logger.info("Agent 2 prewarm complete")


async def entrypoint(ctx: JobContext):
    """Main entry point for Agent 2 (The Creative)"""

    logger.info(f"Agent 2 connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create Agent 2 - The Creative
    logger.info("Creating Agent 2 (The Creative)...")
    agent = Agent(
        instructions="""You are Agent 2 (The Creative) in a multi-agent discussion.

Your role:
- Offer creative and alternative perspectives
- Think outside the box and explore possibilities
- Keep your responses brief (1-2 sentences)
- Listen to the other agent and the user
- Help find innovative solutions and common ground

You are part of a team discussion. Build on what others say.""",
    )

    # Create the agent session with STT, LLM, and TTS
    logger.info("Creating Agent 2 session...")
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model=STT_MODEL),
        llm=openai.LLM(model=LLM_MODEL),
        tts=openai.TTS(model=TTS_MODEL, voice="echo"),  # Different voice from Agent 1
    )

    # Create bitHuman avatar session for Agent 2
    logger.info("Creating bitHuman avatar for Agent 2...")
    avatar = bithuman.AvatarSession(
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID_2", os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779")),
        model="expression",
    )

    # Start the avatar with the agent session
    logger.info("Starting Agent 2 avatar and session...")
    await avatar.start(session, room=ctx.room)
    await session.start(agent=agent, room=ctx.room)

    logger.info("Agent 2 is ready and listening!")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
