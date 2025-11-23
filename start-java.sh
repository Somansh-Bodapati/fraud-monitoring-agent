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

# Configure Java 17 for the build
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
export PATH="$JAVA_HOME/bin:$PATH"

# Check if Maven is installed
if ! command -v $MVN_CMD &> /dev/null; then
    echo "❌ Maven ('$MVN_CMD') not found in PATH!"
    echo "   Please install Maven: brew install maven"
    echo "   Or ensure it is in your PATH."
    exit 1
fi

echo "🔧 Starting Spring Boot backend on http://localhost:8000..."
# Run in background but keep stdout/stderr attached to console
$MVN_CMD spring-boot:run &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   Logs will appear below..."
echo ""

# Wait for backend to initialize (simple sleep)
sleep 15

# Frontend (Angular)
cd ../frontend-angular
if [ ! -f "package.json" ]; then
    echo "❌ Angular project not found!"
    kill $BACKEND_PID
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

