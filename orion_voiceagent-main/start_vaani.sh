#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping Vaani Voice Agent..."
    kill $(jobs -p)
    exit
}

trap cleanup SIGINT SIGTERM

echo "🚀 Starting Vaani Voice Agent..."

# Check for .env keys
if grep -q "your_api_key" backend/.env; then
    echo "⚠️  WARNING: It looks like backend/.env is not configured."
    echo "Please edit backend/.env and add your LiveKit, OpenAI, and ElevenLabs keys."
    read -p "Press Enter to continue anyway (or Ctrl+C to stop)..."
fi

# 1. Start Token Server
echo "Starting Token Server (Port 8000)..."
python3.11 backend/server.py &
SERVER_PID=$!

# 2. Start Agent Worker
echo "Starting AI Agent Worker..."
python3.11 backend/agent.py dev &
AGENT_PID=$!

# 3. Start Frontend
echo "Starting React Client..."
cd client && npm run dev &
CLIENT_PID=$!

# Wait for all
wait
