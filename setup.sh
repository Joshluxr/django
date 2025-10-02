#!/bin/bash
# Labubu Monitor Bot - Quick Setup Script

set -e

echo "🐰 Labubu Monitor Bot - Quick Setup"
echo "===================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Found Python $PYTHON_VERSION"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate 2>/dev/null || {
    echo "❌ Failed to activate virtual environment"
    exit 1
}
echo "✅ Virtual environment activated"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
echo ""
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your Discord bot token!"
    echo "   Open .env and set: DISCORD_TOKEN=your_token_here"
else
    echo "✅ .env file already exists"
fi

# Create config.yaml if it doesn't exist
echo ""
if [ ! -f "config.yaml" ]; then
    echo "📝 Creating config.yaml file..."
    cp config.yaml.example config.yaml
    echo "✅ config.yaml file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit config.yaml and configure:"
    echo "   - source_channels: Add channel IDs to monitor"
    echo "   - destination_channel_id: Where to post alerts"
else
    echo "✅ config.yaml file already exists"
fi

# Run tests
echo ""
echo "🧪 Running tests..."
if python3 -m pytest tests/ -q; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed. Please check the output above."
    exit 1
fi

# Validate configuration
echo ""
echo "🔍 Validating configuration..."
if python3 -c "from config import load_config; load_config()" 2>/dev/null; then
    echo "✅ Configuration is valid"
else
    echo "⚠️  Configuration validation failed (expected if you haven't set up config.yaml yet)"
fi

echo ""
echo "============================================"
echo "✅ Setup complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your DISCORD_TOKEN"
echo "2. Edit config.yaml and add your channel IDs"
echo "3. Read SETUP_GUIDE.md for detailed instructions"
echo "4. Run the bot: python bot.py"
echo ""
echo "Need help? Check SETUP_GUIDE.md or README.md"
echo ""
