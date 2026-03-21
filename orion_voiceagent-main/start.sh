#!/bin/bash

# Vaani Voice Agent - Quick Start Script
# This script helps you start all required services

echo "🌟 Starting Vaani Voice Agent..."
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "client" ]; then
    echo "❌ Error: Please run this script from the orion-voiceagent root directory"
    exit 1
fi

# Check if .env files exist
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Warning: backend/.env not found"
    echo "   Please copy backend/.env.example to backend/.env and configure it"
    exit 1
fi

if [ ! -f "client/.env" ]; then
    echo "⚠️  Warning: client/.env not found"
    echo "   Please copy client/.env.example to client/.env and configure it"
    exit 1
fi

echo "✅ Configuration files found"
echo ""

# Function to check if a port is in use
check_port() {
    lsof -i:$1 > /dev/null 2>&1
    return $?
}

# Check if ports are available
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use (Token Server)"
    echo "   Please stop the process using this port or change the port"
fi

if check_port 5173; then
    echo "⚠️  Port 5173 is already in use (Frontend)"
    echo "   Please stop the process using this port or change the port"
fi

echo "Starting services..."
echo ""

PROJECT_ROOT=$(pwd)
# Resolve Python interpreter — prioritize fresh venv
if [ -f "backend/venv_fresh/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/backend/venv_fresh/bin/python"
elif [ -f "backend/venv311/bin/python" ] && "backend/venv311/bin/python" --version > /dev/null 2>&1; then
    PYTHON="$PROJECT_ROOT/backend/venv311/bin/python"
else
    PYTHON="python3.11"
fi
echo "🐍 Using Python: $PYTHON"

# Start token server in background
echo "🔑 Starting Token Server..."
cd backend
$PYTHON server.py > ../logs/token-server.log 2>&1 &
TOKEN_PID=$!
cd ..

sleep 2

# Start AI agent in background
echo "🤖 Starting AI Agent (Groq + LiveKit)..."
cd backend
$PYTHON agent.py dev >> ../logs/agent.log 2>&1 &
AGENT_PID=$!
cd ..

sleep 2

# Start frontend in background
echo "🎨 Starting Frontend..."
cd client
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 3

echo ""
echo "✨ Vaani is starting up!"
echo ""
echo "📊 Service Status:"
echo "   Token Server: http://localhost:3001 (PID: $TOKEN_PID)"
echo "   AI Agent: Running (PID: $AGENT_PID)"
echo "   Frontend: http://localhost:5173 (PID: $FRONTEND_PID)"
echo ""
echo "📝 Logs are available in the logs/ directory"
echo ""
echo "🌐 Open http://localhost:5173 in your browser to start learning!"
echo ""
echo "To stop all services, run: ./stop.sh"
echo "Or press Ctrl+C and run: kill $TOKEN_PID $AGENT_PID $FRONTEND_PID"
echo ""

# Save PIDs for later
mkdir -p .pids
echo $TOKEN_PID > .pids/token-server.pid
echo $AGENT_PID > .pids/agent.pid
echo $FRONTEND_PID > .pids/frontend.pid

# Wait for user interrupt
echo "Press Ctrl+C to stop all services..."
trap "echo ''; echo '🛑 Stopping services...'; kill $TOKEN_PID $AGENT_PID $FRONTEND_PID 2>/dev/null; echo '✅ All services stopped'; exit 0" INT

# Keep script running
wait
