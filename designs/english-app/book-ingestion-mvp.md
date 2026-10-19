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

### Dictionary ✅ CHỐT: EN-VN combo (Free Dictionary API + Translation API)

Dev yêu cầu EN-VN với **phát âm + phiên âm IPA** → cần kết hợp 2 nguồn (không API free nào cover cả 2):

**Primary — English definition + phonetic + audio**:
| API | Free | Coverage | Notes |
|---|---|---|---|
| **✅ Free Dictionary API** `api.dictionaryapi.dev` | ✅ | Wiktionary-based | IPA phonetic (`/həˈloʊ/`) + audio URL + definitions + synonyms. **MVP CHỐT.** |
| Merriam-Webster | ✅ dev 1000/day | Excellent | Backup nếu Free Dictionary rate limited |

**Secondary — EN → VN translation**:
| Option | Free | Quality | Notes |
|---|---|---|---|
| **✅ LibreTranslate** self-host | ✅ unlimited | Decent cho từ đơn + phrase ngắn | Docker container, run local. **MVP CHỐT.** |
| Google Translate API | $20/1M chars (có free tier) | Best | Paid, cần GCP |
| MyMemory API | ✅ 1000 words/day anonymous, 50000 với email | OK cho từ đơn | HTTP GET, không cần SDK |
| Lingvanex | $x paid | Good | — |

**Flow popup word khi click**:
```
1. User click word "hello"
2. BE lookup cache MongoDB `dictionary_cache { word, data, expiresAt }`
3. Cache miss → parallel fetch:
   a. api.dictionaryapi.dev/api/v2/entries/en/hello → phonetic /həˈloʊ/, audio URL, definitions EN
   b. LibreTranslate local → "xin chào, chào"
4. Merge response + cache 7 ngày
5. Return client:
   {
     word: 'hello',
     phonetic: '/həˈloʊ/',
     audioUrl: 'https://ssl.gstatic.com/...hello.mp3',
     definitionsEn: [{partOfSpeech, meanings[]}],
     translationsVi: ['xin chào', 'chào'],
   }
6. Client popup render + button:
   - "Play audio" (ưu tiên audioUrl từ API, fallback Web Speech API)
   - "+ Add to flashcard" (lưu word + phonetic + VN translation + context sentence)
```

**Cache strategy**: `dictionary_cache` TTL 7 ngày, key = `lowercase(word)`. Sách phổ biến các từ sẽ cache hit >90% sau tuần đầu.

### Processing async queue

**BullMQ + Redis** cho OCR job (có thể chạy vài phút cho sách 300 trang):
- User upload → BE enqueue job → return `{bookId, status: 'processing'}` ngay
- Worker process từng trang (parallel 4 concurrent) → update `pages` collection + emit progress qua Redis pub/sub
- Web client subscribe qua WebSocket (socket.io) → progress bar realtime
- Job xong → book status `ready` → notify user

## Technology stack (locked)

**Chốt từ brainstorm với dev**:
- **OCR**: ✅ Tesseract.js self-host (worker thread, parallel 4)
- **Layout**: ✅ L2 scan + text overlay (bbox normalized 0-1)
- **TTS**: ✅ Web Speech API client-side
- **Dictionary**: ✅ Free Dictionary API (IPA + audio + def EN) + LibreTranslate self-host (EN→VN)
- **Multi-book**: ✅ Library pattern (`/library` list + `/books/:id/read` reader)
- **Upload limit**: ✅ 500MB PDF per upload
- **Processing**: ✅ Async BullMQ + Redis queue + socket.io progress stream
- **User model**: ✅ Single-user (personal, auth tối thiểu — JWT local hoặc skip auth MVP)
- **Storage limit**: ✅ Không giới hạn (local filesystem, dev tự manage disk)
- **Flashcard UI**: ✅ Responsive mobile + desktop (swipe gesture mobile, keyboard shortcut desktop)

**Chốt FE framework** (từ dev):
- **React.js + TypeScript + Vite** — SPA client-side rendering, HMR fast, không cần SSR phase MVP.

**Chốt BE framework** (AI recommend, dev delegate):
- **Fastify + TypeScript** — Node.js framework modern:
  - 2x faster hơn Express (benchmarks), handle upload PDF 500MB tốt hơn
  - Native TypeScript support (type-safe route handlers + schema)
  - Built-in JSON Schema validation (zod via `@fastify/type-provider-typebox` hoặc `@fastify/type-provider-zod`)
  - Plugin system elegant (`fastify-plugin` encapsulation)
  - `@fastify/multipart` cho upload (streaming parser, no buffer all)
  - `@fastify/websocket` cho socket.io compatible layer
  - Ít boilerplate hơn NestJS, modern hơn Express
