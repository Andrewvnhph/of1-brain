"""
run_all.py — Single-command pipeline runner for Xuong Phim AI.

Usage:
    python run_all.py --slug <slug> [--base <dir>] [--skip-audio]

Runs: story → script → shots → audio (vi) → audio (en)
Loads API keys from .env in project root automatically.

Requires:
    .env file with ANTHROPIC_API_KEY (and optionally ELEVENLABS_* for audio)
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path


def _load_dotenv(start: Path) -> None:
    for directory in [start, *start.parents]:
        env_file = directory / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)
            break


_load_dotenv(Path(__file__).parent)

SCRIPTS_DIR = Path(__file__).parent


def run(cmd: list, label: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, env=os.environ)
    if result.returncode != 0:
        print(f"\nFailed at: {label}")
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Xuong Phim AI — full pipeline runner")
    parser.add_argument("--slug", required=True, help="Episode slug")
    parser.add_argument("--base", default=".", help="Base directory (default: current dir)")
    parser.add_argument("--skip-audio", action="store_true", help="Skip ElevenLabs audio render")
    args = parser.parse_args()

    ep_run = [sys.executable, str(SCRIPTS_DIR / "episode_run.py"), "--slug", args.slug, "--base", args.base]
    audio = [sys.executable, str(SCRIPTS_DIR / "audio_render.py"), "--slug", args.slug, "--base", args.base]

    run(ep_run + ["story"],        f"[1/5] Story arc    → episodes/{args.slug}/script/story.yaml")
    run(ep_run + ["script"],       f"[2/5] Bilingual script → episodes/{args.slug}/script/script.yaml")
    run(ep_run + ["shots"],        f"[3/5] Veo prompts  → episodes/{args.slug}/shots/veo-prompts.yaml")

    if args.skip_audio:
        print("\n[4/5] Audio VI — skipped (--skip-audio)")
        print("[5/5] Audio EN — skipped (--skip-audio)")
    else:
        has_elevenlabs = (
            os.environ.get("ELEVENLABS_API_KEY")
            and os.environ.get("ELEVENLABS_VOICE_VI")
            and os.environ.get("ELEVENLABS_VOICE_EN")
        )
        if not has_elevenlabs:
            print("\n[4/5] Audio VI — skipped (ELEVENLABS_* keys not set in .env)")
            print("[5/5] Audio EN — skipped (ELEVENLABS_* keys not set in .env)")
        else:
            run(audio + ["--lang", "vi"], f"[4/5] Audio VI     → episodes/{args.slug}/audio/vi-narrator.mp3")
            run(audio + ["--lang", "en"], f"[5/5] Audio EN     → episodes/{args.slug}/audio/en-narrator.mp3")

    print(f"\n✓ Pipeline complete: episodes/{args.slug}/")
    print(f"  story.yaml      → episodes/{args.slug}/script/story.yaml")
    print(f"  script.yaml     → episodes/{args.slug}/script/script.yaml")
    print(f"  veo-prompts.yaml→ episodes/{args.slug}/shots/veo-prompts.yaml")


if __name__ == "__main__":
    main()
