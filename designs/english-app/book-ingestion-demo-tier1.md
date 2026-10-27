# Book Ingestion — Phase 1 Demo (Tier 1: Library Validation Spike)

> **Project**: english-app · personal
> **Phase**: 1 (spike, library validation only)
> **Parent design**: `./book-ingestion-mvp.md` (Phase 2 — full MVP)
> **Status**: Draft — pending implementation
> **Repo**: `/Users/admin/personal/english-app`

## 1. Mục đích

Spike demo **thuần frontend** để **đo thực tế** từng thư viện có đáp ứng yêu cầu Phase 2 không, trước khi commit effort lớn (~10–14 ngày) build full MVP.

Phase 1 là **throwaway-safe**: toàn bộ code nằm trong `apps/demo-spike/` workspace độc lập, không đụng vào scaffold 1a (`apps/backend`). Nếu validation ❌ cho library nào → document alternative + swap stack cho Phase 2 **trước khi** code production.

### Không phải mục đích

- ❌ Không build feature production
- ❌ Không có persistence (reload = reset)
- ❌ Không có flashcard / SRS / multi-book
- ❌ Không reuse ở Phase 2 ngoài **kết luận validation**

## 2. Validation checklist (deliverable Phase 1)

File `apps/demo-spike/VALIDATION.md` fill tay sau khi test, format sau:

| # | Library | Metric | Target | Measured | Verdict |
|---|---------|--------|--------|----------|---------|
| 1 | `pdfjs-dist` | Text layer extraction accuracy trên native PDF (Word export) | >95% words correct | — | ✅/❌ |
| 2 | `pdfjs-dist` | Render speed trên 50-page native PDF | <5s total | — | ✅/❌ |
| 3 | `tesseract.js` | OCR accuracy trên scanned EN 300dpi | >90% words correct | — | ✅/❌ |
| 4 | `tesseract.js` | OCR speed/page (web worker) | <3s/page | — | ✅/❌ |
| 5 | `tesseract.js` | OCR acceptable trên scanned 150dpi (low quality) | >75% words | — | ✅/❌ |
| 6 | MyMemory API | EN→VN translation quality (manual eval 20 sentences) | >80% acceptable | — | ✅/❌ |
| 7 | MyMemory API | Rate limit experience (free tier 1000 req/day) | Không hit 429 trong 1 session test | — | ✅/❌ |
| 8 | Free Dictionary API | Coverage 100 common English words | >90% có entry | — | ✅/❌ |
| 9 | Free Dictionary API | IPA + audio có đầy đủ | audio present >80% | — | ✅/❌ |
| 10 | Web Speech API | TTS quality EN (Chrome/Safari/Firefox) | Chấp nhận được 3 browser | — | ✅/❌ |
| 11 | `window.getSelection` + bbox overlay | Multi-line selection chính xác qua text layer | Precise selection | — | ✅/❌ |

### Done criteria

Phase 1 **DONE** khi:

1. ✅ Code demo chạy local, drag-drop PDF → select → popup hoạt động end-to-end
2. ✅ `VALIDATION.md` fill đủ 11 rows với số liệu thực đo
3. ✅ Verdict toàn ✅ → confirm stack hiện tại cho Phase 2
4. ⚠️ Verdict có ❌ → `VALIDATION.md` phải document alternative library + đề xuất swap cho Phase 2

## 3. Scope

### Có (in-scope)

- Drag-drop upload 1 file PDF
- Render PDF (both native + scanned auto-detect) in-browser
- OCR scanned PDF in-browser (Tesseract.js, web worker)
- Text overlay selectable trên page images
- `window.getSelection()` capture multi-word range
- Floating popup với translation + IPA (nếu có) + 🔊 TTS button
- Click 🔊 → Web Speech API `speechSynthesis.speak()`
- Click outside / Esc → close popup

### Không có (out-of-scope)

- Backend / BE proxy / BullMQ / Redis
- MongoDB persistence (dùng in-memory state React)
- Multi-book library / `/library` route
- Side-panel / hybrid popup (chỉ floating)
- Flashcard save / SRS / review flow
- Mobile responsive polish (desktop-only OK)
- Auth
- Native/scanned mixed PDF ưu tiên (handle được, nhưng không optimize)
- Caching translation (mỗi select hit API, chấp nhận cho demo)
- Error retry UI (báo lỗi text đơn giản là đủ)

