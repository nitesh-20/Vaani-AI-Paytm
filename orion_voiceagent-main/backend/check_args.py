from livekit.plugins import google, deepgram, elevenlabs
import inspect

print("Google LLM init args:", inspect.getfullargspec(google.LLM.__init__).args)
print("Deepgram STT init args:", inspect.getfullargspec(deepgram.STT.__init__).args)
print("ElevenLabs TTS init args:", inspect.getfullargspec(elevenlabs.TTS.__init__).args)
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
