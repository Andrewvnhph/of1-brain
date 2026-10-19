# Book Ingestion + Reader + Flashcard (MVP phase 1)

## Mục đích

Chuyển sách tiếng Anh giấy (scanned) thành phiên bản web interactive:
- User upload ảnh/PDF scan sách
- Hệ thống OCR + extract text giữ layout
- Hiển thị web reader paginated với scan gốc + text selectable overlay
- Click từ → phát âm (TTS) + lookup định nghĩa + thêm vào flashcard deck
- SRS flashcard review (spaced repetition SM-2) cho các từ user đã lưu

**Not goals (phase 1)**: formula/math rendering, syntax highlight code, chapter TOC auto-detect, multi-language books, EPUB/MOBI import, user annotations/highlights.

## User flow

```
1. Upload scan
   ├─ PDF multipage, hoặc
   └─ List JPG/PNG (user tự order)
   ↓
2. OCR processing (async queue)
   ├─ Trích text từng trang + bounding boxes
   ├─ Detect reading order (paragraph flow)
   └─ Progress bar realtime (socket.io / SSE)
   ↓
3. Book saved MongoDB
   ├─ Metadata (title, author, user)
   └─ Pages[] với scan URL + text blocks
   ↓
4. Reader web
   ├─ Thumbnail nav side panel
   ├─ Page view: scan image bg + text layer transparent on top
   └─ User select word / phrase
   ↓
5. Word popup
   ├─ Phát âm (TTS)
   ├─ Dictionary definition
   └─ [+ Add to deck] button
   ↓
6. Flashcard deck
   ├─ Front: word, Back: definition + context sentence (từ page)
   └─ Review schedule theo SM-2
```

## Architecture

```
┌─────────────────────┐
│  Web (React.js)     │
│  - Upload UI        │
│  - Reader paginated │
│  - Flashcard review │
└──────────┬──────────┘
           │ REST + WebSocket (progress)
           ↓
┌─────────────────────────────────┐
│  BE (Node.js)                   │
│  - Upload endpoint              │
│  - Enqueue OCR job (BullMQ)     │
│  - Serve book/page/deck         │
│  - TTS proxy (nếu dùng cloud)   │
│  - Dictionary proxy             │
└──────────┬────────────┬──────────┘
           ↓            ↓
    ┌──────────┐  ┌─────────────┐
    │ Redis    │  │ MongoDB     │
    │ (queue)  │  │ books/      │
    └──────────┘  │ pages/      │
           ↓      │ decks/      │
    ┌──────────┐  │ cards/      │
    │ Worker   │  │ reviews/    │
    │ OCR task │  │ users       │
    │ Tesseract│  └─────────────┘
    │ or API   │
    └──────────┘
```

## Data model (MongoDB)

### `users`
```typescript
{ _id, email, name, createdAt, locale }
```

### `books`
```typescript
{
  _id, userId,
  title, author, cover?: url,
  status: 'uploading' | 'processing' | 'ready' | 'failed',
  pageCount: number,
  createdAt, updatedAt,
}
```

### `pages`
```typescript
{
  _id, bookId, pageNo,
  scanUrl: string,          // signed URL hoặc path S3/local
  width: number, height: number,  // pixel của scan
  text: string,             // full page text concatenated (search index)
  blocks: [{
    bbox: [x, y, w, h],     // normalized 0-1 hoặc pixel
    text: string,
    type: 'paragraph' | 'heading' | 'list-item' | 'caption',
    confidence: number,     // OCR confidence
  }],
  ocrEngine: 'tesseract' | 'gcp-vision' | '...',
  ocrDoneAt: Date,
}
```

### `decks`
```typescript
{ _id, userId, name, bookId?, createdAt }
```

### `cards`
```typescript
{
  _id, deckId, userId,
  front: string,              // từ
  back: string,               // định nghĩa + example
  context?: {
    bookId, pageNo,
    sentence: string,          // câu chứa từ (từ page)
  },
  phonetic?: string,
  audioUrl?: string,          // cache TTS
  // SM-2 fields:
  easiness: number,            // 2.5 default
  interval: number,            // days
  repetition: number,
  nextReviewAt: Date,
  createdAt,
}
```

### `reviews`
```typescript
{ _id, cardId, userId, quality: 0-5, reviewedAt }
```

## Key technical decisions

### OCR engine lựa chọn

| Engine | Free | Accuracy English | Layout | Note |
|---|---|---|---|---|
| **Tesseract.js** (self-host) | ✅ | 85-90% in sách printed clear | Weak (chỉ text + basic bbox) | Node native, run worker thread, chậm nhưng free |
| Google Vision API | $1.5/1000 pages | 95%+ | Tốt (document detection endpoint cho structured) | Paid, cần GCP account |
| Azure Computer Vision Read | $1/1000 pages | 95%+ | Tốt | Paid, cần Azure |
| AWS Textract | $1.5/1000 pages | 95%+ | Rất tốt cho tables/forms | Overkill cho sách |

