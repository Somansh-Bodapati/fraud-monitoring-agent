#!/bin/bash

echo "🚀 Starting Java Backend..."
echo ""

cd backend-java

# Configure Java 17
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
export PATH="$JAVA_HOME/bin:$PATH"

# Check if Maven wrapper exists
if [ -f "./mvnw" ]; then
    MVN_CMD="./mvnw"
else
    MVN_CMD="mvn"
fi

# Check if Maven is installed
if ! command -v $MVN_CMD &> /dev/null; then
    echo "❌ Maven not found!"
    echo "   Install with: brew install maven"
    exit 1
fi

echo "🔧 Starting Spring Boot on http://localhost:8000..."
echo ""
$MVN_CMD spring-boot:run
