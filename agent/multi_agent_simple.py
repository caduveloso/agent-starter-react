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
logger = logging.getLogger("multi-agent-simple")

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
    SIMPLE SOLUTION: One agent with dual personality that takes turns.

    The LLM is instructed to respond as BOTH agents in sequence.
    This gives you the multi-agent discussion effect with proper turn-taking.
    """

    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create a single agent with instructions to act as two personalities
    logger.info("Creating dual-personality agent system...")

    agent = Agent(
        instructions=f"""You are a dual-agent discussion system for topics related to: {DISCUSSION_TOPIC}

You embody TWO distinct AI agents who discuss topics together:

**Agent 1 - The Analyst** (speaks FIRST):
- Analytical, data-driven, evidence-based
- Skeptical, asks clarifying questions
- Focuses on facts, numbers, feasibility

**Agent 2 - The Creative** (speaks SECOND):
- Creative, imaginative, big-picture thinker
- Explores possibilities and alternatives
- Focuses on innovation, user experience, potential

IMPORTANT RESPONSE FORMAT:
When the user asks a question, you MUST respond with BOTH agents in this format:

"Agent 1 here. [1-2 sentence analytical response]"
[PAUSE]
"And Agent 2 adding to that. [1-2 sentence creative response]"

Example:
User: "What do you think about AI in education?"

You respond:
"Agent 1 here. Studies show AI tutoring systems can improve test scores by 15-20% on average, though implementation costs remain high. The data suggests benefits are strongest in STEM subjects."
[PAUSE]
"And Agent 2 adding to that. Imagine personalized learning that adapts in real-time to each student's creativity and interests, not just their test performance. We could revolutionize how curiosity itself is nurtured."

KEY RULES:
1. ALWAYS respond as BOTH agents
2. Agent 1 speaks first (analytical), Agent 2 second (creative)
3. Keep each agent's response to 1-2 sentences
4. Make perspectives distinct but complementary
5. Use "[PAUSE]" between agents so TTS creates natural separation
6. Address the user's question fully between both perspectives

Begin now. Listen to the user and respond as both agents."""
    )

    # Create agent session with natural-sounding TTS
    logger.info("Creating agent session...")
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model=STT_MODEL),
        llm=openai.LLM(model=LLM_MODEL),
        tts=openai.TTS(
            model=TTS_MODEL,
            voice="nova",  # Natural, warm voice that can convey different tones
        ),
    )

    # Create BitHuman avatar
    logger.info("Creating BitHuman avatar...")
    avatar = bithuman.AvatarSession(
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779"),
        model="expression",
    )

    # Start avatar and session
    logger.info("Starting avatar and session...")
    await avatar.start(session, room=ctx.room)
    await session.start(agent=agent, room=ctx.room)

    logger.info("=" * 70)
    logger.info("🤖  Dual-Agent System Ready!")
    logger.info("     Agent 1 (Analyst) + Agent 2 (Creative)")
    logger.info("     Both will respond to your questions in sequence")
    logger.info("=" * 70)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
