# of1-document — grounding bắt buộc trước pipeline

> File này được Claude Code tự động load khi làm việc trong thư mục `brainstorms/of1-document/`.
> AI đọc trước khi chạy bất kỳ phase nào (design/openspec/code) của pipeline cho `of1-document`.

## Project scope

`of1-document` là lib document management + viewer share dùng cho các app OF1 (TMS, CRM, platform, ...). Repo path `/Users/admin/OF1/forgejo/of1-platform/of1-document`.

Nhiệm vụ chính:
- Viewer readonly cho các file office (xlsx, docx, pdf, img) qua S3DocumentView
- Preview inline trong app host (TMS bill attachment, CRM document, platform admin)
- Module federation shared qua `@of1-webui/document`

## Cấu trúc file trong thư mục này (per-user)

- **Brainstorm tổ chức theo user**: mỗi dev 1 file `<user>.md` (vd `mchien.md`).
- TODO ghi với tag module/scope: `- [ ] [<scope>] <nội dung>`.
- Scope ∈ `{xlsx, docx, pdf, img, s3, accounting, inv, fee, tms, receipt, overview, +ui}`.
- Match pattern của `brainstorms/of1-tms/` — cùng workflow + Forgejo rules.

## ⚠️ HARD SAFETY RULE — Repo scope

Giống `brainstorms/of1-tms/CLAUDE.md`:

| Repo | Path | Scope |
|------|------|-------|
| **`of1-document`** | `/Users/admin/OF1/forgejo/of1-platform/of1-document` | **WRITABLE** — commit nhánh `ai/<slug>` off develop, KHÔNG push develop |
| `of1-tms` | (writable khác, không touch khi làm of1-document) | — |
| `of1-platform` / `of1-core` / `of1-webui` | **READ-ONLY** — grounding only |

**Pre-commit safety**: luôn `git branch --show-current | grep -qE '^ai/'` fail-fast trước commit.

## Rules bắt buộc (load trước — 2 layer)

Load theo thứ tự: **shared** rồi **project-specific**. Project-specific override shared khi conflict.

**Layer 1 — Shared rules** (`../../designs/rules/`):
- **Git (Forgejo)**: `../../designs/rules/forgejo-workflow.md` — git workflow áp cho mọi project.

**Layer 2 — Of1-document rules** (`../../designs/of1-document/rules/`):
- Hiện trạng (phase 1): **chưa có rule riêng** → tham chiếu TMS rules sau đây:
  - `../../designs/of1-tms/rules/backend.md` — Spring/JPA (nếu BE document cùng stack)
  - `../../designs/of1-tms/rules/frontend.md` — React class components, bs.BB*, scroll viewer, notification 3 cấp
- Khi document có pattern đặc thù → tạo `../../designs/of1-document/rules/<file>.md` + note "**Diverges from of1-tms**: ..." để track lineage.

> **Convention 2-layer**: `../../designs/rules/README.md` — khi nào promote rule shared vs giữ project-specific.

## Convention đặc biệt cho of1-document

- **BackendConfig endpoint**: `/platform/plugin/document` + `/rest/v1.0.0` + `/api`
- **Imports từ `@of1-dev01/core`** (đã migrate xong, không dùng `@of1-webui/platform`)
  - `plugin.DOCUMENT_PLUGIN_REGISTRY` thay `module.security.DOCUMENT_PLUGIN_REGISTRY`
  - `UIApiPlugin`, `ApiResponse`, `UIApiPluginManager` named imports
- **FE architecture**: React class components + `@of1-webui/lib` (`bs`, `grid`, `entity`, `app`, `util`, ...)
- **Document viewers**: readonly + fetch bytes qua `S3ToHttpStorageResourceFactory.createHttpStorageResource` → viewUrl same-origin
- **Xlsx viewer stack**: ExcelJS + SheetJS SSF (xem `webui/document/src/app/document/xlsx/README.md` cho chi tiết)

## Trình tự pipeline cho TODO document

Khi gặp TODO chưa checked trong `brainstorms/of1-document/<user>.md`:

1. **Load context** (bắt buộc):
   - 3 rules TMS (ở `../../designs/of1-tms/rules/`)
   - Parse scope tag → load design + spec tương ứng (nếu có)
2. **Design** → `../../designs/of1-document/<slug>.md`
3. **OpenSpec** → `/opsx:propose "<slug>"` (optional, chỉ khi feature lớn)
4. **Code** → nhánh `ai/<slug>` off develop
5. **Review** → tests + manual verify
6. **Commit + push** → tuân thủ pre-commit check (verify branch `ai/*`)
7. **Cleanup** → sau dev merge PR, chạy cleanup combo (xem `../../designs/rules/forgejo-workflow.md` §Cleanup)
