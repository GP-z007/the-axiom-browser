#!/bin/bash
# Installation script for MCP Tools Server

echo "Installing MCP Tools Server dependencies..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install required packages
echo "Installing core dependencies..."
pip install httpx

echo "Installing optional dependencies for better HTML parsing..."
pip install beautifulsoup4 lxml

echo "Making mcp-tools.py executable..."
chmod +x mcp-tools.py

echo ""
echo "✓ Installation complete!"
echo ""
echo "To run the MCP server:"
echo "  python mcp-tools.py"
echo ""
echo "Or test it:"
echo "  python test-mcp-tools.py"

