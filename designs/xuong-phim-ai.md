# Design — Xưởng Phim AI: Khoa Học

**Date:** 2026-11-13  
**Slug:** `xuong-phim-ai`  
**Status:** Draft

## Intent

Xây dựng một pipeline sản xuất AI có thể tái sử dụng: scan sách khoa học → trích xuất nội dung → viết story → render phim ngắn 5–10 phút (nhân vật người que) → publish YouTube + TikTok. Hai ngôn ngữ: Tiếng Việt + Tiếng Anh.

**Mục đích:** Làm cho khoa học dễ tiếp cận và hấp dẫn với học sinh + người trưởng thành tò mò, dùng AI để giảm thời gian và chi phí sản xuất.

## Goals

- Pipeline đầu cuối: scan → content → script → video → publish
- Bilingual output: Tiếng Việt + Tiếng Anh từ cùng một nguồn
- Visual identity nhất quán: nhân vật người que xuyên suốt mọi chủ đề
- Repeatable: áp dụng được cho bất kỳ chủ đề khoa học nào
- Chi phí thấp: mục tiêu $15–40/tập
- Nhanh: mục tiêu 4–8 giờ/tập

## Non-Goals

- Không phải live-action film
- Không phải real-time generation
- Không phải web app cho end-user (đây là creator workflow)
- Không phải custom model training

## Anti-Goals (thất bại dù kỹ thuật đúng)

- Nhân vật không nhất quán giữa các cảnh (character inconsistency)
- Script chỉ liệt kê sự kiện — không có câu chuyện, nhân vật, xung đột
- Thời gian sản xuất > 1 ngày/tập
- Chất lượng thấp hơn ngưỡng monetize YouTube

## Constraints

- Dùng công cụ AI sẵn có (không train model mới)
- Budget: $15–40/tập
- Nguồn nội dung: sách vật lý được scan (PDF / ảnh)
- Tái sử dụng các skill repos đã tồn tại thay vì build từ đầu

---

## Tool Stack Chính

```
Google Ecosystem (cốt lõi):
  NotebookLM   → Content extraction từ sách scan
  Google Flow  → Visual production workspace (image + video + audio)
    ├─ Nano Banana 2  → Stick-figure reference sheet (tối đa 5 nhân vật, 14 objects)
    └─ Veo 3.1        → Video per scene (native audio, character consistency)

Claude (AI brain):
  → Story arc, script song ngữ, shot list, prompt engineering

Post-production:
  ElevenLabs   → Professional voice (Vietnamese + English)
  DaVinci Resolve / CapCut → Edit + export
```

**Lý do chọn Google Flow**: Character consistency built-in (Nano Banana → Veo 3.1 seamless),
all-in-one workspace, native audio trong Veo 3.1, cùng ecosystem với NotebookLM.

**Mode**: Semi-automated — Claude tạo script/prompt, người dùng thao tác Google Flow để
kiểm soát chất lượng từng shot, không fully automated.

---

## Pipeline Chi Tiết

### Stage 1 — Content Extraction

| Item | Chi tiết |
|---|---|
| Input | Sách scan (PDF hoặc ảnh) |
| Tool | NotebookLM: upload PDF → extract key concepts, generate Q&A |
| Output | Story brief: 3–5 khái niệm khoa học cốt lõi + 1 "discovery moment" trung tâm |
| Claude role | Nhận brief từ NotebookLM → cấu trúc thành narrative seed |

### Stage 2 — Story Development

Claude tạo story arc:

```
Nhân vật:  2–3 người que có cá tính (scientist, curious student, narrator)
Xung đột:  misconception → curiosity → discovery
Cấu trúc:  3-act
  - Setup (1 phút):       Giới thiệu câu hỏi / hiện tượng
  - Exploration (7 phút): Nhân vật khám phá, thất bại, thử lại
  - Revelation (2 phút):  "Aha moment" + ứng dụng thực tế
```

Output: Story brief + Character Bible (2 trang)

### Stage 3 — Script + Shot List (Claude)

Adapt `wuwangzhang1216/DirectorSKILL` → sinh ra:

- Full script Tiếng Việt (primary) + English (parallel)
- Shot list theo Director's Schema:

```
Subject:     [người que cụ thể, pose, trạng thái]
Action:      [chuyển động / hành động cụ thể]
Camera:      [góc quay + chuyển động camera]
Lighting:    [nguồn sáng + hướng + chất lượng — whiteboard style]
Constraints: [bối cảnh, background sạch, giới hạn frame]
```

- Sound plan: timing narrator, music cue, SFX
- Director style: **Whiteboard/Kurzgesagt** (clean background, minimalist, educational)

### Stage 4 — Visual Production (Google Flow)

**Step 4a — Character Reference Sheet (Nano Banana 2):**
- Sinh stick-figure chính trong 4–6 poses
- Visual bible: background trắng/whiteboard, người que simple line 2–3 màu accent
- Builder decision: màu accent mặc định = xanh dương + đỏ cam (science palette)
- Feed reference sheet vào tất cả Veo prompts → consistency đảm bảo

