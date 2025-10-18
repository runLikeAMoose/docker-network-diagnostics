#!/bin/bash

# Kill any existing server
pkill -f "uvicorn main:app" 2>/dev/null

# Activate virtual environment
source venv/bin/activate

# Start server
echo "🚀 Starting Docker Network Diagnostics..."
echo "📍 Server will be at: http://localhost:8000"
echo "🔄 Auto-reload enabled - code changes will apply automatically"
echo ""
echo "Press Ctrl+C to stop"
echo ""

uvicorn main:app --reload --port 8000
