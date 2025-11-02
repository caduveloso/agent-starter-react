import asyncio
import logging
import os
from pathlib import Path
from enum import Enum
from typing import Optional, List
from dataclasses import dataclass
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
)
from livekit.plugins import openai, silero, bithuman

# Load .env from project root (parent directory)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger("multi-agent")

# Model configuration
STT_MODEL = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")


class SpeakerRole(Enum):
    """Defines the different speaker roles in the conversation"""
    AGENT_1 = "agent_1"
    AGENT_2 = "agent_2"
    USER = "user"


@dataclass
class TurnState:
    """Manages the state of conversation turns"""
    current_speaker: SpeakerRole
    turn_number: int = 0
    max_turn_duration: float = 30.0  # seconds
    last_turn_start: Optional[datetime] = None

    def start_turn(self, speaker: SpeakerRole):
        """Start a new turn for the specified speaker"""
        self.current_speaker = speaker
        self.turn_number += 1
        self.last_turn_start = datetime.now()
        logger.info(f"Turn {self.turn_number}: {speaker.value} is speaking")

    def is_turn_expired(self) -> bool:
        """Check if the current turn has exceeded the maximum duration"""
        if self.last_turn_start is None:
            return False
        elapsed = (datetime.now() - self.last_turn_start).total_seconds()
        return elapsed > self.max_turn_duration


