# of1-tms · Overview — TODO closed timeline

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
| 12 | Add `TMSBillBookingForwarder` @Embeddable vào TMSBill + wire vào BFSOne flow (Beetrans mapper lookup `TMSPartner.getByCode(hcm/han/hph/dad)` thay hardcoded SHIPPER_MAP → set bill.bookingForwarder; Selling template override PartnerID từ bookingForwarder bfsOneCode). Non-scope: FE picker, validation strict, chain intermediary | `bill,core,ops,integration` | `ai/bill-booking-forwarder` · PR pending | 2026-10-27 → 2026-10-27 | **<1 ngày** (4 commits) | ⏳ pushed, chờ dev merge. **Prereq**: TMSPartner có records code=hcm/han/hph/dad + bfsOneCode đúng |
| 11 | UI Create HBL BFSOne flow full (Phase 1 popup Preview + Phase 2 breadcrumb Post Save; `pushHbl` single-request + `showResultDialog` dialog; mapper plugin + fee lookup col Ext.; bug fixes BBSelectPermissionCompanies cache + readOnly bypass ghép) | `+ui,integration,bill,ops` | `ai/ui-create-hbl-bfsone` · **PR #433** | 2026-10-23 → 2026-10-26 | **~3 ngày** (~55 commits) | ✅ merged → develop |
| 10 | BFSOne `insertHawb` API — plugin pattern `BFSOneHawbMapper` + Beetran group 3 codes (DAD/HCM/HPH) + HWBNO formula `{label}/{maVP}/{MM}{STT:04d}` + `TMSSeqService` atomic sequence | `integration,bill` | `ai/bfsone-insert-hawb` · **PR #431** | 2026-10-19 → 2026-10-20 | **~1 ngày** (7 commits) | ✅ merged → develop |
| 9 | Migrate imports `@of1-webui/platform` → `@of1-dev01/core` + clone `BBRefAccessToken` local — 18 files, drop dep | `overview,+ui` | `ai/migrate-platform-to-core` · **PR #428** | 2026-10-16 → 2026-10-19 | **~3 ngày** (2 commits) | ✅ merged → develop |
| 8 | Import bản kê cước Excel B2.2 + B3..B10 — template persistence + Apply vào TMSBill + Compare panel + Imported history + merged POI fix + numeric dataType + fake progress bar + notification refactor | `+ui,bill,core` | `ai/bill-import-excel-template` · **PR #427 (10-16) + PR #429 (10-19)** | 2026-10-15 → 2026-10-19 | **~4 ngày** | ✅ merged → develop |
| 7 | Import bản kê cước Excel B1 + B2 — parse Excel BE + display raw rows FE + fill click + custom header mapping + preview mapped VGrid | `+ui,bill,vendor` | `ai/bill-import-excel-b1` · **PR #426** | 2026-10-14 → 2026-10-15 | **~1 ngày** | ✅ merged → develop |
| 6 | Phase 1.1 — Paste (Ctrl+V) attachment cho `UIMessageForm` (chuyển từ drag-drop Outlook virtual-file vì không reliable) | `+ui,bill` | `ai/attachment-dragdrop-body-zone` · **PR #425** | ~2026-10-14 | **~1 ngày** (9 commits + cleanup) | ✅ merged → develop |
| 5 | Phase 1 — Drag-drop handler cho `UIMessageForm` attachment area (FE only, 1 file) | `+ui,bill` | `ai/attachment-outlook-dragdrop` · **PR #424** | ~2026-10-14 | **~1 ngày** | ✅ merged → develop |
| 4 | Nghiên cứu khả năng kéo-thả attachment từ Outlook mà không cần tải file về máy | `+ui,bill` | — (research only) | — | — | ✅ research done → design doc |

## Pending TODOs

| # | TODO | Scope | Status |
|---|---|---|---|
| — | (none) — tất cả TODO hiện tại đã closed. Thêm mới ở `mchien.md` section `## TODO (dev)`. |  |  |

## Reference

- Chi tiết implementation + Rule mới sinh ra từ mỗi TODO: xem `mchien.md` Summary.
- Branches `ai/*` sau khi merged → cleanup theo rule `../../designs/rules/forgejo-workflow.md` §"Cleanup".
- Rules TMS: `../../designs/of1-tms/rules/{backend,frontend,forgejo-workflow}.md`.
