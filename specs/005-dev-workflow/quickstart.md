# Quickstart: Dev Workflow Setup

**Feature**: 005-dev-workflow
**Time to Complete**: ~5 minutes

## For Contributors

### 1. Install Pre-commit Hooks (Recommended)

```bash
# Install pre-commit (if not already installed)
pip install pre-commit

# Install hooks in this repository
pre-commit install

# Verify installation
pre-commit run --all-files
```

That's it! Now your commits will be automatically checked for:
- Linting issues (auto-fixed when possible)
- Formatting issues (auto-fixed)

### 2. Manual Quality Checks

If you prefer not to use pre-commit, run these before committing:

```bash
# Check and fix linting
uv run ruff check --fix .

# Format code
uv run ruff format .

# Run tests
uv run pytest
```

## For Maintainers

### CI Workflow

The CI workflow runs automatically on:
- All pull requests to `main`
- All pushes to `main`

**Checks performed**:
1. `ruff check .` - Linting
2. `ruff format --check .` - Formatting
3. `pytest` - Tests

### Dependabot

Dependabot is configured to:
- Check for Python dependency updates weekly
- Create PRs automatically for updates
- Group minor/patch updates to reduce noise

### Issue Templates

When users click "New Issue", they'll see:
- **Bug Report**: Structured form for reproduction steps
- **Feature Request**: Form for problem/solution description

## Verification Checklist

After implementation, verify:

- [ ] CI runs on a test PR
- [ ] Pre-commit blocks bad commits locally
- [ ] PR template appears when creating PR
- [ ] Dependabot is enabled in repo settings
- [ ] Issue templates appear when creating issues
- [ ] CLAUDE.md has dev workflow section
