#!/bin/bash
# Setup script for Scopus Search API

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Scopus Search API - Setup Script                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed"
    exit 1
fi

echo "✅ Python found: $(python --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Setup .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env and add your SCOPUS_API_KEY"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     Setup Complete!                                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env and add your SCOPUS_API_KEY"
echo "   2. Run: python run.py"
echo "   3. Open: http://localhost:8000"
echo ""
echo "📚 Documentation:"
echo "   • README_NEW.md   - Full documentation"
echo "   • MIGRATION.md    - Migration guide"
echo "   • ARCHITECTURE.txt - Architecture overview"
echo ""
