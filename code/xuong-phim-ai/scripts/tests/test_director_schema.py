import yaml
import pytest
from pathlib import Path

SCHEMA_KEYS = {"subject", "action", "camera", "lighting", "constraints"}
FIXTURE_PATH = Path(__file__).parent / "fixtures/sample_veo_prompt.yaml"
import re

# "stick figure" là style descriptor bắt buộc — chỉ reject standalone generic nouns
GENERIC_STANDALONE = ["a character", "a person", "someone", "a figure", "nhân vật", "người"]


def load_prompt():
    if not FIXTURE_PATH.exists():
        pytest.skip("sample_veo_prompt.yaml chưa tồn tại — generate trước bằng science-director skill")
    return yaml.safe_load(FIXTURE_PATH.read_text(encoding="utf-8"))


def test_schema_keys_present():
    prompt = load_prompt()
    missing = SCHEMA_KEYS - prompt.keys()
    assert not missing, f"Thiếu Director's Schema keys: {missing}"


def test_subject_not_generic():
    prompt = load_prompt()
    subject = prompt["subject"].lower()
    for phrase in GENERIC_STANDALONE:
        assert phrase not in subject, \
            f"Subject quá chung chung ('{phrase}' found): '{prompt['subject']}'"
    # Subject phải có ít nhất 1 specific visual detail (glasses, pose, item)
    has_specific = any(w in subject for w in ["glasses", "lab coat", "backpack", "holding", "leaning", "raised", "bent"])
    assert has_specific, f"Subject thiếu visual specifics: '{prompt['subject']}'"


def test_lighting_has_sufficient_detail():
    prompt = load_prompt()
    lighting = prompt["lighting"]
    assert len(str(lighting)) >= 20, \
        f"Lighting quá ngắn/chung: '{lighting}' — cần mô tả nguồn sáng + hướng + chất lượng"


def test_whiteboard_aesthetic_in_constraints():
    prompt = load_prompt()
    constraints = prompt["constraints"].lower()
    has_whiteboard = any(w in constraints for w in ["white", "whiteboard", "clean background"])
    assert has_whiteboard, \
        f"Constraints không enforce whiteboard aesthetic: '{prompt['constraints']}'"


def test_all_fields_non_empty():
    prompt = load_prompt()
    for key in SCHEMA_KEYS:
        val = prompt.get(key, "")
        assert val and len(str(val).strip()) > 0, f"Field '{key}' rỗng"


def test_action_is_specific_movement():
    prompt = load_prompt()
    action = prompt["action"]
    assert len(str(action)) >= 15, \
        f"Action quá chung chung: '{action}' — cần mô tả chuyển động cụ thể"
