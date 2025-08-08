from __future__ import annotations
import os, sys, textwrap, argparse
from urllib.parse import urlparse, parse_qs

from rich.console import Console
from .caption import fetch_caption
from .summarizer import summarize
from .config import load, YAIRConfig
from .speech import speak

console = Console()

cfg: YAIRConfig = load()

def extract_video_id(target: str) -> str:
    """
    Accepts a full YouTube URL or a bare video_id and returns the ID.
    Supports:
      • https://www.youtube.com/watch?v=dQw4w9WgXcQ
      • https://youtu.be/dQw4w9WgXcQ
      • dQw4w9WgXcQ
    Raises ValueError if it cannot determine the ID.
    """
    # bare ID (11 characters, alnum/_/-)
    if len(target) == 11 and all(c.isalnum() or c in "-_" for c in target):
        return target

    parsed = urlparse(target)

    # youtu.be short link → path starts with /
    if parsed.netloc in {"youtu.be"} and parsed.path:
        return parsed.path.lstrip("/")

    # standard watch URL → v query param
    if parsed.netloc.endswith("youtube.com"):
        qs = parse_qs(parsed.query)
        vid = qs.get("v", [None])[0]
        if vid:
            return vid

    raise ValueError(f"Can't extract video ID from: {target}")


def app() -> None:
    parser = argparse.ArgumentParser(
        prog="youtube-ai-resume",
        description="Generate an AI summary of a YouTube video."
    )
    parser.add_argument(
        "video",                    # agora aceita URL ou ID
        help="YouTube video URL or video ID"
    )
    parser.add_argument(
        "-m", "--model",
        default=cfg.get("openai_model", "gpt-3.5-turbo"),
        help=f"OpenAI model (default in config: {cfg.get('openai_model', 'gpt-3.5-turbo')})"
    )
    parser.add_argument(
        "-l", "--lang",
        default=cfg.get("output_lang", "en"),
        help=f"Output language (default: {cfg.get('output_lang', 'en')})"
    )
    parser.add_argument(
        "--voice", action="store_true",
        help="Narrate the summary aloud using Google Text-to-Speech"
    )

    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Set OPENAI_API_KEY in your environment.[/red]")
        sys.exit(1)

    try:
        video_id = extract_video_id(args.video)
        transcript = fetch_caption(video_id)
    except Exception as exc:
        console.print(f"[red]❌  {exc}[/red]")
        sys.exit(1)

    with console.status("[green]Contacting OpenAI…"):
        summary = summarize(
            transcript,
            api_key,
            model=args.model,
            out_lang=args.lang,
        )

    console.print("\n[bold cyan]Summary:[/bold cyan]\n")
    console.print(textwrap.dedent(summary))

    if args.voice or cfg.get("voice_enabled", False):
        try:
            console.print("\n[green]▶ Reproduzindo narração...[/green]")
            speak(summary) # default voice and rate
        except Exception as err:
            console.print(f"[red]Narration failed: {err}[/red]")

if __name__ == "__main__":
    app()
