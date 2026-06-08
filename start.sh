#!/bin/bash
# OutreachOS - One-command startup script

set -e

echo ""
echo "  ╔═══════════════════════════════════╗"
echo "  ║   OutreachOS - Outreach Pipeline  ║"
echo "  ╚═══════════════════════════════════╝"
echo ""

# Check dependencies
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found. Please install Python 3.11+"; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found. Please install Node.js 18+"; exit 1; }

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

# Setup backend
echo "📦 Setting up backend..."
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt -q

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "⚠️  Created .env from .env.example — add your API keys for real data (mock mode active)"
fi

# Start backend in background
echo "🚀 Starting backend on http://localhost:8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Setup frontend
echo "📦 Setting up frontend..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
  npm install -q
fi

echo "🚀 Starting frontend on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "  ✅ OutreachOS is running!"
echo "  → Frontend: http://localhost:3000"
echo "  → API Docs: http://localhost:8000/docs"
echo ""
echo "  Press Ctrl+C to stop all services"
echo ""

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
