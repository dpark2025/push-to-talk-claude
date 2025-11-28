# Workflow Reminders

## "Push" Command Convention

When user says **"push"**, it means:
1. **Commit** all work with descriptive message
2. **Push** to remote repository
3. **Create PR** using `gh pr create` with full summary

Always include a comprehensive PR description summarizing:
- What was implemented/fixed
- Key changes made
- Any configuration or usage notes

```bash
# Full "push" workflow:
git add -A && git commit -m "feat/fix: <description>"
git push origin <branch-name>
gh pr create --title "<type>: <title>" --body "$(cat <<'EOF'
## Summary
<bullet points of what was done>

## Changes
<list of key files/components modified>

## Testing
<how it was tested>

## Usage
<any usage notes if applicable>

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Feature Branch Lifecycle

After PR is merged:

```bash
git checkout main && git pull
git branch -d <branch-name>
git push origin --delete <branch-name>
```

## Checkpoint Strategy

Create checkpoint commits at key milestones:
- After `/speckit.specify` - spec defined
- After `/speckit.plan` + `/speckit.tasks` - design complete
- After `/speckit.analyze` - ready for implementation
- After `/speckit.implement` - feature complete

## Implementation Verification Protocol

**CRITICAL**: Before claiming implementation is complete, run these checks in order.

### 1. Subagent Dependency Rule

When delegating to subagents that write code depending on other modules:
- **MUST** provide the actual interface/signatures of dependencies
- **MUST** have subagent read existing files before writing dependent code
- **NEVER** let subagents assume/invent interfaces

```
❌ BAD:  "Write app.py that uses Config class"
✅ GOOD: "Read config.py first, then write app.py using the actual Config interface"
```

### 2. Verification Ladder (run in order)

| Level | Command | Catches |
|-------|---------|---------|
| Syntax | `python -m py_compile <file>` | Syntax errors |
| Import | `python -c "from module import Class"` | Missing deps, wrong references |
| Instantiation | `python -c "from module import Class; Class()"` | Constructor errors, config mismatches |
| Entry Point | `uv run <command> --help` | CLI wiring issues |
| Runtime | `uv run <command>` | Actual execution errors |

**Minimum before commit**: Pass through Level 4 (Entry Point)

### 3. Integration Checkpoint Script

After implementation, run:
```bash
# Verify all imports work
python -c "
from push_to_talk_claude.app import App
from push_to_talk_claude.utils.config import Config
from push_to_talk_claude.core.keyboard_monitor import KeyboardMonitor
# ... all main classes
print('All imports OK')
"

# Verify CLI works
uv run claude-voice --help
uv run claude-voice --check
```

### 4. Cross-Module Verification

When multiple subagents write interdependent code:
1. Define interfaces in contracts/ FIRST
2. Have each subagent read the contract before implementing
3. After all modules written, run integration checkpoint
4. Fix mismatches BEFORE committing

### 5. Common Failure Modes

| Symptom | Cause | Prevention |
|---------|-------|------------|
| `AttributeError: 'X' has no attribute 'y'` | Subagent assumed wrong interface | Read actual file first |
| `ImportError: cannot import name` | Module structure mismatch | Verify imports after writing |
| `TypeError: __init__() got unexpected keyword` | Constructor signature mismatch | Check actual signatures |

**Rule**: Syntax check passes ≠ Code works. Always run the actual command.
