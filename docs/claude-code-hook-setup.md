# Claude Code TTS Hook Setup Guide

## ⚠️ IMPORTANT WARNING

**This is a BRITTLE integration that depends on Claude Code's internal hook system.**

- Claude Code's hook API is **NOT officially documented**
- Hook behavior may change without notice in future Claude Code updates
- This integration **WILL BREAK** if Anthropic modifies the hook system
- You may need to manually fix or disable this feature after Claude Code updates

**Use at your own risk.** This is an experimental feature for power users comfortable with manual configuration.

---

## Overview

This feature adds Text-to-Speech (TTS) responses to Claude Code by hooking into Claude's Stop event. When enabled, Claude's responses are automatically spoken aloud using macOS's `say` command.

**Features:**
- Automatic TTS for all Claude responses
- Smart summarization for long responses (>50 words)
- Code block filtering (code isn't spoken)
- Toggle on/off with `s` key in the TUI
- Configurable voice and speech rate

**Limitations:**
- macOS only (requires `say` command)
- Manual configuration required
- May break with Claude Code updates
- Requires running push-to-talk-claude TUI to enable/disable

---

## Prerequisites

Before setting up the TTS hook, ensure you have:

### 1. System Requirements
- macOS 11.0+ (Big Sur or later)
- Claude Code CLI installed and working
- Terminal with bash shell

### 2. Required Tools

Install `jq` (JSON processor):
```bash
brew install jq
```

Install `uv` (Python package runner):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify `say` command (built into macOS):
```bash
say "Hello, this is a test"
```

### 3. Push-to-Talk Claude Installation

This feature requires the push-to-talk-claude project to be installed:
```bash
git clone https://github.com/dpark2025/push-to-talk-claude.git
cd push-to-talk-claude
uv sync
```

---

## Quick Install (Recommended)

Run the install script to automatically configure the hook:

```bash
./scripts/install-claude-tts-hook.sh
```

This script will:
- Check prerequisites (jq, macOS, Claude Code)
- Make the hook script executable
- Configure Claude Code's `settings.json` with the Stop hook
- Create the `~/.claude-voice` directory

After running, start the TUI with `uv run claude-voice` and press `s` to enable TTS.

If you prefer manual setup or need to troubleshoot, follow the detailed steps below.

---

## Manual Setup Instructions

### Step 1: Locate the Hook Script

The hook script is located at:
```
/path/to/push-to-talk-claude/src/push_to_talk_claude/hooks/stop_hook.sh
```

**Find the absolute path:**
```bash
cd push-to-talk-claude
echo "$(pwd)/src/push_to_talk_claude/hooks/stop_hook.sh"
```

Copy this path - you'll need it for the next step.

### Step 2: Configure Claude Code Settings

Claude Code reads hook configuration from `~/.claude/settings.json`.

**Open or create the settings file:**
```bash
mkdir -p ~/.claude
touch ~/.claude/settings.json
```

**Edit the file** with your preferred editor:
```bash
nano ~/.claude/settings.json
# or
code ~/.claude/settings.json
# or
vim ~/.claude/settings.json
```

### Step 3: Add the Stop Hook Configuration

Add the following JSON to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "/ABSOLUTE/PATH/TO/push-to-talk-claude/src/push_to_talk_claude/hooks/stop_hook.sh"
          }
        ]
      }
    ]
  }
}
```

**IMPORTANT:** Replace `/ABSOLUTE/PATH/TO/push-to-talk-claude` with the actual absolute path from Step 1.

**Example:**
```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "/Users/username/projects/push-to-talk-claude/src/push_to_talk_claude/hooks/stop_hook.sh"
          }
        ]
      }
    ]
  }
}
```

**If you already have other settings** in `settings.json`, merge the `hooks` section:
```json
{
  "existingSetting": "value",
  "hooks": {
    "Stop": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "/Users/username/projects/push-to-talk-claude/src/push_to_talk_claude/hooks/stop_hook.sh"
          }
        ]
      }
    ]
  }
}
```

**Verify JSON syntax** after editing:
```bash
jq empty ~/.claude/settings.json && echo "Valid JSON" || echo "Invalid JSON - fix syntax errors"
```

### Step 4: Make Hook Script Executable

```bash
cd push-to-talk-claude
chmod +x src/push_to_talk_claude/hooks/stop_hook.sh
```

### Step 5: Configure TTS Settings (Optional)

Edit `~/.claude-voice/config.yaml` to customize voice and rate:

```yaml
tts:
  enabled: false        # Default state (toggle with 's' key in TUI)
  rate: 200             # Words per minute (150-250 recommended)
  voice: null           # Leave null for system default, or set to specific voice
```

**List available voices:**
```bash
say -v '?'
```

**Example with custom voice:**
```yaml
tts:
  enabled: false
  rate: 200
  voice: "Samantha"     # Use "Samantha" voice
