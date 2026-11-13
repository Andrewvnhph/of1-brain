import yaml
import pytest
from pathlib import Path

STORY_KEYS = {"title", "characters", "conflict", "resolution", "acts"}
CHARACTER_KEYS = {"name", "role", "personality"}
ACT_KEYS = {"name", "duration_min", "summary"}
FIXTURE_PATH = Path(__file__).parent / "fixtures/sample_story.yaml"


def load_story():
    if not FIXTURE_PATH.exists():
        pytest.skip("sample_story.yaml chưa tồn tại — generate trước bằng science-story skill")
    return yaml.safe_load(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_required_keys():
    story = load_story()
    missing = STORY_KEYS - story.keys()
    assert not missing, f"Missing keys: {missing}"


def test_has_conflict_and_resolution():
    story = load_story()
    assert story.get("conflict") and len(str(story["conflict"])) > 10, "conflict quá ngắn hoặc thiếu"
    assert story.get("resolution") and len(str(story["resolution"])) > 10, "resolution quá ngắn hoặc thiếu"


def test_characters_count():
    story = load_story()
    count = len(story["characters"])
    assert 2 <= count <= 3, f"Cần 2-3 nhân vật, có {count}"


def test_character_keys():
    story = load_story()
    for c in story["characters"]:
        missing = CHARACTER_KEYS - c.keys()
        assert not missing, f"Nhân vật '{c.get('name', '?')}' thiếu keys: {missing}"


def test_three_acts():
    story = load_story()
    assert len(story["acts"]) == 3, f"Cần đúng 3 acts, có {len(story['acts'])}"
    total = sum(a["duration_min"] for a in story["acts"])
    assert 5 <= total <= 10, f"Tổng duration {total} phút — cần 5-10 phút"


def test_acts_have_required_keys():
    story = load_story()
    for act in story["acts"]:
        missing = ACT_KEYS - act.keys()
        assert not missing, f"Act '{act.get('name', '?')}' thiếu keys: {missing}"
