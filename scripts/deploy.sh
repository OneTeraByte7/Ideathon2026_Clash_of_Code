#!/bin/bash
# Render deployment script

set -e

echo "🚀 Starting deployment..."

# Upgrade pip and build tools
pip install --upgrade pip setuptools wheel

# Install packages individually to handle build failures
echo "📦 Installing core dependencies..."
pip install fastapi==0.104.1
pip install uvicorn==0.24.0

# Install database dependencies
echo "📦 Installing database dependencies..."
pip install motor==3.3.2
pip install beanie==1.20.0

# Install pydantic with compatible version
echo "📦 Installing pydantic dependencies..."
pip install pydantic==2.4.2
pip install pydantic-settings==2.1.0

# Install other dependencies
echo "📦 Installing other dependencies..."
pip install python-dotenv==1.0.0
pip install httpx==0.25.2
pip install python-multipart==0.0.6
pip install apscheduler==3.10.4
pip install requests==2.31.0
pip install websockets==11.0.3

# Try to install optional AI dependency
echo "📦 Installing optional dependencies..."
pip install google-generativeai==0.3.2 || echo "⚠️ Skipping google-generativeai"

echo "✅ Deployment complete!"