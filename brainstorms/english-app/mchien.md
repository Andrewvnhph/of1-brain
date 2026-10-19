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

- [ ] [overview] Chốt stack framework: Express/Fastify/NestJS? Vite/Next.js?
- [ ] [overview] Setup repo + folder structure (monorepo pnpm workspaces hay 2 repos riêng BE+FE?)
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
    - **Chốt** ✅:
      - OCR: **Tesseract.js** self-host (free, BE worker thread, parallel 4)
      - Layout: **L2 scan + text overlay** (bbox normalized 0-1, PDF-like)
      - TTS: **Web Speech API** client-side (zero cost, offline)
    - **Pending** (chờ dev chốt tiếp):
      - [ ] Dictionary API: Free Dictionary API / Merriam-Webster / Oxford
      - [ ] Multi-book MVP vs 1-book-at-a-time (ảnh hưởng UI book list)
      - [ ] Upload size limit (sách 300 trang → ~500MB PDF?)
      - [ ] Processing: async queue BullMQ+Redis (recommend) hay sync với SSE progress

## Summary (AI)
<!-- AI điền ngay dưới TODO sau khi chạy pipeline. Dev không sửa tay. -->

| TODO | scope | design | openspecs | code | review | status |
|---|---|---|---|---|---|---|
| Book ingestion + reader + flashcard MVP | `overview,backend,web` | [`book-ingestion-mvp.md`](../../designs/english-app/book-ingestion-mvp.md) — architecture + data model + OCR/TTS/dictionary options + phased delivery (1a→1d) | — (chờ dev chốt pending decisions trước) | — (chờ repo setup) | — | 🧠 **brainstorm — design done, chờ dev chốt 7 pending decisions** |
