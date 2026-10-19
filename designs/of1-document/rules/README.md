# of1-document rules — Project-specific

Rules áp **chỉ** cho project `of1-document` (repo `/Users/admin/OF1/forgejo/of1-platform/of1-document`).

**Shared rules** load trước từ `../../rules/*.md` (xem `../../rules/README.md` cho convention 2-layer).

## Status (phase 1)

**Chưa có rule riêng** — hiện tham chiếu rules của `of1-tms` (`../of1-tms/rules/{backend,frontend}.md`) vì stack giống (Spring Boot BE + React FE + Module Federation).

**Dự kiến tạo khi cần**:
- `document-viewer-pattern.md` — Convention viewer stack (ExcelJS + SSF, viewer toggle 2 option, S3 proxy approach, bytes-via-RPC pitfall `UEsDBB` JSON parse fail)
- `s3-storage.md` — Pattern dùng `S3ToHttpStorageResourceFactory.createHttpStorageResource` + viewUrl same-origin
- `backend.md` override — nếu BE của1-document có convention khác TMS (vd document plugin registry, không có TMSDAOService layer)

## Nguyên tắc

Khi rule TMS không áp dụng cho document:
1. Copy từ TMS → `of1-document/rules/<file>.md`, chỉnh sửa phần divergent.
2. Note trong file header "**Diverges from of1-tms**: ..." để dev tương lai biết lý do split.
3. Nếu convention promote lên shared sau — delete file này + update `rules/README.md`.
