- Refer to /github/spec-kit from context7 for spec-kit documentation
- Subagents MUST read existing files before writing dependent code (never assume interfaces)

@.specify/memory/workflow.md

## Active Technologies
- Python 3.9+ (targeting 3.11 for performance) + pynput (keyboard), PyAudio (audio capture), openai-whisper (STT), subprocess (tmux/say) (001-voice-interface)
- YAML config files (~/.claude-voice/config.yaml), temporary WAV files (deleted after transcription) (001-voice-interface)
- Python 3.9+ (targeting 3.11 for performance) + Textual (TUI framework), pynput (keyboard), PyAudio (audio), openai-whisper (STT) (002-textual-tui)
- In-memory log buffer (100 lines max), existing config.yaml for settings (002-textual-tui)
- Python 3.9+ (targeting 3.11) + pynput (keyboard), Textual (TUI), PyYAML (config) (003-auto-return-config)
- YAML config file (~/.claude-voice/config.yaml) (003-auto-return-config)

## Recent Changes
- 001-voice-interface: Added Python 3.9+ (targeting 3.11 for performance) + pynput (keyboard), PyAudio (audio capture), openai-whisper (STT), subprocess (tmux/say)
