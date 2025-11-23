#!/bin/bash

echo "🎨 Starting Angular Frontend..."
echo ""

cd frontend-angular

if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

echo "Starting on http://localhost:4200..."
echo ""
npm start
