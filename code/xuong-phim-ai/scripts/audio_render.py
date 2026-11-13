"""
audio_render.py — ElevenLabs voice renderer for Xuong Phim AI.

Usage:
    python audio_render.py --slug <slug> --lang vi [--base <dir>]
    python audio_render.py --slug <slug> --lang en [--base <dir>]

Reads script.yaml, concatenates vi_narrator or en_narrator lines,
calls ElevenLabs API, saves MP3 to episodes/<slug>/audio/.

Requires:
    ELEVENLABS_API_KEY env var
    ELEVENLABS_VOICE_VI env var (ElevenLabs voice ID for Vietnamese)
    ELEVENLABS_VOICE_EN env var (ElevenLabs voice ID for English)
"""

import sys
import os
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: pyyaml not installed. Run: pip3 install pyyaml")
    sys.exit(1)

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import save
except ImportError:
    print("Error: elevenlabs package not installed. Run: pip3 install elevenlabs")
    sys.exit(1)

LANG_NARRATOR_KEY = {"vi": "vi_narrator", "en": "en_narrator"}
LANG_VOICE_ENV = {"vi": "ELEVENLABS_VOICE_VI", "en": "ELEVENLABS_VOICE_EN"}
LANG_FILENAME = {"vi": "vi-narrator.mp3", "en": "en-narrator.mp3"}


def episode_path(slug: str, base_dir: str) -> Path:
    ep = Path(base_dir) / "episodes" / slug
    if not ep.exists():
        raise FileNotFoundError(f"Episode not found: {ep}")
    return ep


def build_narration_text(script_path: Path, narrator_key: str) -> str:
    data = yaml.safe_load(script_path.read_text(encoding="utf-8"))
    scenes = data.get("scenes", [])
    lines = [scene[narrator_key] for scene in scenes if scene.get(narrator_key)]
    if not lines:
        raise ValueError(f"No {narrator_key} lines found in script.yaml")
    return "\n\n".join(lines)


def render_audio(text: str, voice_id: str, out_path: Path) -> None:
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        raise EnvironmentError("ELEVENLABS_API_KEY not set")
    client = ElevenLabs(api_key=api_key)
    audio = client.generate(
        text=text,
        voice=voice_id,
        model="eleven_multilingual_v2",
    )
    save(audio, str(out_path))


def main():
    parser = argparse.ArgumentParser(description="Render narrator voice track via ElevenLabs")
    parser.add_argument("--slug", required=True, help="Episode slug")
    parser.add_argument("--lang", required=True, choices=["vi", "en"], help="Language (vi or en)")
    parser.add_argument("--base", default=".", help="Base directory (default: current dir)")
    args = parser.parse_args()

    ep = episode_path(args.slug, args.base)
    script_path = ep / "script" / "script.yaml"
    if not script_path.exists():
        raise FileNotFoundError(f"script.yaml not found — run episode_run.py script first")

    voice_env = LANG_VOICE_ENV[args.lang]
    voice_id = os.environ.get(voice_env)
    if not voice_id:
        raise EnvironmentError(f"{voice_env} not set — set your ElevenLabs voice ID")

    narrator_key = LANG_NARRATOR_KEY[args.lang]
    print(f"Building {args.lang.upper()} narration text from {ep.name}...")
    text = build_narration_text(script_path, narrator_key)
    print(f"Total characters: {len(text)}")

    out = ep / "audio" / LANG_FILENAME[args.lang]
    print(f"Rendering voice ({voice_id}) → {out}...")
    render_audio(text, voice_id, out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    main()
