#!/usr/bin/env bash
# Build script for Render
set -o errexit

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

echo "Build completed successfully!"