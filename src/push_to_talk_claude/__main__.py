"""CLI entry point for push-to-talk voice interface."""

# CRITICAL: Set these BEFORE any imports to prevent PyTorch subprocess conflicts
# with Textual TUI. The fds_to_keep error occurs when PyTorch tries to fork
# while Textual has terminal file descriptors open.
import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
# Disable MPS (Apple Metal) to avoid subprocess issues - force CPU
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
# Disable torch compile which may spawn processes
os.environ.setdefault("TORCH_COMPILE_DISABLE", "1")

import argparse
import sys
import warnings
from pathlib import Path

# Suppress multiprocessing resource tracker warnings on exit
warnings.filterwarnings("ignore", message="resource_tracker:")


def main() -> int:
    """Main entry point for claude-voice command."""
    parser = argparse.ArgumentParser(
        prog="claude-voice",
        description="Push-to-talk voice interface for Claude Code"
    )
    parser.add_argument(
        "--config", "-c",
        type=Path,
        help="Path to config file (default: ~/.claude-voice/config.yaml)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check prerequisites and exit"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--version", "-v",
        action="store_true",
        help="Show version and exit"
    )

    args = parser.parse_args()

    if args.version:
        from . import __version__
        print(f"claude-voice {__version__}")
        return 0

    # Load config
    from .utils.config import Config
    if args.config:
        config = Config.load(args.config)
    else:
        config = Config.load()

    # Set debug logging if requested
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        config.logging.level = "DEBUG"

    # Check mode
    if args.check:
        return check_prerequisites(config)

    # Run main app
    from .app import App
    app = App(config)
    return app.run()


def check_prerequisites(config) -> int:
    """Check all prerequisites and print status."""
    from .utils.permissions import (
        check_microphone_permission,
        check_accessibility_permission,
        check_tmux_available,
        PermissionState
    )
    from .utils.session_detector import SessionDetector
    from rich.console import Console

    console = Console()
    all_ok = True

    # Check microphone
    mic = check_microphone_permission()
    if mic == PermissionState.GRANTED:
        console.print("✅ Microphone permission: granted")
    else:
        console.print(f"❌ Microphone permission: {mic.value}")
        all_ok = False

    # Check accessibility
    acc = check_accessibility_permission()
    if acc == PermissionState.GRANTED:
        console.print("✅ Accessibility permission: granted")
    else:
        console.print(f"❌ Accessibility permission: {acc.value}")
        all_ok = False

    # Check tmux
    if check_tmux_available():
        console.print("✅ tmux: installed")
    else:
        console.print("❌ tmux: not found")
        all_ok = False

    # Check Claude session
    detector = SessionDetector()
    if detector.is_tmux_running():
        session = detector.get_best_target()
        if session:
            console.print(f"✅ Claude Code session: found ({session.target_string})")
        else:
            console.print("⚠️  Claude Code session: not found (start Claude in tmux)")
    else:
        console.print("⚠️  tmux server: not running")

    # Check Whisper model
    console.print(f"ℹ️  Whisper model: {config.whisper.model}")

    return 0 if all_ok else 1


def setup() -> int:
    """Setup entry point for claude-voice-setup command."""
    # This could run the install scripts or guided setup
    print("Setup not yet implemented. See README.md for manual setup instructions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
