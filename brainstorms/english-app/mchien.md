# english-app · mchien — TODO cá nhân

> Brainstorm file của **mchien**. Mỗi TODO ghi scope rõ để AI load đúng grounding.
> Convention + HARD SAFETY RULE + rules xem `./CLAUDE.md`.

## Format TODO

```
- [ ] [<scope>] <nội dung ngắn gọn, 1 ý>
```

- `<scope>` ∈ `{backend, web, mongo, shared, infra, overview}`
- Multi scope → `[backend,mongo]` hoặc `[web,shared]`

## TODO (dev)

<!-- Dev fill ideas tự do ở đây. AI chạy pipeline khi TODO không có `[?]` ambiguous. -->

- [x] [overview] Chốt stack framework ✅: BE **Fastify + TS** (AI recommend) + FE **React + TS + Vite** (dev)
- [ ] [overview] Setup repo + folder structure (monorepo pnpm workspaces hay 2 repos riêng BE+FE?) — path `/Users/admin/personal/english-app`
- [ ] [overview,backend,web] **Book ingestion + reader + flashcard (MVP phase 1)**:
    - **Input**: tài liệu giấy scanned (ảnh/PDF nhiều trang)
    - **Pipeline**:
      1. User upload scan (ảnh JPG/PNG hoặc PDF) → BE lưu raw
      2. **OCR** extract text từng trang → giữ bounding box + reading order
      3. **Layout preservation** càng nhiều càng tốt (page break, paragraph, heading, image anchor)
      4. Store MongoDB: `Book {title, author, pages: [{pageNo, imageUrl, text, blocks: [{bbox, text, type}]}]}`
      5. Serve web reader
    - **UI web**:
      - Paginated reader (như Google Books) — hiển thị original scan + overlay text selectable
      - Click/select từ → popup phát âm (TTS) + definition + nút "Add to flashcard deck"
      - Flashcard deck list → SRS review (SM-2)
    - **Chốt tech** ✅:
      - OCR: **Tesseract.js** self-host (free, BE worker thread, parallel 4)
      - Layout: **L2 scan + text overlay** (bbox normalized 0-1, PDF-like)
      - TTS: **Web Speech API** client-side (zero cost, offline)
      - Dictionary: **Free Dictionary API** (IPA + audio + def EN) + **LibreTranslate** self-host (EN→VN)
      - Multi-book: **Library pattern** (`/library` + `/books/:id/read`)
      - Upload limit: **500MB PDF** / upload
      - Processing: **Async BullMQ + Redis** queue + socket.io progress
    - **Chốt business** ✅:
      - User model: **Single-user** (personal, mchien)
      - Storage: **Không giới hạn** (local filesystem)
      - Dictionary: **EN-VN với IPA phiên âm + audio** phát âm
      - Flashcard UI: **Mobile + desktop responsive** (swipe gesture mobile, keyboard shortcut desktop)
      - OCR fallback: **Phase 2 research** PaddleOCR / EasyOCR / docTR / GCP Vision (document trong design)

## Summary (AI)
<!-- AI điền ngay dưới TODO sau khi chạy pipeline. Dev không sửa tay. -->

| TODO | scope | design | openspecs | code | review | status |
|---|---|---|---|---|---|---|
| Book ingestion + reader + flashcard MVP | `overview,backend,web` | [`book-ingestion-mvp.md`](../../designs/english-app/book-ingestion-mvp.md) — architecture + data model + full tech stack locked (BE Fastify+TS, FE React+TS+Vite, Tesseract.js / L2 overlay / Web Speech API / Free Dictionary + LibreTranslate / BullMQ) + OCR fallback research phase 2 + phased delivery (1a→1d) | — | — (chờ dev confirm scaffold repo `/Users/admin/personal/english-app`) | — | 🧠 **design done, 100% decisions chốt. Ready scaffold phase 1a — chờ dev gõ "scaffold" / "start"** |
