#!/usr/bin/env bash
#
# TTS Response Hook for Claude Code
# Speaks Claude's responses aloud with automatic summarization for long responses
#
# Usage: stop_hook.sh <transcript_file_path>
#
# Contract: This script is invoked by Claude Code after each assistant response.
# It must ALWAYS exit 0 to avoid disrupting Claude Code operation.

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

FLAG_FILE="$HOME/.claude-voice/tts-hook-enabled"
CONFIG_FILE="$HOME/.claude-voice/config.yaml"
LOG_FILE="$HOME/.claude-voice/hook.log"

# Default TTS settings (overridden by config.yaml)
DEFAULT_RATE=200
DEFAULT_VOICE=""

# Word count threshold for summarization
WORD_THRESHOLD=50

# ============================================================================
# Logging Functions
# ============================================================================

log_info() {
    if [ "${DEBUG:-0}" = "1" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1" >> "$LOG_FILE"
    fi
}

log_error() {
    if [ "${DEBUG:-0}" = "1" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" >> "$LOG_FILE"
    fi
}

# ============================================================================
# Project Path Resolution
# ============================================================================

find_project_root() {
    # 1. Check if CLAUDE_PROJECT_DIR is set (Claude Code provides this)
    if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -d "$CLAUDE_PROJECT_DIR" ]; then
        echo "$CLAUDE_PROJECT_DIR"
        return 0
    fi

    # 2. Search upward from current directory for pyproject.toml
    local dir="$PWD"
    while [ "$dir" != "/" ]; do
        if [ -f "$dir/pyproject.toml" ]; then
            echo "$dir"
            return 0
        fi
        dir=$(dirname "$dir")
    done

    # 3. Fall back to script's parent directory (assuming installed package)
    local script_dir
    script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
    if [ -f "$script_dir/pyproject.toml" ]; then
        echo "$script_dir"
        return 0
    fi

    log_error "Could not find project root (no pyproject.toml found)"
    return 1
}

# ============================================================================
# Dependency Checks
# ============================================================================

check_dependencies() {
    local missing_deps=0

    if ! command -v jq &> /dev/null; then
        log_error "jq not installed. Install with: brew install jq"
        missing_deps=1
    fi

    if ! command -v say &> /dev/null; then
        log_error "say command not found (macOS only)"
        missing_deps=1
    fi

    if ! command -v uv &> /dev/null; then
        log_error "uv not found (required for running Python modules)"
        missing_deps=1
    fi

    return $missing_deps
}

# ============================================================================
# Configuration Reading
# ============================================================================

read_tts_config() {
    local rate="$DEFAULT_RATE"
    local voice="$DEFAULT_VOICE"

    if [ -f "$CONFIG_FILE" ]; then
        # Extract TTS rate from config.yaml
        if command -v yq &> /dev/null; then
            rate=$(yq e '.tts.rate // 200' "$CONFIG_FILE" 2>/dev/null || echo "$DEFAULT_RATE")
            voice=$(yq e '.tts.voice // ""' "$CONFIG_FILE" 2>/dev/null || echo "$DEFAULT_VOICE")
        else
            # Fallback: simple grep-based extraction (less reliable)
            rate=$(grep -A 10 '^tts:' "$CONFIG_FILE" 2>/dev/null | grep 'rate:' | sed 's/.*rate: *//;s/ *#.*//' || echo "$DEFAULT_RATE")
            voice=$(grep -A 10 '^tts:' "$CONFIG_FILE" 2>/dev/null | grep 'voice:' | sed 's/.*voice: *//;s/ *#.*//;s/null//' || echo "$DEFAULT_VOICE")
        fi
    fi

    # Export for use in speak_text function
    export TTS_RATE="$rate"
    export TTS_VOICE="$voice"

    log_info "TTS config: rate=$TTS_RATE, voice=${TTS_VOICE:-default}"
}

# ============================================================================
# Text Processing
# ============================================================================

strip_code_blocks() {
    local text="$1"

    # Remove fenced code blocks (```...```) using sed
    # This handles multiline code blocks
    echo "$text" | sed '/```/,/```/d'
}

count_words() {
    local text="$1"
    echo "$text" | wc -w | tr -d ' '
}

# ============================================================================
# TTS Functions
# ============================================================================

speak_text() {
    local text="$1"
    local rate="${TTS_RATE:-$DEFAULT_RATE}"
    local voice="${TTS_VOICE:-$DEFAULT_VOICE}"

    # Build say command with optional voice parameter
    local say_cmd="say -r $rate"
    if [ -n "$voice" ] && [ "$voice" != "null" ]; then
        say_cmd="$say_cmd -v $voice"
    fi

    # Speak asynchronously (fire-and-forget)
    $say_cmd "$text" &

    log_info "TTS invoked: $say_cmd (async)"
}

# ============================================================================
# Transcript Processing
# ============================================================================

extract_last_assistant_message() {
    local transcript_file="$1"

    # Extract last assistant message using jq
    # Format: {"message":{"role":"assistant","content":[{"type":"text","text":"..."}]}}
    jq -r 'select(.message.role == "assistant") | .message.content[] | select(.type == "text") | .text' "$transcript_file" 2>/dev/null | tail -1
}

# ============================================================================
# Main Hook Logic
# ============================================================================

main() {
    # Check if hook is enabled via flag file
    if [ ! -f "$FLAG_FILE" ]; then
        log_info "Hook disabled (flag file missing)"
        exit 0
    fi

    log_info "Hook triggered"

    # Read JSON input from stdin (Claude Code passes hook data via stdin)
    local input
    input=$(cat)

    if [ -z "$input" ]; then
        log_error "No input received from stdin"
        exit 0
    fi

    log_info "Input received: ${input:0:100}..."

    # Extract transcript_path from JSON input
    local transcript_file
    transcript_file=$(echo "$input" | jq -r '.transcript_path // empty' 2>/dev/null)

    if [ -z "$transcript_file" ]; then
        log_error "No transcript_path in input JSON"
        exit 0
    fi

    if [ ! -f "$transcript_file" ]; then
        log_error "Transcript file not found: $transcript_file"
        exit 0
    fi

    log_info "Processing transcript: $transcript_file"

    # Check dependencies
    if ! check_dependencies; then
        log_error "Missing required dependencies"
        exit 0
    fi

    # Read TTS configuration
    read_tts_config

    # Extract last assistant message
    local response
    response=$(extract_last_assistant_message "$transcript_file")

    if [ -z "$response" ]; then
        log_info "No assistant message found in transcript"
        exit 0
    fi

    log_info "Response extracted (${#response} chars)"

    # Strip code blocks
    local cleaned_response
    cleaned_response=$(strip_code_blocks "$response")

    if [ -z "$cleaned_response" ]; then
        log_info "Response empty after stripping code blocks"
        exit 0
    fi

    # Count words
    local word_count
    word_count=$(count_words "$cleaned_response")

    log_info "Word count: $word_count (threshold: $WORD_THRESHOLD)"

    # Decide: speak verbatim or summarize
    if [ "$word_count" -lt "$WORD_THRESHOLD" ]; then
        # Short response: speak verbatim
        log_info "Short response - speaking verbatim"
        speak_text "$cleaned_response"
    else
        # Long response: summarize first
        log_info "Long response - summarizing"

        # Find project root for uv execution
        local project_root
        project_root=$(find_project_root)

        if [ $? -ne 0 ]; then
            log_error "Could not find project root, falling back to truncation"
            summary=$(echo "$cleaned_response" | head -c 300)
        else
            # Run summarizer using uv from project directory
            local summary
            summary=$(cd "$project_root" && echo "$cleaned_response" | uv run python -m push_to_talk_claude.hooks.summarizer --stdin 2>/dev/null)

            if [ $? -ne 0 ] || [ -z "$summary" ]; then
                log_error "Summarizer failed, falling back to truncation"
                # Fallback: truncate to first 50 words
                summary=$(echo "$cleaned_response" | head -c 300)
            fi
        fi

        log_info "Summary generated (${#summary} chars)"
        speak_text "$summary"
    fi

    log_info "Hook completed successfully"
    exit 0
}

# ============================================================================
# Entry Point
# ============================================================================

main "$@"
