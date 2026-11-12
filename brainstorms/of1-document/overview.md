# of1-document · Overview — TODO closed timeline

> **File owner**: AI (sinh/cập nhật tự động). Dev không sửa tay.
> **Purpose**: Theo dõi mỗi TODO đã đóng — nội dung ngắn gọn, branch, PR, thời gian thực hiện (từ commit đầu tới merge). Mới nhất lên đầu.
> **Rule**: xem `../CLAUDE.md` section "Overview on close" — mỗi khi 1 TODO được mark `[x]` → AI append (hoặc update) 1 row ở đây.

## Convention

- **Thời gian** = ngày commit đầu nhánh `ai/<slug>` → ngày merge PR vào `develop`. Nếu không có branch (incremental patch) → ghi khoảng ngày đầu-cuối commit.
- **Scope** = tag module gốc TODO (`[<module>]`).
- **Outcome** = PR# + state (merged / open / abandoned).
- **Chi tiết kỹ thuật** vẫn ở `mchien.md` Summary row. File này chỉ index.

## Closed TODOs

| # | TODO (tóm tắt) | Scope | Branch · PR | Thời gian | Duration | Outcome |
|---|---|---|---|---|---|---|
| 2 | **Liquibase + credential cleanup + gradle centralize** — `DocumentJpaConfiguration @Primary`; master changelog + `document_log` test changeset; move hardcoded credentials sang `${env.*}`; centralize dep versions + Nexus repo; `release/build.gradle` add `opencsv:5.9` + `commons-text:1.11.0` (fix Liquibase `NoClassDefFoundError`); `env.sh` template; remove of1-platform from tools.sh build chain | `build,security,db` | `ai/liquibase-integration` · merge `1cf941d02c` (no PR — direct merge) | 2026-11-12 → 2026-11-12 | **~1 ngày** (12 commits) | ✅ merged → develop |
| 1 | **Xlsx readonly viewer thay Office Online** — ExcelJS parse style + SheetJS SSF numFmt + React renderer; fidelity ~90%; multi-sheet tabs, zoom, drag range selection, copy clipboard, download; Univer prototype rollback | `+ui,xlsx,s3` | `ai/xlsx-viewer` · merged | — | — | ✅ merged → develop |

## Pending TODOs

| # | TODO | Scope | Status |
|---|---|---|---|
| — | S3DocumentView toggle 2 viewer options (Office Online / Self-host) | `+ui,xlsx,docx,s3` | ⏳ open |

## Reference

- Chi tiết implementation + Rule mới sinh ra từ mỗi TODO: xem `mchien.md` Summary.
- Branches `ai/*` sau khi merged → cleanup theo rule `../../designs/rules/forgejo-workflow.md` §"Cleanup".
- Rules của1-document reuse TMS: `../../designs/of1-tms/rules/{backend,frontend}.md`.
