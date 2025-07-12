#!/bin/bash

# LOTRO Forge Deployment Setup Script
# This script creates the fly.io app and performs initial setup

set -e  # Exit on any error

echo "🚀 LOTRO Forge Deployment Setup"
echo "================================"

# Check if flyctl is installed and authenticated
if ! command -v flyctl &> /dev/null; then
    echo "❌ Error: flyctl is not installed. Please install it first."
    exit 1
fi

# Check if user is authenticated
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ Error: Not authenticated with fly.io. Please run 'flyctl auth login' first."
    exit 1
fi

echo "✅ Fly.io CLI is ready"

# Check if app already exists
if flyctl apps list | grep -q "lotro-forge"; then
    echo "⚠️  App 'lotro-forge' already exists. Skipping app creation."
else
    echo "📦 Creating fly.io app 'lotro-forge'..."
    flyctl apps create lotro-forge --org personal
    echo "✅ App created successfully"
fi

# Create volume for LOTRO companion data if it doesn't exist
echo "💾 Setting up data volume..."
if ! flyctl volumes list | grep -q "lotro_companion"; then
    echo "Creating volume 'lotro_companion'..."
    flyctl volumes create lotro_companion --size 1 --region iad
    echo "✅ Volume created successfully"
else
    echo "✅ Volume 'lotro_companion' already exists"
fi

echo ""
echo "🎉 Initial setup complete!"
echo ""
echo "Next steps:"
echo "1. Push your code to main branch to trigger deployment"
echo "2. Set up environment secrets:"
echo "   flyctl secrets set DB_HOST=host.internal"
echo "   flyctl secrets set DB_PORT=5432"
echo "   flyctl secrets set DB_NAME=lotro_forge"
echo "   flyctl secrets set DB_USER=postgres"
echo "   flyctl secrets set DB_PASSWORD=<your-production-password>"
echo "   flyctl secrets set LOTRO_FORGE_ENV=production"
echo "   flyctl secrets set LOTRO_FORGE_SECRET_KEY=<your-super-secret-key>"
echo "   flyctl secrets set CORS_ORIGINS=https://lotroforge.com,https://www.lotroforge.com"
echo "3. Add custom domain: flyctl certs add lotroforge.com"
echo "4. Import LOTRO companion data (see deployment checklist)"
echo ""
echo "To check app status: flyctl status"
echo "To view logs: flyctl logs" 