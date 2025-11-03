import asyncio
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
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
logger = logging.getLogger("multi-agent-handoff")

# Model configuration
STT_MODEL = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")
DISCUSSION_TOPIC = os.getenv("DISCUSSION_TOPIC", "the future of AI")


@dataclass
class ConversationState:
    """Tracks the multi-agent conversation state"""
    round_number: int = 1
    agent1_last_response: str = ""
    agent2_last_response: str = ""
    consensus_reached: bool = False


def prewarm(proc: JobContext):
    """Prewarm process"""
    logger.info("Prewarm complete")


async def entrypoint(ctx: JobContext):
    """
    Professional multi-agent system using LiveKit's handoff workflow.

    This is the PROFESSIONAL approach using LiveKit's native agent handoff feature.
    Agent 1 speaks first, then explicitly hands off to Agent 2 via a tool call.
    Agent 2 is fully aware of Agent 1's response through the conversation context.
    """

    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Initialize shared conversation state
    conversation_state = ConversationState()

    # Create Agent 2 (must be defined before Agent 1 can reference it)
    logger.info("Creating Agent 2 (The Creative)...")

    class CreativeAgent(Agent):
        """Agent 2 - The Creative thinker who provides imaginative perspectives"""

        def __init__(self, avatar_session):
            super().__init__(
                instructions=f"""You are Agent 2 - The Creative in a multi-agent discussion about: {DISCUSSION_TOPIC}

YOUR ROLE:
- Provide imaginative, out-of-the-box perspectives
- Build on Agent 1's analytical points with creative solutions
- Reference what Agent 1 just said to show you're listening
- Keep responses concise (1-2 sentences max)

CONVERSATION PROTOCOL:
- Start with "Agent 2 here:"
- Reference Agent 1's specific point: "Building on Agent 1's insight about X..."
- Offer your creative perspective
- When ready to continue discussion, use pass_back_to_analyst tool
- If you sense consensus, use declare_consensus tool

IMPORTANT: You were handed control by Agent 1. Acknowledge their point before adding yours."""
            )
            self.avatar_session = avatar_session

        async def on_enter(self) -> None:
            """Called when this agent takes control via handoff"""
            state: ConversationState = self.session.userdata
            logger.info(f"🎨 Agent 2 (Creative) taking control - Round {state.round_number}")

        @function_tool()
        async def pass_back_to_analyst(self, context: RunContext) -> tuple[Agent, str]:
            """Pass control back to Agent 1 to continue the discussion"""
            state: ConversationState = context.session.userdata
            state.round_number += 1
            logger.info(f"🎨 Agent 2 passing back to Agent 1 - Starting Round {state.round_number}")
            return analyst_agent, "Passing control back to the analyst"

        @function_tool()
        async def declare_consensus(self, context: RunContext, agreement: str) -> str:
            """Declare that consensus has been reached on a topic"""
            state: ConversationState = context.session.userdata
            state.consensus_reached = True
            logger.info(f"✅ Consensus reached: {agreement}")
            return f"Consensus reached: {agreement}. Discussion complete."

    # Create Agent 1 (references Agent 2 for handoff)
    logger.info("Creating Agent 1 (The Analyst)...")

    class AnalystAgent(Agent):
        """Agent 1 - The Analyst who provides data-driven perspectives"""

        def __init__(self, avatar_session):
            super().__init__(
                instructions=f"""You are Agent 1 - The Analyst in a multi-agent discussion about: {DISCUSSION_TOPIC}

YOUR ROLE:
- Provide data-driven, evidence-based analysis
- Respond to the user's question first
- After giving your perspective, ALWAYS hand off to Agent 2
- Keep responses concise (1-2 sentences max)

CONVERSATION PROTOCOL:
- Start with "Agent 1 here:"
- Give your analytical perspective
- ALWAYS use hand_off_to_creative tool after responding
- If consensus is clear, use declare_consensus tool instead

IMPORTANT: After you speak, you MUST hand off to Agent 2 so they can respond. Don't monopolize the conversation."""
            )
            self.avatar_session = avatar_session

        async def on_enter(self) -> None:
            """Called when this agent takes control"""
            state: ConversationState = self.session.userdata
            logger.info(f"📊 Agent 1 (Analyst) taking control - Round {state.round_number}")

        @function_tool()
        async def hand_off_to_creative(self, context: RunContext) -> tuple[Agent, str]:
            """Hand off control to Agent 2 (The Creative) to get their perspective"""
            logger.info("📊 Agent 1 handing off to Agent 2...")
            return creative_agent, "Handing off to the creative agent for their perspective"

        @function_tool()
        async def declare_consensus(self, context: RunContext, agreement: str) -> str:
            """Declare that consensus has been reached on a topic"""
            state: ConversationState = context.session.userdata
            state.consensus_reached = True
            logger.info(f"✅ Consensus reached: {agreement}")
            return f"Consensus reached: {agreement}. Discussion complete."

    # Create BitHuman avatars with custom identities
    logger.info("Creating BitHuman avatars...")

    avatar1 = bithuman.AvatarSession(
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID_1", os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779")),
        model="expression",
        avatar_participant_identity="agent-1-analyst",
        avatar_participant_name="Agent 1 - Analyst",
    )

    avatar2 = bithuman.AvatarSession(
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID_2", os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779")),
        model="expression",
        avatar_participant_identity="agent-2-creative",
        avatar_participant_name="Agent 2 - Creative",
    )

    # Create agent instances with their avatars
    analyst_agent = AnalystAgent(avatar_session=avatar1)
    creative_agent = CreativeAgent(avatar_session=avatar2)

    # Create single session that will be shared between agents during handoffs
    logger.info("Creating shared agent session...")
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model=STT_MODEL),
        llm=openai.LLM(model=LLM_MODEL, temperature=0.7),
        tts=openai.TTS(model=TTS_MODEL, voice="alloy"),
    )

    # Set the conversation state in session userdata
    session.userdata = conversation_state

    # Start both avatars (they'll show as thumbnails)
    logger.info("Starting Avatar 1 (Analyst)...")
    await avatar1.start(session, room=ctx.room)

    logger.info("Starting Avatar 2 (Creative)...")
    await avatar2.start(session, room=ctx.room)

    # Start session with Agent 1 (Analyst) as the initial agent
    logger.info("Starting session with Agent 1 (Analyst) as initial agent...")
    await session.start(agent=analyst_agent, room=ctx.room)

    logger.info("=" * 70)
    logger.info("🤖🤖  Professional Multi-Agent Handoff System Ready!")
    logger.info("     Agent 1 (Analyst) speaks first → hands off → Agent 2 (Creative)")
    logger.info("     Using LiveKit's native agent handoff workflow")
    logger.info("     Both agents are fully aware of conversation context")
    logger.info("=" * 70)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
