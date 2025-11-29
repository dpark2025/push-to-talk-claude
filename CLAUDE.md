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
- Python 3.11 (existing project standard) (004-tts-response-hook)
- YAML (GitHub Actions, pre-commit), Markdown (templates, docs) + GitHub Actions, pre-commit framework, Dependabot, ruff, pytes (005-dev-workflow)
- N/A (configuration files only) (005-dev-workflow)

## Recent Changes
- 001-voice-interface: Added Python 3.9+ (targeting 3.11 for performance) + pynput (keyboard), PyAudio (audio capture), openai-whisper (STT), subprocess (tmux/say)

## Dev Workflow

### CI Checks (GitHub Actions)
All PRs and pushes to main are automatically checked:
1. `ruff check .` - Linting (must pass)
2. `ruff format --check .` - Formatting (must pass)
3. `pytest -v` - Tests (must pass)

### Pre-commit Hooks (Local)
Set up local hooks to catch issues before committing:
```bash
pip install pre-commit
pre-commit install
```

Hooks run automatically on `git commit`:
- ruff check with --fix (auto-fixes lint issues)
- ruff format (auto-formats code)
- trailing-whitespace, end-of-file-fixer

### Before Committing
Always ensure code passes checks:
```bash
uv run ruff check --fix .
uv run ruff format .
uv run pytest
```

### PR Guidelines
- PRs use a template with Summary, Changes, and Testing sections
- All CI checks must pass before merge
- Dependabot creates PRs for dependency updates weekly
