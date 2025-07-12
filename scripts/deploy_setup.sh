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
    flyctl volumes create lotro_companion --size 2 --region iad
    echo "✅ Volume created successfully"
else
    echo "✅ Volume 'lotro_companion' already exists"
fi

# Create PostgreSQL database if it doesn't exist
echo "🗄️  Setting up PostgreSQL database..."
if ! flyctl postgres list | grep -q "lotro-forge-db"; then
    echo "Creating PostgreSQL database 'lotro-forge-db'..."
    flyctl postgres create --name lotro-forge-db --region iad
    echo "✅ Database created successfully"
else
    echo "✅ Database 'lotro-forge-db' already exists"
fi

# Attach database to app
echo "🔗 Attaching database to app..."
flyctl postgres attach lotro-forge-db --app lotro-forge

# Get database connection details
echo "📋 Getting database connection details..."
DB_INFO=$(flyctl postgres connect -a lotro-forge-db --command "echo \$DATABASE_URL")
DB_PASSWORD=$(echo $DB_INFO | grep -o 'password=[^;]*' | cut -d'=' -f2)

echo ""
echo "🎉 Database setup complete!"
echo ""
echo "Database connection details:"
echo "Host: host.internal"
echo "Port: 5432"
echo "Database: lotro_forge"
echo "User: postgres"
echo "Password: $DB_PASSWORD"
echo ""
echo "Next steps:"
echo "1. Set up environment secrets with the database password above"
echo "2. Import LOTRO companion data"
echo "3. Deploy via GitHub Actions (push to main)"
echo ""
echo "To check app status: flyctl status"
echo "To view logs: flyctl logs" 