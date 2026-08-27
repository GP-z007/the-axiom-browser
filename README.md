# Axiom Browser - Setup and Launch Guide

Complete setup scripts to install all dependencies, configure Ollama, and launch the Axiom Browser.

## Quick Start

### macOS / Linux

```bash
# Make script executable (first time only)
chmod +x setup_and_launch.sh

# Run the setup and launch script
./setup_and_launch.sh
```

Or use the Python version (cross-platform):

```bash
# Make executable (first time only)
chmod +x setup_and_launch.py

# Run
python3 setup_and_launch.py
```

### Windows

Double-click `launch.bat` or run from command prompt:

```cmd
launch.bat
```

Or use the Python version:

```cmd
python setup_and_launch.py
```

## What the Scripts Do

### Automated Setup Process

1. ✅ **Check Python Installation**
   - Verifies Python 3.8+ is installed
   - Shows Python version

2. ✅ **Create Virtual Environment**
   - Creates `venv/` directory if it doesn't exist
   - Sets up isolated Python environment

3. ✅ **Install Dependencies**
   - Installs PyQt5 for GUI
   - Installs PyQtWebEngine for browser engine
   - Installs httpx for MCP tools
   - Installs ollama Python client
   - Installs other required packages

4. ✅ **Check Ollama Installation**
   - Verifies Ollama CLI is installed
   - Provides installation instructions if missing

5. ✅ **Start Ollama Service**
   - Starts Ollama server in background
   - Waits for service to be ready

6. ✅ **List Available Models**
   - Fetches and displays all installed Ollama models
   - Shows download instructions if no models found

7. ✅ **Launch Browser**
   - Opens the Axiom Browser with MCP tools enabled
   - Browser runs until closed

## Manual Setup (If Needed)

### 1. Install Python

Ensure Python 3.8+ is installed:

```bash
python3 --version
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from: https://ollama.ai/download

### 5. Start Ollama Service

```bash
ollama serve
```

### 6. Download Models (Optional)

```bash
# Download a model
ollama pull llama2

# Or use the model from your app.py
ollama pull gemma3:27b
```

### 7. Launch Browser

```bash
python web-browser.py
```

## Requirements

### Python Packages

All packages are listed in `requirements.txt`:

- **PyQt5** - GUI framework
- **PyQtWebEngine** - Web browser engine
- **httpx** - HTTP client for MCP tools
- **ollama** - Ollama Python client
- **requests** - Additional HTTP utilities
- **beautifulsoup4** - HTML parsing (optional)
- **lxml** - XML/HTML parser (optional)

### System Requirements

- **Python**: 3.8 or higher
- **Ollama**: Latest version (optional, for AI features)
- **Operating System**: macOS, Linux, or Windows

## Troubleshooting

### Python Not Found

**Error:** `python3: command not found`

**Solution:**
- macOS/Linux: Install Python from python.org or use `brew install python3`
- Windows: Install Python from python.org and check "Add to PATH"

### Virtual Environment Issues

**Error:** `venv module not found`

**Solution:**
```bash
# Install venv module
python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
```

### PyQt5 Installation Fails

**macOS:**
```bash
brew install pyqt5
pip install PyQt5 PyQtWebEngine
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine
```

**Windows:**
```bash
pip install PyQt5 PyQtWebEngine
```

### Ollama Not Starting

1. Check if Ollama is installed:
   ```bash
   ollama --version
   ```

2. Try starting manually:
   ```bash
   ollama serve
   ```

3. Check if port 11434 is available:
   ```bash
   # macOS/Linux
   lsof -i :11434
   
   # Windows
   netstat -ano | findstr :11434
   ```

### No Models Found

Download a model:
```bash
ollama pull llama2
# or
ollama pull gemma3:27b
```

### Browser Won't Launch

1. Check all dependencies are installed:
   ```bash
   pip list | grep -i pyqt
   ```

2. Try running directly:
   ```bash
   python web-browser.py
   ```

3. Check for error messages in terminal

### MCP Tools Not Working

1. Verify httpx is installed:
   ```bash
   pip install httpx
   ```

2. Check browser status bar for MCP status

3. Restart browser after installing httpx

## Script Files

- **setup_and_launch.sh** - Bash script for macOS/Linux
- **setup_and_launch.py** - Python script (cross-platform)
- **launch.bat** - Batch script for Windows

## Features After Setup

Once setup is complete, your browser will have:

✅ **Dark theme modern UI**  
✅ **MCP-powered web search**  
✅ **MCP-powered webpage fetching**  
✅ **Ollama integration ready**  
✅ **Beautiful search results display**  
✅ **Smart URL/search detection**  

## Next Steps

1. **Use the Browser:**
   - Search: Type a query and press Enter
   - Navigate: Type a URL and press Enter

2. **Connect to Ollama:**
   - The browser is ready for Ollama integration
   - Configure MCP tools to connect to Ollama

3. **Customize:**
   - Modify `web-browser.py` for custom features
   - Add more MCP tools as needed

## Support

For issues or questions:
- Check the troubleshooting section above
- Review browser logs in the terminal
- Check Ollama service status

## License

Part of the Axiom OS project.

