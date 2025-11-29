# Research: Dev Workflow & GitHub Integrations

**Feature**: 005-dev-workflow
**Date**: 2025-11-28

## Research Summary

This feature uses well-established patterns with no unknowns requiring deep research. All technologies are industry-standard with extensive documentation.

## Technology Decisions

### 1. CI Platform: GitHub Actions

**Decision**: Use GitHub Actions for CI/CD

**Rationale**:
- Native integration with GitHub (already hosting the repo)
- Free for public repositories
- Extensive marketplace of actions
- Simple YAML configuration
- Built-in caching for dependencies

**Alternatives Considered**:
- CircleCI: Good but adds external service dependency
- Travis CI: Less active development recently
- GitLab CI: Would require migration

### 2. Linting/Formatting: ruff

**Decision**: Use ruff for both linting and formatting (already configured)

**Rationale**:
- Already configured in pyproject.toml
- Extremely fast (Rust-based)
- Replaces multiple tools (flake8, isort, black)
- Single tool simplifies CI and pre-commit

**Existing Configuration** (from pyproject.toml):
```toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

### 3. Pre-commit Framework

**Decision**: Use pre-commit framework with ruff hooks

**Rationale**:
- Industry standard for git hooks
- Language-agnostic
- Easy installation (`pre-commit install`)
- Automatic updates via `pre-commit autoupdate`

**Hook Strategy**:
- `ruff check --fix`: Auto-fix lint issues
- `ruff format`: Auto-format code
- Both run on staged files only (fast)

### 4. Testing: pytest

**Decision**: Use pytest (already configured)

**Rationale**:
- Already configured in pyproject.toml
- Industry standard for Python
- Rich plugin ecosystem
- Excellent assertion introspection

**Existing Configuration**:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
```

### 5. Dependency Updates: Dependabot

**Decision**: Use GitHub Dependabot

**Rationale**:
- Native GitHub integration
- Zero configuration maintenance
- Automatic security updates
- Groups updates to reduce PR noise

**Update Cadence**: Weekly (industry standard)

### 6. Issue Templates: YAML Forms

**Decision**: Use GitHub's YAML-based issue forms

**Rationale**:
- Structured input (dropdowns, required fields)
- Better than markdown templates
- Reduces incomplete bug reports
- Native GitHub feature

## Best Practices Applied

### GitHub Actions CI

1. **Use matrix strategy** for testing multiple Python versions (future-proofing)
2. **Cache uv dependencies** for faster builds
3. **Fail fast** on lint/format to save CI minutes
4. **Run tests last** (most expensive operation)

### Pre-commit

1. **Auto-fix when possible** (reduce friction)
2. **Fast hooks only** (< 10s total)
3. **Skip on CI** (redundant with CI checks)

### PR Template

1. **Keep it minimal** (3-4 sections max)
2. **Include checklist** for common items
3. **Link to contributing guide** for details

### AI Memory File

1. **Update existing CLAUDE.md** (not a new file)
2. **Add "Dev Workflow" section** with key commands
3. **Include pre-commit setup instructions**

## No Unknowns Remaining

All NEEDS CLARIFICATION items from Technical Context have been resolved through standard patterns. Implementation can proceed to Phase 1.
