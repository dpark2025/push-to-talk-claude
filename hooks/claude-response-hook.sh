#!/bin/bash
# Claude Code response hook for push-to-talk TTS
# Install: Add to ~/.claude/settings.json hooks section

# This script is called by Claude Code after each response
# It sends the response to our voice interface for TTS processing

VOICE_SOCKET="${CLAUDE_VOICE_SOCKET:-/tmp/claude-voice.sock}"
VOICE_FIFO="${CLAUDE_VOICE_FIFO:-/tmp/claude-voice.fifo}"

# Get response text from stdin or argument
if [ -n "$1" ]; then
    RESPONSE="$1"
else
    RESPONSE=$(cat)
fi

# Try socket first, then FIFO, then HTTP
if [ -S "$VOICE_SOCKET" ]; then
    echo "$RESPONSE" | nc -U "$VOICE_SOCKET"
elif [ -p "$VOICE_FIFO" ]; then
    echo "$RESPONSE" > "$VOICE_FIFO"
else
    # Fallback: write to temp file that voice interface watches
    TEMP_FILE="/tmp/claude-voice-response-$$.txt"
    echo "$RESPONSE" > "$TEMP_FILE"
fi
