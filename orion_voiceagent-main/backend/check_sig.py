from livekit.plugins import google, deepgram, elevenlabs
import inspect

print("Google LLM signature:", inspect.signature(google.LLM.__init__))
print("Deepgram STT signature:", inspect.signature(deepgram.STT.__init__))
print("ElevenLabs TTS signature:", inspect.signature(elevenlabs.TTS.__init__))
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
