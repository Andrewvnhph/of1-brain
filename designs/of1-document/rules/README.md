# of1-document rules — Project-specific

Rules áp **chỉ** cho project `of1-document` (repo `/Users/admin/OF1/forgejo/of1-platform/of1-document`).

**Shared rules** load trước từ `../../rules/*.md` (xem `../../rules/README.md` cho convention 2-layer).

## Status (phase 2)

**Of1-document dùng chung rules với of1-tms** — same stack (Spring Boot BE + React FE + Module Federation + `@of1-webui/lib`). Rule references trỏ thẳng sang TMS folder:

| Rule | Path |
|---|---|
| Backend (Spring/JPA/DDD) | `../../of1-tms/rules/backend.md` |
| Frontend (React/bs.*/VGrid) | `../../of1-tms/rules/frontend.md` |

**Lưu ý khi đọc TMS rules trong context document**:
- Replace `TMSDAOService` → `DocumentDAOService` (hoặc base class tương đương của document stack).
- Replace `tmsTransactionManager` → `documentTransactionManager` (hoặc tên bean document dùng).
- Replace `TMSBill` / `TMSEmployee` prefix → entity thực của document (`Document`, `DocumentSet`, ...).
- Pattern + architecture **identical**, chỉ naming layer khác.

## Khi document diverge khỏi TMS rules

Nếu document có convention đặc thù không áp cho TMS (vd S3 proxy chain, viewer stack, Office Online fallback):

1. Tạo file **override** riêng tại đây: `of1-document/rules/<topic>.md`.
2. Header file **phải có** section "**Diverges from of1-tms**: ..." để dev tương lai biết lý do split.
3. Pattern:
   ```markdown
   # Document Viewer Stack

   **Diverges from of1-tms rules**: TMS không có viewer stack generic; document cần
   convention riêng cho S3 bytes fetching, viewer toggle, Office Online fallback.

   ## Convention
   ...
   ```
4. Khi 2+ projects dùng convention tương tự → promote lên `../../rules/` (shared) + xoá project overrides.

## Future dự kiến có rule riêng

- `document-viewer-stack.md` — ExcelJS + SSF, viewer toggle, S3 proxy via `S3ToHttpStorageResourceFactory`.
- `s3-bytes-fetching.md` — Pattern tránh RPC `byte[]` JSON parse fail (`UEsDBB` issue), dùng viewUrl same-origin.
- Khi phát sinh → tạo file + reference trong `brainstorms/of1-document/CLAUDE.md` layer 2.
