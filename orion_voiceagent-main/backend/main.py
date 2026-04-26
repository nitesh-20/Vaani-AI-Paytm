import asyncio
import logging
import os

from dotenv import load_dotenv
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, deepgram, elevenlabs, silero

# Load environment variables
load_dotenv()

# Logger setup
logger = logging.getLogger("orion-agent")
logger.setLevel(logging.INFO)

async def entrypoint(ctx: JobContext):
    # Connect to the room
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    
    # Wait for participant to connect
    participant = await ctx.wait_for_participant()
    
    logger.info(f"Connected to room {ctx.room.name} with participant {participant.identity}")

    # Build the Voice Agent
    agent = VoicePipelineAgent(
        instructions=(
            "You are Vaani, an advanced AI voice assistant. "
            "You are helpful, concise, and friendly. "
            "You speak in a natural, conversational tone. "
            "Keep your responses relatively short to maintain a fluid conversation. "
            "If the user interrupts, stop speaking immediately."
        ),
        vad=silero.VAD.load(),
        stt=openai.STT(), # Using OpenAI Whisper
        llm=openai.LLM(model="gpt-4o"),
        tts=elevenlabs.TTS(), # Using ElevenLabs for best quality
        chat_ctx=llm.ChatContext()
    )

    # Start the agent
    agent.start(ctx.room, participant)
    
    await agent.say("Hi there! I'm Orion. I'm ready to chat.", allow_interruptions=True)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
