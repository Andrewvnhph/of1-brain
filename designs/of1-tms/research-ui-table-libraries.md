# Research: UI Table Libraries

> **TODO**: Nghiên cứu thư viện bảng — aggregation, tree, copy/paste Excel, inline edit  
> **Status**: research done  
> **Date**: 2026-11-16

---

## 1. Hiện trạng VGrid

VGrid là **custom-built**, không wrap thư viện bên ngoài. Dùng `react-window` cho virtual scroll.

### Features hiện có ✅

| Feature | Trạng thái | Ghi chú |
|---------|-----------|---------|
| Aggregation view | ✅ Có | Multi-level, Sum/Avg function |
| Tree view | ✅ Có | Hierarchy + collapse/expand |
| Inline edit | ✅ Có | Per-field, có validator |
| Sorting | ✅ Có | Per-column, custom sorter |
| Filtering | ✅ Có | Per-column filter plugin |
| Frozen columns | ✅ Có | fixed-left, fixed-right |
| Virtual scroll | ✅ Có | react-window |
| DnD row | ✅ Có | @dnd-kit |
| Column resize | ✅ Có (partial) | `resizable` flag tồn tại trong FieldConfig |

### Features còn thiếu ❌

| Feature | Hiện trạng |
|---------|-----------|
| Copy/paste như Excel | ❌ Không — clipboard util (`ObjUtil.copyToClipboard`) tồn tại nhưng chưa wire vào grid |
| Export Excel/CSV | ❌ Không — `exceljs` + `xlsx` có sẵn trong of1-document nhưng chưa tích hợp vào VGrid |
| Multi-column sort | ❌ Không |
| Column reorder (drag) | ❌ Không |
| Row pinning (top/bottom) | ❌ Không |
| Global search | ❌ Không (chỉ có column-level filter) |

---

## 2. Candidate Libraries

### 2.1 AG Grid Community (ag-grid-react)

| Tiêu chí | Đánh giá |
|---------|---------|
| Aggregation | ✅ Group + aggregate built-in |
| Tree data | ✅ Hierarchical rows |
| Copy/paste | ✅ Native Ctrl+C/V (cả cell lẫn range) |
| Inline edit | ✅ Cell editors |
| Column resize | ✅ |
| Export Excel | ⚠️ Enterprise only (CSV free) |
| License | MIT (Community) / Paid (Enterprise) |
| Bundle size | ~700KB–1MB |
| React 18 | ✅ |
| **Rủi ro** | Community thiếu Excel export; Enterprise tốn phí (~$1800/dev/năm) |

### 2.2 TanStack Table v8

| Tiêu chí | Đánh giá |
|---------|---------|
| Aggregation | ✅ Plugin |
| Tree data | ✅ |
| Copy/paste | ❌ Headless — tự implement |
| Inline edit | ❌ Headless — tự implement |
| License | MIT |
| Bundle size | ~15KB (headless) |
| **Rủi ro** | Headless = phải tự build toàn bộ UI. Với OF1 component system sẽ mất nhiều công. Không phù hợp thay thế VGrid. |

### 2.3 Handsontable

| Tiêu chí | Đánh giá |
|---------|---------|
| Aggregation | ⚠️ Có nhưng hạn chế |
| Tree data | ✅ Nested rows |
| Copy/paste | ✅ **Best-in-class** — native Ctrl+C/V, range select, paste từ Excel |
| Inline edit | ✅ |
| Export Excel | ✅ (Pro feature) |
| License | **Non-commercial free, commercial PAID** |
| Bundle size | ~500KB |
| **Rủi ro** | License — dự án thương mại cần trả phí. Aggregation yếu hơn AG Grid. |

### 2.4 React Data Grid (adazzle/react-data-grid)

| Tiêu chí | Đánh giá |
|---------|---------|
| Aggregation | ✅ Row grouping + summaries |
| Tree data | ⚠️ Limited |
| Copy/paste | ✅ Range copy/paste |
| Inline edit | ✅ |
| Export Excel | ❌ Không built-in |
| License | MIT |
| Bundle size | ~200KB |
| React 18 | ✅ |
| **Rủi ro** | Community nhỏ hơn AG Grid. Tree view yếu. |

