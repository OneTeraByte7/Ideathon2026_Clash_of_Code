#!/bin/bash
# Quick fix script for Render deployment issues

echo "🔧 Fixing Render deployment dependencies..."

# Backup original requirements
cp server/requirements.txt server/requirements.txt.backup

# Create render-compatible requirements
cat > server/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
motor==3.3.2
pydantic==2.5.2
pydantic-settings==2.1.0
python-dotenv==1.0.0
httpx==0.25.2
python-multipart==0.0.6
apscheduler==3.10.4
requests==2.31.0
beanie==1.20.0
google-generativeai==0.3.2
EOF

echo "✅ Updated requirements.txt with Render-compatible versions"

# Update render.yaml with optimizations
cat > render.yaml << 'EOF'
services:
  - type: web
    name: asclepius-api
    env: python
    plan: free
    buildCommand: cd server && pip install --upgrade pip && pip install -r requirements.txt
    startCommand: cd server && python -m uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.7
      - key: PIP_NO_CACHE_DIR
        value: 1
      - key: PIP_DISABLE_PIP_VERSION_CHECK
        value: 1
EOF

echo "✅ Updated render.yaml with build optimizations"

# Test installation locally (optional)
echo "🧪 Testing requirements locally..."
if command -v python3 &> /dev/null; then
    cd server
    python3 -m pip install -r requirements.txt --dry-run
    if [ $? -eq 0 ]; then
        echo "✅ Requirements look good for installation"
    else
        echo "⚠️ Some issues detected, but may work on Render"
    fi
    cd ..
else
    echo "ℹ️ Python not found locally, skipping test"
fi

echo ""
echo "🚀 Ready to deploy! Next steps:"
echo "1. Commit and push these changes"
echo "2. Try deployment on Render again"  
echo "3. If still failing, check RENDER_TROUBLESHOOTING.md"
echo ""