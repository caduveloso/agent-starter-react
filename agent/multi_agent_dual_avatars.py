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

    # Create Agent 1 - The Analyst (speaks first, then pauses)
    logger.info("Creating Agent 1 (The Analyst)...")
    agent1 = Agent(
        instructions=f"""You are Agent 1 - The Analyst in a two-agent discussion about: {DISCUSSION_TOPIC}

CRITICAL INSTRUCTIONS:
- YOU ALWAYS SPEAK FIRST after the user asks a question
- Wait 2-3 seconds after you hear the user finish speaking before you respond
- Keep your response VERY brief (1 sentence only)
- After you finish speaking, STAY SILENT to let Agent 2 respond
- DO NOT respond to Agent 2's voice - only respond to the USER

Your role:
- Provide analytical, data-driven, evidence-based perspectives
- Question assumptions and look for facts
- Keep responses to ONE sentence maximum

Always start with "Agent 1 here." then give your brief analytical response."""
    )

    session1 = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model=STT_MODEL),
        llm=openai.LLM(model=LLM_MODEL),
        tts=openai.TTS(model=TTS_MODEL, voice="alloy"),
        min_endpointing_delay=2.0,  # Wait 2 seconds before responding
    )

    # Create Agent 2 - The Creative (speaks second, after Agent 1)
    logger.info("Creating Agent 2 (The Creative)...")
    agent2 = Agent(
        instructions=f"""You are Agent 2 - The Creative in a two-agent discussion about: {DISCUSSION_TOPIC}

CRITICAL INSTRUCTIONS:
- WAIT for Agent 1 to finish speaking first
- Count to 5 after Agent 1 stops before you respond
- Keep your response VERY brief (1 sentence only)
- After you finish speaking, STAY SILENT and wait for the next user question
- DO NOT respond to Agent 1's voice - only respond to the USER

Your role:
- Provide creative, imaginative, alternative perspectives
- Think outside the box and explore possibilities
- Keep responses to ONE sentence maximum
- Build on or offer alternative to Agent 1's analytical view

Always start with "Agent 2 here." then give your brief creative response."""
    )

    session2 = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model=STT_MODEL),
        llm=openai.LLM(model=LLM_MODEL),
        tts=openai.TTS(model=TTS_MODEL, voice="echo"),
        min_endpointing_delay=5.0,  # Wait 5 seconds before responding (after Agent 1)
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
