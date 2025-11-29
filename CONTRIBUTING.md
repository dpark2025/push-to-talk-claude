# Contributing to Push-to-Talk Claude

Thanks for your interest in contributing! This document outlines the development workflow and guidelines.

## Development Setup

### Prerequisites

- macOS 11.0+ (Big Sur or later)
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Git

### Installation

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/push-to-talk-claude.git
cd push-to-talk-claude

# Install system dependencies
brew install portaudio ffmpeg

# Install Python dependencies
uv sync

# Set up pre-commit hooks (recommended)
pip install pre-commit
pre-commit install
```

## Development Workflow

### Code Quality

Before submitting a PR, ensure your code passes all checks:

```bash
# Lint (with auto-fix)
uv run ruff check --fix .

# Format
uv run ruff format .

# Run tests
uv run pytest -v
```

### Pre-commit Hooks

If you installed pre-commit hooks, these checks run automatically before each commit:

- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml**: Validate YAML syntax
- **ruff**: Lint Python code (with auto-fix)
- **ruff-format**: Format Python code

### CI Pipeline

All PRs automatically run:

1. **Lint & Format** - `ruff check` and `ruff format --check`
2. **Tests** - `pytest -v`

PRs must pass all checks before merging.

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feat/add-new-feature`
- `fix/bug-description`
- `docs/update-readme`

### Commit Messages

Follow conventional commit format:

```
type: short description

Longer description if needed.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Requests

1. Create a feature branch from `main`
2. Make your changes
3. Ensure all checks pass locally
4. Push and create a PR
5. Fill out the PR template
6. Wait for CI and code review

## Project Structure

```
push-to-talk-claude/
├── src/push_to_talk_claude/    # Main source code
│   ├── core/                   # Core functionality
│   ├── hooks/                  # Claude Code hooks
│   ├── ui/                     # TUI components
│   └── utils/                  # Utilities
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── hooks/                  # Hook tests
├── docs/                       # Documentation
├── specs/                      # Feature specifications
└── scripts/                    # Helper scripts
```

## Testing

```bash
# Run all tests
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/ui/test_tui_app.py -v

# Run with coverage
uv run pytest --cov=push_to_talk_claude
```

## Getting Help

- [Open an issue](https://github.com/dpark2025/push-to-talk-claude/issues) for bugs or feature requests
- [Start a discussion](https://github.com/dpark2025/push-to-talk-claude/discussions) for questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