```

---

## Usage

### Enable TTS Hook

1. **Start the push-to-talk-claude TUI:**
   ```bash
   cd push-to-talk-claude
   uv run claude-voice
   ```

2. **Press `s` key** to enable TTS
   - Status panel will show "TTS: Enabled"
   - Hook flag file created at `~/.claude-voice/tts-hook-enabled`

3. **Start or use Claude Code:**
   ```bash
   claude
   ```

4. Ask Claude a question - the response will be spoken aloud!

### Disable TTS Hook

Press `s` key again in the TUI to disable:
- Status panel shows "TTS: Disabled"
- Hook flag file removed
- Claude responses no longer spoken

### Toggle Without TUI

**Manually enable:**
```bash
mkdir -p ~/.claude-voice
touch ~/.claude-voice/tts-hook-enabled
```

**Manually disable:**
```bash
rm ~/.claude-voice/tts-hook-enabled
```

---

## Verification

### Test the Hook Manually

**Create a test transcript file:**
```bash
cat > /tmp/test-transcript.jsonl << 'EOF'
{"role":"user","content":"Hello"}
{"role":"assistant","content":"Hi there! How can I help you today?"}
EOF
```

**Run the hook script:**
```bash
# Enable hook first
touch ~/.claude-voice/tts-hook-enabled

# Test hook
/path/to/push-to-talk-claude/src/push_to_talk_claude/hooks/stop_hook.sh /tmp/test-transcript.jsonl
```

**Expected result:** You should hear "Hi there! How can I help you today?"

### Check Hook Logs (Debug Mode)

**Enable debug logging:**
```bash
export DEBUG=1
/path/to/push-to-talk-claude/src/push_to_talk_claude/hooks/stop_hook.sh /tmp/test-transcript.jsonl
```

**View logs:**
```bash
cat ~/.claude-voice/hook.log
```

**Expected log output:**
```
[2025-11-28 10:30:00] INFO: Hook triggered
[2025-11-28 10:30:00] INFO: Processing transcript: /tmp/test-transcript.jsonl
[2025-11-28 10:30:00] INFO: TTS config: rate=200, voice=default
[2025-11-28 10:30:00] INFO: Response extracted (42 chars)
[2025-11-28 10:30:00] INFO: Word count: 8 (threshold: 50)
[2025-11-28 10:30:00] INFO: Short response - speaking verbatim
[2025-11-28 10:30:00] INFO: TTS invoked: say -r 200 (async)
[2025-11-28 10:30:00] INFO: Hook completed successfully
```

### Verify Claude Code Integration

1. Start Claude Code and ask a question
2. Check if response is spoken
3. If not spoken:
   - Verify hook is enabled (`ls ~/.claude-voice/tts-hook-enabled`)
   - Check `settings.json` has correct path
   - Run manual test above to isolate issue

---

## Troubleshooting

### Hook Not Triggering

**Symptoms:** Claude responses not spoken, no `say` command executed

**Checks:**
```bash
# 1. Verify flag file exists
ls -la ~/.claude-voice/tts-hook-enabled
# Should exist if enabled in TUI

# 2. Verify settings.json syntax
jq empty ~/.claude/settings.json

# 3. Verify hook script path
cat ~/.claude/settings.json | jq '.hooks.Stop[0].hooks[0].command'
# Should print absolute path to stop_hook.sh

# 4. Verify script is executable
ls -la /path/to/stop_hook.sh
# Should show -rwxr-xr-x (executable)

# 5. Test hook manually
touch ~/.claude-voice/tts-hook-enabled
/path/to/stop_hook.sh /tmp/test-transcript.jsonl
```

**Common fixes:**
- Restart Claude Code after editing `settings.json`
- Verify absolute path has no typos
- Ensure script has execute permissions: `chmod +x stop_hook.sh`

### "jq command not found"

**Symptom:** Hook fails with "jq not installed" error

**Fix:**
```bash
brew install jq
```

### "uv command not found"

**Symptom:** Long responses not summarized, fallback to truncation

**Fix:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Restart terminal after install
```

### "Could not find project root"

**Symptom:** Summarizer fails, uses truncation instead

**Checks:**
```bash
# 1. Verify push-to-talk-claude is installed
ls -la /path/to/push-to-talk-claude/pyproject.toml

# 2. Verify hook can find project
cd /path/to/push-to-talk-claude
echo "$PWD"  # This should be the project root

# 3. Test uv from project directory
cd /path/to/push-to-talk-claude
uv run python -m push_to_talk_claude.hooks.summarizer --help
```

**Fix:** Ensure Claude Code is run from within the push-to-talk-claude project directory, or set `CLAUDE_PROJECT_DIR` environment variable:
```bash
export CLAUDE_PROJECT_DIR=/path/to/push-to-talk-claude
claude
```

### Speech Rate Too Fast/Slow

**Fix:** Edit `~/.claude-voice/config.yaml`:
```yaml
tts:
  rate: 180  # Slow down (default 200)
  # or
  rate: 220  # Speed up
```

Recommended range: 150-250 words per minute

### Wrong Voice or Accent

**Fix:** Set specific voice in config:
```bash
# List available voices
say -v '?'

# Edit config
nano ~/.claude-voice/config.yaml
```

