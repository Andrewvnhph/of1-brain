from pathlib import Path
import sys


def episode_init(slug: str, base_dir: str) -> Path:
    base = Path(base_dir)
    ep = base / "episodes" / slug
    if ep.exists():
        raise FileExistsError(f"Episode already exists: {ep}")
    for sub in ["scan", "script", "shots", "audio", "video/raw"]:
        (ep / sub).mkdir(parents=True, exist_ok=False)
    return ep


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: episode_init.py <slug> [base_dir]")
        sys.exit(1)
    slug = sys.argv[1]
    base = sys.argv[2] if len(sys.argv) > 2 else "."
    path = episode_init(slug, base)
    print(f"Created episode: {path}")
