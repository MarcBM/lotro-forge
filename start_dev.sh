#!/bin/bash

# LOTRO Forge Development Environment Setup

echo "🚀 Setting up LOTRO Forge development environment..."

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip and install requirements
echo "📦 Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Install flyctl if not present
if ! command -v flyctl &> /dev/null; then
    echo "📦 Installing flyctl..."
    curl -L https://fly.io/install.sh | sh
    export PATH="$HOME/.fly/bin:$PATH"
fi

# Check auth status (safely)
check_fly_auth() {
    if command -v flyctl &> /dev/null; then
        if flyctl auth whoami &> /dev/null 2>&1; then
            echo "✅ Authenticated with Fly.io as: $(flyctl auth whoami 2>/dev/null)"
            return 0
        else
            echo "🔐 Please authenticate with Fly.io: flyctl auth login"
            return 1
        fi
    else
        echo "⚠️  flyctl not available"
        return 1
    fi
}

# Run auth check
check_fly_auth

echo "✅ Development environment ready!"
echo "🌐 Start server: python scripts/run_web.py" 