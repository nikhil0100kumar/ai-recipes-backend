#!/usr/bin/env python
"""
Deployment Validation Script for AI Recipes Backend
This script checks if the backend is properly configured for Render deployment
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title:^60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}")

def check_mark(passed: bool) -> str:
    """Return check or cross mark based on status"""
    return f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"

def check_file_exists(filename: str, required: bool = True) -> Tuple[bool, str]:
    """Check if a file exists"""
    exists = Path(filename).exists()
    if exists:
        return True, f"{check_mark(True)} {filename} found"
    elif required:
        return False, f"{check_mark(False)} {filename} NOT FOUND (REQUIRED)"
    else:
        return True, f"{Colors.YELLOW}⚠{Colors.RESET} {filename} not found (optional)"

def validate_dockerfile() -> Tuple[bool, List[str]]:
    """Validate Dockerfile content"""
    messages = []
    passed = True
    
    if not Path("Dockerfile").exists():
        return False, [f"{check_mark(False)} Dockerfile not found"]
    
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    # Check for essential Dockerfile components
    checks = [
        ("FROM python:3.11", "Python 3.11 base image"),
        ("WORKDIR /app", "Working directory set"),
        ("COPY requirements.txt", "Requirements copy"),
        ("RUN pip install", "Pip install command"),
        ("EXPOSE 8000", "Port 8000 exposed"),
        ("CMD", "Start command defined")
    ]
    
    for check_str, description in checks:
        if check_str in content:
            messages.append(f"  {check_mark(True)} {description}")
        else:
            messages.append(f"  {check_mark(False)} {description} - MISSING")
            passed = False
    
    return passed, messages

def validate_render_yaml() -> Tuple[bool, List[str]]:
    """Validate render.yaml configuration"""
    messages = []
    passed = True
    
    if not Path("render.yaml").exists():
        return False, [f"{check_mark(False)} render.yaml not found"]
    
    import yaml
    with open("render.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Check render.yaml structure
    if "services" not in config:
        messages.append(f"  {check_mark(False)} Services section missing")
        return False, messages
    
    service = config["services"][0] if config["services"] else {}
    
    checks = {
        "type": "web",
        "runtime": "docker",
        "name": "ai-recipes-backend",
        "plan": "free"
    }
    
    for key, expected in checks.items():
        actual = service.get(key)
        if actual == expected:
            messages.append(f"  {check_mark(True)} {key}: {actual}")
        else:
            messages.append(f"  {check_mark(False)} {key}: {actual} (expected: {expected})")
            passed = False if key in ["type", "runtime"] else passed
    
    # Check environment variables
    env_vars = service.get("envVars", [])
    env_keys = [var.get("key") for var in env_vars if isinstance(var, dict)]
    
    if env_vars:
        messages.append(f"  {check_mark(True)} Environment variables configured: {', '.join(env_keys[:3])}...")
    else:
        messages.append(f"  {Colors.YELLOW}⚠{Colors.RESET} No environment variables in render.yaml (will need to add in dashboard)")
    
    return passed, messages

def validate_requirements() -> Tuple[bool, List[str]]:
    """Validate requirements.txt"""
    messages = []
    passed = True
    
    if not Path("requirements.txt").exists():
        return False, [f"{check_mark(False)} requirements.txt not found"]
    
    with open("requirements.txt", "r") as f:
        requirements = f.read()
    
    essential_packages = [
        "fastapi",
        "uvicorn",
        "google-generativeai",
        "python-dotenv",
        "Pillow",
        "pydantic"
    ]
    
    for package in essential_packages:
        if package in requirements:
            messages.append(f"  {check_mark(True)} {package} included")
        else:
            messages.append(f"  {check_mark(False)} {package} NOT FOUND")
            passed = False
    
    return passed, messages

def validate_python_files() -> Tuple[bool, List[str]]:
    """Validate Python application files"""
    messages = []
    passed = True
    
    files_to_check = [
        ("main.py", True),
        ("config.py", True),
        ("models.py", True),
        ("gemini_service.py", True),
        (".env", False),
        (".env.example", True)
    ]
    
    for filename, required in files_to_check:
        exists = Path(filename).exists()
        if exists:
            messages.append(f"  {check_mark(True)} {filename}")
        elif required:
            messages.append(f"  {check_mark(False)} {filename} NOT FOUND")
            passed = False
        else:
            messages.append(f"  {Colors.YELLOW}⚠{Colors.RESET} {filename} not found (create from .env.example)")
    
    return passed, messages

def check_git_status() -> Tuple[bool, List[str]]:
    """Check Git repository status"""
    messages = []
    passed = True
    
    try:
        # Check if it's a git repository
        result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            return False, [f"{check_mark(False)} Not a Git repository"]
        
        # Check remote
        result = subprocess.run(["git", "remote", "get-url", "origin"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            remote_url = result.stdout.strip()
            messages.append(f"  {check_mark(True)} Remote: {remote_url}")
        else:
            messages.append(f"  {check_mark(False)} No Git remote configured")
            passed = False
        
        # Check for uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            messages.append(f"  {Colors.YELLOW}⚠{Colors.RESET} Uncommitted changes detected")
            messages.append(f"    Run: git add -A && git commit -m 'message' && git push")
        else:
            messages.append(f"  {check_mark(True)} All changes committed")
        
        # Check current branch
        result = subprocess.run(["git", "branch", "--show-current"], 
                              capture_output=True, text=True)
        branch = result.stdout.strip()
        messages.append(f"  {check_mark(True)} Current branch: {branch}")
        
    except Exception as e:
        messages.append(f"  {check_mark(False)} Git error: {str(e)}")
        passed = False
    
    return passed, messages

def test_python_syntax() -> Tuple[bool, List[str]]:
    """Test Python files for syntax errors"""
    messages = []
    passed = True
    
    python_files = ["main.py", "config.py", "models.py", "gemini_service.py"]
    
    for filename in python_files:
        if not Path(filename).exists():
            continue
        
        try:
            with open(filename, "r") as f:
                code = f.read()
            compile(code, filename, "exec")
            messages.append(f"  {check_mark(True)} {filename} syntax OK")
        except SyntaxError as e:
            messages.append(f"  {check_mark(False)} {filename} has syntax error: {e}")
            passed = False
    
    return passed, messages

def check_environment_variables() -> Tuple[bool, List[str]]:
    """Check if required environment variables are configured"""
    messages = []
    passed = True
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        messages.append(f"  {check_mark(True)} .env file exists")
        
        with open(".env", "r") as f:
            env_content = f.read()
        
        if "GEMINI_API_KEY" in env_content and "your_gemini_api_key_here" not in env_content:
            messages.append(f"  {check_mark(True)} GEMINI_API_KEY appears configured")
        else:
            messages.append(f"  {Colors.YELLOW}⚠{Colors.RESET} GEMINI_API_KEY needs to be set in Render dashboard")
    else:
        messages.append(f"  {Colors.YELLOW}⚠{Colors.RESET} .env file not found (OK for production)")
        messages.append(f"    Remember to set environment variables in Render dashboard")
    
    return passed, messages

def main():
    """Run all validation checks"""
    print_header("AI RECIPES BACKEND - DEPLOYMENT VALIDATION")
    
    all_passed = True
    
    # 1. Check essential files
    print(f"\n{Colors.BOLD}1. Essential Files Check{Colors.RESET}")
    checks = [
        ("Dockerfile", True),
        ("render.yaml", True),
        ("requirements.txt", True),
        ("main.py", True),
        (".gitignore", True),
        ("README.md", False)
    ]
    
    for filename, required in checks:
        passed, message = check_file_exists(filename, required)
        print(f"   {message}")
        if not passed and required:
            all_passed = False
    
    # 2. Validate Dockerfile
    print(f"\n{Colors.BOLD}2. Dockerfile Validation{Colors.RESET}")
    passed, messages = validate_dockerfile()
    for msg in messages:
        print(msg)
    if not passed:
        all_passed = False
    
    # 3. Validate render.yaml
    print(f"\n{Colors.BOLD}3. Render.yaml Validation{Colors.RESET}")
    try:
        import yaml
        passed, messages = validate_render_yaml()
        for msg in messages:
            print(msg)
        if not passed:
            all_passed = False
    except ImportError:
        print(f"  {Colors.YELLOW}⚠{Colors.RESET} PyYAML not installed, skipping YAML validation")
    
    # 4. Validate requirements.txt
    print(f"\n{Colors.BOLD}4. Requirements Validation{Colors.RESET}")
    passed, messages = validate_requirements()
    for msg in messages:
        print(msg)
    if not passed:
        all_passed = False
    
    # 5. Validate Python files
    print(f"\n{Colors.BOLD}5. Python Files Check{Colors.RESET}")
    passed, messages = validate_python_files()
    for msg in messages:
        print(msg)
    if not passed:
        all_passed = False
    
    # 6. Test Python syntax
    print(f"\n{Colors.BOLD}6. Python Syntax Check{Colors.RESET}")
    passed, messages = test_python_syntax()
    for msg in messages:
        print(msg)
    if not passed:
        all_passed = False
    
    # 7. Git status
    print(f"\n{Colors.BOLD}7. Git Repository Status{Colors.RESET}")
    passed, messages = check_git_status()
    for msg in messages:
        print(msg)
    
    # 8. Environment variables
    print(f"\n{Colors.BOLD}8. Environment Variables{Colors.RESET}")
    passed, messages = check_environment_variables()
    for msg in messages:
        print(msg)
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    if all_passed:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED!{Colors.RESET}")
        print(f"\nYour backend is ready for deployment to Render!")
        print(f"\n{Colors.BOLD}Next Steps:{Colors.RESET}")
        print("1. Go to https://dashboard.render.com/blueprints")
        print("2. Click 'New Blueprint Instance'")
        print("3. Select repository: nikhil0100kumar/ai-recipes-backend")
        print("4. Add GEMINI_API_KEY in environment variables")
        print("5. Click 'Apply' to deploy")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME CHECKS FAILED{Colors.RESET}")
        print(f"\nPlease fix the issues above before deploying.")
    
    print(f"\n{Colors.BLUE}Repository: https://github.com/nikhil0100kumar/ai-recipes-backend{Colors.RESET}")
    print(f"{Colors.BLUE}After deployment: https://ai-recipes-backend.onrender.com{Colors.RESET}\n")

if __name__ == "__main__":
    main()