## 4. Architecture

Pure client-side SPA:

```
┌──────────────────────────────────────────────────────┐
│ Browser (Vite dev server)                            │
│                                                      │
│  ┌──────────────┐    ┌──────────────────────────┐   │
│  │ <Dropzone/>  │───▶│ pdf.js render + extract  │   │
│  │  drag-drop   │    │ textLayer (per page)      │   │
│  └──────────────┘    └──────────┬───────────────┘   │
│                                 │                    │
│                        hasText? ├─ y ─▶ nativeBlocks │
│                                 │                    │
│                                 └─ n ─▶ tesseract.js │
│                                        (web worker)  │
│                                        → OCR blocks  │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │ <Reader/>: <canvas/> image + <Overlay/>     │    │
│  │  transparent <span/> per block (bbox pos)   │    │
│  └──────────────┬──────────────────────────────┘    │
│                 │ mouseup → window.getSelection()    │
│                 ▼                                    │
│  ┌─────────────────────────────────────────────┐    │
│  │ parallel fetch:                              │    │
│  │  - api.dictionaryapi.dev/.../word (if 1 wrd) │    │
│  │  - api.mymemory.translated.net?...&langpair=│    │
│  │    en|vi                                     │    │
│  └──────────────┬──────────────────────────────┘    │
│                 ▼                                    │
│  ┌─────────────────────────────────────────────┐    │
│  │ <Popup/>: translation + IPA + audio + 🔊    │    │
│  │  🔊 → window.speechSynthesis.speak(text)    │    │
│  └─────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

Không có server. Mọi state giữ trong React component (reload = reset).

## 5. File structure

```
/Users/admin/personal/english-app/
└── apps/
    ├── backend/                       # existing scaffold 1a, UNTOUCHED
    └── demo-spike/                    # NEW, Phase 1 spike
        ├── package.json
        ├── tsconfig.json
        ├── vite.config.ts
        ├── index.html
        ├── fixtures/                  # test PDFs for validation
        │   ├── native-small.pdf       # 2-page Word export
        │   ├── native-large.pdf       # 50-page e-book EN
        │   ├── scanned-good.pdf       # 2-page scan 300dpi
        │   ├── scanned-poor.pdf       # 2-page scan 150dpi, slight skew
        │   ├── mixed.pdf              # 1 native + 1 scanned
        │   └── words-100.txt          # 100 common EN words
        ├── VALIDATION.md              # fill-in deliverable
        └── src/
            ├── main.tsx
            ├── App.tsx                # root: dropzone + reader + popup
            ├── pdf/
            │   ├── render.ts          # pdf.js: renderPage(doc, pageNo) → canvas + textContent
            │   └── ocr.ts             # tesseract.js: ocrPage(canvas) → blocks[]
            ├── lookup/
            │   ├── dictionary.ts      # Free Dictionary API client
            │   ├── translate.ts       # MyMemory API client
            │   └── tts.ts             # speechSynthesis wrapper + voice selection
            ├── ui/
            │   ├── Dropzone.tsx
            │   ├── Reader.tsx         # paginated viewer
            │   ├── Overlay.tsx        # absolute positioned text spans
            │   └── Popup.tsx          # floating result card
            └── types.ts               # Block { bbox, text, source: 'native' | 'ocr' }
```

## 6. Data types (TypeScript)

```ts
// src/types.ts

export type Bbox = { x: number; y: number; w: number; h: number }; // normalized 0–1

export type Block = {
  bbox: Bbox;
  text: string;
  source: 'native' | 'ocr';
};

export type Page = {
  pageNo: number;
  width: number;        // canvas width px
  height: number;       // canvas height px
  canvas: HTMLCanvasElement;
  blocks: Block[];
  status: 'rendering' | 'ocr-pending' | 'ocr-processing' | 'ready' | 'failed';
};

export type DictEntry = {
  word: string;
  ipa?: string;
  audioUrl?: string;
  definitions: Array<{ pos: string; meaning: string; example?: string }>;
};

export type LookupResult = {
  input: string;
  isSingleWord: boolean;
  dict?: DictEntry;
  translation: string;
};
```

## 7. External APIs

### Free Dictionary API

- URL: `https://api.dictionaryapi.dev/api/v2/entries/en/<word>`
- Auth: none
- CORS: ✅ enabled
- Rate limit: không công bố, best-effort fair use
- Response: array of entries với phonetic/phonetics[].{text,audio} + meanings[].{partOfSpeech, definitions[].{definition,example}}