### 2.5 Tabulator (react-tabulator)

| Tiêu chí | Đánh giá |
|---------|---------|
| Aggregation | ✅ |
| Tree data | ✅ |
| Copy/paste | ✅ Clipboard module |
| Inline edit | ✅ |
| Export | ✅ CSV, JSON, XLSX (via SheetJS) |
| License | MIT |
| Bundle size | ~400KB |
| **Rủi ro** | Wrapper react-tabulator không official. Vanilla JS core — ít React-idiomatic. |

---

## 3. So sánh tổng hợp

| | VGrid (hiện tại) | AG Grid CE | TanStack | Handsontable | react-data-grid | Tabulator |
|--|--|--|--|--|--|--|
| Aggregation | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| Tree | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Copy/paste | ❌ | ✅ | ❌ | ✅✅ | ✅ | ✅ |
| Inline edit | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ |
| Excel export | ❌ | ⚠️ Enterprise | ❌ | ⚠️ Pro | ❌ | ✅ |
| Column resize | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| License | MIT | MIT/Paid | MIT | Dual | MIT | MIT |
| Tích hợp OF1 | ✅ Sâu | Cần build | Cần build | Cần build | Cần build | Cần build |

---

## 4. Phân tích

### Lý do không thay thế VGrid toàn bộ

VGrid được tích hợp sâu vào OF1 ecosystem:
- `entity.DbEntityList` + `entity.DbEntityListPlugin` wrap VGrid
- `VGridConfig` là interface xuyên suốt toàn bộ TMS UI
- Thay thế = rewrite hàng chục màn hình

### Hướng đề xuất: Extend VGrid + chọn 1 lib cho use-case đặc biệt

**Option A — Extend VGrid** (dev modify `of1-webui`):
- Copy/paste: wire `ObjUtil.copyToClipboard` vào grid, add keyboard handler Ctrl+C cho selected range
- Export Excel: integrate `exceljs` (đã có trong of1-document) vào VGrid toolbar action
- Chi phí: thấp, không thêm dependency mới
- Phù hợp 80% use-case

**Option B — Dùng AG Grid Community cho màn hình cần Excel-like**:
- Thêm AG Grid CE song song VGrid, chỉ dùng cho các màn hình cần copy/paste range
- Ví dụ: Pricing table, reconcile sheet
- Chi phí: trung bình, cần build wrapper component riêng

**Option C — Dùng react-data-grid cho màn hình cụ thể**:
- MIT license, nhẹ hơn AG Grid
- Copy/paste + inline edit tốt
- Phù hợp cho màn hình dạng spreadsheet thuần

---

## 5. Recommendation

| Priority | Hành động |
|---------|----------|
| **Ngắn hạn** | Extend VGrid: add copy/paste + Excel export — ít rủi ro, không phá existing code |
| **Trung hạn** | Nếu cần range selection phức tạp (multi-cell, formula): pilot AG Grid CE trên 1 màn hình (vd Pricing batch) |
| **Không làm** | TanStack Table (headless, tốn công) · Handsontable (license) |

### Copy/paste plan cụ thể (extend VGrid)

1. Add `Ctrl+C` keyboard handler trên selected rows/cells → `ObjUtil.copyToClipboard(tsvString)` (tab-separated = paste được vào Excel)
2. Add toolbar button "Export Excel" → gọi `exceljs` generate file từ current data + VGridConfig field definitions
3. Implement trong `of1-webui` → expose qua `VGridActionConfig` hoặc `VGridConfig.onCopy`

---

## 6. Nguồn / References

- VGrid source: `of1-webui/src/wbootstrap/grid/`
- Clipboard util: `of1-webui/src/util/common.tsx` → `ObjUtil.copyToClipboard`
- Excel libs: `of1-document` → `exceljs@4.4.0`, `xlsx@0.18.5`
- AG Grid: https://ag-grid.com/react-data-grid/ (Community = MIT)
- react-data-grid: https://github.com/adazzle/react-data-grid (MIT)
- Tabulator: https://tabulator.info/ (MIT)
