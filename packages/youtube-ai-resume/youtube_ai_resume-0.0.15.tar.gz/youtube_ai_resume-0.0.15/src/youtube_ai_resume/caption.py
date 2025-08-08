"""
captions.py - support for auto-generated captions.
"""
from __future__ import annotations

import os
from typing import List

from youtube_transcript_api._api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable

# Proxy support: load config and prepare proxies dict if configured
# Proxy support: load config and prepare proxy env vars if configured
from .config import load as load_config
cfg = load_config()
proxy_http = cfg.get("proxy_http", "")
proxy_https = cfg.get("proxy_https", "")


def _snippet_to_text(chunk) -> str:
    """
    Accept dicts with 'text' key or objects with .text attribute.
    Returns the text content of the caption chunk.
    """
    if isinstance(chunk, dict):
        return chunk.get("text", "").strip()
    # recent versions of the library return objects with .text attribute
    return getattr(chunk, "text", "").strip()

def _best_transcript(video_id: str, pref: list[str] | None) -> str:
    """
    Returns the plain text of the best available caption.
    Preference order:
      1. Manually created caption in the desired language (pref)
      2. Auto-generated caption in the desired language (pref)
      3. Any existing caption (manual or auto)
    """
    try:
        # Set proxy env vars only for this call if configured
        orig_http = os.environ.get("HTTP_PROXY")
        orig_https = os.environ.get("HTTPS_PROXY")
        if proxy_http:
            os.environ["HTTP_PROXY"] = proxy_http
        if proxy_https:
            os.environ["HTTPS_PROXY"] = proxy_https

        transcripts = YouTubeTranscriptApi().list(video_id)

        # Restore original env vars to avoid side effects
        if proxy_http:
            if orig_http is not None:
                os.environ["HTTP_PROXY"] = orig_http
            else:
                del os.environ["HTTP_PROXY"]
        if proxy_https:
            if orig_https is not None:
                os.environ["HTTPS_PROXY"] = orig_https
            else:
                del os.environ["HTTPS_PROXY"]

        transcript = None
        # 1) manually created caption in the desired language
        if pref:
            try:
                transcript = transcripts.find_manually_created_transcript(pref)
            except Exception:
                pass

        # 2) auto-generated caption in the desired language
        if not transcript and pref:
            try:
                transcript = transcripts.find_generated_transcript(pref)
            except Exception:
                pass

        # 3) pick the first available caption
        if not transcript:
            # generate list of all available language codes
            all_langs = [t.language_code for t in transcripts]
            transcript = transcripts.find_transcript(all_langs)

        data = transcript.fetch()
        return "\n".join(t for t in (_snippet_to_text(c) for c in data) if t).strip()

    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        raise RuntimeError("No captions available for this video.")


# ---- Public API -----------------------------------------------------------

def list_captions(video_id: str) -> List[str]:
    """List all available caption languages for a video."""
    try:
        # Set proxy env vars only for this call if configured
        orig_http = os.environ.get("HTTP_PROXY")
        orig_https = os.environ.get("HTTPS_PROXY")
        if proxy_http:
            os.environ["HTTP_PROXY"] = proxy_http
        if proxy_https:
            os.environ["HTTPS_PROXY"] = proxy_https

        tr = YouTubeTranscriptApi().list(video_id)

        # Restore original env vars to avoid side effects
        if proxy_http:
            if orig_http is not None:
                os.environ["HTTP_PROXY"] = orig_http
            else:
                del os.environ["HTTP_PROXY"]
        if proxy_https:
            if orig_https is not None:
                os.environ["HTTPS_PROXY"] = orig_https
            else:
                del os.environ["HTTPS_PROXY"]

        return [t.language_code for t in tr]
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable):
        return []


def fetch_caption(video_id: str, preferred_langs: list[str] | None = None) -> str:
    return _best_transcript(video_id, preferred_langs)
