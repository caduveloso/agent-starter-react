import asyncio
import logging
import os
import json
from pathlib import Path
from enum import Enum
from typing import Optional, List, Dict
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
logger = logging.getLogger("multi-agent-advanced")

# Model configuration
STT_MODEL = os.getenv("OPENAI_STT_MODEL", "gpt-4o-mini-transcribe")
LLM_MODEL = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "tts-1")


class SpeakerRole(Enum):
    """Defines the different speaker roles in the conversation"""
    AGENT_1 = "agent_1"
    AGENT_2 = "agent_2"
    USER = "user"
    MODERATOR = "moderator"  # For system messages


class ConversationPhase(Enum):
    """Different phases of the conversation"""
    INTRODUCTION = "introduction"
    DISCUSSION = "discussion"
    CONSENSUS = "consensus"
    DECISION = "decision"
    CONCLUSION = "conclusion"


@dataclass
class TurnState:
    """Manages the state of conversation turns"""
    current_speaker: SpeakerRole
    turn_number: int = 0
    max_turn_duration: float = 30.0  # seconds
    last_turn_start: Optional[datetime] = None
    phase: ConversationPhase = ConversationPhase.INTRODUCTION

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
    Advanced turn management with consensus detection and decision-making.
    """

    def __init__(self, turn_order: List[SpeakerRole], topic: str = ""):
        self.turn_order = turn_order
        self.current_index = 0
        self.state = TurnState(current_speaker=turn_order[0])
        self.conversation_history = []
        self.topic = topic
        self.agent_positions: Dict[SpeakerRole, str] = {}
        self.agreement_count = 0
        self.rounds_completed = 0

    def get_current_speaker(self) -> SpeakerRole:
        """Get the current speaker"""
        return self.state.current_speaker

    def next_turn(self) -> SpeakerRole:
        """Move to the next speaker in the turn order"""
        self.current_index = (self.current_index + 1) % len(self.turn_order)
        next_speaker = self.turn_order[self.current_index]

        # Check if we completed a round
        if self.current_index == 0:
            self.rounds_completed += 1
            logger.info(f"Round {self.rounds_completed} completed")

        self.state.start_turn(next_speaker)
        return next_speaker

    def record_utterance(self, speaker: SpeakerRole, text: str):
        """Record what was said for future consensus/decision logic"""
        self.conversation_history.append({
            "turn": self.state.turn_number,
            "speaker": speaker.value,
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "phase": self.state.phase.value
        })
        logger.info(f"[{speaker.value}]: {text}")

        # Detect consensus keywords
        self._detect_agreement(speaker, text)

    def _detect_agreement(self, speaker: SpeakerRole, text: str):
        """Simple consensus detection based on keywords"""
        agreement_words = ["agree", "consensus", "yes", "correct", "exactly", "right"]
        text_lower = text.lower()

        if any(word in text_lower for word in agreement_words):
            self.agreement_count += 1
            logger.info(f"Agreement detected! Count: {self.agreement_count}")

    def should_yield_turn(self) -> bool:
        """Determine if the current speaker should yield their turn"""
        return self.state.is_turn_expired()

    def check_consensus_reached(self) -> bool:
        """
        Check if consensus has been reached.
        This is a simple implementation - can be made more sophisticated.
        """
        # Simple rule: If we've had 2+ agreements in recent turns
        if self.agreement_count >= 2 and self.rounds_completed >= 1:
            logger.info("Consensus appears to be reached!")
            return True
        return False

    def get_conversation_context(self, for_speaker: SpeakerRole) -> str:
        """
        Get context-aware conversation summary for a specific speaker.
        This helps agents understand what's been discussed.
        """
        if not self.conversation_history:
            intro = f"This is the beginning of our discussion about: {self.topic}\n"
            intro += f"You are {for_speaker.value}. Please share your initial thoughts."
            return intro

        recent_turns = self.conversation_history[-5:]  # Last 5 turns
        context = f"Discussion topic: {self.topic}\n"
        context += f"Round {self.rounds_completed}, Turn {self.state.turn_number}\n"
        context += f"Phase: {self.state.phase.value}\n\n"
        context += "Recent conversation:\n"

        for entry in recent_turns:
            context += f"[{entry['speaker']}]: {entry['text']}\n"

        context += f"\nYou are {for_speaker.value}. "

        # Add phase-specific guidance
        if self.state.phase == ConversationPhase.INTRODUCTION:
            context += "Share your initial perspective on this topic."
        elif self.state.phase == ConversationPhase.DISCUSSION:
            context += "Build on the previous points or offer a different perspective."
        elif self.state.phase == ConversationPhase.CONSENSUS:
            context += "Try to find common ground and areas of agreement."
        elif self.state.phase == ConversationPhase.DECISION:
            context += "Help finalize the decision based on the discussion."

        return context

    def advance_phase(self):
        """Move to the next phase of conversation"""
        phases = list(ConversationPhase)
        current_idx = phases.index(self.state.phase)
        if current_idx < len(phases) - 1:
            self.state.phase = phases[current_idx + 1]
            logger.info(f"Advanced to phase: {self.state.phase.value}")

    def get_summary(self) -> Dict:
        """Get a summary of the entire conversation"""
        return {
            "topic": self.topic,
            "total_turns": self.state.turn_number,
            "rounds_completed": self.rounds_completed,
            "final_phase": self.state.phase.value,
            "agreement_count": self.agreement_count,
            "conversation_history": self.conversation_history
        }


class MultiAgentCoordinator:
    """
    Advanced multi-agent coordinator with turn management and consensus detection.
    """

    def __init__(self, ctx: JobContext, discussion_topic: str = ""):
        self.ctx = ctx
        self.discussion_topic = discussion_topic or "a topic to be determined"
        self.turn_manager = TurnManager(
            turn_order=[
                SpeakerRole.USER,      # User speaks first to set the topic
                SpeakerRole.AGENT_1,   # Agent 1 responds
                SpeakerRole.AGENT_2,   # Agent 2 adds their input
            ],
            topic=self.discussion_topic
        )
        self.agents = {}
        self.sessions = {}
        self.avatars = {}
        self.is_running = True

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
            model="expression",
        )

        # Store references
        self.agents[role] = agent
        self.sessions[role] = session
        self.avatars[role] = avatar

        return agent, session, avatar

    async def start_agents(self):
        """Start all agent sessions and avatars"""

        # Agent 1 - The Analyst
        agent1, session1, avatar1 = await self.create_agent(
            role=SpeakerRole.AGENT_1,
            avatar_id=os.getenv("BITHUMAN_AVATAR_ID_1", os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779")),
            instructions=f"""You are Agent 1 (The Analyst) in a structured multi-agent discussion about: {self.discussion_topic}

