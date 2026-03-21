#!/bin/bash

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use node 2>/dev/null

# Kill anything already on these ports
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null
sleep 1

# Start Ollama if not running
pgrep -x "ollama" > /dev/null || open -a Ollama
sleep 2

# Start backend
cd /Users/Yuvi10/Desktop/infinit
python3 -m uvicorn server:app --host 0.0.0.0 --port 8000 &> /tmp/infinit-backend.log &
BACKEND_PID=$!
echo "Backend starting (pid $BACKEND_PID)..."

# Wait up to 60s for backend
TRIES=0
until curl -s http://127.0.0.1:8000/models > /dev/null 2>&1; do
    sleep 2
    TRIES=$((TRIES+1))
    echo "Waiting for backend... ($((TRIES*2))s)"
    if [ $TRIES -ge 30 ]; then
        echo "Backend failed to start. Check /tmp/infinit-backend.log"
        cat /tmp/infinit-backend.log
        exit 1
    fi
done
echo "Backend ready"

# Start frontend
cd /Users/Yuvi10/infinit-app
npm run dev &> /tmp/infinit-frontend.log &
echo "Frontend starting..."

# Wait up to 30s for frontend
TRIES=0
until curl -s http://localhost:5173 > /dev/null 2>&1; do
    sleep 1
    TRIES=$((TRIES+1))
    if [ $TRIES -ge 30 ]; then
        echo "Frontend failed. Check /tmp/infinit-frontend.log"
        cat /tmp/infinit-frontend.log
        exit 1
    fi
done
echo "Frontend ready"

open http://localhost:5173
echo "Infinit is running"
