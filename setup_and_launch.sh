#!/bin/bash
# Axiom Browser Setup and Launch Script
# This script installs all dependencies, starts Ollama, loads models, and launches the browser

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_separator() {
    echo "=========================================="
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_separator
echo "  Axiom Browser - Setup & Launch Script"
print_separator
echo ""

# Step 1: Check Python installation
print_info "Checking Python installation..."
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Step 2: Check pip
print_info "Checking pip installation..."
if ! command_exists pip3; then
    print_warning "pip3 not found. Attempting to install..."
    python3 -m ensurepip --upgrade
fi
print_success "pip is available"

# Step 3: Create/activate virtual environment
print_info "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Step 4: Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Step 5: Install Python dependencies
print_separator
print_info "Installing Python dependencies..."
print_separator

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "All Python dependencies installed"
else
    print_warning "requirements.txt not found. Installing individual packages..."
    pip install PyQt5 PyQtWebEngine httpx ollama requests beautifulsoup4 lxml
    print_success "Python packages installed"
fi

# Step 6: Check Ollama CLI installation
print_separator
print_info "Checking Ollama installation..."
print_separator

if command_exists ollama; then
    print_success "Ollama CLI found"
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -n1 || echo "unknown")
    print_info "Version: $OLLAMA_VERSION"
else
    print_warning "Ollama CLI not found in PATH"
    print_info "Please install Ollama from: https://ollama.ai"
    print_info "On macOS: brew install ollama"
    print_info "Or download from: https://ollama.ai/download"
    echo ""
    read -p "Continue without Ollama? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Exiting. Please install Ollama and run this script again."
        exit 1
    fi
    SKIP_OLLAMA=true
fi

# Step 7: Start Ollama service
if [ -z "$SKIP_OLLAMA" ]; then
    print_separator
    print_info "Starting Ollama service..."
    print_separator
    
    # Check if Ollama is already running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        print_success "Ollama service is already running"
    else
        print_info "Starting Ollama service..."
        ollama serve > /dev/null 2>&1 &
        OLLAMA_PID=$!
        
        # Wait for Ollama to start
        print_info "Waiting for Ollama to start..."
        sleep 3
        
        # Check if it started successfully
        if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
            print_success "Ollama service started (PID: $OLLAMA_PID)"
        else
            print_warning "Ollama service may not have started properly"
            print_info "You may need to start it manually: ollama serve"
        fi
    fi
    
    # Step 8: List available models
    print_separator
    print_info "Fetching available Ollama models..."
    print_separator
    
    MODELS=$(curl -s http://localhost:11434/api/tags 2>/dev/null | python3 -c "import sys, json; data=json.load(sys.stdin); models=[m['name'] for m in data.get('models', [])]; print('\n'.join(models))" 2>/dev/null || echo "")
    
    if [ -z "$MODELS" ]; then
        print_warning "No models found or unable to connect to Ollama"
        print_info "You can download models using: ollama pull <model-name>"
        print_info "Example: ollama pull llama2"
    else
        print_success "Available models:"
        echo "$MODELS" | while read -r model; do
            echo "  - $model"
        done
    fi
    echo ""
fi

# Step 9: Launch the browser
print_separator
print_info "Launching Axiom Browser..."
print_separator

if [ ! -f "web-browser.py" ]; then
    print_error "web-browser.py not found!"
    exit 1
fi

# Make sure script is executable
chmod +x web-browser.py

print_success "Starting Axiom Browser..."
echo ""
print_info "Browser will open in a new window"
print_info "Press Ctrl+C to stop the browser"
echo ""

# Launch browser
python3 web-browser.py

# Cleanup on exit
if [ ! -z "$OLLAMA_PID" ]; then
    print_info "Cleaning up..."
fi

