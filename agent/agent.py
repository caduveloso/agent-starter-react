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
logger = logging.getLogger("voice-agent")

# Model configuration
STT_MODEL = os.getenv("OPENAI_STT_MODEL", "whisper-1")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")
TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy")


def prewarm(proc: JobContext):
    """Prewarm process to load models before handling requests"""
    logger.info("Prewarm complete")


async def entrypoint(ctx: JobContext):
    """Main entry point for the agent"""

    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create the agent with instructions
    logger.info("Creating agent...")
    agent = Agent(
        instructions="You are a friendly voice assistant built by LiveKit.",
    )

    # Create the agent session with STT, LLM, and TTS
    logger.info("Creating agent session...")
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model=STT_MODEL),
        llm=openai.LLM(model=LLM_MODEL),
        tts=openai.TTS(model=TTS_MODEL, voice=TTS_VOICE),
    )

    # Create bitHuman avatar session using the avatar ID
    logger.info("Creating bitHuman avatar session...")
    avatar = bithuman.AvatarSession(
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779"),
        model="expression",  # Use 'expression' for dynamic emotional responses
    )

    # Start the avatar with the agent session
    logger.info("Starting bitHuman avatar with agent session...")
    await avatar.start(session, room=ctx.room)

    # Start the agent session with the agent
    logger.info("Starting agent session...")
    await session.start(agent=agent, room=ctx.room)

    logger.info("Agent is ready - avatar and session started")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