Your role:
- Provide analytical and data-driven perspectives
- Question assumptions and look for evidence
- Keep your responses brief (1-2 sentences per turn)
- Listen to Agent 2 and the user
- Work toward consensus but be willing to disagree respectfully

The discussion follows rounds where User speaks, then you, then Agent 2.
Build on what others say and help reach a thoughtful conclusion.""",
            tts_voice="alloy"
        )

        # Agent 2 - The Creative
        agent2, session2, avatar2 = await self.create_agent(
            role=SpeakerRole.AGENT_2,
            avatar_id=os.getenv("BITHUMAN_AVATAR_ID_2", os.getenv("BITHUMAN_AVATAR_ID", "A48QHJ6779")),
            instructions=f"""You are Agent 2 (The Creative) in a structured multi-agent discussion about: {self.discussion_topic}

Your role:
- Offer creative and alternative perspectives
- Think outside the box and explore possibilities
- Keep your responses brief (1-2 sentences per turn)
- Listen to Agent 1 and the user
- Help find innovative solutions and common ground

The discussion follows rounds where User speaks, then Agent 1, then you.
Build on what others say and help reach a thoughtful conclusion.""",
            tts_voice="echo"
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
        Active turn management with explicit control.
        """
        logger.info("Turn management starting...")

        # Set up event listeners for the room with sync wrappers
        def on_track_subscribed(track, publication, participant):
            """Sync wrapper for track subscription"""
            logger.info(f"Track subscribed: {participant.identity}")

        def on_data_received(data):
            """Sync wrapper for data received"""
            asyncio.create_task(self._handle_data_received(data))

        self.ctx.room.on("track_subscribed", on_track_subscribed)
        self.ctx.room.on("data_received", on_data_received)

        # Initial announcement
        await self._send_moderator_message(
            f"Welcome! We'll be discussing: {self.discussion_topic}\n"
            f"Taking turns - User, then Agent 1, then Agent 2.\n"
            f"User, please start the discussion!"
        )

        # Keep the system running
        while self.is_running:
            await asyncio.sleep(1)

            # Check for consensus
            if self.turn_manager.check_consensus_reached():
                await self._handle_consensus()
                break

            # Auto-advance if turn is taking too long
            if self.turn_manager.should_yield_turn():
                logger.warning("Turn timeout - advancing to next speaker")
                self.turn_manager.next_turn()

    async def _handle_data_received(self, data: rtc.DataPacket):
        """
        Handle data messages from agents and users.
        This can be used for turn control and metadata.
        """
        try:
            message = json.loads(data.data.decode())
            logger.info(f"Data received: {message}")

            if message.get("type") == "turn_complete":
                # Agent signals they're done talking
                speaker = message.get("speaker")
                text = message.get("text", "")
                self.turn_manager.record_utterance(SpeakerRole(speaker), text)
                self.turn_manager.next_turn()

        except Exception as e:
            logger.error(f"Error processing data: {e}")

    async def _send_moderator_message(self, message: str):
        """Send a moderator message to all participants"""
        logger.info(f"[MODERATOR]: {message}")

        # Publish as data message
        await self.ctx.room.local_participant.publish_data(
            json.dumps({
                "type": "moderator_message",
                "text": message,
                "timestamp": datetime.now().isoformat()
            }).encode()
        )

    async def _handle_consensus(self):
        """Handle consensus reached"""
        self.turn_manager.advance_phase()

        await self._send_moderator_message(
            "Consensus appears to be reached! Moving to conclusion phase."
        )

        summary = self.turn_manager.get_summary()
        logger.info(f"Conversation summary: {json.dumps(summary, indent=2)}")

    async def send_turn_signal(self, role: SpeakerRole):
        """Send explicit turn signal to agents"""
        context = self.turn_manager.get_conversation_context(role)

        await self.ctx.room.local_participant.publish_data(
            json.dumps({
                "type": "turn_signal",
                "speaker": role.value,
                "context": context,
                "turn": self.turn_manager.state.turn_number,
                "phase": self.turn_manager.state.phase.value
            }).encode()
        )

    async def stop(self):
        """Stop the multi-agent system"""
        self.is_running = False
        summary = self.turn_manager.get_summary()

        await self._send_moderator_message(
            f"Discussion concluded after {summary['total_turns']} turns and {summary['rounds_completed']} rounds."
        )


def prewarm(proc: JobContext):
    """Prewarm process to load models before handling requests"""
    logger.info("Prewarm complete")


async def entrypoint(ctx: JobContext):
    """Main entry point for the advanced multi-agent system"""

    # You can customize the discussion topic here
    discussion_topic = os.getenv("DISCUSSION_TOPIC", "the future of AI")

    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create the multi-agent coordinator
    coordinator = MultiAgentCoordinator(ctx, discussion_topic)

    # Start both agents
    await coordinator.start_agents()

    # Start turn management
    await coordinator.manage_turns()

    logger.info("Multi-agent discussion concluded.")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
