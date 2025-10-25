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
)
from livekit.agents.voice import Agent as VoiceAgent
from livekit.plugins import openai, silero

# Load .env from project root (parent directory)
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
logger = logging.getLogger("voice-agent")


def prewarm(proc: JobContext):
    """Prewarm process to load models before handling requests"""
    proc.add_shutdown_callback(lambda: logger.info("Shutting down"))


async def entrypoint(ctx: JobContext):
    """Main entry point for the voice-only agent"""

    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a helpful AI assistant. "
            "You can have natural conversations with users and provide assistance. "
            "Keep your responses concise and engaging."
        ),
    )

    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Create the voice agent
    agent = VoiceAgent(
        vad=silero.VAD.load(),
        stt=openai.STT(),
        llm=openai.LLM(),
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
    )

    logger.info("Starting voice agent...")
    await agent.start(ctx.room)

    # Log when a user connects
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant: rtc.RemoteParticipant):
        logger.info(f"Participant connected: {participant.identity}")

    logger.info("Voice agent is ready and waiting for participants")


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
