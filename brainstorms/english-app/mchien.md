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
- [x] [overview] Setup repo + folder structure ✅ pnpm workspaces · `/Users/admin/personal/english-app` · commit `f505b5e`
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
| Book ingestion + reader + flashcard MVP | `overview,backend,web` | **Phase 2 (full MVP)**: [`book-ingestion-mvp.md`](../../designs/english-app/book-ingestion-mvp.md) — full architecture + BullMQ async + Redis cache + hybrid popup/side-panel + flashcard SRS. **Phase 1 (library validation spike)**: [`book-ingestion-demo-tier1.md`](../../designs/english-app/book-ingestion-demo-tier1.md) — pure-frontend demo (pdf.js + tesseract.js + MyMemory + Free Dict + Web Speech). | — | **Phase 1a scaffold done** · commit `f505b5e`. **Phase 1 spike done** · branch `ai/demo-spike-book-ingestion` · 9 commits HEAD `5f2fb3b` · 39 tests passing (vitest) · `apps/demo-spike/` end-to-end working: drag-drop PDF → render + OCR fallback → select → floating popup translate+TTS+dict. | **VALIDATION.md** (5 ✅ auto / 1 ❌ / 5 ⏳ browser-manual): #1 pdf.js 100%, #2 render-speed 28ms Node, #6 MyMemory 19/20, #7 rate-limit 0 × 429, #9 IPA audio 96%, ❌ #8 Free Dict 24.5% top-100 / 83.3% content-only (coverage gaps + Cloudflare 429), ⏳ #3/#4/#5 OCR (needs scanned fixtures), ⏳ #10 TTS 3-browser, ⏳ #11 selection. **Critical**: Free Dictionary needs Wiktionary/offline fallback for Phase 2. | ⏳ **Phase 1 demo-spike shippable + 6/11 metrics measured. Phase 2 blocked until pending metrics #3/#4/#5/#10/#11 collected via browser demo + dev decides Free Dict replacement.** |
