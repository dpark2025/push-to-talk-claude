from typing import Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml
import shutil


SUPPORTED_HOTKEYS = {
    "ctrl_r", "ctrl_l", "alt_r", "alt_l",
    "cmd_r", "cmd_l", "f13", "f14", "f15",
    "f16", "f17", "f18", "f19", "f20"
}

SUPPORTED_WHISPER_MODELS = {"tiny", "base", "small", "medium", "large"}

SUPPORTED_INJECTION_MODES = {"focused", "tmux"}


@dataclass
class PushToTalkConfig:
    hotkey: str = "ctrl_r"
    visual_feedback: bool = True
    audio_feedback: bool = True
    silence_timeout: float = 2.0


@dataclass
class WhisperConfig:
    model: str = "tiny"
    device: str = "auto"
    language: Optional[str] = "en"


@dataclass
class InjectionConfig:
    mode: str = "focused"  # "focused" (type into active window) or "tmux" (send to tmux pane)


@dataclass
class TmuxConfig:
    session_name: Optional[str] = None
    window_index: Optional[int] = None
    pane_index: Optional[int] = None
    auto_detect: bool = True


@dataclass
class TTSConfig:
    enabled: bool = True
    voice: Optional[str] = None
    rate: int = 200
    max_length: int = 500


@dataclass
class SecurityConfig:
    max_input_length: int = 500


@dataclass
class LoggingConfig:
    level: str = "INFO"
    save_transcripts: bool = False
    transcripts_dir: str = ".tts-transcriptions"  # Relative to cwd or absolute path


@dataclass
class Config:
    push_to_talk: PushToTalkConfig
    whisper: WhisperConfig
    injection: InjectionConfig
    tmux: TmuxConfig
    tts: TTSConfig
    security: SecurityConfig
    logging: LoggingConfig

    @classmethod
    def ensure_config_exists(cls) -> Path:
        """Create config directory and default config file if they don't exist.

        Returns:
            Path to the config file
        """
        config_dir = Path.home() / ".claude-voice"
        config_path = config_dir / "config.yaml"

        # Create directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)

        # Copy default config if config doesn't exist
        if not config_path.exists():
            default_config = Path(__file__).parent.parent.parent.parent / "config.default.yaml"
            if default_config.exists():
                shutil.copy(default_config, config_path)

        return config_path

    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """Load config from file or use defaults."""
        if path is None:
            path = cls.ensure_config_exists()

        if not path.exists():
            return cls.default()

        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        if data is None:
            return cls.default()

        return cls(
            push_to_talk=PushToTalkConfig(**data.get('push_to_talk', {})),
            whisper=WhisperConfig(**data.get('whisper', {})),
            injection=InjectionConfig(**data.get('injection', {})),
            tmux=TmuxConfig(**data.get('tmux', {})),
            tts=TTSConfig(**data.get('tts', {})),
            security=SecurityConfig(**data.get('security', {})),
            logging=LoggingConfig(**data.get('logging', {}))
        )

    @classmethod
    def default(cls) -> "Config":
        """Create config with default values."""
        return cls(
            push_to_talk=PushToTalkConfig(),
            whisper=WhisperConfig(),
            injection=InjectionConfig(),
            tmux=TmuxConfig(),
            tts=TTSConfig(),
            security=SecurityConfig(),
            logging=LoggingConfig()
        )

    def save(self, path: Path) -> None:
        """Save config to YAML file."""
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'push_to_talk': asdict(self.push_to_talk),
            'whisper': asdict(self.whisper),
            'injection': asdict(self.injection),
            'tmux': asdict(self.tmux),
            'tts': asdict(self.tts),
            'security': asdict(self.security),
            'logging': asdict(self.logging)
        }

        with open(path, 'w') as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    def validate(self) -> List[str]:
        """Validate config values. Returns list of error messages (empty if valid)."""
        errors = []

        if self.push_to_talk.hotkey not in SUPPORTED_HOTKEYS:
            errors.append(
                f"Invalid hotkey '{self.push_to_talk.hotkey}'. "
                f"Supported hotkeys: {', '.join(sorted(SUPPORTED_HOTKEYS))}"
            )

        if self.whisper.model not in SUPPORTED_WHISPER_MODELS:
            errors.append(
                f"Invalid whisper model '{self.whisper.model}'. "
                f"Supported models: {', '.join(sorted(SUPPORTED_WHISPER_MODELS))}"
            )

        if self.injection.mode not in SUPPORTED_INJECTION_MODES:
            errors.append(
                f"Invalid injection mode '{self.injection.mode}'. "
                f"Supported modes: {', '.join(sorted(SUPPORTED_INJECTION_MODES))}"
            )

        if not (100 <= self.tts.rate <= 400):
            errors.append(
                f"Invalid TTS rate {self.tts.rate}. "
                f"Rate must be between 100 and 400"
            )

        if not (100 <= self.security.max_input_length <= 5000):
            errors.append(
                f"Invalid max_input_length {self.security.max_input_length}. "
                f"Must be between 100 and 5000"
            )

        return errors