- Alternatives rejected:
  - **Express**: deprecated 4.x async handling, không TS native, overused
  - **NestJS**: overkill cho personal MVP, Angular-like DI boilerplate heavy, learning curve
- Dev có thể revert nếu prefer tool khác, pattern code generic đủ.

**Chốt repo path** (từ dev):
- `/Users/admin/personal/english-app` — chưa tồn tại, cần `mkdir -p` + `git init` khi scaffold phase 1a.

**Chốt infra trong MVP design**:
- **File storage**: Local filesystem (phase 1 personal use) → S3/MinIO phase 2 (nếu cần cloud).
- **Queue**: Redis + BullMQ.
- **Realtime**: socket.io (progress streaming).
- **File upload**: Multer (Express) hoặc @fastify/multipart.
- **PDF handling**: `pdf-lib` (split pages) + `pdf2pic` (convert page → image cho OCR).
- **Image preprocessing**: `sharp` grayscale + normalize + deskew (boost OCR accuracy).

## OCR fallback research (phase 2)

Khi dev feedback Tesseract.js accuracy không đủ cho sách khó (handwritten, poor scan, complex layout), các alternatives cần research:

| Engine | License | Lang | Pros | Cons |
|---|---|---|---|---|
| **PaddleOCR** (PP-OCRv4) | Apache 2.0 | 80+ incl. EN+VN | DL-based, SOTA accuracy ~95%+, layout parser tốt (table + figure detect) | Python-only, cần spawn child process từ Node, docker container |
| **EasyOCR** | Apache 2.0 | 80+ | Simple API, PyTorch backend | Chậm hơn Paddle, cần GPU cho tốc độ production |
| **docTR** | Apache 2.0 | EN primary (có cộng đồng port) | Hugging Face ecosystem, modern transformers architecture | Model lớn (~500MB download), cold start chậm |
| **Google Vision API** | Paid $1.5/1000 pages | 50+ | 95%+ accuracy, zero infra | Paid, cần GCP account + billing |
| **Azure Computer Vision Read** | Paid $1/1000 pages | 50+ | 95%+ accuracy | Cần Azure account |

**Strategy swap engine**:
```typescript
interface OcrProvider {
  recognize(imageBuf: Buffer): Promise<PageOcrResult>;
  readonly name: 'tesseract' | 'paddle' | 'gcp-vision' | 'azure-read';
}
```

Phase 1 chỉ `TesseractProvider`. Phase 2 thêm `PaddleOcrProvider` (spawn Python child process qua docker exec) hoặc `GoogleVisionProvider` tùy accuracy requirement.

**Decision tree phase 2**:
- Accuracy acceptable + sách printed thường → giữ Tesseract.
- Sách printed nhưng Tesseract < 90% → PaddleOCR (free, best balance).
- Sách handwritten / historical → Google Vision (paid, worth cho use case khó).

## Open questions ✅ ALL RESOLVED

- ✅ **5.1 Multi-user**: Single-user (personal, mchien) → auth tối thiểu hoặc skip MVP.
- ✅ **5.2 Storage limit**: Không giới hạn (local filesystem, dev tự manage).
- ✅ **5.3 Dictionary EN-VN**: Free Dictionary API (IPA + audio + definition EN) + LibreTranslate self-host (EN→VN translation). Response flow + cache strategy trong section Dictionary ở trên.
- ✅ **5.4 Flashcard review UI**: Mobile + desktop dual support — responsive layout, swipe gesture mobile (left=again, right=good, up=easy) + keyboard shortcut desktop (space=flip, 1-4=quality rating).
- ✅ **5.5 OCR fallback**: Research phase 2 với 4 candidates ở trên, interface `OcrProvider` chuẩn bị swap sẵn.

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

<!-- Open questions moved to section "Open questions ✅ ALL RESOLVED" ở trên. -->

## Pending ✅ ALL RESOLVED

Zero blockers còn lại. Dev chốt → scaffold phase 1a sẵn sàng:
- ✅ Framework BE: **Fastify + TypeScript** (AI recommend, dev delegate)
- ✅ Framework FE: **React.js + TypeScript + Vite** (dev chốt)
- ✅ Repo path: `/Users/admin/personal/english-app` (chưa tồn tại, `mkdir -p` khi scaffold)

**Framework FE detail**: Vite + `@vitejs/plugin-react` + `vite-tsconfig-paths` + env `.env.local` cho API URL.
