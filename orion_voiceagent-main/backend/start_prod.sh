#!/bin/bash

# Default port to 8000 if not set
PORT="${PORT:-8000}"

echo "Starting Orion Production Services..."

# 1. Start the Token Server (FastAPI) in the background
# We bind to 0.0.0.0 and the PORT environment variable provided by the host
echo "Starting Token Server on port $PORT..."
uvicorn server:app --host 0.0.0.0 --port $PORT &
TOKEN_SERVER_PID=$!

# 2. Start the Voice Agent
# This connects strictly as a client to LiveKit Cloud, so it doesn't need an inbound port.
echo "Starting Voice Agent..."
python agent.py start &
AGENT_PID=$!

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $?