```yaml
tts:
  voice: "Samantha"  # or "Alex", "Victoria", etc.
```

### Code Being Spoken

**Symptom:** Hearing code snippets read aloud (garbled speech)

**Expected behavior:** Code blocks should be automatically filtered

**Debug:** Check if summarizer is working:
```bash
cd push-to-talk-claude
echo '```python\nprint("hello")\n```\nThis is text' | uv run python -m push_to_talk_claude.hooks.summarizer --stdin
# Should output "This is text" only
```

**If failing:** Check project installation:
```bash
cd push-to-talk-claude
uv sync
```

### Hook Stops Working After Claude Code Update

**This is expected** - see warning at top of document.

**Diagnosis:**
```bash
# Check if Claude Code still supports hooks
claude --help | grep -i hook
# If no output, hook system may have been removed

# Check Claude Code version
claude --version
```

**Fix:**
1. Check push-to-talk-claude repository for updates
2. File an issue at https://github.com/dpark2025/push-to-talk-claude/issues
3. Disable hook temporarily by removing flag file:
   ```bash
   rm ~/.claude-voice/tts-hook-enabled
   ```

---

## Advanced Configuration

### Custom Word Threshold

By default, responses >50 words are summarized. To change:

**Edit hook script:**
```bash
nano /path/to/stop_hook.sh
```

**Find line:**
```bash
WORD_THRESHOLD=50
```

**Change to desired value:**
```bash
WORD_THRESHOLD=100  # Summarize only if >100 words
```

### Skip Summarization Entirely

To always speak verbatim (no summarization):

**Set threshold very high:**
```bash
WORD_THRESHOLD=999999
```

### Multiple Claude Code Instances

If running multiple Claude sessions, each will trigger the hook. The toggle flag affects ALL instances.

**To isolate per-session:**
1. Create separate config directories
2. Modify `FLAG_FILE` path in `stop_hook.sh`
3. Use different TUI instances for each

---

## Architecture Notes

### How It Works

1. **Claude Code Stop Event:** Claude Code invokes hooks listed in `settings.json` after each assistant response
2. **Hook Script Execution:** `stop_hook.sh` receives path to transcript JSONL file
3. **Flag Check:** Script checks if `~/.claude-voice/tts-hook-enabled` exists
4. **Text Extraction:** Uses `jq` to extract last assistant message from transcript
5. **Code Filtering:** Removes fenced code blocks using `sed`
6. **Word Count:** Counts remaining words to decide verbatim vs summarization
7. **TTS Invocation:** Calls macOS `say` command asynchronously
8. **Summarization (if needed):** Uses Claude API via Python module to summarize long responses

### Files Involved

| File | Purpose |
|------|---------|
| `~/.claude/settings.json` | Claude Code hook configuration |
| `~/.claude-voice/config.yaml` | TTS voice/rate settings |
| `~/.claude-voice/tts-hook-enabled` | Flag file (presence enables hook) |
| `~/.claude-voice/hook.log` | Debug logs (when `DEBUG=1`) |
| `stop_hook.sh` | Bash script invoked by Claude Code |
| `summarizer.py` | Python module for long response summarization |

### Hook Contract

The hook script MUST:
- Accept transcript file path as first argument (`$1`)
- Exit with code 0 (success) to avoid disrupting Claude Code
- Never block or hang (all TTS is async)
- Be executable (`chmod +x`)

---

## Uninstallation

To completely remove the TTS hook:

### 1. Remove Hook Configuration

**Edit `~/.claude/settings.json`:**
```bash
nano ~/.claude/settings.json
```

**Remove the `Stop` hook section**, leaving other settings intact:
```json
{
  "hooks": {}
}
```

Or delete the entire `hooks` key if empty.

### 2. Disable Hook Flag

```bash
rm ~/.claude-voice/tts-hook-enabled
```

### 3. Clean Up Config (Optional)

```bash
# Remove TTS config section from config.yaml
nano ~/.claude-voice/config.yaml
# Delete the 'tts:' section

# Or remove entire config directory
rm -rf ~/.claude-voice
```

### 4. Verify Removal

```bash
# Restart Claude Code
claude

# Ask a question - response should NOT be spoken
```

---

## Related Documentation

- [Main README](../README.md) - Push-to-talk-claude overview
- [Configuration Guide](../config.default.yaml) - Full config reference
- [TUI Guide](../README.md#tui-interface) - TUI keyboard shortcuts

---

## Support

**If you encounter issues:**

1. Check [Troubleshooting](#troubleshooting) section above
2. Review hook logs: `cat ~/.claude-voice/hook.log` (with `DEBUG=1`)
3. Test hook manually with sample transcript
4. File issue: https://github.com/dpark2025/push-to-talk-claude/issues

**Include in bug reports:**
- macOS version (`sw_vers`)
- Claude Code version (`claude --version`)
- Hook log output (with `DEBUG=1`)
- Contents of `settings.json` (sanitized)
- Output of manual hook test

---

**Remember:** This is an experimental feature using undocumented Claude Code APIs. Expect breakage.
