# Tasks: Dev Workflow & GitHub Integrations

**Input**: Design documents from `/specs/005-dev-workflow/`
**Prerequisites**: plan.md, spec.md, research.md, quickstart.md

**Tests**: Tests are NOT required for this feature (configuration files only). Verification is manual.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure for GitHub configuration

- [x] T001 Create .github/workflows/ directory structure
- [x] T002 [P] Create .github/ISSUE_TEMPLATE/ directory structure

---

## Phase 2: User Story 1 - CI Workflow (Priority: P1) 🎯 MVP

**Goal**: Automated linting, formatting, and test checks on all PRs and pushes to main

**Independent Test**: Create a PR with intentional lint errors and verify CI fails with clear error messages

### Implementation for User Story 1

- [x] T003 [US1] Create GitHub Actions CI workflow in .github/workflows/ci.yml
- [x] T004 [US1] Configure workflow triggers (push to main, all PRs)
- [x] T005 [US1] Add ruff check step for linting in .github/workflows/ci.yml
- [x] T006 [US1] Add ruff format --check step for formatting in .github/workflows/ci.yml
- [x] T007 [US1] Add pytest step for running tests in .github/workflows/ci.yml
- [x] T008 [US1] Add uv dependency caching for faster builds in .github/workflows/ci.yml
- [x] T009 [US1] Verify CI workflow syntax with `act` or by creating test PR

**Checkpoint**: CI workflow runs on PRs and catches lint/format/test issues

---

## Phase 3: User Story 2 - Pre-commit Hooks (Priority: P1)

**Goal**: Local code quality checks that run automatically before each commit

**Independent Test**: Attempt to commit code with lint errors and verify commit is blocked

### Implementation for User Story 2

- [x] T010 [US2] Create pre-commit configuration file at .pre-commit-config.yaml
- [x] T011 [US2] Add ruff check hook with --fix for auto-fixing lint issues
- [x] T012 [US2] Add ruff format hook for auto-formatting
- [x] T013 [US2] Add trailing-whitespace and end-of-file-fixer hooks
- [ ] T014 [US2] Test pre-commit hooks locally with `pre-commit run --all-files`

**Checkpoint**: Pre-commit hooks catch and auto-fix issues locally before commit

---

## Phase 4: User Story 6 - AI Memory File (Priority: P1)

**Goal**: Document dev workflow processes so Claude remembers them in future sessions

**Independent Test**: Start new Claude session and ask about the dev workflow

### Implementation for User Story 6

- [x] T015 [US6] Add "Dev Workflow" section to CLAUDE.md
- [x] T016 [US6] Document CI checks (ruff lint, ruff format, pytest) in CLAUDE.md
- [x] T017 [US6] Document pre-commit setup instructions in CLAUDE.md
- [x] T018 [US6] Document PR workflow and commit guidelines in CLAUDE.md

**Checkpoint**: Claude can reference dev workflow when asked in a new session

---

## Phase 5: User Story 3 - PR Template (Priority: P2)

**Goal**: Consistent PR descriptions with summary, changes, and testing sections

**Independent Test**: Create a new PR and verify template auto-populates

### Implementation for User Story 3

- [x] T019 [US3] Create PR template at .github/PULL_REQUEST_TEMPLATE.md
- [x] T020 [US3] Add Summary section with bullet points placeholder
- [x] T021 [US3] Add Changes section for listing modified files/components
- [x] T022 [US3] Add Testing section with checklist for verification steps
- [ ] T023 [US3] Verify template appears when creating new PR

**Checkpoint**: New PRs have consistent template structure

---

## Phase 6: User Story 4 - Dependabot (Priority: P2)

**Goal**: Automated PRs when dependencies have updates

**Independent Test**: Verify Dependabot is enabled and configured in repo settings

### Implementation for User Story 4

- [x] T024 [US4] Create Dependabot configuration at .github/dependabot.yml
- [x] T025 [US4] Configure Python (pip) ecosystem updates
- [x] T026 [US4] Set weekly update schedule
- [x] T027 [US4] Configure GitHub Actions updates for workflow files
- [ ] T028 [US4] Verify Dependabot appears in repository Security settings

**Checkpoint**: Dependabot creates PRs for dependency updates

---

## Phase 7: User Story 5 - Issue Templates (Priority: P3)

**Goal**: Structured issue forms for bug reports and feature requests

**Independent Test**: Click "New Issue" on GitHub and verify template options appear

### Implementation for User Story 5

- [x] T029 [US5] Create bug report template at .github/ISSUE_TEMPLATE/bug_report.yml
- [x] T030 [US5] Add required fields: description, steps to reproduce, expected behavior
- [x] T031 [US5] Add environment fields: OS, Python version, app version
- [x] T032 [P] [US5] Create feature request template at .github/ISSUE_TEMPLATE/feature_request.yml
- [x] T033 [US5] Add fields: problem description, proposed solution, alternatives
- [x] T034 [US5] Create config.yml to customize issue template chooser
- [ ] T035 [US5] Verify templates appear when creating new issue

**Checkpoint**: Issue templates guide users to provide complete information

---

## Phase 8: Polish & Verification

**Purpose**: Final validation and documentation updates

- [x] T036 [P] Update README.md with pre-commit setup instructions
- [ ] T037 [P] Add CONTRIBUTING.md with development workflow overview
- [ ] T038 Run quickstart.md validation with manual testing
- [x] T039 Create test PR to verify full CI pipeline works
- [ ] T040 Verify all checkpoints from quickstart.md pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Stories (Phase 2-7)**: All depend on Setup completion
  - US1, US2, US6 are P1 - implement first
  - US3, US4 are P2 - implement after P1 complete
  - US5 is P3 - implement last
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (CI Workflow)**: Independent - no dependencies on other stories
- **US2 (Pre-commit)**: Independent - can run parallel with US1
- **US6 (AI Memory)**: Independent - can run parallel with US1 and US2
- **US3 (PR Template)**: Independent - can run parallel with US4
- **US4 (Dependabot)**: Independent - can run parallel with US3
- **US5 (Issue Templates)**: Independent - no dependencies

### Parallel Opportunities

All user stories are independent (different files) and can run in parallel:

```
Phase 1: T001, T002 (parallel - different directories)

After Phase 1:
├── US1: T003-T009 (sequential within story)
├── US2: T010-T014 (parallel with US1)
└── US6: T015-T018 (parallel with US1, US2)

After P1 Stories:
├── US3: T019-T023 (parallel with US4)
└── US4: T024-T028 (parallel with US3)

After P2 Stories:
└── US5: T029-T035

Phase 8: T036-T040 (after all stories)
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US6)

1. Complete Phase 1: Setup
2. Complete Phase 2-4: User Stories 1, 2, 6 (all P1)
3. **STOP and VALIDATE**: Test CI, pre-commit, and AI memory
4. Merge if ready

### Incremental Delivery

1. Setup → Ready for config files
2. Add US1 (CI) → PRs get automated feedback
3. Add US2 (Pre-commit) → Local quality checks work
4. Add US6 (Memory) → Claude knows the workflow
5. Add US3+US4 (PR template + Dependabot) → Better contributor experience
6. Add US5 (Issue templates) → Better issue reporting
7. Polish → Documentation complete

---

## Notes

- All config files are YAML or Markdown - no code compilation needed
- [P] tasks = different files, can run in parallel
- Each user story creates independent GitHub/git functionality
- Verify each checkpoint before moving to next phase
- Test PR (T039) is critical - validates entire pipeline works
