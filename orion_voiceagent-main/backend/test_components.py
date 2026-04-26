
import os
import asyncio
from dotenv import load_dotenv

# Load env manually
load_dotenv()

try:
    from livekit.plugins import google, deepgram, elevenlabs, silero
    print("Imports success")
except ImportError as e:
    print(f"Import failed: {e}")
    exit(1)

def test_components():
    print("Testing Deepgram STT...")
    try:
        dg_key = os.getenv("DEEPGRAM_API_KEY")
        if not dg_key:
            print("DEEPGRAM_API_KEY missing")
        else:
            stt = deepgram.STT(api_key=dg_key)
            print("Deepgram STT initialized")
    except Exception as e:
        print(f"Deepgram Init Failed: {e}")

    print("Testing Google LLM...")
    try:
        g_key = os.getenv("GOOGLE_API_KEY")
        if not g_key:
            print("GOOGLE_API_KEY missing")
        else:
            llm = google.LLM(model="gemini-1.5-flash", api_key=g_key)
            print("Google LLM initialized")
    except Exception as e:
        print(f"Google LLM Init Failed: {e}")

    print("Testing ElevenLabs TTS...")
    try:
        el_key = os.getenv("ELEVENLABS_API_KEY")
        if not el_key:
            print("ELEVENLABS_API_KEY missing")
        else:
           tts = elevenlabs.TTS(api_key=el_key)
           print("ElevenLabs TTS initialized")
    except Exception as e:
        print(f"ElevenLabs TTS Init Failed: {e}")
        
    print("Testing Silero VAD...")
    try:
        vad = silero.VAD.load()
        print("Silero VAD initialized")
    except Exception as e:
        print(f"Silero VAD Init Failed: {e}")

if __name__ == "__main__":
    test_components()
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
