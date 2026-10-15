# of1-tms · mchien — TODO cá nhân

> Brainstorm file của **mchien** (`196phamminhchien`). Mỗi TODO phải ghi rõ **module ảnh hưởng** để AI tự load đúng grounding (`designs/of1-tms/<module>.md` + `openspec/specs/of1-tms/<module>/spec.md`).
> Convention + HARD SAFETY RULE (write/read-only scope) + rule backend/frontend/forgejo xem `./CLAUDE.md`.

## Format TODO

```
- [ ] [<module>] <nội dung ngắn gọn, 1 ý>
```

- `<module>` ∈ `{core, http, rpc, bill, fleet, vendor, ops, integration, notification, webhook}`
- Nhiều module cùng ảnh hưởng → ghi `[bill,vendor]` hoặc tách ra 2 TODO.
- TODO đụng frontend → thêm tag `[+ui]` hoặc chỉ dùng `[ui]`.
- TODO cross-cutting (không thuộc module nào) → `[overview]`.

## TODO (dev)
- [x] [+ui,bill] Chứng từ đính kèm: nghiên cứu khả năng kéo-thả từ Outlook mà không cần tải file về máy
- [x] [+ui,bill] Phase 1 — Add drag-drop handler cho `UIMessageForm` attachment area (FE only, 1 file, dropped file → `attB64DataMap`, không BE/DB change) ✅ merged PR #424
- [x] [+ui,bill] Phase 1.1 — Add paste (Ctrl+V) attachment cho `UIMessageForm` — Outlook drag-drop ko reliable (virtual-file CFSTR_FILEDESCRIPTOR + dropEffect negotiation phức tạp qua test), chuyển sang paste. Code drag-drop research đã clean up (-210/+10 lines). ✅ merged PR #425
- [ ] [+ui,bill,vendor] Import bản kê cước vận chuyển (Excel) vào `TMSBill` — sample file: `CƯỚC & CHI HỘ BS TUẦN 4 THÁNG 09.2026-Thầu phụ Đức Toàn Phát.xlsx`
    - [x] B1 — Parse Excel BE + display raw rows FE (CHƯA save TMSBill)
    - [x] B2 — Fill FE click + custom header mapping input + required filter + Next convert → UIMappedList VGrid breadcrumb preview
    - [x] B2.1 — Sum values khi nhiều Excel col map cùng TMSBill field (vd CVC + LẠCH HUYỆN + PHÁT SINH → fee)
    - [x] B2.2 — Cache config (fillCols + requiredCols + colMapping) xuống DB `tms_xlsx_template` (CompanyEntity) — dropdown load inline + auto-save on Next convert
    - [x] B3 — Apply mapped records vào TMSBill: find by (label=fileNo + forwarder.containerNo), 1 match → updateFixedPayment/updateExtraPayment với B_TRUCK + "Domestic Trucking Fee"; status column trong UIMappedList

## Summary (AI)
<!-- AI điền ngay dưới TODO sau khi chạy pipeline. Dev không sửa tay. -->

| TODO | module | design | openspecs | code | review | status |
|---|---|---|---|---|---|---|
| Nghiên cứu drag-drop attachment từ Outlook | `+ui,bill` | [`research-outlook-attachment-dragdrop.md`](../../designs/of1-tms/research-outlook-attachment-dragdrop.md) | — | — | — | ✅ **done** |
| Phase 1 — Drag-drop handler cho UIMessageForm attachment | `+ui,bill` | [`bill-attachment-phase1.md`](../../designs/of1-tms/bill-attachment-phase1.md) | — | branch `ai/attachment-outlook-dragdrop` · commit `ddfe2c06d2` · UIMessage.tsx +71/-10 | tsc clean | ✅ **merged PR #424 → develop** |
| Phase 1.1 — Paste (Ctrl+V) attachment cho UIMessageForm | `+ui,bill` | — (follow-up patch, no new spec) | — | branch `ai/attachment-dragdrop-body-zone` · 9 commits `14dc56a → d096865081` · merge commit `70fc301955` · final net: +58/-73 lines (sau cleanup) · research refs: [MS Q&A 455366](https://learn.microsoft.com/en-us/answers/questions/455366) · [DataTables fix](https://datatables.net/forums/discussion/60533) | tsc clean; paste verified work | ✅ **merged PR #425 → develop** · local branch cleaned |
| Import bản kê cước Excel B1+B2 — parse + display + fill + map + preview mapped | `+ui,bill,vendor` | [`bill-import-excel.md`](../../designs/of1-tms/bill-import-excel.md) | — | branch `ai/bill-import-excel-b1` merged · BE core generic + FE UIRawRowList + UIMappedList · Rule mới: frontend.md §3.3.9-11, §3.4.0-2 | manual verified | ✅ **merged → develop** · local branch cleaned |
| B2.1 — Sum values khi nhiều Excel col map cùng TMSBill field | `+ui,bill` | — (incremental, no spec) | branch standalone `ai/bill-import-excel-b2-sum-dup-cols` commit `997251ca96` — **đã merge vào** branch tổng `ai/bill-import-excel-template` qua commit `21706b3f82` (sum + concat ' + ' fallback, dedupe tmsFieldKeys qua Set) | manual test | ⏳ **pushed trong branch tổng, có thể drop standalone branch** |
| B2.2 + B3 — Template persistence + Apply mapped vào TMSBill | `+ui,bill,core` | — (incremental, entity + CRUD + mapping flow) | branch `ai/bill-import-excel-template` · HEAD `e3aa56547e` · [compare](https://git.datatp.cloud/of1-tms/of1-tms/compare/develop...ai/bill-import-excel-template) · **BE B2.2**: `TMSXlsxTemplate` entity + Repo (`<domain>.repository` sub-pkg) + Logic + Service (upsert by company+group+name, soft delete) · **BE B3**: `TMSBillRepository.findByLabelAndContainerNo` (join forwarder) + `TMSBillLogic.applyExcelImportRow` + `TMSBillService.applyExcelImport` (TransactionTemplate REQUIRES_NEW per-row) · **FE**: dropdown BBSelectField inline (auto-select most-recent, auto fill+select-by-required on load), auto-save/update on Next convert, "Apply to TMSBill" button với status column (✓ #billId / Not found / N matches / Invalid / Error) · **Rules mới**: backend.md §2.6 (Repository package convention + `@EnableJpaRepositories.basePackages`), §2.7 (`MapObject.getXxx(key, def)` HARD RULE) | manual test | ⏳ **pushed, chờ dev merge PR** |
