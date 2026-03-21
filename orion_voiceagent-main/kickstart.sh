#!/bin/bash
PROJECT_ROOT=$(pwd)
mkdir -p "$PROJECT_ROOT/logs" "$PROJECT_ROOT/.pids"

# Resolve Python interpreter
if [ -f "backend/venv_fresh/bin/python" ] && "backend/venv_fresh/bin/python" --version > /dev/null 2>&1; then
    PYTHON="$PROJECT_ROOT/backend/venv_fresh/bin/python"
elif [ -f "backend/venv311/bin/python" ] && "backend/venv311/bin/python" --version > /dev/null 2>&1; then
    PYTHON="$PROJECT_ROOT/backend/venv311/bin/python"
else
    PYTHON="python3.11"
fi

echo "🔑 Starting Token Server..."
nohup $PYTHON "$PROJECT_ROOT/backend/server.py" > "$PROJECT_ROOT/logs/token-server.log" 2>&1 &
echo $! > "$PROJECT_ROOT/.pids/token-server.pid"

echo "🤖 Starting AI Agent..."
nohup $PYTHON "$PROJECT_ROOT/backend/agent.py" dev > "$PROJECT_ROOT/logs/agent.log" 2>&1 &
echo $! > "$PROJECT_ROOT/.pids/agent.pid"

echo "🎨 Starting Frontend..."
cd "$PROJECT_ROOT/client"
nohup npm run dev -- --host > "$PROJECT_ROOT/logs/frontend.log" 2>&1 &
echo $! > "$PROJECT_ROOT/.pids/frontend.pid"

echo "Waiting for services to initialize (5s)..."
sleep 5

echo "📊 Service Status:"
ps -p $(cat "$PROJECT_ROOT/.pids/token-server.pid") && echo "✅ Token Server OK" || echo "❌ Token Server FAILED"
ps -p $(cat "$PROJECT_ROOT/.pids/agent.pid") && echo "✅ AI Agent OK" || echo "❌ AI Agent FAILED"
ps -p $(cat "$PROJECT_ROOT/.pids/frontend.pid") && echo "✅ Frontend OK" || echo "❌ Frontend FAILED"

echo "Checking logs for errors..."
grep -i "error" "$PROJECT_ROOT/logs/"*.log | head -n 10