class TurnManager:
    """
    Manages turn-taking logic for multi-agent conversations.

    Basic implementation:
    - Round-robin: Agent1 -> Agent2 -> User -> Agent1...
    - Time limits to prevent one speaker from dominating
    - Extensible for future consensus and decision logic
    """

    def __init__(self, turn_order: List[SpeakerRole]):
        self.turn_order = turn_order
        self.current_index = 0
        self.state = TurnState(current_speaker=turn_order[0])
        self.conversation_history = []

    def get_current_speaker(self) -> SpeakerRole:
        """Get the current speaker"""
        return self.state.current_speaker

    def next_turn(self) -> SpeakerRole:
        """Move to the next speaker in the turn order"""
        self.current_index = (self.current_index + 1) % len(self.turn_order)
        next_speaker = self.turn_order[self.current_index]
        self.state.start_turn(next_speaker)
        return next_speaker

    def record_utterance(self, speaker: SpeakerRole, text: str):
        """Record what was said for future consensus/decision logic"""
        self.conversation_history.append({
            "turn": self.state.turn_number,
            "speaker": speaker.value,
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
        logger.info(f"[{speaker.value}]: {text}")

    def should_yield_turn(self) -> bool:
        """
        Determine if the current speaker should yield their turn.
        Future: Add logic for interruptions, consensus detection, etc.
        """
        return self.state.is_turn_expired()

    def get_conversation_context(self) -> str:
        """
        Get a summary of the conversation for agents to understand context.
        This helps agents stay on topic and build on previous statements.
        """
        if not self.conversation_history:
            return "This is the beginning of the conversation."

        recent_turns = self.conversation_history[-5:]  # Last 5 turns
        context = "Recent conversation:\n"
        for entry in recent_turns:
            context += f"[{entry['speaker']}]: {entry['text']}\n"
        return context


class MultiAgentCoordinator:
    """
    Coordinates multiple agents in a LiveKit room.
    Handles turn-taking and ensures agents can hear each other.
    """

    def __init__(self, ctx: JobContext):
        self.ctx = ctx
        self.turn_manager = TurnManager([
            SpeakerRole.USER,      # User speaks first
            SpeakerRole.AGENT_1,   # Agent 1 responds
            SpeakerRole.AGENT_2,   # Agent 2 adds their input
        ])
        self.agents = {}
        self.sessions = {}
        self.avatars = {}

    async def create_agent(
        self,
        role: SpeakerRole,
        avatar_id: str,
        instructions: str,
        tts_voice: str = "alloy"
    ) -> tuple[Agent, AgentSession, bithuman.AvatarSession]:
        """Create an agent with its session and avatar"""

        logger.info(f"Creating {role.value}...")

        # Create the agent with role-specific instructions
        agent = Agent(instructions=instructions)

        # Create the agent session with STT, LLM, and TTS
        session = AgentSession(
            vad=silero.VAD.load(),
            stt=openai.STT(model=STT_MODEL),
            llm=openai.LLM(model=LLM_MODEL),
            tts=openai.TTS(model=TTS_MODEL, voice=tts_voice),
        )

        # Create bitHuman avatar session
        avatar = bithuman.AvatarSession(
            avatar_id=avatar_id,
            model="expression",  # Use 'expression' for dynamic emotional responses
        )

        # Store references
        self.agents[role] = agent
        self.sessions[role] = session
        self.avatars[role] = avatar

        return agent, session, avatar

    async def start_agents(self):
        """Start all agent sessions and avatars"""

        # Agent 1 configuration
        agent1, session1, avatar1 = await self.create_agent(
            role=SpeakerRole.AGENT_1,
            avatar_id=os.getenv("BITHUMAN_AVATAR_ID_1", os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779")),
            instructions="""You are Agent 1, a thoughtful AI assistant participating in a multi-agent discussion.
            You will discuss topics with another AI agent and a human user.

            When it's your turn to speak:
            - Listen carefully to what others have said
            - Provide your perspective or analysis
            - Keep responses concise (2-3 sentences)
            - Build on previous points made by others
            - Be respectful and collaborative

            You are part of a team working toward understanding and consensus.""",
            tts_voice="alloy"
        )

        # Agent 2 configuration
        agent2, session2, avatar2 = await self.create_agent(
            role=SpeakerRole.AGENT_2,
            avatar_id=os.getenv("BITHUMAN_AVATAR_ID_2", os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779")),
            instructions="""You are Agent 2, an analytical AI assistant participating in a multi-agent discussion.
            You will discuss topics with another AI agent and a human user.

            When it's your turn to speak:
            - Consider different angles and perspectives
            - Ask clarifying questions when needed
            - Keep responses concise (2-3 sentences)
            - Challenge assumptions constructively
            - Help move the discussion toward resolution

            You are part of a team working toward understanding and consensus.""",
            tts_voice="echo"  # Different voice for distinction
        )

        logger.info("Starting agent 1 avatar and session...")
        await avatar1.start(session1, room=self.ctx.room)
        await session1.start(agent=agent1, room=self.ctx.room)

        logger.info("Starting agent 2 avatar and session...")
        await avatar2.start(session2, room=self.ctx.room)
        await session2.start(agent=agent2, room=self.ctx.room)

        logger.info("All agents are ready!")

    async def manage_turns(self):
        """
        Manage the conversation flow and turn-taking.
        This is where you'll implement the discussion logic.
        """

        # TODO: Implement turn management logic
        # This could involve:
        # 1. Listening to room events
        # 2. Detecting when someone stops speaking
        # 3. Prompting the next agent to speak
        # 4. Monitoring for consensus or decision points

        logger.info("Turn management active - agents can now converse")

        # For now, agents will respond naturally to audio in the room
        # Future enhancement: Add explicit turn signals via data messages

    async def send_turn_signal(self, role: SpeakerRole):
        """
        Send a signal to indicate whose turn it is.
        This can be expanded to send data messages to control agent behavior.
        """
        logger.info(f"Turn signal: {role.value}'s turn to speak")

        # Future: Send data message to agents
        # await self.ctx.room.local_participant.publish_data(
        #     json.dumps({"type": "turn_signal", "speaker": role.value})
        # )


def prewarm(proc: JobContext):
    """Prewarm process to load models before handling requests"""
    logger.info("Prewarm complete")


async def entrypoint(ctx: JobContext):
    """Main entry point for the multi-agent system"""

    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create the multi-agent coordinator
    coordinator = MultiAgentCoordinator(ctx)

    # Start both agents
    await coordinator.start_agents()

    # Start turn management
    await coordinator.manage_turns()

    # Keep the connection alive
    logger.info("Multi-agent system is running. All participants can now talk.")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
