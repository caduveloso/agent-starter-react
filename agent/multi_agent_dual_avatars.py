import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    AgentSession,
    Agent,
)
from livekit.plugins import openai, silero, bithuman

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger("multi-agent-dual-avatars")

# Model configuration
STT_MODEL = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")
DISCUSSION_TOPIC = os.getenv("DISCUSSION_TOPIC", "various topics")


def prewarm(proc: JobContext):
    """Prewarm process"""
    logger.info("Prewarm complete")


async def entrypoint(ctx: JobContext):
    """
    Dual avatar display with coordinated turn-taking.

    Creates two BitHuman avatar sessions that will each create a video participant.
    Both agents listen but only respond at their designated turn.
    """

    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create Agent 1 - The Analyst (responds on odd turns)
    logger.info("Creating Agent 1 (The Analyst)...")
    agent1 = Agent(
        instructions=f"""You are Agent 1 - The Analyst in a two-agent discussion about: {DISCUSSION_TOPIC}

Your role:
- Provide analytical, data-driven, evidence-based perspectives
- Question assumptions and look for facts
- Respond with 1-2 sentences maximum
- YOU SPEAK FIRST after each user question
- Keep responses brief and analytical

Start your responses with "Agent 1 here." so the user knows who's speaking."""
    )

    session1 = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model=STT_MODEL),
        llm=openai.LLM(model=LLM_MODEL),
        tts=openai.TTS(model=TTS_MODEL, voice="alloy"),
    )

    # Create Agent 2 - The Creative (responds on even turns)
    logger.info("Creating Agent 2 (The Creative)...")
    agent2 = Agent(
        instructions=f"""You are Agent 2 - The Creative in a two-agent discussion about: {DISCUSSION_TOPIC}

Your role:
- Provide creative, imaginative, alternative perspectives
- Think outside the box and explore possibilities
- Respond with 1-2 sentences maximum
- YOU SPEAK SECOND, after Agent 1 finishes
- Build on or challenge Agent 1's analytical points

Start your responses with "Agent 2 here." so the user knows who's speaking."""
    )

    session2 = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model=STT_MODEL),
        llm=openai.LLM(model=LLM_MODEL),
        tts=openai.TTS(model=TTS_MODEL, voice="echo"),
    )

    # Create FIRST BitHuman avatar for Agent 1 with CUSTOM IDENTITY
    logger.info("Creating BitHuman avatar for Agent 1 with custom identity...")
    avatar1 = bithuman.AvatarSession(
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID_1", os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779")),
        model="expression",
        avatar_participant_identity="agent-1-analyst-avatar",  # Custom identity!
        avatar_participant_name="Agent 1 - Analyst",
    )

    # Create SECOND BitHuman avatar for Agent 2 with DIFFERENT IDENTITY
    logger.info("Creating BitHuman avatar for Agent 2 with custom identity...")
    avatar2 = bithuman.AvatarSession(
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID_2", os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779")),
        model="expression",
        avatar_participant_identity="agent-2-creative-avatar",  # Different identity!
        avatar_participant_name="Agent 2 - Creative",
    )

    # Start first avatar and session
    logger.info("Starting Agent 1 avatar and session...")
    await avatar1.start(session1, room=ctx.room)
    await session1.start(agent=agent1, room=ctx.room)

    # Small delay to help differentiate the avatar participants
    await asyncio.sleep(1)

    # Start second avatar and session
    logger.info("Starting Agent 2 avatar and session...")
    await avatar2.start(session2, room=ctx.room)
    await session2.start(agent=agent2, room=ctx.room)

    logger.info("=" * 70)
    logger.info("🤖🤖  Dual-Avatar System Ready!")
    logger.info("     Agent 1 (Analyst - left) + Agent 2 (Creative - right)")
    logger.info("     Both avatars visible, taking turns speaking")
    logger.info("=" * 70)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
