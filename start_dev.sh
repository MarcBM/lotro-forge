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

# Add flyctl to PATH for this session
export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"

echo "✅ Development environment ready!"
echo ""
echo "🌐 To start the web server:"
echo "   1. Open a new terminal tab in Cursor"
echo "   2. Run: source venv/bin/activate"
echo "   3. Run: python scripts/run_web.py"
echo ""
echo "📱 Web interface: http://localhost:8000"
echo "📚 API docs: http://localhost:8000/docs"
echo ""
echo "🔧 flyctl is now available in this terminal for deployment commands"
echo "⏹️  Press Ctrl+C to stop the server (when running)"
echo "" 