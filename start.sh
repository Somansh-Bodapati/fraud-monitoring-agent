#!/bin/bash

# Script to start both backend and frontend servers

echo "🚀 Starting Expense & Fraud Monitoring Agent..."
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f "backend/.env.example" ]; then
        cp backend/.env.example backend/.env
        echo "✅ Created .env file. Please add your OPENAI_API_KEY!"
        echo ""
    else
        echo "❌ .env.example not found. Please create backend/.env manually."
        exit 1
    fi
fi

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment and install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
source venv/bin/activate
pip install -q -r requirements.txt
echo "✅ Backend dependencies installed"
echo ""

# Initialize database and create admin user if needed
if [ ! -f "fraud_monitoring.db" ]; then
    echo "🗄️  Initializing database..."
    python setup.py
    echo ""
fi

# Start backend server in background
echo "🔧 Starting backend server on http://localhost:8000..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

# Wait a bit for backend to start
sleep 3

# Check if frontend node_modules exists
cd ../frontend
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
    echo "✅ Frontend dependencies installed"
    echo ""
fi

# Start frontend server
echo "🎨 Starting frontend server on http://localhost:3000..."
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  🌐 Application is running!"
echo "  📊 Frontend: http://localhost:3000"
echo "  🔌 Backend API: http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo ""
echo "  👤 Default Login:"
echo "     Email: admin@example.com"
echo "     Password: admin123"
echo ""
echo "  Press Ctrl+C to stop both servers"
echo "═══════════════════════════════════════════════════════════"
echo ""

npm run dev

# Cleanup on exit
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID 2>/dev/null; exit" INT TERM

