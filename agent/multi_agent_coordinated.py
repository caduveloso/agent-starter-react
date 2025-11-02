import asyncio
import logging
import os
import json
from pathlib import Path
from enum import Enum
from typing import Optional
from datetime import datetime

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
    llm as agent_llm,
)
from livekit.plugins import openai, silero, bithuman

# Load .env from project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger("multi-agent-coordinated")

# Model configuration
STT_MODEL = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")


class AgentRole(Enum):
    AGENT_1 = "agent_1"
    AGENT_2 = "agent_2"


class TurnCoordinator:
    """
    Coordinates turn-taking between two agents using LiveKit data messages.
    """

    def __init__(self, room: rtc.Room):
        self.room = room
        self.current_speaker: Optional[AgentRole] = None
        self.conversation_count = 0
        self.is_speaking = False

    async def request_turn(self, agent_role: AgentRole) -> bool:
        """Request permission to speak"""
        if self.is_speaking:
            logger.info(f"{agent_role.value} waiting for current speaker to finish...")
            return False

        self.current_speaker = agent_role
        self.is_speaking = True
        logger.info(f"✓ {agent_role.value} has the floor")

        # Broadcast who's speaking
        await self.broadcast_turn_status(agent_role)
        return True

    async def release_turn(self, agent_role: AgentRole):
        """Release the speaking turn"""
        if self.current_speaker == agent_role:
            self.is_speaking = False
            self.current_speaker = None
            self.conversation_count += 1
            logger.info(f"✓ {agent_role.value} finished speaking (turn #{self.conversation_count})")

            # Broadcast turn released
            await self.broadcast_turn_status(None)

    async def broadcast_turn_status(self, speaker: Optional[AgentRole]):
        """Broadcast current speaker via data channel"""
        try:
            message = {
                "type": "turn_status",
                "speaker": speaker.value if speaker else None,
                "turn_count": self.conversation_count,
                "timestamp": datetime.now().isoformat()
            }
            await self.room.local_participant.publish_data(
                json.dumps(message).encode(),
                reliable=True
            )
        except Exception as e:
            logger.error(f"Failed to broadcast turn status: {e}")

    def should_respond(self, agent_role: AgentRole, user_finished_speaking: bool) -> bool:
        """
        Determine if this agent should respond based on turn order.
        Agent 1 responds first, then Agent 2.
        """
        if not user_finished_speaking:
            return False

        if self.is_speaking:
            return False

        # Turn order: Agent 1 goes first, then Agent 2
        if self.conversation_count % 2 == 0:
            return agent_role == AgentRole.AGENT_1
        else:
            return agent_role == AgentRole.AGENT_2


class CoordinatedAgentSession:
    """
    Wrapper around AgentSession that adds turn coordination.
    """

    def __init__(
        self,
        agent_role: AgentRole,
        coordinator: TurnCoordinator,
        instructions: str,
        tts_voice: str,
    ):
        self.role = agent_role
        self.coordinator = coordinator
        self.instructions = instructions
        self.tts_voice = tts_voice
        self.agent = None
        self.session = None
        self.is_ready = False

    async def create_and_start(self, room: rtc.Room):
        """Create and start the agent session"""

        logger.info(f"Creating {self.role.value}...")

        # Create the agent with role-specific instructions
        self.agent = Agent(instructions=self.instructions)

        # Create agent session
        self.session = AgentSession(
            vad=silero.VAD.load(),
            stt=openai.STT(model=STT_MODEL),
            llm=openai.LLM(model=LLM_MODEL),
            tts=openai.TTS(model=TTS_MODEL, voice=self.tts_voice),
        )

        # Hook into before_llm_cb to implement turn coordination
        original_before_llm = self.session._before_llm_cb

        async def coordinated_before_llm(agent, chat_ctx):
            """Check if it's our turn before responding"""
            user_msg = chat_ctx.messages[-1] if chat_ctx.messages else None
            user_finished = user_msg and user_msg.role == "user" if user_msg else False

            if not self.coordinator.should_respond(self.role, user_finished):
                logger.info(f"{self.role.value} skipping response - not their turn")
                return None  # Don't respond

            # Request turn
            if not await self.coordinator.request_turn(self.role):
                logger.info(f"{self.role.value} couldn't get turn")
                return None

            # Call original callback if exists
            if original_before_llm:
                return await original_before_llm(agent, chat_ctx)

        async def coordinated_after_tts(agent, *args):
            """Release turn after speaking"""
            await self.coordinator.release_turn(self.role)

        # Set callbacks
        self.session.on("agent_started_speaking", lambda: logger.info(f"🗣️  {self.role.value} speaking..."))
        self.session.on("agent_stopped_speaking", lambda: asyncio.create_task(coordinated_after_tts(self.agent)))
        # Note: before_llm_cb approach needs session internals access

        await self.session.start(agent=self.agent, room=room)
        self.is_ready = True
        logger.info(f"✓ {self.role.value} ready")


def prewarm(proc: JobContext):
    """Prewarm process"""
    logger.info("Prewarm complete")


async def entrypoint(ctx: JobContext):
    """
    Multi-agent system with turn coordination.

    Two agents share one avatar video but take turns speaking in an organized manner.
    """

    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create turn coordinator
    coordinator = TurnCoordinator(ctx.room)

    # Create Agent 1 - The Analyst
    agent1_session = CoordinatedAgentSession(
        agent_role=AgentRole.AGENT_1,
        coordinator=coordinator,
        instructions="""You are Agent 1 (The Analyst) in a two-agent discussion.

Your role:
- Provide analytical, data-driven perspectives
- Question assumptions and look for evidence
- Keep responses VERY brief (1-2 sentences maximum)
- You speak FIRST after the user
- Listen to Agent 2's response that follows yours

Be concise and analytical.""",
        tts_voice="alloy"
    )

    # Create Agent 2 - The Creative
    agent2_session = CoordinatedAgentSession(
        agent_role=AgentRole.AGENT_2,
        coordinator=coordinator,
        instructions="""You are Agent 2 (The Creative) in a two-agent discussion.

Your role:
- Offer creative, alternative perspectives
- Think outside the box and explore possibilities
- Keep responses VERY brief (1-2 sentences maximum)
- You speak SECOND, after Agent 1
- Build on or challenge Agent 1's points

Be concise and creative.""",
        tts_voice="echo"
    )

    # Create ONE shared BitHuman avatar
    logger.info("Creating shared BitHuman avatar...")
    avatar = bithuman.AvatarSession(
        avatar_id=os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779"),
        model="expression",
    )

    # Start agent 1 session
    logger.info("Starting Agent 1 session...")
    await agent1_session.create_and_start(ctx.room)

    # Start agent 2 session
    logger.info("Starting Agent 2 session...")
    await agent2_session.create_and_start(ctx.room)

    # Start the shared avatar with agent 1's session (they'll alternate usage)
    logger.info("Starting shared avatar...")
    await avatar.start(agent1_session.session, room=ctx.room)

    logger.info("=" * 60)
    logger.info("Multi-agent system ready!")
    logger.info("Turn order: User → Agent 1 (Analyst) → Agent 2 (Creative)")
    logger.info("=" * 60)

    # Send welcome message
    await ctx.room.local_participant.publish_data(
        json.dumps({
            "type": "system_message",
            "message": "Two agents ready! Agent 1 (Analyst) speaks first, then Agent 2 (Creative).",
            "timestamp": datetime.now().isoformat()
        }).encode()
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
