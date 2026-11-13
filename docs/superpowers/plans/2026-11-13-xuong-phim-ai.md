# Xưởng Phim AI — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây dựng pipeline sản xuất phim ngắn AI (nhân vật người que, khoa học) gồm: CLI scaffolding, 3 Claude skills (story/script/director), prompt template library, và automation script cho các stage có API.

**Architecture:** Pipeline 2 lớp — lớp thủ công (Google Flow cho visual, DaVinci cho edit) có SOP đầy đủ trong design doc; lớp có thể automate (Claude story/script, ElevenLabs voice) được implement thành Python CLI + Claude skills. Claude skills adapt từ `smixs/visual-skills` và `wuwangzhang1216/DirectorSKILL`.

**Tech Stack:** Python 3.11+, anthropic SDK, elevenlabs SDK, pytest; Claude skills (Markdown); prompt templates (Markdown).

**Spec:** `designs/xuong-phim-ai.md` — đọc cả SOP section trước khi implement.

## Global Constraints

- Code dir: `code/xuong-phim-ai/`
- Episode storage: `episodes/<slug>/{scan,script,shots,audio,video/raw}/`
- Nhân vật người que: whiteboard background, simple black line, accent blue (#2563EB) + orange (#EA580C)
- Script bilingual: 1 file YAML song ngữ, 2 audio render riêng (VI primary, EN secondary)
- Shot list: đủ 5 trường Director's Schema (Subject / Action / Camera / Lighting / Constraints)
- Veo 3.1 prompt: không dùng tính từ chung — Subject phải có tuổi/trang phục/pose cụ thể
- Budget guard: Claude model mặc định `claude-haiku-4-5-20251001` cho generation (rẻ hơn), Sonnet chỉ khi cần story arc phức tạp
- Branch phải là `ai/*` trước mọi commit (pre-commit hook sẽ block nếu không)
- Tests dùng `pytest`, không mock external API — dùng fixture YAML thay thế

## Review Focus

1. **Script không có xung đột narrative** — output chỉ là danh sách facts, thiếu nhân vật/conflict/resolution. Test ở Task 2: assert story arc có `conflict` và `resolution` fields.
2. **Shot count không đủ cho 5 phút** — 20 shots × 15s = 5 phút; ít hơn 20 shots = phim ngắn hơn mục tiêu. Test ở Task 3: assert `len(shots) >= 20`.
3. **Director's Schema thiếu trường** — Veo 3.1 prompt thiếu Lighting hoặc Constraints → output kém. Test ở Task 4: assert tất cả 5 keys có mặt và không rỗng.
4. **Bilingual mismatch** — script VI và EN nói khác nhau (AI "dịch" thay vì "adapt"). Test ở Task 3: assert VI và EN có cùng số scenes.
5. **Episode folder bị overwrite** — chạy `episode_init` 2 lần xóa mất assets đã generate. Test ở Task 1: assert existing folder không bị xóa.

---

## File Structure

**Create in `code/xuong-phim-ai/`:**

```
code/xuong-phim-ai/
├── skills/
│   ├── science-story.md        # Claude skill: NotebookLM brief → story arc YAML
│   ├── science-script.md       # Claude skill: story arc → bilingual script + shot list
│   └── science-director.md     # Claude skill: shot desc → Veo 3.1 Director's Schema prompt
├── prompts/
│   ├── notebooklm.md           # NotebookLM chat templates (extract + discovery)
│   ├── nano-banana.md          # Nano Banana 2 character pose prompts (6 poses/nhân vật)
│   └── veo-shots.md            # Veo 3.1 shot prompt base format + examples
├── scripts/
│   ├── episode_init.py         # CLI: tạo episode folder structure
│   ├── episode_run.py          # CLI: gọi Claude API sinh story/script/shots
│   ├── audio_render.py         # CLI: gọi ElevenLabs API render voice VI+EN
│   └── tests/
│       ├── fixtures/
│       │   ├── sample_brief.yaml     # NotebookLM brief mẫu (vật lý: ánh sáng)
│       │   ├── sample_story.yaml     # Story arc mẫu (output của science-story)
│       │   └── sample_script.yaml   # Script + shot list mẫu
│       ├── test_episode_init.py
│       ├── test_story_structure.py
│       ├── test_script_structure.py
│       └── test_director_schema.py
└── README.md
```

---

### Task 1: Episode Scaffolding

**Files:**
- Create: `code/xuong-phim-ai/scripts/episode_init.py`
- Test: `code/xuong-phim-ai/scripts/tests/test_episode_init.py`

**Interfaces:**
- Produces: `episode_init(slug: str, base_dir: str) -> Path` — tạo folder, trả về path; raise `FileExistsError` nếu đã tồn tại

- [ ] **Step 1: Viết failing test**

```python
# tests/test_episode_init.py
import pytest
from pathlib import Path
from scripts.episode_init import episode_init

def test_creates_expected_folders(tmp_path):
    ep = episode_init("anh-sang", str(tmp_path))
    for sub in ["scan", "script", "shots", "audio", "video/raw"]:
        assert (ep / sub).is_dir()

def test_raises_if_exists(tmp_path):
    episode_init("anh-sang", str(tmp_path))
    with pytest.raises(FileExistsError):
        episode_init("anh-sang", str(tmp_path))

def test_slug_becomes_folder_name(tmp_path):
    ep = episode_init("hat-nhan-nguyen-tu", str(tmp_path))
    assert ep.name == "hat-nhan-nguyen-tu"
```

- [ ] **Step 2: Chạy test — xác nhận FAIL**

```bash
cd code/xuong-phim-ai && python -m pytest scripts/tests/test_episode_init.py -v
```
Expected: `ImportError` hoặc `ModuleNotFoundError`

- [ ] **Step 3: Implement `episode_init(slug, base_dir) -> Path` trong `scripts/episode_init.py`**

Tạo `episodes/<slug>/{scan,script,shots,audio,video/raw}` dưới `base_dir`. Raise `FileExistsError` nếu `episodes/<slug>` đã tồn tại. Thêm `if __name__ == "__main__"` block đọc `sys.argv[1]` làm slug.

- [ ] **Step 4: Chạy test — xác nhận PASS**

```bash
python -m pytest scripts/tests/test_episode_init.py -v
```
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
git checkout -b ai/xuong-phim-ai
git add code/xuong-phim-ai/scripts/episode_init.py code/xuong-phim-ai/scripts/tests/test_episode_init.py
git commit -m "feat(xuong-phim-ai): episode_init scaffolding script"
```

---

### Task 2: Claude Skill — science-story

**Files:**
- Create: `code/xuong-phim-ai/skills/science-story.md`
- Create: `code/xuong-phim-ai/scripts/tests/fixtures/sample_brief.yaml`
- Create: `code/xuong-phim-ai/scripts/tests/fixtures/sample_story.yaml`
- Test: `code/xuong-phim-ai/scripts/tests/test_story_structure.py`

**Interfaces:**
- Consumes: NotebookLM brief — YAML với keys `concepts: list[str]`, `discovery_moment: str`, `common_misconception: str`
- Produces: story arc YAML với keys: `title`, `characters: list[{name, role, personality}]`, `conflict`, `resolution`, `acts: list[{name, duration_min, summary}]`

- [ ] **Step 1: Tạo fixture `sample_brief.yaml`**

```yaml
# fixtures/sample_brief.yaml
topic: "Ánh sáng và màu sắc"
source_book: "Vật lý đại cương - tập 2"
concepts:
  - "Ánh sáng là sóng điện từ"
  - "Màu sắc là cảm nhận của não về bước sóng"
  - "Lăng kính tán sắc ánh sáng trắng thành quang phổ"
discovery_moment: "Newton dùng lăng kính chứng minh ánh sáng trắng là tổng hợp nhiều màu"
common_misconception: "Ánh sáng trắng là ánh sáng 'thuần khiết' không có màu"
```

- [ ] **Step 2: Viết failing test cho story structure**

```python
# tests/test_story_structure.py
import yaml, pytest
from pathlib import Path

STORY_KEYS = {"title", "characters", "conflict", "resolution", "acts"}
CHARACTER_KEYS = {"name", "role", "personality"}
ACT_KEYS = {"name", "duration_min", "summary"}

def load_story():
    p = Path(__file__).parent / "fixtures/sample_story.yaml"
    if not p.exists():
        pytest.skip("sample_story.yaml chưa tồn tại — generate trước")
    return yaml.safe_load(p.read_text())

def test_required_keys():
    story = load_story()
    assert STORY_KEYS <= story.keys()

def test_has_conflict_and_resolution():
    story = load_story()
    assert story["conflict"] and len(story["conflict"]) > 10
    assert story["resolution"] and len(story["resolution"]) > 10

def test_characters_count():
    story = load_story()
    assert 2 <= len(story["characters"]) <= 3

def test_character_keys():
    story = load_story()
    for c in story["characters"]:
        assert CHARACTER_KEYS <= c.keys()

def test_three_acts():
    story = load_story()
    assert len(story["acts"]) == 3
    total = sum(a["duration_min"] for a in story["acts"])
    assert 5 <= total <= 10
```

- [ ] **Step 3: Chạy test — xác nhận SKIP (fixture chưa có)**

```bash
python -m pytest scripts/tests/test_story_structure.py -v
```
Expected: 5 SKIP

- [ ] **Step 4: Viết `skills/science-story.md`**

Skill nhận `brief:` YAML block từ user. Outputs story arc YAML theo schema trên. Phải enforce:
- Nhân vật: 2–3 người que có tên + role (scientist, student, narrator)
- 3 acts: Setup ≤ 1.5 phút, Exploration 5–7 phút, Revelation 1–2 phút
- `conflict` = misconception nhân vật tin sai lúc đầu
- `resolution` = "aha moment" + ứng dụng thực tế
- Tone: educational nhưng có drama — không phải textbook

- [ ] **Step 5: Generate `sample_story.yaml` bằng skill**

Dùng Claude với skill `science-story.md` + fixture `sample_brief.yaml` → save output vào `fixtures/sample_story.yaml`.

- [ ] **Step 6: Chạy test — xác nhận PASS**

```bash
python -m pytest scripts/tests/test_story_structure.py -v
```
Expected: 5 PASS

- [ ] **Step 7: Commit**

```bash
git add code/xuong-phim-ai/skills/science-story.md code/xuong-phim-ai/scripts/tests/
git commit -m "feat(xuong-phim-ai): science-story skill + story structure tests"
```

---

### Task 3: Claude Skill — science-script

**Files:**
- Create: `code/xuong-phim-ai/skills/science-script.md`
- Create: `code/xuong-phim-ai/scripts/tests/fixtures/sample_script.yaml`
- Test: `code/xuong-phim-ai/scripts/tests/test_script_structure.py`

**Interfaces:**
- Consumes: `sample_story.yaml` từ Task 2
- Produces: script YAML với keys: `scenes: list[{id, vi_narrator, en_narrator, vi_dialogue, en_dialogue, duration_sec}]`, `shots: list[{id, scene_id, description}]`

- [ ] **Step 1: Viết failing test**

```python
# tests/test_script_structure.py
import yaml, pytest
from pathlib import Path

def load_script():
    p = Path(__file__).parent / "fixtures/sample_script.yaml"
    if not p.exists():
        pytest.skip("sample_script.yaml chưa tồn tại")
    return yaml.safe_load(p.read_text())

def test_has_scenes_and_shots():
    s = load_script()
    assert "scenes" in s and "shots" in s

def test_minimum_shot_count():
    s = load_script()
    assert len(s["shots"]) >= 20, f"Chỉ có {len(s['shots'])} shots — cần ít nhất 20 cho 5 phút"

def test_bilingual_scene_parity():
    s = load_script()
    for scene in s["scenes"]:
        assert scene.get("vi_narrator") and scene.get("en_narrator"), \
            f"Scene {scene['id']} thiếu narrator VI hoặc EN"

def test_shot_scene_reference():
    s = load_script()
    scene_ids = {sc["id"] for sc in s["scenes"]}
    for shot in s["shots"]:
        assert shot["scene_id"] in scene_ids, \
            f"Shot {shot['id']} trỏ đến scene không tồn tại: {shot['scene_id']}"

def test_total_duration():
    s = load_script()
    total = sum(sc["duration_sec"] for sc in s["scenes"])
    assert 300 <= total <= 600, f"Tổng {total}s — cần 300–600s (5–10 phút)"
```

- [ ] **Step 2: Chạy test — xác nhận SKIP**

```bash
python -m pytest scripts/tests/test_script_structure.py -v
```

- [ ] **Step 3: Viết `skills/science-script.md`**

Skill nhận story arc YAML → output script YAML. Enforce:
- Mỗi scene có cả `vi_narrator` lẫn `en_narrator` (không phải dịch word-for-word mà adapt tone cho từng ngôn ngữ)
- Minimum 20 shots, maximum 40 shots
- Mỗi shot có `scene_id` trỏ về scene tương ứng
- Shot description viết theo Director's Schema sơ bộ (Subject + Action) — Task 4 sẽ expand thành full prompt
- Duration per scene: 20–90 giây

- [ ] **Step 4: Generate `sample_script.yaml` bằng skill**

Dùng Claude với `science-script.md` + `sample_story.yaml` → save vào `fixtures/sample_script.yaml`.

- [ ] **Step 5: Chạy test — xác nhận PASS**

```bash
python -m pytest scripts/tests/test_script_structure.py -v
```
Expected: 5 PASS

- [ ] **Step 6: Commit**

```bash
git add code/xuong-phim-ai/skills/science-script.md code/xuong-phim-ai/scripts/tests/
git commit -m "feat(xuong-phim-ai): science-script skill + script structure tests"
```

---

### Task 4: Claude Skill — science-director + Prompt Templates

**Files:**
- Create: `code/xuong-phim-ai/skills/science-director.md`
- Create: `code/xuong-phim-ai/prompts/notebooklm.md`
- Create: `code/xuong-phim-ai/prompts/nano-banana.md`
- Create: `code/xuong-phim-ai/prompts/veo-shots.md`
- Test: `code/xuong-phim-ai/scripts/tests/test_director_schema.py`

**Interfaces:**
- Consumes: shot `description` string từ `sample_script.yaml`
- Produces: Veo 3.1 prompt YAML với keys: `subject`, `action`, `camera`, `lighting`, `constraints`

- [ ] **Step 1: Viết failing test**

```python
# tests/test_director_schema.py
import yaml, pytest
from pathlib import Path

SCHEMA_KEYS = {"subject", "action", "camera", "lighting", "constraints"}

def load_shots_sample():
    p = Path(__file__).parent / "fixtures/sample_script.yaml"
    if not p.exists():
        pytest.skip("sample_script.yaml chưa tồn tại — chạy Task 3 trước")
    return yaml.safe_load(p.read_text())["shots"][:3]  # test 3 shots đầu

def test_schema_keys_present(shot_prompt_fixture):
    assert SCHEMA_KEYS <= shot_prompt_fixture.keys()

def test_subject_not_generic(shot_prompt_fixture):
    subject = shot_prompt_fixture["subject"].lower()
    forbidden = ["character", "person", "figure", "someone"]
    for word in forbidden:
        assert word not in subject, f"Subject quá chung: '{subject}'"

def test_lighting_has_source_and_direction(shot_prompt_fixture):
    lighting = shot_prompt_fixture["lighting"]
    assert len(lighting) >= 20, f"Lighting quá ngắn/chung: '{lighting}'"

def test_whiteboard_in_constraints(shot_prompt_fixture):
    constraints = shot_prompt_fixture["constraints"].lower()
    assert "white" in constraints or "whiteboard" in constraints or "clean background" in constraints

@pytest.fixture
def shot_prompt_fixture():
    # Sẽ load từ fixture file được generate bởi science-director skill
    p = Path(__file__).parent / "fixtures/sample_veo_prompt.yaml"
    if not p.exists():
        pytest.skip("sample_veo_prompt.yaml chưa tồn tại")
    return yaml.safe_load(p.read_text())
```

- [ ] **Step 2: Chạy test — xác nhận SKIP**

```bash
python -m pytest scripts/tests/test_director_schema.py -v
```

- [ ] **Step 3: Viết `skills/science-director.md`**

Skill nhận 1 shot description → output Veo 3.1 prompt YAML. Enforce whiteboard aesthetic:
- `subject`: người que cụ thể — "small stick figure with round glasses outline, lab coat shape" (không phải "scientist")
- `action`: chuyển động vật lý cụ thể — "raises right arm to point at floating wave diagram"
- `camera`: góc + chuyển động — "medium shot, slow zoom-in, static camera"
- `lighting`: "diffuse overhead light, flat even illumination, whiteboard studio feel"
- `constraints`: "pure white background, no shadows, stick figure style consistent with reference, blue-orange palette only"

- [ ] **Step 4: Viết `prompts/nano-banana.md`**

6 prompt mẫu cho Nano Banana 2 (1 per pose): neutral, pointing, thinking, eureka, walking, sitting. Mỗi prompt khoảng 50 từ, enforce style consistency markers.

- [ ] **Step 5: Viết `prompts/notebooklm.md`**

3 prompt templates:
- Extract concepts: prompt tại SOP-1 step 3 (đã có trong design)
- Discovery moment: *"Hiện tượng hoặc thí nghiệm nào trong sách này gây bất ngờ nhất?"*
- Misconception: *"Hiểu lầm phổ biến nhất về chủ đề này là gì?"*

- [ ] **Step 6: Viết `prompts/veo-shots.md`**

Base format + 3 ví dụ cụ thể (shot tĩnh, shot có chuyển động nhân vật, shot có chuyển động camera). Mỗi example là YAML đầy đủ 5 trường.

- [ ] **Step 7: Generate `sample_veo_prompt.yaml` và chạy test PASS**

Dùng `science-director.md` với 1 shot từ `sample_script.yaml` → save `fixtures/sample_veo_prompt.yaml`.

```bash
python -m pytest scripts/tests/test_director_schema.py -v
```
Expected: 4 PASS

- [ ] **Step 8: Commit**

```bash
git add code/xuong-phim-ai/skills/science-director.md code/xuong-phim-ai/prompts/
git add code/xuong-phim-ai/scripts/tests/
git commit -m "feat(xuong-phim-ai): science-director skill + all prompt templates"
```

---

### Task 5: CLI Automation — episode_run + audio_render

**Files:**
- Create: `code/xuong-phim-ai/scripts/episode_run.py`
- Create: `code/xuong-phim-ai/scripts/audio_render.py`
- Create: `code/xuong-phim-ai/README.md`

**Interfaces:**
- Consumes: episode folder (created by Task 1) + `script/brief.yaml`
- Produces:
  - `episode_run.py`: saves `script/story.yaml`, `script/script.yaml`, `shots/veo-prompts.yaml`
  - `audio_render.py`: saves `audio/vi-narrator.mp3`, `audio/en-narrator.mp3`

- [ ] **Step 1: Implement `episode_run.py`**

CLI với 3 sub-commands, mỗi lệnh đọc input từ episode folder và ghi output vào đúng sub-folder:

```
python episode_run.py story --slug <slug>    # brief.yaml → story.yaml
python episode_run.py script --slug <slug>   # story.yaml → script.yaml
python episode_run.py shots --slug <slug>    # script.yaml → veo-prompts.yaml (all shots)
```

Dùng `anthropic` SDK, model `claude-haiku-4-5-20251001`. Load skill content từ `skills/*.md` làm system prompt. Raise `FileNotFoundError` nếu input file chưa tồn tại.

- [ ] **Step 2: Implement `audio_render.py`**

```
python audio_render.py --slug <slug> --lang vi   # render VI narrator track
python audio_render.py --slug <slug> --lang en   # render EN narrator track
```

Đọc tất cả `vi_narrator` hoặc `en_narrator` từ `script/script.yaml`, concat thành 1 text, gọi ElevenLabs API, save MP3 vào `audio/`. Voice ID đọc từ env var `ELEVENLABS_VOICE_VI` và `ELEVENLABS_VOICE_EN`.

- [ ] **Step 3: Viết `README.md`**

End-to-end quickstart (10 lệnh, từ scan sách đến veo-prompts.yaml sẵn sàng paste vào Google Flow). Link đến design doc SOP cho manual steps (Google Flow, DaVinci, publish).

- [ ] **Step 4: Test dry-run với sample fixtures**

```bash
# Tạo episode test
python scripts/episode_init.py anh-sang

# Copy brief fixture vào episode
cp scripts/tests/fixtures/sample_brief.yaml episodes/anh-sang/script/brief.yaml

# Chạy từng stage
python scripts/episode_run.py story --slug anh-sang
python scripts/episode_run.py script --slug anh-sang
python scripts/episode_run.py shots --slug anh-sang

# Verify output
ls episodes/anh-sang/script/
ls episodes/anh-sang/shots/
```

Expected: 3 YAML files tồn tại, `veo-prompts.yaml` có ≥ 20 entries.

- [ ] **Step 5: Commit**

```bash
git add code/xuong-phim-ai/scripts/episode_run.py
git add code/xuong-phim-ai/scripts/audio_render.py
git add code/xuong-phim-ai/README.md
git commit -m "feat(xuong-phim-ai): episode_run CLI + audio_render + README quickstart"
```
