#!/bin/bash
# Install Homebrew dependencies for Push-to-Talk Claude

set -e

echo "Checking Homebrew..."
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Install from https://brew.sh"
    exit 1
fi

echo "Installing dependencies..."

# Python 3.11
if ! brew list python@3.11 &>/dev/null; then
    echo "  Installing python@3.11..."
    brew install python@3.11
else
    echo "  ✓ python@3.11 already installed"
fi

# tmux
if ! command -v tmux &>/dev/null; then
    echo "  Installing tmux..."
    brew install tmux
else
    echo "  ✓ tmux already installed"
fi

# portaudio (required for PyAudio)
if ! brew list portaudio &>/dev/null; then
    echo "  Installing portaudio..."
    brew install portaudio
else
    echo "  ✓ portaudio already installed"
fi

# ffmpeg (optional, for some audio formats)
if ! command -v ffmpeg &>/dev/null; then
    echo "  Installing ffmpeg..."
    brew install ffmpeg
else
    echo "  ✓ ffmpeg already installed"
fi

echo "✓ All Homebrew dependencies installed"
