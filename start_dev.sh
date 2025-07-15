#!/bin/bash

# LOTRO Forge Development Server Startup Script
# This script sets up the complete development environment including flyctl

set -e  # Exit on any error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🚀 Starting LOTRO Forge Development Environment Setup..."
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

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "📦 flyctl not found. Installing Fly.io CLI..."
    
    # Install flyctl
    curl -L https://fly.io/install.sh | sh
    
    # Add flyctl to PATH permanently
    export FLYCTL_INSTALL="$HOME/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"
    
    # Add to shell profile for permanent access
    SHELL_PROFILE=""
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_PROFILE="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_PROFILE="$HOME/.zshrc"
    elif [ -f "$HOME/.profile" ]; then
        SHELL_PROFILE="$HOME/.profile"
    fi
    
    if [ -n "$SHELL_PROFILE" ]; then
        # Check if flyctl PATH is already in the profile
        if ! grep -q "FLYCTL_INSTALL" "$SHELL_PROFILE"; then
            echo "" >> "$SHELL_PROFILE"
            echo "# Fly.io CLI" >> "$SHELL_PROFILE"
            echo "export FLYCTL_INSTALL=\"\$HOME/.fly\"" >> "$SHELL_PROFILE"
            echo "export PATH=\"\$FLYCTL_INSTALL/bin:\$PATH\"" >> "$SHELL_PROFILE"
            echo "✅ Added flyctl to $SHELL_PROFILE for permanent access"
        else
            echo "✅ flyctl PATH already configured in $SHELL_PROFILE"
        fi
    else
        echo "⚠️  Could not find shell profile to add flyctl PATH permanently"
        echo "   You may need to manually add to your shell profile:"
        echo "   export FLYCTL_INSTALL=\"\$HOME/.fly\""
        echo "   export PATH=\"\$FLYCTL_INSTALL/bin:\$PATH\""
    fi
    
    echo "✅ flyctl installed successfully!"
else
    echo "✅ flyctl is already installed"
fi

# Add flyctl to PATH for this session
export FLYCTL_INSTALL="$HOME/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"

# Source the shell profile to load any new PATH settings
if [ -f "$HOME/.bashrc" ]; then
    source "$HOME/.bashrc"
elif [ -f "$HOME/.zshrc" ]; then
    source "$HOME/.zshrc"
elif [ -f "$HOME/.profile" ]; then
    source "$HOME/.profile"
fi

# Verify flyctl is accessible
if ! command -v flyctl &> /dev/null; then
    echo "❌ flyctl is still not accessible after PATH setup"
    echo "   Please run: source ~/.bashrc"
    echo "   Or restart your terminal session"
    exit 1
else
    echo "✅ flyctl is accessible: $(which flyctl)"
fi

# Check if user is authenticated with Fly.io
if ! flyctl auth whoami &> /dev/null; then
    echo ""
    echo "🔐 You need to authenticate with Fly.io:"
    echo "   Run: flyctl auth login"
    echo "   This will open your browser for authentication."
    echo ""
    echo "After authentication, you can continue with deployment commands."
    echo ""
    echo "⚠️  Development environment setup incomplete - please authenticate first"
    exit 1
else
    echo "✅ Already authenticated with Fly.io as: $(flyctl auth whoami)"
fi

echo ""
echo "✅ Development environment ready!"
echo ""
echo "🔧 flyctl is now available in this terminal for deployment commands"
echo ""
echo "🌐 To start the web server:"
echo "   1. Open a new terminal tab in Cursor"
echo "   2. Run: source venv/bin/activate"
echo "   3. Run: python scripts/run_web.py"
echo ""
echo "📱 Web interface: http://localhost:8000"
echo "📚 API docs: http://localhost:8000/docs"
echo ""
echo "💡 Note: flyctl will be available in new terminal sessions automatically"
echo "⏹️  Press Ctrl+C to stop the server (when running)"
echo "" 