### MyMemory Translation API

- URL: `https://api.mymemory.translated.net/get?q=<text>&langpair=en|vi`
- Auth: none (free tier anonymous)
- CORS: ✅ enabled
- Rate limit: 1000 words/day anonymous, 50000 nếu add `&de=<email>`
- Response: `{ responseData: { translatedText }, matches: [...] }`

Note: nếu rate limit đau trong test → tạm thời add `&de=196phamminhchien@gmail.com` để lên 50K/day.

### Web Speech API

- `window.speechSynthesis.getVoices()` → chọn voice `lang.startsWith('en')` ưu tiên `en-US`
- `new SpeechSynthesisUtterance(text)` → `.voice = <chosen>; .rate = 1.0; .pitch = 1.0`
- `window.speechSynthesis.speak(utterance)`

## 8. Key implementation notes

### 8.1 pdf.js text layer extraction

```ts
import * as pdfjs from 'pdfjs-dist';
pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

const doc = await pdfjs.getDocument(arrayBuffer).promise;
const page = await doc.getPage(pageNo);
const viewport = page.getViewport({ scale: 1.5 });
const canvas = document.createElement('canvas');
canvas.width = viewport.width;
canvas.height = viewport.height;
await page.render({ canvasContext: canvas.getContext('2d')!, viewport }).promise;

const textContent = await page.getTextContent();
const hasNativeText = textContent.items.length > 0
  && textContent.items.some(i => 'str' in i && i.str.trim().length > 0);

const blocks: Block[] = hasNativeText
  ? textContent.items.map(item => ({
      source: 'native',
      text: 'str' in item ? item.str : '',
      bbox: computeBboxFromTransform(item, viewport),
    }))
  : await ocrPage(canvas); // tesseract fallback
```

### 8.2 tesseract.js OCR worker

```ts
import { createWorker, PSM } from 'tesseract.js';

const worker = await createWorker('eng');
await worker.setParameters({ tessedit_pageseg_mode: PSM.AUTO });

export async function ocrPage(canvas: HTMLCanvasElement): Promise<Block[]> {
  const { data } = await worker.recognize(canvas);
  return data.words.map(w => ({
    source: 'ocr',
    text: w.text,
    bbox: {
      x: w.bbox.x0 / canvas.width,
      y: w.bbox.y0 / canvas.height,
      w: (w.bbox.x1 - w.bbox.x0) / canvas.width,
      h: (w.bbox.y1 - w.bbox.y0) / canvas.height,
    },
  }));
}
```

### 8.3 Overlay text layer

Mỗi block → absolute positioned `<span>` trong suốt (color transparent) nhưng selectable. Container `<div position:relative>` chứa `<canvas>` + overlay `<div position:absolute>`.

```tsx
<div style={{ position: 'relative' }}>
  <canvas ref={canvasRef} />
  <div className="text-layer" style={{ position: 'absolute', inset: 0 }}>
    {page.blocks.map((b, i) => (
      <span
        key={i}
        style={{
          position: 'absolute',
          left: `${b.bbox.x * 100}%`,
          top: `${b.bbox.y * 100}%`,
          width: `${b.bbox.w * 100}%`,
          height: `${b.bbox.h * 100}%`,
          color: 'transparent',
          cursor: 'text',
          userSelect: 'text',
        }}
      >
        {b.text}
      </span>
    ))}
  </div>
</div>
```

### 8.4 Selection capture

```ts
useEffect(() => {
  const onMouseUp = () => {
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed) return;
    const text = sel.toString().trim();
    if (!text) return;
    const rect = sel.getRangeAt(0).getBoundingClientRect();
    setPopupAt({ x: rect.left, y: rect.bottom, text });
  };
  document.addEventListener('mouseup', onMouseUp);
  return () => document.removeEventListener('mouseup', onMouseUp);
}, []);
```

### 8.5 Lookup parallel fan-out

```ts
async function lookup(text: string): Promise<LookupResult> {
  const isSingleWord = !text.includes(' ') && /^[a-zA-Z-']+$/.test(text);
  const [dict, translation] = await Promise.all([
    isSingleWord ? fetchDictionary(text).catch(() => undefined) : Promise.resolve(undefined),
    fetchTranslate(text).catch(() => '(dịch không khả dụng)'),
  ]);
  return { input: text, isSingleWord, dict, translation };
}
```

