#!/usr/bin/env python3
"""
Axiom Browser Setup and Launch Script
Installs all dependencies, starts Ollama, loads models, and launches the browser
Works on macOS, Linux, and Windows
"""

import sys
import os
import subprocess
import time
import json
import urllib.request
import urllib.error
from pathlib import Path

# Colors for output (cross-platform)
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color=Colors.RESET):
    """Print colored text"""
    if sys.platform == 'win32':
        # Windows doesn't support ANSI colors in older terminals
        print(text)
    else:
        print(f"{color}{text}{Colors.RESET}")

def print_info(msg):
    print_colored(f"[INFO] {msg}", Colors.BLUE)

def print_success(msg):
    print_colored(f"[SUCCESS] {msg}", Colors.GREEN)

def print_warning(msg):
    print_colored(f"[WARNING] {msg}", Colors.YELLOW)

def print_error(msg):
    print_colored(f"[ERROR] {msg}", Colors.RED)

def print_separator():
    print("=" * 50)

def check_command(cmd):
    """Check if a command exists"""
    try:
        subprocess.run([cmd, '--version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL,
                      check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def run_command(cmd, check=True, shell=False):
    """Run a command and return success status"""
    try:
        if isinstance(cmd, str) and not shell:
            cmd = cmd.split()
        subprocess.run(cmd, check=check, shell=shell, 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_python():
    """Check Python version"""
    print_info("Checking Python installation...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Python 3.8 or higher is required")
        print_error(f"Current version: {version.major}.{version.minor}")
        return False
    print_success(f"Python {version.major}.{version.minor}.{version.micro} found")
    return True

def setup_venv():
    """Create and activate virtual environment"""
    venv_path = Path("venv")
    
    print_info("Setting up virtual environment...")
    if not venv_path.exists():
        print_info("Creating virtual environment...")
        if run_command([sys.executable, "-m", "venv", "venv"]):
            print_success("Virtual environment created")
        else:
            print_error("Failed to create virtual environment")
            return False
    else:
        print_info("Virtual environment already exists")
    
    # Determine activation script path based on OS
    if sys.platform == 'win32':
        activate_script = venv_path / "Scripts" / "activate.bat"
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:
        activate_script = venv_path / "bin" / "activate"
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    if not python_exe.exists():
        print_error("Virtual environment Python not found")
        return False
    
    print_success("Virtual environment ready")
    return python_exe, pip_exe

def install_dependencies(pip_exe):
    """Install all required dependencies"""
    print_separator()
    print_info("Installing Python dependencies...")
    print_separator()
    
    requirements_file = Path("requirements.txt")
    
    if requirements_file.exists():
        print_info(f"Installing from {requirements_file}...")
        if run_command([str(pip_exe), "install", "-r", str(requirements_file)], check=False):
            print_success("All dependencies installed")
        else:
            print_warning("Some packages may have failed to install")
    else:
        print_warning("requirements.txt not found. Installing core packages...")
        packages = [
            "PyQt5>=5.15.0",
            "PyQtWebEngine>=5.15.0",
            "httpx>=0.24.0",
            "ollama>=0.6.0",
            "requests>=2.28.0"
        ]
        for pkg in packages:
            if run_command([str(pip_exe), "install", pkg], check=False):
                print_success(f"Installed {pkg}")
            else:
                print_warning(f"Failed to install {pkg}")
    
    return True

def check_ollama():
    """Check if Ollama is installed"""
    print_separator()
    print_info("Checking Ollama installation...")
    print_separator()
    
    if check_command("ollama"):
        try:
            result = subprocess.run(["ollama", "--version"], 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            version = result.stdout.strip() if result.stdout else "unknown"
            print_success(f"Ollama found: {version}")
            return True
        except:
            print_warning("Ollama found but version check failed")
            return True
    else:
        print_warning("Ollama CLI not found")
        print_info("Install from: https://ollama.ai")
        print_info("macOS: brew install ollama")
        print_info("Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        print_info("Windows: Download from https://ollama.ai/download")
        return False

def start_ollama():
    """Start Ollama service"""
    print_separator()
    print_info("Starting Ollama service...")
    print_separator()
    
    # Check if Ollama is already running
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=2) as response:
            print_success("Ollama service is already running")
            return True
    except (urllib.error.URLError, OSError):
        pass
    
    print_info("Starting Ollama service...")
    if sys.platform == 'win32':
        # Windows: start in background
        subprocess.Popen(["ollama", "serve"], 
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        # Unix: start in background
        subprocess.Popen(["ollama", "serve"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
    
    # Wait for service to start
    print_info("Waiting for Ollama to start...")
    for i in range(10):
        time.sleep(1)
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=2) as response:
                print_success("Ollama service started")
                return True
        except (urllib.error.URLError, OSError):
            if i == 9:
                print_warning("Ollama may not have started. Try manually: ollama serve")
                return False
    
    return False

def list_ollama_models():
    """List available Ollama models"""
    print_separator()
    print_info("Fetching available Ollama models...")
    print_separator()
    
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            models = [model['name'] for model in data.get('models', [])]
            
            if models:
                print_success("Available models:")
                for model in models:
                    print(f"  • {model}")
            else:
                print_warning("No models found")
                print_info("Download a model: ollama pull llama2")
                print_info("Example: ollama pull gemma3:27b")
            return models
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
        print_warning(f"Could not fetch models: {e}")
        return []

def launch_browser(python_exe):
    """Launch the Axiom Browser"""
    print_separator()
    print_info("Launching Axiom Browser...")
    print_separator()
    
    browser_script = Path("web-browser.py")
    if not browser_script.exists():
        print_error("web-browser.py not found!")
        return False
    
    print_success("Starting Axiom Browser...")
    print()
    print_info("Browser will open in a new window")
    print_info("Press Ctrl+C to stop the browser")
    print()
    
    try:
        # Launch browser (this will block until browser closes)
        subprocess.run([str(python_exe), str(browser_script)], check=True)
        return True
    except KeyboardInterrupt:
        print()
        print_info("Browser stopped by user")
        return True
    except Exception as e:
        print_error(f"Failed to launch browser: {e}")
        return False

def main():
    """Main setup and launch function"""
    print_separator()
    print_colored("  Axiom Browser - Setup & Launch", Colors.BOLD + Colors.CYAN)
    print_separator()
    print()
    
    # Get script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Step 1: Check Python
    if not check_python():
        sys.exit(1)
    
    # Step 2: Setup virtual environment
    venv_result = setup_venv()
    if not venv_result:
        sys.exit(1)
    python_exe, pip_exe = venv_result
    
    # Step 3: Install dependencies
    if not install_dependencies(pip_exe):
        print_warning("Continuing despite installation warnings...")
    
    # Step 4: Check Ollama
    ollama_available = check_ollama()
    
    # Step 5: Start Ollama if available
    if ollama_available:
        if start_ollama():
            # Step 6: List models
            list_ollama_models()
    else:
        response = input("\nContinue without Ollama? (y/n): ").strip().lower()
        if response != 'y':
            print_info("Exiting. Please install Ollama and run this script again.")
            sys.exit(0)
    
    print()
    
    # Step 7: Launch browser
    launch_browser(python_exe)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_info("Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