**Step 4b — Video per Scene (Veo 3.1):**
- Paste từng shot prompt từ Stage 3 vào Google Flow
- Up tới 3 reference images/shot → character lock
- Native audio option: dùng Veo 3.1 ambient sound nếu cần
- Mỗi clip: 5–15 giây, batch theo scene

### Stage 5 — Audio

| Element | Tool | Ghi chú |
|---|---|---|
| Vietnamese voice | ElevenLabs | Warm, educational tone — primary |
| English voice | ElevenLabs | Separate render, cùng script |
| Background music | Suno | Science/discovery ambient |
| SFX | Veo 3.1 native / Freesound | Transition sounds, "aha" moments |

### Stage 6 — Post-Production

| Output | Tool | Thời lượng |
|---|---|---|
| YouTube version | DaVinci Resolve | 5–10 phút, full narrative |
| TikTok version | CapCut | 60 giây, hook-first (dramatic moment đầu tiên) |

Bilingual: 2 audio tracks riêng, captions per ngôn ngữ.

### Stage 7 — Publish

- **YouTube**: title + description + chapters (Vietnamese + English), thumbnail người que
- **TikTok**: hook caption, hashtag (#science #LearnScience #KhoaHoc), 60s cut

---

## Skill Stack Tái Sử Dụng

| Skill | Nguồn | Cách adapt |
|---|---|---|
| `visual` (video prompts) | `smixs/visual-skills` | Thêm stick-figure rules + whiteboard aesthetic |
| `DirectorSKILL` | `wuwangzhang1216/DirectorSKILL` | Thêm science-education overlay, 3-act template |
| `video-scriptwriting` | `skills.rest` | Adapt bilingual science script |
| NotebookLM workflow | Google | Manual step — upload sách, export Q&A |
| Google Flow | Google | Main visual workspace |

---

## Quyết định Đã Thống Nhất (Builder)

| # | Quyết định | Chọn |
|---|---|---|
| 1 | Pipeline mode | Semi-automated (Claude text + Google Flow visual) |
| 2 | Bilingual | Một script song ngữ, hai audio render riêng |
| 3 | Stick-figure style | Whiteboard bg, simple line, accent xanh + cam |
| 4 | Visual tool | Google Flow (Nano Banana 2 + Veo 3.1) |
| 5 | Project storage | `episodes/<slug>/` → scan/, script/, shots/, audio/, video/ |
| 6 | Quality gate | Phải approve từng shot trước khi edit — không publish nếu chưa đạt |

---

---

## SOP — Hướng Dẫn Các Bước Thủ Công

### SOP-1: Scan Sách → NotebookLM

**Mục tiêu:** Trích xuất 3–5 khái niệm khoa học cốt lõi từ sách vật lý.

**Bước:**
1. **Scan sách**
   - Dùng camera điện thoại (Adobe Scan / Google PhotoScan) hoặc máy scan
   - Chụp các chương liên quan — không cần toàn bộ sách
   - Export thành PDF (tối thiểu 300 DPI để OCR đọc được)

2. **Upload vào NotebookLM**
   - Vào [notebooklm.google.com](https://notebooklm.google.com)
   - Tạo notebook mới → Add source → Upload PDF
   - Chờ NotebookLM index (1–3 phút)

3. **Extract nội dung**
   - Dùng prompt sau trong NotebookLM chat:
     ```
     Hãy liệt kê 5 khái niệm khoa học quan trọng nhất trong tài liệu này.
     Với mỗi khái niệm: (1) giải thích đơn giản cho học sinh lớp 10,
     (2) một ví dụ thực tế trong cuộc sống, (3) hiểu lầm phổ biến nhất.
     ```
   - Copy output → paste vào Claude để bắt đầu Stage 2

4. **Kiểm tra chất lượng extract**
   - Đảm bảo có ít nhất 1 "discovery moment" (khoảnh khắc wow)
   - Nếu thiếu: hỏi thêm NotebookLM: *"Hiện tượng hoặc thí nghiệm nào trong sách này gây bất ngờ nhất?"*

---

### SOP-2: Google Flow — Tạo Character Reference Sheet (Nano Banana)

**Mục tiêu:** Tạo bộ nhân vật người que nhất quán dùng xuyên suốt phim.

**Bước:**
1. **Mở Google Flow** → chọn **Nano Banana 2**

2. **Tạo nhân vật chính (Scientist)** — dùng prompt mẫu:
   ```
   Minimalist stick figure scientist, simple black line drawing on white background,
   wearing small round glasses, lab coat outline, friendly expression,
   clean whiteboard illustration style, 2-color accent (blue + orange),
   full body, standing pose
   ```

3. **Generate 6 poses cho mỗi nhân vật:**
   - Standing neutral
   - Pointing at whiteboard
   - Thinking (hand on chin)
   - Excited / eureka moment
   - Walking
   - Sitting / reading

4. **Lưu Reference Sheet**
   - Download tất cả 6 ảnh
   - Lưu vào `episodes/<slug>/assets/characters/`
   - Đặt tên: `char-scientist-01.png` → `char-scientist-06.png`

5. **Approve tiêu chí:**
   - ✅ Style nhất quán giữa 6 poses (cùng độ dày nét, cùng màu)
   - ✅ Rõ ràng ở kích thước nhỏ (sẽ xuất hiện trong frame rộng)
   - ✅ Biểu cảm đọc được
   - ❌ Reject nếu: quá phức tạp, màu sắc không nhất quán, không nhận ra là cùng nhân vật

---

### SOP-3: Google Flow — Sinh Video Từng Cảnh (Veo 3.1)

**Mục tiêu:** Render từng shot từ shot list của Claude thành video clip 5–15 giây.

**Bước:**
1. **Lấy shot list từ Claude** (Stage 3 output) — mỗi shot có đủ 5 trường Director's Schema

2. **Với mỗi shot, mở Veo 3.1 trong Google Flow:**
   - Upload 2–3 reference images từ Character Reference Sheet (SOP-2)
   - Paste shot prompt vào text field
   - Chọn duration: 5s / 8s / 15s tùy độ phức tạp cảnh
   - Generate

3. **Review từng clip — Approve/Reject checklist:**

   | Tiêu chí | Approve ✅ | Reject ❌ |
   |---|---|---|
   | Nhân vật | Giống reference sheet | Hình dạng/màu khác |
   | Action | Đúng với script | Sai chuyển động |
   | Camera | Đúng góc quay | Sai framing |
   | Chất lượng | Mượt, không artifact | Glitch, blur, deform |
   | Timing | Vừa đủ cho narrator | Quá nhanh/chậm |

4. **Nếu Reject:**
   - Thử regenerate 2–3 lần trước khi sửa prompt
   - Nếu vẫn fail: điều chỉnh prompt (đơn giản hóa action, thay đổi góc camera)
   - Ghi note vào shot list: `regenerated x3, changed camera from close-up to medium`

5. **Lưu approved clips:**
   - Download → `episodes/<slug>/video/raw/shot-01.mp4`, `shot-02.mp4`...
   - Chỉ giữ file approved, xóa rejected

---

### SOP-4: Quality Review Trước Khi Edit

**Mục tiêu:** Đảm bảo toàn bộ raw clips đủ chất lượng trước khi vào DaVinci.

**Checklist per tập:**
- [ ] Tất cả shots đã có clip approved
- [ ] Character nhất quán xuyên suốt (không bị "drift" style)
- [ ] Không có clip nào dưới 5 giây
- [ ] Tổng thời lượng raw clips ≥ 5 phút (đủ để edit thành 5–10 phút với B-roll)
- [ ] ElevenLabs audio đã render xong (VI + EN)
- [ ] Suno music đã chọn track

---

### SOP-5: DaVinci Resolve — Final Assembly

**Mục tiêu:** Ghép clips + audio thành phim hoàn chỉnh.

**Setup:**
- Timeline: 1920×1080 (YouTube) và 1080×1920 (TikTok) — tạo 2 timeline riêng
- FPS: 24fps (cinematic feel)
- Color space: Rec.709

**Bước assembly:**
1. Import tất cả `video/raw/shot-*.mp4` → sắp xếp theo thứ tự shot list
2. Import audio: ElevenLabs voice (VI) + Suno music
3. Sync voice với video — mỗi clip khớp với đoạn narrator tương ứng
4. Add music track: volume -18dB dưới voice
5. Add captions: dùng DaVinci subtitle tool
   - Track 1: Tiếng Việt (burn-in hoặc SRT)
   - Track 2: Tiếng Anh (SRT cho YouTube CC)
6. Add transitions: cut thẳng (không dùng dissolve quá nhiều)
7. Color grade nhẹ: tăng contrast, giữ whiteboard background thuần trắng

**Export:**
| Output | Settings |
|---|---|
| YouTube | MP4, H.264, 1080p, 8Mbps |
| YouTube thumbnail | Frame export PNG, 1280×720 |
| TikTok | MP4, H.264, 1080×1920, 60s cut |

---

### SOP-6: Publish

**YouTube:**
1. Upload → chọn "Not listed" trước
2. Điền title: `[Tiếng Việt] / [English title]`
3. Description: tóm tắt + chapters (timestamp) + link sách nguồn
4. Thêm chapters: `0:00 Intro`, `1:00 [Concept 1]`...
5. Thumbnail: screenshot người que + title text
6. Publish → Public

**TikTok:**
1. Upload 60s cut
2. Caption: hook sentence đầu tiên (câu hỏi gây tò mò)
3. Hashtags: `#KhoaHoc #Science #LearnScience #HocSinh #AI`
4. Post giờ vàng: 7–9pm giờ VN

---

## Tham Khảo

- [smixs/visual-skills](https://github.com/smixs/visual-skills) — cinematic dramaturgy + prompt syntax
- [wuwangzhang1216/DirectorSKILL](https://github.com/wuwangzhang1216/DirectorSKILL) — 13-step production workflow
- [aiworkflows.tools/workflows/short-film](https://aiworkflows.tools/workflows/short-film) — 9-tool workflow reference
- [breakoutlens.com/ai-short-films](https://breakoutlens.com/ai-short-films) — 150 tracked AI shorts, velocity data
