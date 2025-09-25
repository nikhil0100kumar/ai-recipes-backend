#!/usr/bin/env python3
"""
Startup script for AI Recipes Backend
"""
import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python version: {sys.version.split()[0]}")


def check_env_file():
    """Check if .env file exists."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please create a .env file based on .env.example")
        print("Make sure to set your GEMINI_API_KEY")
        sys.exit(1)
    print("✓ .env file found")


def install_dependencies():
    """Install Python dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)


def start_server():
    """Start the FastAPI server."""
    print("Starting AI Recipes Backend...")
    print("Server will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.check_call([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n✓ Server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)


def main():
    """Main startup routine."""
    print("🚀 AI Recipes Backend Startup")
    print("-" * 30)
    
    check_python_version()
    check_env_file()
    install_dependencies()
    start_server()


if __name__ == "__main__":
    main()
