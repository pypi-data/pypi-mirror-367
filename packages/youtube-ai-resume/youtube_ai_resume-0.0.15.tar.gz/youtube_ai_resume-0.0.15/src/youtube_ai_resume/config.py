r"""
Centralised config handling for youtube-ai-resume.

File location:
  Linux/macOS  → ~/.config/youtube-ai-resume/config.json
  Windows      → %APPDATA%\youtube-ai-resume\config.json
"""

from __future__ import annotations
import json, os
from pathlib import Path
from typing import TypedDict

class YAIRConfig(TypedDict, total=False):
    openai_model: str
    output_lang: str
    google_credentials: str
    voice_enabled: bool
    default_voice: str
    proxy_http: str
    proxy_https: str

DEFAULTS: YAIRConfig = {
    "openai_model": "gpt-4.1-mini",
    "output_lang": "en_US",
    "google_credentials": "~/.config/youtube-ai-resume/.google-credentials.json",
    "voice_enabled": False,
    "default_voice": "en-US-Chirp-HD-D",
    "proxy_http": "",
    "proxy_https": ""
}

def _config_dir() -> Path:
    if os.name == "nt":       # Windows
        return Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming")) / "youtube-ai-resume"
    return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / "youtube-ai-resume"

CONFIG_PATH = _config_dir() / "config.json"


def load() -> YAIRConfig:
    """Return merged config (file ⊕ defaults). Creates file if missing."""
    cfg: YAIRConfig = DEFAULTS.copy()
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open(encoding="utf-8") as fh:
                cfg.update(json.load(fh))     # type: ignore[arg-type]
        except json.JSONDecodeError:
            # fallback to defaults; don’t overwrite broken file
            pass
    else:
        save(cfg)   # write template on first run
    return cfg


def save(cfg: YAIRConfig) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)
