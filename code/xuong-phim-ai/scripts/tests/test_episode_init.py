import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from episode_init import episode_init


def test_creates_expected_folders(tmp_path):
    ep = episode_init("anh-sang", str(tmp_path))
    for sub in ["scan", "script", "shots", "audio", "video/raw"]:
        assert (ep / sub).is_dir(), f"Missing subfolder: {sub}"


def test_raises_if_exists(tmp_path):
    episode_init("anh-sang", str(tmp_path))
    with pytest.raises(FileExistsError):
        episode_init("anh-sang", str(tmp_path))


def test_slug_becomes_folder_name(tmp_path):
    ep = episode_init("hat-nhan-nguyen-tu", str(tmp_path))
    assert ep.name == "hat-nhan-nguyen-tu"


def test_returns_path_object(tmp_path):
    ep = episode_init("test-slug", str(tmp_path))
    assert isinstance(ep, Path)
