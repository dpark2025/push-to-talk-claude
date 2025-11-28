# Quickstart: Auto-Return Configuration

**Feature**: 003-auto-return-config
**Date**: 2025-11-28

## What This Feature Does

Automatically presses Enter after voice transcription is injected, enabling hands-free command submission.

## Quick Toggle (Runtime)

Press **`a`** in the TUI to toggle auto-return on/off instantly.

```
┌──────────────────────────────────────┐
│  🎤 Push-to-Talk Claude              │
│                                      │
│  ┌─ Startup Configuration ─────────┐ │
│  │ Hotkey: ctrl_r                  │ │
│  │ Model: small                    │ │
│  │ Mode: focused                   │ │
│  │ Target: Active window           │ │
│  │ Transcript Logging: DISABLED    │ │
│  └─────────────────────────────────┘ │
│                                      │
│  Auto-Return: OFF  ← press 'a'       │
│                                      │
└──────────────────────────────────────┘
Footer: [l] Logs  [a] Auto-Return  [q] Quit
```

**Note**: Settings inside the "Startup Configuration" box are read from config at startup. Auto-Return (outside the box) can be toggled at runtime.

When you press `a`:
- Indicator updates immediately (OFF → ON or ON → OFF)
- A notification confirms the change
- Takes effect on your next voice command
- Resets to config file setting when you restart

## Persistent Configuration

To make auto-return enabled by default, edit `~/.claude-voice/config.yaml`:

```yaml
injection:
  mode: "focused"    # or "tmux"
  auto_return: true  # Enable automatic Enter after transcription
```

Restart the application for config changes to take effect.

## Verification

1. Launch the application:
   ```bash
   uv run claude-voice
   ```

2. Check the TUI info panel displays:
   ```
   Auto-Return: OFF
   ```

3. Press `a` to toggle:
   ```
   Auto-Return: ON
   ```

4. Hold hotkey, speak a command, release hotkey

5. Text should be typed AND Enter pressed automatically

## Usage Tips

**When to enable auto-return:**
- Running commands in Claude Code
- Sending complete messages
- Hands-free workflow

**When to disable auto-return:**
- Dictating partial text you want to edit
- Multi-line input where you'll add more
- When target app has special Enter behavior

## Troubleshooting

**Enter not being sent?**
- Check indicator shows "Auto-Return: ON"
- Verify transcription is not empty (check logs with `L` key)

**Want auto-return always on?**
- Set `auto_return: true` in config file for persistence across restarts

**Toggle not working?**
- Make sure TUI has focus (not recording)
- Press `a` key (not modifier+a)
