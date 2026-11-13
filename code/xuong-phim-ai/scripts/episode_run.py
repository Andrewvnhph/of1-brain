"""
episode_run.py — Claude API orchestrator for Xuong Phim AI pipeline.

Usage:
    python episode_run.py story  --slug <slug> [--base <dir>]
    python episode_run.py script --slug <slug> [--base <dir>]
    python episode_run.py shots  --slug <slug> [--base <dir>]

Reads input YAML from episodes/<slug>/script/, writes output YAML to same dir.
Loads Claude skills from skills/ directory relative to this script.
Requires: ANTHROPIC_API_KEY env var.
"""

import sys
import os
import time
import argparse
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("Error: anthropic package not installed. Run: pip3 install anthropic")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("Error: pyyaml not installed. Run: pip3 install pyyaml")
    sys.exit(1)

SCRIPTS_DIR = Path(__file__).parent
SKILLS_DIR = SCRIPTS_DIR.parent / "skills"
MODEL = "claude-haiku-4-5-20251001"
DIRECTOR_SCHEMA_KEYS = {"subject", "action", "camera", "lighting", "constraints"}


def load_skill(skill_name: str) -> str:
    path = SKILLS_DIR / f"{skill_name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Skill not found: {path}")
    return path.read_text(encoding="utf-8")


def episode_path(slug: str, base_dir: str) -> Path:
    ep = Path(base_dir) / "episodes" / slug
    if not ep.exists():
        raise FileNotFoundError(f"Episode not found: {ep} — run episode_init.py first")
    return ep


def call_claude(system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY not set")
    client = anthropic.Anthropic(api_key=api_key)
    for attempt in range(4):
        try:
            message = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return message.content[0].text
        except anthropic.RateLimitError:
            if attempt == 3:
                raise
            wait = 2 ** attempt * 5
            print(f"  Rate limited — retrying in {wait}s...")
            time.sleep(wait)
        except anthropic.APIStatusError as e:
            if e.status_code in (529,) and attempt < 3:
                wait = 2 ** attempt * 10
                print(f"  API overloaded — retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Claude API failed after 4 attempts")


def extract_yaml_block(text: str) -> str:
    if "```yaml" in text:
        fence_start = text.index("```yaml") + len("```yaml")
        closing = text.find("```", fence_start)
        if closing == -1:
            raise ValueError(f"unclosed ```yaml fence in Claude response (len={len(text)})")
        return text[fence_start:closing].strip()
    return text.strip()


def validate_director_schema(data: dict, shot_id: str) -> None:
    if "raw" in data and len(data) == 1:
        raise ValueError(f"Shot {shot_id}: schema validation failed — Claude returned unparseable YAML")
    missing = DIRECTOR_SCHEMA_KEYS - data.keys()
    if missing:
        raise ValueError(f"Shot {shot_id}: missing Director's Schema keys: {missing}")
    empty = [k for k in DIRECTOR_SCHEMA_KEYS if not str(data.get(k, "")).strip()]
    if empty:
        raise ValueError(f"Shot {shot_id}: empty Director's Schema fields: {empty}")


def run_story(ep: Path) -> None:
    brief_path = ep / "script" / "brief.yaml"
    if not brief_path.exists():
        raise FileNotFoundError(f"brief.yaml not found at {brief_path}")

    brief_text = brief_path.read_text(encoding="utf-8")
    skill = load_skill("science-story")

    print(f"Generating story arc for {ep.name}...")
    response = call_claude(skill, f"brief:\n{brief_text}", max_tokens=8192)
    story_yaml = extract_yaml_block(response)

    out = ep / "script" / "story.yaml"
    out.write_text(story_yaml, encoding="utf-8")
    print(f"Saved: {out}")


def run_script(ep: Path) -> None:
    story_path = ep / "script" / "story.yaml"
    if not story_path.exists():
        raise FileNotFoundError(f"story.yaml not found — run 'story' stage first")

    story_text = story_path.read_text(encoding="utf-8")
    skill = load_skill("science-script")

    print(f"Generating bilingual script for {ep.name}...")
    response = call_claude(skill, f"Story arc:\n```yaml\n{story_text}\n```", max_tokens=8192)
    script_yaml = extract_yaml_block(response)

    out = ep / "script" / "script.yaml"
    out.write_text(script_yaml, encoding="utf-8")
    print(f"Saved: {out}")


def run_shots(ep: Path) -> None:
    script_path = ep / "script" / "script.yaml"
    if not script_path.exists():
        raise FileNotFoundError(f"script.yaml not found — run 'script' stage first")

    data = yaml.safe_load(script_path.read_text(encoding="utf-8"))
    shots = data.get("shots", [])
    if not shots:
        raise ValueError("No shots found in script.yaml")

    skill = load_skill("science-director")
    print(f"Generating {len(shots)} Veo 3.1 prompts for {ep.name}...")

    checkpoint_dir = ep / "shots" / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=True)

    veo_prompts = []
    for i, shot in enumerate(shots, 1):
        shot_id = shot.get("id", f"sh{i:02d}")
        desc = shot.get("description", "")
        checkpoint = checkpoint_dir / f"{shot_id}.yaml"

        if checkpoint.exists():
            print(f"  [{i}/{len(shots)}] {shot_id}: using checkpoint")
            veo_prompts.append(yaml.safe_load(checkpoint.read_text(encoding="utf-8")))
            continue

        print(f"  [{i}/{len(shots)}] {shot_id}: {desc[:50]}...")
        response = call_claude(skill, desc)
        prompt_yaml = extract_yaml_block(response)
        try:
            prompt_data = yaml.safe_load(prompt_yaml)
        except yaml.YAMLError as e:
            raise ValueError(f"Shot {shot_id}: Claude returned invalid YAML: {e}")

        validate_director_schema(prompt_data, shot_id)

        entry = {"shot_id": shot_id, "scene_id": shot.get("scene_id"), "prompt": prompt_data}
        checkpoint.write_text(yaml.dump(entry, allow_unicode=True), encoding="utf-8")
        veo_prompts.append(entry)

    out = ep / "shots" / "veo-prompts.yaml"
    out.write_text(yaml.dump(veo_prompts, allow_unicode=True, default_flow_style=False), encoding="utf-8")
    print(f"Saved: {out} ({len(veo_prompts)} prompts)")


def main():
    parser = argparse.ArgumentParser(description="Xuong Phim AI — episode pipeline runner")
    parser.add_argument("stage", choices=["story", "script", "shots"], help="Pipeline stage to run")
    parser.add_argument("--slug", required=True, help="Episode slug")
    parser.add_argument("--base", default=".", help="Base directory (default: current dir)")
    args = parser.parse_args()

    ep = episode_path(args.slug, args.base)

    if args.stage == "story":
        run_story(ep)
    elif args.stage == "script":
        run_script(ep)
    elif args.stage == "shots":
        run_shots(ep)


if __name__ == "__main__":
    main()
