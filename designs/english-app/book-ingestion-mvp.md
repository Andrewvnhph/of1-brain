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

### OCR engine ✅ CHỐT: Tesseract.js self-host

| Engine | Free | Accuracy English | Layout | Note |
|---|---|---|---|---|
| **✅ Tesseract.js** (self-host) | ✅ | 85-90% in sách printed clear | Weak (chỉ text + basic bbox) | Node native, run worker thread, chậm nhưng free. **MVP CHỐT.** |
| Google Vision API | $1.5/1000 pages | 95%+ | Tốt (document detection endpoint cho structured) | Phase 2 upgrade khi accuracy không đủ |
| Azure Computer Vision Read | $1/1000 pages | 95%+ | Tốt | — |
| AWS Textract | $1.5/1000 pages | 95%+ | Rất tốt cho tables/forms | Overkill |

Code behind interface để swap sau nếu cần:
```typescript
interface OcrProvider {
  recognize(imageBuf: Buffer): Promise<PageOcrResult>;
}
class TesseractProvider implements OcrProvider { ... }  // phase 1
// class GoogleVisionProvider — phase 2 nếu dev feedback accuracy không đủ
```

**Tesseract config khuyến nghị cho sách English**:
- `lang: 'eng'`, optionally `+vie` nếu sách có từ vựng Việt chú thích
- `tessedit_pageseg_mode: 1` (auto segmentation with OSD) — tốt cho sách multi-paragraph
- Preprocess với `sharp`: grayscale + normalize + rotate nếu lệch (OSD detect)
- Worker thread parallelism: 4 pages concurrent trên máy dev 8-core

### Layout fidelity level ✅ CHỐT: L2 scan + text overlay

- (L1) Text-only — không chọn.
- **✅ (L2) Scan + text overlay** — hiển thị ảnh scan làm background + text layer transparent position theo bbox từ OCR → user vẫn thấy sách như scan nhưng select được text. Pattern giống PDF có text layer.
- (L3) Reconstruct HTML — overkill cho MVP.

Reader component skeleton:
```tsx
<PageView style={{ position: 'relative', width: page.width, height: page.height }}>
  <img src={page.scanUrl} style={{ width: '100%', display: 'block' }} />
  {page.blocks.map((b, i) => (
    <span
      key={i}
      style={{
        position: 'absolute',
        left: `${b.bbox.x * 100}%`, top: `${b.bbox.y * 100}%`,
        width: `${b.bbox.w * 100}%`, height: `${b.bbox.h * 100}%`,
        color: 'transparent',
        userSelect: 'text',
        cursor: 'text',
      }}
      onMouseUp={onTextSelected}
    >
      {b.text}
    </span>
  ))}
</PageView>
```
`bbox` normalized 0-1 (ratio) → responsive khi parent resize (zoom in/out).

### TTS ✅ CHỐT: Web Speech API client-side

| Option | Free | Quality | Latency |
|---|---|---|---|
| **✅ Web Speech API** `window.speechSynthesis` | ✅ | Phụ thuộc OS/browser voice | <100ms (local). **MVP CHỐT.** |
| Google Cloud TTS | $4/1M chars | Rất tự nhiên (WaveNet) | ~500ms. Phase 2 upgrade. |
| Azure Neural TTS | $16/1M chars | Rất tự nhiên | — |
| ElevenLabs | $5/mo cho 30k chars | Nhất, có emotion | — |

**Implementation**:
```typescript
function speak(text: string, lang: string = 'en-US', rate: number = 0.9) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang;
  utterance.rate = rate;  // 0.9 = chậm hơn chút cho learner
  // Chọn voice English native (ưu tiên 'en-US' hoặc 'en-GB')
  const voices = window.speechSynthesis.getVoices();
  const voice = voices.find(v => v.lang === lang && v.localService)
             || voices.find(v => v.lang.startsWith('en'));
  if (voice) utterance.voice = voice;
  window.speechSynthesis.speak(utterance);
}
```

**Lưu ý**:
- `getVoices()` async load, phải wait `voiceschanged` event lần đầu.
- Chrome Mac/Windows có voice offline, Linux may không có → fallback cloud TTS phase 2.
- Zero cost + offline, không cần BE proxy.

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

**Chốt từ brainstorm**:
- **OCR**: ✅ Tesseract.js self-host (worker thread, parallel 4)
- **Layout**: ✅ L2 scan + text overlay (bbox normalized 0-1)
- **TTS**: ✅ Web Speech API client-side

**Chốt trong MVP design**:
- **File storage**: Local filesystem (phase 1 personal use) → S3/MinIO phase 2 (prod).
- **Queue**: Redis + BullMQ.
- **Realtime**: socket.io (progress streaming).
- **File upload**: Multer (Express) hoặc @fastify/multipart.
- **PDF handling**: `pdf-lib` (split pages) + `pdf2pic` (convert page → image cho OCR).
- **Image preprocessing**: `sharp` grayscale + normalize + deskew (boost OCR accuracy).

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
