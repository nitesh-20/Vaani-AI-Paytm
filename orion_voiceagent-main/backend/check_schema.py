from livekit.agents import llm
import pydantic
from pydantic import TypeAdapter

try:
    print(f"ChatMessage fields: {llm.ChatMessage.__fields__}")
except AttributeError:
    # Pydantic v2
    print(f"ChatMessage fields: {llm.ChatMessage.model_fields.keys()}")
    print(f"ChatMessage content type: {llm.ChatMessage.model_fields['content'].annotation}")
 
 
 
 
 
 
 
 
 
 
 
 
