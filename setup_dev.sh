#!/bin/bash

# ATS Resume Scanner - Local Dev Setup Script

echo "🚀 Starting local development setup..."

# 1. Check for Python 3.11+
if ! command -v python3 &> /dev/null
then
    echo "❌ python3 could not be found. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# 2. Create Virtual Environment
echo "📦 Creating virtual environment in 'backend/venv'..."
python3 -m venv backend/venv

# 3. Activate venv and install dependencies
echo "🛠 Installing dependencies..."
source backend/venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# 4. Handle .env file
if [ ! -f .env ]; then
    echo "📄 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Action Required: Update the .env file with your actual API keys!"
else
    echo "✅ .env file already exists."
fi

echo ""
echo "---------------------------------------------------"
echo "🎉 Setup complete!"
echo ""
echo "To start developing:"
echo "1. Start local infrastructure (Postgres, Redis, Qdrant):"
echo "   docker-compose -f infra/docker-compose.yml up -d"
echo ""
echo "2. Activate the virtual environment:"
echo "   source backend/venv/bin/activate"
echo ""
echo "3. Run the FastAPI server:"
echo "   cd backend && uvicorn app.main:app --reload"
echo ""
echo "4. Verify health:"
echo "   curl http://localhost:8000/health"
echo "---------------------------------------------------"