## 9. Testing approach (Phase 1 relaxed)

Phase 1 ưu tiên **tốc độ demo** hơn test coverage. Cho phép relaxed TDD:

- **Smoke test** mỗi module (Vitest):
  - `pdf/render.ts` — load fixture `native-small.pdf`, expect 2 pages với blocks[]
  - `pdf/ocr.ts` — mock canvas, test block mapping shape
  - `lookup/dictionary.ts` — nock HTTP, test 1 từ có entry + 1 từ 404
  - `lookup/translate.ts` — nock, test parse response
- **Manual E2E**: dev tự test drag-drop → select → popup theo scenario trong `VALIDATION.md`.
- Không cần Playwright (overkill cho spike 1 ngày).

## 10. Risks & mitigation

| Risk | Mitigation |
|---|---|
| Tesseract.js load WASM lần đầu chậm (~5s) | Pre-init worker lúc app mount, show "Loading OCR engine..." splash |
| Free Dictionary 404 cho common words | Catch 404 → `dict: undefined`, UI vẫn show translation |
| MyMemory rate limit 429 giữa demo | Fallback: show cached last response hoặc "Rate limited, try again" |
| pdf.js worker require CDN hoặc self-host | Self-host `pdf.worker.min.js` trong `public/` để offline-friendly |
| Chrome TTS voices load async | Listen `voiceschanged` event trước khi pick voice |
| Scanned PDF 500MB OOM in-browser | Validation 1: giới hạn fixture <20MB cho spike. Phase 2 BE handle lớn |

## 11. Transition sang Phase 2

Khi Phase 1 done (VALIDATION.md complete):

- **All ✅** → Phase 2 scope = full MVP phase 1b trong `book-ingestion-mvp.md`, giữ stack: Tesseract.js + Free Dictionary + LibreTranslate (swap MyMemory→LibreTranslate self-host). BE proxy pattern + Redis cache + BullMQ.
- **Có ❌** → `VALIDATION.md` ghi alternative:
  - Tesseract fail accuracy → thử PaddleOCR WASM / docTR / fallback GCP Vision API (paid)
  - MyMemory fail quality → LibreTranslate self-host sớm trong Phase 2
  - Web Speech API fail Firefox → fallback ResponsiveVoice / Amazon Polly API
  - pdf.js text extraction fail → thử `pdf2htmlEX` server-side (Phase 2 only)

## 12. Phased delivery (within Phase 1)

| Step | Deliverable | Rough effort |
|---|---|---|
| 1.1 | pnpm workspace `apps/demo-spike` + Vite + React + TS scaffold | 1h |
| 1.2 | `pdf/render.ts` + fixture `native-small.pdf` smoke test | 2h |
| 1.3 | `pdf/ocr.ts` + fixture `scanned-good.pdf` smoke test | 2h |
| 1.4 | `<Reader/>` + `<Overlay/>` render page + selectable | 3h |
| 1.5 | `lookup/dictionary.ts` + `lookup/translate.ts` + `lookup/tts.ts` | 2h |
| 1.6 | `<Popup/>` + selection → fetch → render | 2h |
| 1.7 | Collect/prepare fixtures (`native-large`, `scanned-poor`, `mixed`) | 1h |
| 1.8 | Chạy test VALIDATION.md 11 metrics, fill số liệu + verdict | 2h |
| 1.9 | Document verdict + alternatives nếu cần | 1h |

**Total**: ~16h = **~2 ngày thực tế** (1.5 ngày code + 0.5 ngày validation).

## 13. Open questions

Không còn — scope lock ở các decisions brainstorm (gộp vào phase 1b parent, auto-detect PDF, dual-API call, floating popup only cho spike, no flashcard spike).

## 14. References

- Parent full MVP: `./book-ingestion-mvp.md`
- Brainstorm nguồn: `../../brainstorms/english-app/mchien.md` (TODO Book ingestion)
- Project rules: `../../brainstorms/english-app/CLAUDE.md`
- Git workflow: `../rules/forgejo-workflow.md`
- pdf.js: https://mozilla.github.io/pdf.js/
- tesseract.js: https://tesseract.projectnaptha.com/
- Free Dictionary API: https://dictionaryapi.dev/
- MyMemory API: https://mymemory.translated.net/doc/spec.php
- Web Speech API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API
