#!/bin/bash

echo "🚀 Starting Expense & Fraud Monitoring Agent (Java + Angular)..."
echo ""

# Backend (Spring Boot)
echo "📦 Building Spring Boot backend..."
cd backend-java
if [ ! -f "pom.xml" ]; then
    echo "❌ Maven project not found!"
    exit 1
fi

# Check if Maven wrapper exists, if not use system Maven
if [ -f "./mvnw" ]; then
    MVN_CMD="./mvnw"
else
    MVN_CMD="mvn"
fi

echo "🔧 Starting Spring Boot backend on http://localhost:8000..."
$MVN_CMD spring-boot:run > ../backend-java.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

# Wait for backend to start
sleep 10

# Frontend (Angular)
cd ../frontend-angular
if [ ! -f "package.json" ]; then
    echo "❌ Angular project not found!"
    exit 1
fi

if [ ! -d "node_modules" ]; then
    echo "📦 Installing Angular dependencies..."
    npm install
    echo "✅ Dependencies installed"
    echo ""
fi

echo "🎨 Starting Angular frontend on http://localhost:4200..."
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  🌐 Application is running!"
echo "  📊 Frontend: http://localhost:4200"
echo "  🔌 Backend API: http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/swagger-ui.html"
echo ""
echo "  👤 Default Login:"
echo "     Email: admin@example.com"
echo "     Password: admin123"
echo ""
echo "  Press Ctrl+C to stop both servers"
echo "═══════════════════════════════════════════════════════════"
echo ""

npm start

# Cleanup on exit
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID 2>/dev/null; exit" INT TERM

