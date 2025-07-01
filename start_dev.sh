#!/bin/bash

# LOTRO Forge Development Server Startup Script
# This script activates the virtual environment and starts the development web server

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🚀 Starting LOTRO Forge Development Server..."
echo "📁 Project root: $PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/venv" ]; then
    echo "❌ Virtual environment not found at $PROJECT_ROOT/venv"
    echo "Please run the setup script first: ./scripts/setup_dev.sh"
    exit 1
fi

# Check if run_web.py exists
if [ ! -f "$PROJECT_ROOT/scripts/run_web.py" ]; then
    echo "❌ run_web.py script not found at $PROJECT_ROOT/scripts/run_web.py"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$PROJECT_ROOT/venv/bin/activate"

# Verify activation
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $VIRTUAL_ENV"

# Change to project root directory
cd "$PROJECT_ROOT"

# Run the web server
echo "🌐 Starting web server..."
echo "📱 Web interface: http://localhost:8000"
echo "📚 API docs: http://localhost:8000/docs"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

python "$PROJECT_ROOT/scripts/run_web.py" 