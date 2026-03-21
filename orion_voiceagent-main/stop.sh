#!/bin/bash

# Vaani Voice Agent - Stop Script

echo "🛑 Stopping Vaani services..."

# Check if PID files exist
if [ -d ".pids" ]; then
    # Stop token server
    if [ -f ".pids/token-server.pid" ]; then
        PID=$(cat .pids/token-server.pid)
        kill $PID 2>/dev/null && echo "✅ Token Server stopped (PID: $PID)"
        rm .pids/token-server.pid
    fi
    
    # Stop agent
    if [ -f ".pids/agent.pid" ]; then
        PID=$(cat .pids/agent.pid)
        kill $PID 2>/dev/null && echo "✅ AI Agent stopped (PID: $PID)"
        rm .pids/agent.pid
    fi
    
    # Stop frontend
    if [ -f ".pids/frontend.pid" ]; then
        PID=$(cat .pids/frontend.pid)
        kill $PID 2>/dev/null && echo "✅ Frontend stopped (PID: $PID)"
        rm .pids/frontend.pid
    fi
    
    rmdir .pids 2>/dev/null
else
    echo "⚠️  No PID files found. Services may not be running."
    echo "   You can manually stop processes on ports 3001 and 5173"
fi

echo ""
echo "✨ All Vaani services have been stopped"
