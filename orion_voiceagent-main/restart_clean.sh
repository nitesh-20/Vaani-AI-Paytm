#!/bin/bash
PROJECT_ROOT=$(pwd)

# 1. Force kill existing processes on known ports
echo "🧹 Cleaning up old processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3001 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# 2. Use NEW directories to bypass permission locks
mkdir -p "$PROJECT_ROOT/logs_fresh" "$PROJECT_ROOT/.pids_fresh"

# 3. Resolve Python interpreter (prioritizing venv_fresh)
if [ -f "backend/venv_fresh/bin/python3" ]; then
    PYTHON="$PROJECT_ROOT/backend/venv_fresh/bin/python3"
elif [ -f "backend/venv311/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/backend/venv311/bin/python"
else
    PYTHON="python3.11"
fi

echo "🐍 Using Python: $PYTHON"

# 4. Start Services
echo "🔑 Starting Token Server..."
nohup $PYTHON "$PROJECT_ROOT/backend/server.py" > "$PROJECT_ROOT/logs_fresh/token-server.log" 2>&1 &
echo $! > "$PROJECT_ROOT/.pids_fresh/token-server.pid"

echo "🤖 Starting AI Agent..."
nohup $PYTHON "$PROJECT_ROOT/backend/agent.py" dev > "$PROJECT_ROOT/logs_fresh/agent.log" 2>&1 &
echo $! > "$PROJECT_ROOT/.pids_fresh/agent.pid"

echo "🎨 Starting Frontend..."
cd "$PROJECT_ROOT/client"
nohup npm run dev -- --host > "$PROJECT_ROOT/logs_fresh/frontend.log" 2>&1 &
echo $! > "$PROJECT_ROOT/.pids_fresh/frontend.pid"

echo "⏳ Waiting for initialization..."
sleep 5

echo "📊 Status Check:"
ps -p $(cat "$PROJECT_ROOT/.pids_fresh/token-server.pid") >/dev/null && echo "✅ Token Server OK" || echo "❌ Token Server FAILED"
ps -p $(cat "$PROJECT_ROOT/.pids_fresh/agent.pid") >/dev/null && echo "✅ AI Agent OK" || echo "❌ AI Agent FAILED"
ps -p $(cat "$PROJECT_ROOT/.pids_fresh/frontend.pid") >/dev/null && echo "✅ Frontend OK" || echo "❌ Frontend FAILED"

echo "🚀 All services started in 'logs_fresh' and '.pids_fresh'"
