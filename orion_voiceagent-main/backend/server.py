import os
import random
import time
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from livekit.api import AccessToken, VideoGrants, LiveKitAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Orion Token Server")

# LiveKit API client for agent dispatch
livekit_api = None

# Cache for dispatched rooms to prevent duplicates (room -> timestamp)
dispatched_rooms: dict[str, float] = {}
DISPATCH_CACHE_TTL = 10  # seconds - prevent duplicate dispatches within this window

# Configure CORS - Allow all origins for development
# Configure CORS
origins = os.getenv("CORS_ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi import FastAPI, Query, Header, HTTPException
...
@app.get("/token")
async def get_token(
    room: str = Query(default="gemini-room", description="Room name"),
    identity: str = Query(default=None, description="Participant identity"),
    x_authorization: str = Header(default=None)
):
    """Generate a LiveKit access token for the specified room and participant."""
    auth_token = os.getenv("ORION_AUTH_TOKEN", "change-me-123")
    if x_authorization != auth_token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    global livekit_api

    # Generate random identity if not provided
    if not identity:
        identity = f"user-{random.randint(100, 999)}"

    api_key = os.getenv('LIVEKIT_API_KEY')
    api_secret = os.getenv('LIVEKIT_API_SECRET')
    livekit_url = os.getenv('LIVEKIT_URL')
    agent_name = os.getenv('AGENT_NAME', 'Orion')

    if not api_key or not api_secret or not livekit_url:
        return {
            "error": "Server configuration error: Missing environment variables"
        }, 500

    # Initialize LiveKit API client if needed
    if livekit_api is None:
        livekit_api = LiveKitAPI(
            url=livekit_url,
            api_key=api_key,
            api_secret=api_secret,
        )

    # Create agent dispatch (with deduplication)
    current_time = time.time()

    # Clean up old cache entries
    expired_rooms = [r for r, t in dispatched_rooms.items() if current_time - t > DISPATCH_CACHE_TTL]
    for r in expired_rooms:
        del dispatched_rooms[r]

    # Only dispatch if not recently dispatched
    if room not in dispatched_rooms:
        try:
            from livekit.api import CreateAgentDispatchRequest
            dispatch_request = CreateAgentDispatchRequest(
                agent_name=agent_name,
                room=room,
            )
            await livekit_api.agent_dispatch.create_dispatch(dispatch_request)
            dispatched_rooms[room] = current_time
            print(f"✅ Agent dispatch created for room: {room}, agent: {agent_name}")
        except Exception as e:
            print(f"⚠️ Agent dispatch failed: {e}")
    else:
        print(f"ℹ️ Skipping duplicate dispatch for room: {room}")

    # Create access token
    token = AccessToken(api_key, api_secret)
    token.with_identity(identity).with_name(identity).with_grants(
        VideoGrants(room_join=True, room=room)
    )

    return {
        "token": token.to_jwt(),
        "url": livekit_url
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "vaani-token-server"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
