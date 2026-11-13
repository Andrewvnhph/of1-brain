"""Tests for episode_run utility functions — extracted for direct testing."""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import utils we'll test — these functions will be extracted from episode_run
from episode_run import extract_yaml_block, validate_director_schema


VALID_PROMPT = """
```yaml
subject: "small stick figure with glasses outline"
action: "raises right arm to point at prism shape slowly"
camera: "medium shot, side angle, static camera"
lighting: "diffuse overhead light, flat even illumination from above, whiteboard quality"
constraints: "pure white background, stick figure style, blue and orange accents only"
```
"""

SCHEMA_KEYS = {"subject", "action", "camera", "lighting", "constraints"}


class TestExtractYamlBlock:
    def test_extracts_from_fenced_block(self):
        result = extract_yaml_block(VALID_PROMPT)
        assert result.startswith("subject:")

    def test_returns_raw_when_no_fence(self):
        raw = "subject: test\naction: something"
        result = extract_yaml_block(raw)
        assert result == raw.strip()

    def test_raises_on_unclosed_fence(self):
        broken = "```yaml\nsubject: test\n"
        with pytest.raises(ValueError, match="unclosed"):
            extract_yaml_block(broken)

    def test_handles_extra_text_around_fence(self):
        text = "Here is the prompt:\n```yaml\nsubject: hi\n```\nSome trailing text."
        result = extract_yaml_block(text)
        assert result == "subject: hi"


class TestValidateDirectorSchema:
    def test_passes_valid_schema(self):
        data = {k: "some value" for k in SCHEMA_KEYS}
        validate_director_schema(data, shot_id="sh01")  # should not raise

    def test_raises_on_missing_key(self):
        data = {"subject": "x", "action": "y", "camera": "z", "lighting": "w"}
        # missing 'constraints'
        with pytest.raises(ValueError, match="constraints"):
            validate_director_schema(data, shot_id="sh01")

    def test_raises_on_empty_value(self):
        data = {k: "value" for k in SCHEMA_KEYS}
        data["lighting"] = ""
        with pytest.raises(ValueError, match="lighting"):
            validate_director_schema(data, shot_id="sh01")

    def test_raises_on_raw_fallback(self):
        data = {"raw": "some unparsed text"}
        with pytest.raises(ValueError, match="schema"):
            validate_director_schema(data, shot_id="sh01")


class TestBilingualParity:
    def test_equal_scene_counts(self):
        from audio_render import assert_bilingual_parity
        scenes = [
            {"id": "s01", "vi_narrator": "text vi", "en_narrator": "text en"},
            {"id": "s02", "vi_narrator": "text vi 2", "en_narrator": "text en 2"},
        ]
        assert_bilingual_parity(scenes)  # should not raise

    def test_raises_when_vi_missing(self):
        from audio_render import assert_bilingual_parity
        scenes = [
            {"id": "s01", "vi_narrator": "vi text", "en_narrator": "en text"},
            {"id": "s02", "en_narrator": "en text"},  # missing vi
        ]
        with pytest.raises(ValueError, match="s02"):
            assert_bilingual_parity(scenes)

    def test_raises_when_en_missing(self):
        from audio_render import assert_bilingual_parity
        scenes = [
            {"id": "s01", "vi_narrator": "vi text"},  # missing en
        ]
        with pytest.raises(ValueError, match="s01"):
            assert_bilingual_parity(scenes)
