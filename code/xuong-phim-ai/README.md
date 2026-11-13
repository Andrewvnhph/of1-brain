# Xưởng Phim AI — Khoa Học

Pipeline sản xuất phim ngắn AI (5–10 phút), nhân vật người que, chủ đề khoa học.
Từ sách scan đến veo-prompts.yaml sẵn sàng paste vào Google Flow.

## Quickstart — 10 lệnh từ sách đến video-ready

```bash
# 0. Setup
cd code/xuong-phim-ai
pip3 install anthropic pyyaml elevenlabs
export ANTHROPIC_API_KEY="sk-..."
export ELEVENLABS_API_KEY="..."
export ELEVENLABS_VOICE_VI="<voice-id-vietnamese>"
export ELEVENLABS_VOICE_EN="<voice-id-english>"

# 1. Tạo episode folder
python3 scripts/episode_init.py anh-sang .

# 2. [MANUAL — SOP-1] Scan sách → NotebookLM → export brief
#    Dùng prompts/notebooklm.md → paste output vào episodes/anh-sang/script/brief.yaml

# 3. Generate story arc (Claude)
python3 scripts/episode_run.py story --slug anh-sang

# 4. Generate bilingual script + shot list (Claude)
python3 scripts/episode_run.py script --slug anh-sang

# 5. Generate Veo 3.1 prompts for all shots (Claude)
python3 scripts/episode_run.py shots --slug anh-sang

# 6. Render Vietnamese voice (ElevenLabs)
python3 scripts/audio_render.py --slug anh-sang --lang vi

# 7. Render English voice (ElevenLabs)
python3 scripts/audio_render.py --slug anh-sang --lang en

# 8. [MANUAL — SOP-2] Google Flow: Nano Banana → Character Reference Sheet
#    Dùng prompts/nano-banana.md

# 9. [MANUAL — SOP-3] Google Flow: Veo 3.1 → video per shot
#    Dùng episodes/anh-sang/shots/veo-prompts.yaml

# 10. [MANUAL — SOP-5] DaVinci Resolve → final assembly + export
```

## Episode Folder Structure

```
episodes/<slug>/
├── scan/           # PDF / ảnh sách scan
├── script/
│   ├── brief.yaml      # NotebookLM output (input thủ công)
│   ├── story.yaml      # Story arc (auto — episode_run story)
│   ├── script.yaml     # Bilingual script + shots (auto — episode_run script)
├── shots/
│   └── veo-prompts.yaml  # Veo 3.1 prompts per shot (auto — episode_run shots)
├── audio/
│   ├── vi-narrator.mp3   # Vietnamese voice (auto — audio_render)
│   └── en-narrator.mp3   # English voice (auto — audio_render)
└── video/
    └── raw/              # Approved Veo 3.1 clips (manual — Google Flow)
```

## Claude Skills

| Skill | Input | Output |
|---|---|---|
| `skills/science-story.md` | `brief.yaml` | Story arc YAML (3-act, characters, conflict) |
| `skills/science-script.md` | `story.yaml` | Bilingual script + ≥20 shots YAML |
| `skills/science-director.md` | Shot description | Veo 3.1 Director's Schema YAML |

Skills có thể dùng trực tiếp trong Claude.ai với `npx skills add` hoặc copy vào `.claude/skills/`.

## Prompt Templates

| File | Dùng khi |
|---|---|
| `prompts/notebooklm.md` | Extract content từ sách scan (SOP-1) |
| `prompts/nano-banana.md` | Tạo Character Reference Sheet (SOP-2) |
| `prompts/veo-shots.md` | Generate video per shot (SOP-3) |

## Manual Steps (SOP)

Các bước thủ công được hướng dẫn chi tiết trong:
`designs/xuong-phim-ai.md` → section **SOP — Hướng Dẫn Các Bước Thủ Công**

- **SOP-1**: Scan sách → NotebookLM
- **SOP-2**: Google Flow — Character Reference Sheet (Nano Banana)
- **SOP-3**: Google Flow — Video per scene (Veo 3.1)
- **SOP-4**: Quality review trước khi edit
- **SOP-5**: DaVinci Resolve — Final assembly
- **SOP-6**: Publish YouTube + TikTok

## Tests

```bash
cd code/xuong-phim-ai
python3 -m pytest scripts/tests/ -v
# Expected: 22 passed
```

## Stack

- **Claude** (`claude-haiku-4-5-20251001`) — story, script, shot prompts
- **Google Flow** — Nano Banana 2 (images) + Veo 3.1 (video)
- **ElevenLabs** — `eleven_multilingual_v2` voice
- **DaVinci Resolve** — final edit (YouTube 1080p + TikTok 1080×1920)

## Budget per tập

| Item | Cost |
|---|---|
| Claude story + script (~8K tokens haiku) | ~$0.01 |
| Claude 23 shot prompts (~15K tokens haiku) | ~$0.02 |
| Veo 3.1 23 clips × $0.10 | ~$2.30 |
| ElevenLabs 2 tracks (~2K chars) | ~$0.60 |
| Total | **~$3–5/tập** |
