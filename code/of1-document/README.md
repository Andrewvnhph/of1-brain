# of1-document · Excel Viewer Demo (SheetJS)

Standalone HTML prove-of-concept cho lib viewer xlsx readonly, dùng SheetJS parse + render qua `XLSX.utils.sheet_to_html`.

## Chạy local

**Khuyến nghị — dùng `server.js`** (có CORS proxy tích hợp, Node 18+):

```bash
cd /Users/admin/OF1/forgejo/of1-platform/of1-brain/code/of1-document
node server.js
# → mở http://localhost:8765/
```

Server expose 2 endpoint:
- `/` serve `index.html`
- `/proxy?url=<xlsx-url>` fetch URL server-side + stream về client với header CORS `*` — bypass hoàn toàn CORS block khi BE storage chưa fix.

Checkbox **"Via proxy"** trong UI (checked mặc định) → wrap URL qua `/proxy?url=...`.

**Alternative — chỉ static (không proxy)**:
```bash
python3 -m http.server 8765
```
→ File picker vẫn hoạt động, "Load from URL" sẽ FAIL với URL CORS-block (uncheck "Via proxy" + chỉ dùng URL public có CORS).

## 2 cách test

### A — Local file (an toàn, không CORS)
Click **"Chọn file"** → pick 1 file `.xlsx` bất kỳ. Verify SheetJS parse + render multi-sheet tabs.

### B — Fetch URL (test CORS)
URL mặc định điền sẵn: `https://beelogistics.cloud/storage/s3/46ACIDIUP27YQYPDRAQ3WSHSGPINJGCSMLQ5JXTWPWYA4575DZP74NU66VICXZSAVH3OJRKAVTDRUUXBVV4F7TWQYYGC4SWSRP6JRMQQSUPDEHH3KZA5MJONSZNBNHSLV6GXZPCUVNBWJOYBTLACYJX3AJCCTDRCPBTBWNQ2D2LV5QXZGARQ====`

Click **Load from URL** →
- **Nếu BE enable CORS** (`Access-Control-Allow-Origin: *` cho endpoint `/storage/s3/*`) → sheet render OK, elapsedMs < 1s cho file ~2MB.
- **Nếu chưa enable CORS** → fetch throws `TypeError: Failed to fetch` (browser block cross-origin). Status bar hiển thị FAIL + console log chi tiết.

Test với URL public khác (confirm pipeline SheetJS hoạt động):
```
https://sheetjs.com/pres.xlsx
```
→ Load từ URL này phải thành công vì SheetJS CDN cho phép CORS.

## Expected behavior

- Parse ~2MB xlsx trong **200–500 ms** (SheetJS CE).
- Multi-sheet navigation qua tab buttons.
- Readonly table render với border + alternating row color.
- Merged cells preserved (SheetJS tự hiểu `!merges`).
- `sheet_to_html` default output giữ format cơ bản (bold header của xlsx, number align right).

## Giới hạn demo hiện tại

- **CORS**: không có proxy fallback (option B từ brainstorm). Fix BE enable CORS hoặc proxy qua BE TMS khi integrate production.
- **Styling fidelity**: `sheet_to_html` không render font/color/fill từ xlsx. Nếu cần → dùng SheetJS `sheet_to_json` + VGrid custom render; hoặc swap sang Univer cho Excel-exact fidelity.
- **Large files** (> 20 MB): có thể freeze main thread. Production cần Web Worker (SheetJS hỗ trợ `xlsx.worker.js`).
- **Formulas**: SheetJS parse formula được nhưng không re-evaluate — hiển thị cached value từ xlsx.

## Next step (của1-document lib)

1. Verify demo chạy OK với local file picker.
2. Fix BE CORS → test URL B.
3. Convert demo thành React component `UIXlsxViewer` reusable:
   - Props: `url` hoặc `blob` + `sheetIndex?`
   - Dùng `grid.VGridConfig` của OF1 thay `sheet_to_html` để tận dụng sort/filter/column resize.
   - Loading state + error state với `UIFakeProgressBar` (common lib đã có).
4. Package thành workspace `of1-document` riêng, publish `@of1/document` cho TMS + CRM + các app khác consume.
