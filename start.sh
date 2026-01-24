#!/bin/bash

echo "🚀 Starting Study Planner..."
echo ""

# Check if running with Docker
if [ "$1" = "docker" ]; then
    echo "📦 Starting with Docker Compose..."
    docker-compose up
    exit 0
fi

# Backend setup
echo "⚙️  Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "✅ Backend dependencies installed"
echo "🚀 Starting FastAPI server on http://localhost:8000"
python main.py &
BACKEND_PID=$!

cd ..

# Frontend setup
echo ""
echo "⚙️  Setting up Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install > /dev/null 2>&1
fi

echo "✅ Frontend dependencies installed"
echo "🚀 Starting Next.js on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "================================"
echo "✨ Study Planner is Running! ✨"
echo "================================"
echo ""
echo "📱 Frontend:  http://localhost:3000"
echo "🔌 Backend:   http://localhost:8000"
echo "📚 Docs:      http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Keep script running
wait $BACKEND_PID $FRONTEND_PID
