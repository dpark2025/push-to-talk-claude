# Implementation Plan: Dev Workflow & GitHub Integrations

**Branch**: `005-dev-workflow` | **Date**: 2025-11-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-dev-workflow/spec.md`

## Summary

Establish automated code quality checks and standardized contribution processes through GitHub Actions CI, pre-commit hooks, templates, and AI-aware documentation. This is primarily a configuration feature with no application code changes.

## Technical Context

**Language/Version**: YAML (GitHub Actions, pre-commit), Markdown (templates, docs)
**Primary Dependencies**: GitHub Actions, pre-commit framework, Dependabot, ruff, pytest
**Storage**: N/A (configuration files only)
**Testing**: Manual verification + CI self-test on first PR
**Target Platform**: GitHub (repository configuration)
**Project Type**: Configuration/DevOps (no source code changes)
**Performance Goals**: CI completes in < 5 minutes
**Constraints**: Must work with existing pyproject.toml configuration
**Scale/Scope**: Single repository, ~5 contributors

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy is Non-Negotiable | ✅ PASS | No external data sharing; CI runs on GitHub's infrastructure |
| II. Speed Matters | ✅ PASS | CI target < 5 min; pre-commit runs locally |
| III. Smart Filtering | N/A | Not applicable to dev workflow |
| IV. Reliability Over Features | ✅ PASS | Core PTT loop unaffected; these are auxiliary tools |
| V. Terminal Agnostic, macOS Native | ✅ PASS | Pre-commit works everywhere; CI is cloud-based |
| VI. Smart Defaults, Deep Customization | ✅ PASS | Works immediately; all config in standard files |
| VII. Secure by Default | ✅ PASS | No user input processing; standard GitHub security |
| VIII. Ship Small, Ship Often | ✅ PASS | Incremental: P1 first (CI + pre-commit), then P2 |

**Technical Standards Compliance:**
- Code Quality: ✅ Enforced by this feature (ruff, pytest)
- Dependencies: ✅ All standard, actively maintained tools
- Documentation: ✅ Memory file documents workflow for AI/humans

## Project Structure

### Documentation (this feature)

```text
specs/005-dev-workflow/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # N/A for config feature
├── quickstart.md        # Setup instructions
├── contracts/           # N/A for config feature
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
.github/
├── workflows/
│   └── ci.yml                    # CI workflow (P1)
├── PULL_REQUEST_TEMPLATE.md      # PR template (P2)
├── dependabot.yml                # Dependency updates (P2)
└── ISSUE_TEMPLATE/
    ├── bug_report.yml            # Bug report form (P3)
    └── feature_request.yml       # Feature request form (P3)

.pre-commit-config.yaml           # Pre-commit hooks (P1)

CLAUDE.md                         # AI memory file update (P1)
```

**Structure Decision**: Standard GitHub repository configuration layout. All files go in `.github/` directory except pre-commit config (root) and CLAUDE.md (root).

## Complexity Tracking

No constitution violations. This feature adds development infrastructure without impacting core functionality.
