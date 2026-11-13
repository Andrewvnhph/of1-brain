import yaml
import pytest
from pathlib import Path

FIXTURE_PATH = Path(__file__).parent / "fixtures/sample_script.yaml"


def load_script():
    if not FIXTURE_PATH.exists():
        pytest.skip("sample_script.yaml chưa tồn tại — generate trước bằng science-script skill")
    return yaml.safe_load(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_has_scenes_and_shots():
    s = load_script()
    assert "scenes" in s, "Thiếu key 'scenes'"
    assert "shots" in s, "Thiếu key 'shots'"
    assert len(s["scenes"]) > 0, "scenes rỗng"
    assert len(s["shots"]) > 0, "shots rỗng"


def test_minimum_shot_count():
    s = load_script()
    count = len(s["shots"])
    assert count >= 20, f"Chỉ có {count} shots — cần ít nhất 20 cho 5 phút"


def test_bilingual_scene_parity():
    s = load_script()
    for scene in s["scenes"]:
        sid = scene.get("id", "?")
        assert scene.get("vi_narrator"), f"Scene {sid} thiếu vi_narrator"
        assert scene.get("en_narrator"), f"Scene {sid} thiếu en_narrator"


def test_shot_scene_reference():
    s = load_script()
    scene_ids = {sc["id"] for sc in s["scenes"]}
    for shot in s["shots"]:
        assert shot.get("scene_id") in scene_ids, \
            f"Shot {shot.get('id', '?')} trỏ đến scene không tồn tại: {shot.get('scene_id')}"


def test_total_duration():
    s = load_script()
    total = sum(sc.get("duration_sec", 0) for sc in s["scenes"])
    assert 300 <= total <= 600, f"Tổng {total}s — cần 300-600s (5-10 phút)"


def test_shots_have_required_fields():
    s = load_script()
    for shot in s["shots"]:
        sid = shot.get("id", "?")
        assert shot.get("scene_id"), f"Shot {sid} thiếu scene_id"
        assert shot.get("description"), f"Shot {sid} thiếu description"