**Khuyến nghị MVP**: Tesseract.js self-host trước (free, control). Nếu accuracy không đủ → swap sang Google Vision (change provider mỗi engine). Code behind interface:
```typescript
interface OcrProvider {
  recognize(imageBuf: Buffer): Promise<PageOcrResult>;
}
class TesseractProvider implements OcrProvider { ... }
class GoogleVisionProvider implements OcrProvider { ... }
```

### Layout fidelity level

**3 options**:
- **(L1) Text-only**: concat text từng paragraph, bỏ layout → viewer render markdown-like. Đơn giản nhất, nhưng mất feel sách gốc.
- **(L2) Scan + text overlay** ⭐ **MVP khuyến nghị**: hiển thị ảnh scan làm background + text layer transparent position theo bbox từ OCR → user vẫn thấy sách như scan nhưng select được text. Pattern giống PDF có text layer.
- **(L3) Reconstruct HTML**: parse text blocks → render HTML tương đương (font estimate, column detect, image anchor). Fidelity cao nhưng OCR structured output cần (Google Vision document detect) + logic phức tạp.

**Phase 1**: L2. Reader component:
```tsx
<PageView>
  <img src={page.scanUrl} />
  {page.blocks.map(b => (
    <span style={{position: 'absolute', left: b.bbox.x, top: b.bbox.y, width: b.w, height: b.h,
                   color: 'transparent', userSelect: 'text'}}>
      {b.text}
    </span>
  ))}
</PageView>
```

### TTS

| Option | Free | Quality | Latency |
|---|---|---|---|
| **Web Speech API** `window.speechSynthesis` | ✅ | Phụ thuộc OS/browser voice | <100ms (local) |
| Google Cloud TTS | $4/1M chars | Rất tự nhiên (WaveNet) | ~500ms |
| Azure Neural TTS | $16/1M chars | Rất tự nhiên | ~500ms |
| ElevenLabs | $5/mo cho 30k chars | Nhất, có emotion | ~1s |

**MVP**: Web Speech API client-side (zero cost, works offline). Cache audio blob trong IndexedDB nếu cần replay. Upgrade cloud TTS phase 2 khi user feedback voice quality thấp.

### Dictionary

| API | Free | Coverage | Rate limit |
|---|---|---|---|
| **Free Dictionary API** `api.dictionaryapi.dev` | ✅ | Decent (Wiktionary-based) | Không rõ, không key |
| Merriam-Webster | ✅ (dev tier) 1000/day | Excellent | Need API key, dev-only |
| Oxford Dictionaries | $x paid | Best | Paid |
| WordsAPI | $x paid | Rất đầy đủ (synonyms, examples) | Paid |

**MVP**: Free Dictionary API. BE proxy cache 24h vào MongoDB `dictionary_cache` tránh rate limit.

### Processing async queue

**BullMQ + Redis** cho OCR job (có thể chạy vài phút cho sách 300 trang):
- User upload → BE enqueue job → return `{bookId, status: 'processing'}` ngay
- Worker process từng trang (parallel 4 concurrent) → update `pages` collection + emit progress qua Redis pub/sub
- Web client subscribe qua WebSocket (socket.io) → progress bar realtime
- Job xong → book status `ready` → notify user

## Technology stack (locked)

Trong context MVP này, chốt thêm (ngoài stack chung của1-app):
- **File storage**: Local filesystem (phase 1 personal use) → S3/MinIO phase 2 (prod).
- **Queue**: Redis + BullMQ.
- **Realtime**: socket.io (progress streaming).
- **File upload**: Multer (Express) hoặc @fastify/multipart.
- **PDF handling**: `pdf-lib` (split pages) + `pdf2pic` (convert page → image cho OCR).
- **Image preprocessing** (optional, boost OCR accuracy): `sharp` grayscale + contrast + deskew.

## Phased delivery

**Phase 1a — Upload + OCR pipeline** (2-3 ngày code):
- Upload endpoint
- BullMQ worker + Tesseract.js
- Progress stream
- `books` + `pages` CRUD

**Phase 1b — Reader web** (2-3 ngày):
- Thumbnail navigation
- Page view scan + text overlay
- Word selection + popup

**Phase 1c — Dictionary + TTS popup** (1-2 ngày):
- Dictionary proxy
- Web Speech API hook
- Context sentence extraction

**Phase 1d — Flashcard deck + SRS** (2-3 ngày):
- Deck CRUD
- Card SM-2 scheduling
- Review UI (next card, quality rating 0-5)

**Phase 2 (sau)**: cloud OCR option, cloud TTS, highlights/annotations, EPUB import, mobile app, PDF export of flashcards, social decks sharing.

## Open questions

- [ ] Multi-user hay single-user (chỉ mchien dùng)? Ảnh hưởng auth complexity.
- [ ] Book storage limit? (1 user upload 10 sách x 500MB = 5GB — local disk OK, cloud phase 2)
- [ ] Dictionary coverage English-English hay English-Vietnamese? (học viên Việt có thể prefer EN-VN translation)
- [ ] Flashcard review UI: desktop web vs mobile responsive — swipe gesture tap for mobile reviewer?
- [ ] OCR quality fallback khi Tesseract không đủ: user manual edit text per page? Hoặc re-run cloud OCR?
