- Refer to /github/spec-kit from context7 for spec-kit documentation
- **CRITICAL**: Follow `.specify/memory/workflow.md` Verification Protocol before claiming implementation complete
- Subagents MUST read existing files before writing dependent code (never assume interfaces)

## Active Technologies
- Python 3.9+ (targeting 3.11 for performance) + pynput (keyboard), PyAudio (audio capture), openai-whisper (STT), subprocess (tmux/say) (001-voice-interface)
- YAML config files (~/.claude-voice/config.yaml), temporary WAV files (deleted after transcription) (001-voice-interface)

## Recent Changes
- 001-voice-interface: Added Python 3.9+ (targeting 3.11 for performance) + pynput (keyboard), PyAudio (audio capture), openai-whisper (STT), subprocess (tmux/say)
