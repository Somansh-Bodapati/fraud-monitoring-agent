@echo off
REM Script to start both backend and frontend servers on Windows

echo 🚀 Starting Expense ^& Fraud Monitoring Agent...
echo.

REM Check if .env exists
if not exist "backend\.env" (
    echo ⚠️  .env file not found. Creating from .env.example...
    if exist "backend\.env.example" (
        copy backend\.env.example backend\.env
        echo ✅ Created .env file. Please add your OPENAI_API_KEY!
        echo.
    ) else (
        echo ❌ .env.example not found. Please create backend\.env manually.
        pause
        exit /b 1
    )
)

REM Check if virtual environment exists
if not exist "backend\venv" (
    echo 📦 Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
    echo ✅ Virtual environment created
    echo.
)

REM Activate virtual environment and install backend dependencies
echo 📦 Installing backend dependencies...
cd backend
call venv\Scripts\activate.bat
pip install -q -r requirements.txt
echo ✅ Backend dependencies installed
echo.

REM Initialize database and create admin user if needed
if not exist "fraud_monitoring.db" (
    echo 🗄️  Initializing database...
    python setup.py
    echo.
)

REM Start backend server in new window
echo 🔧 Starting backend server on http://localhost:8000...
start "Backend Server" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ✅ Backend started
echo.

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Check if frontend node_modules exists
cd ..\frontend
if not exist "node_modules" (
    echo 📦 Installing frontend dependencies...
    call npm install
    echo ✅ Frontend dependencies installed
    echo.
)

REM Start frontend server
echo 🎨 Starting frontend server on http://localhost:3000...
echo.
echo ═══════════════════════════════════════════════════════════
echo   🌐 Application is running!
echo   📊 Frontend: http://localhost:3000
echo   🔌 Backend API: http://localhost:8000
echo   📚 API Docs: http://localhost:8000/docs
echo.
echo   👤 Default Login:
echo      Email: admin@example.com
echo      Password: admin123
echo.
echo   Close this window to stop the frontend server
echo ═══════════════════════════════════════════════════════════
echo.

npm run dev

