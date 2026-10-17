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
- [ ] [overview,+ui] `of1-tms`: migrate imports `@of1-webui/platform` → `@of1-dev01/core` (partial). **Research kết quả**: 16 files impacted, chia 2 nhóm. **Nhóm A** (12 files, migrate hoàn toàn): dùng `DOCUMENT_PLUGIN_REGISTRY` / `UIApiPlugin` / `UIApiPluginManager` / `ApiResponse` → có sẵn trong `@of1-dev01/core` (`plugin.DOCUMENT_PLUGIN_REGISTRY` hoặc named export). **Nhóm B** (4 files, không migrate được): `UITMSPartnerBaseList`, `UIVehicleList`, `UIVehicleFleet` dùng `BBRefAccessToken` + `UITMSEmployeeList` dùng `module/hrm.employee` → chỉ có trong `@of1-webui/platform`, chưa port sang core. **Deliverable**: migrate nhóm A → giảm import platform (nhưng không drop dep hoàn toàn vì nhóm B vẫn cần). Reference: `of1-document/webui/document/src/Init.tsx` dùng `plugin.DOCUMENT_PLUGIN_REGISTRY`. Follow-up: port `BBRefAccessToken` + `employee` sang `@of1-dev01/core` ở phase sau để drop dep hoàn toàn
- [ ] [overview,+ui] `of1-document`: lib document viewer file Excel (xlsx) — thay thế Office Web Viewer (`view.officeapps.live.com`) hay bị stuck "fetching your file". Research options SheetJS / luckysheet / x-spreadsheet / handsontable + build embeddable component dùng chung cho TMS (bill attachment preview, imported history xlsx) và các app OF1 khác
- [x] [+ui,bill] Chứng từ đính kèm: nghiên cứu khả năng kéo-thả từ Outlook mà không cần tải file về máy
- [x] [+ui,bill] Phase 1 — Add drag-drop handler cho `UIMessageForm` attachment area (FE only, 1 file, dropped file → `attB64DataMap`, không BE/DB change) ✅ merged PR #424
- [x] [+ui,bill] Phase 1.1 — Add paste (Ctrl+V) attachment cho `UIMessageForm` — Outlook drag-drop ko reliable (virtual-file CFSTR_FILEDESCRIPTOR + dropEffect negotiation phức tạp qua test), chuyển sang paste. Code drag-drop research đã clean up (-210/+10 lines). ✅ merged PR #425
- [ ] [+ui,bill,vendor] Import bản kê cước vận chuyển (Excel) vào `TMSBill` — sample file: `CƯỚC & CHI HỘ BS TUẦN 4 THÁNG 09.2026-Thầu phụ Đức Toàn Phát.xlsx`
    - [x] B1 — Parse Excel BE + display raw rows FE (CHƯA save TMSBill)
    - [x] B2 — Fill FE click + custom header mapping input + required filter + Next convert → UIMappedList VGrid breadcrumb preview
    - [x] B2.1 — Sum values khi nhiều Excel col map cùng TMSBill field (vd CVC + LẠCH HUYỆN + PHÁT SINH → fee)
    - [x] B2.2 — Cache config (fillCols + requiredCols + colMapping) xuống DB `tms_xlsx_template` (CompanyEntity) — dropdown load inline + auto-save on Next convert
    - [x] B3 — Apply mapped records vào TMSBill: find by (label=fileNo + forwarder.containerNo), 1 match → updateFixedPayment/updateExtraPayment với B_TRUCK + "Domestic Trucking Fee"; status column trong UIMappedList
    - [x] B3.1 — Fallback match by fileNo (status=MATCH_BY_FILE_NO + needReview) khi containerNo mismatch
    - [x] B3.2 — Compare panel 1/3 màn hình dưới mapped preview: UITMSBillList `type='selector' + onSelect` auto apply vào bill user click (status=MATCHED_MANUAL)
    - [x] B4 — TMSXlsxImport entity: snapshot mapped list + importStatus sau Apply. "Imported history" button trong `TMSBillListPageControl` Tools popover → list → click View → breadcrumb UIMappedList (re-render status column từ initialStatus)
    - [x] B5 — Fix merged cell POI (SỐ XE bị mất value): pre-compute merged region map, lookup khi cell blank → nhận anchor value
    - [x] B6 — Detect numeric field trong UIMappedList → `field.dataType = 'double'` cho sort/filter đúng kiểu
    - [x] B7 — Imported history → `UIImportedHistoryList` + `UIImportedHistoryListPlugin` (loadData gọi `listRecent`). Click `Tools > Imported history` → popup md minHeight 500, cols `View / Name / Time / Created By`. Click View → close popup + push breadcrumb preview (initialStatus seeded)
    - [x] B8 — Fake progress bar khi Apply manual match: common lib `UIFakeProgressBar.tsx` (`FakeProgressController` class + stateless component). Dùng trong compare panel header, phase labels (Chuẩn bị / Finding bill / Updating fees / Saving), ease-out 90% → BE respond jump 100% + autoCloseMs
    - [x] B8.1 — Fix remount storm: stable key compare panel (`select-tms-bill-row-${rowNumber}`) + `'overview'` thay vì `IDTracker.next()` — tránh UITMSBillList reload mỗi progress tick 100ms
    - [x] B9 — Save button cạnh Apply để chốt snapshot manual match vào Imported history (bên cạnh fire-and-forget auto-save sau Apply)
    - [x] B10 — Refactor notification dùng `.withEntityOpNotification(op, label, count?)` chained (3 cấp ưu tiên: chained → `appContext.addOSNotification` → `bs.notificationShow`). Rule mới `frontend.md` §3.4.3

## Summary (AI)
<!-- AI điền ngay dưới TODO sau khi chạy pipeline. Dev không sửa tay. -->

| TODO | module | design | openspecs | code | review | status |
|---|---|---|---|---|---|---|
| Nghiên cứu drag-drop attachment từ Outlook | `+ui,bill` | [`research-outlook-attachment-dragdrop.md`](../../designs/of1-tms/research-outlook-attachment-dragdrop.md) | — | — | — | ✅ **done** |
| Phase 1 — Drag-drop handler cho UIMessageForm attachment | `+ui,bill` | [`bill-attachment-phase1.md`](../../designs/of1-tms/bill-attachment-phase1.md) | — | branch `ai/attachment-outlook-dragdrop` · commit `ddfe2c06d2` · UIMessage.tsx +71/-10 | tsc clean | ✅ **merged PR #424 → develop** |
| Phase 1.1 — Paste (Ctrl+V) attachment cho UIMessageForm | `+ui,bill` | — (follow-up patch, no new spec) | — | branch `ai/attachment-dragdrop-body-zone` · 9 commits `14dc56a → d096865081` · merge commit `70fc301955` · final net: +58/-73 lines (sau cleanup) · research refs: [MS Q&A 455366](https://learn.microsoft.com/en-us/answers/questions/455366) · [DataTables fix](https://datatables.net/forums/discussion/60533) | tsc clean; paste verified work | ✅ **merged PR #425 → develop** · local branch cleaned |
| Import bản kê cước Excel B1+B2 — parse + display + fill + map + preview mapped | `+ui,bill,vendor` | [`bill-import-excel.md`](../../designs/of1-tms/bill-import-excel.md) | — | branch `ai/bill-import-excel-b1` merged · BE core generic + FE UIRawRowList + UIMappedList · Rule mới: frontend.md §3.3.9-11, §3.4.0-2 | manual verified | ✅ **merged → develop** · local branch cleaned |
| B2.1 — Sum values khi nhiều Excel col map cùng TMSBill field | `+ui,bill` | — (incremental, no spec) | branch standalone `ai/bill-import-excel-b2-sum-dup-cols` commit `997251ca96` — **đã merge vào** branch tổng `ai/bill-import-excel-template` qua commit `21706b3f82` (sum + concat ' + ' fallback, dedupe tmsFieldKeys qua Set) | manual test | ⏳ **pushed trong branch tổng, có thể drop standalone branch** |
| B2.2 + B3..B10 — Template persistence + Apply vào TMSBill + Compare panel + Imported history (UIList + popup) + merged POI fix + numeric dataType + fake progress bar + notification refactor | `+ui,bill,core` | — (incremental, entity + CRUD + mapping flow + UX polish) | branch `ai/bill-import-excel-template` · HEAD `ba3db243ac` · [compare](https://git.datatp.cloud/of1-tms/of1-tms/compare/develop...ai/bill-import-excel-template) · **BE**: `TMSXlsxTemplate` + `TMSXlsxImport` entity (CompanyEntity, sub-pkg `.repository`) · `TMSBillRepository.findByLabelAndContainerNo` + `findByCompanyAndLabel` (join forwarder) · `TMSBillLogic.applyExcelImportRow` 2 phase + billId override (manual match) + `applyFees` helper · `TMSBillService.applyExcelImport` TransactionTemplate REQUIRES_NEW per-row · `ExcelImportLogic.buildMergedCellValues` fix merged POI (SỐ XE) · **FE**: dropdown BBSelectField template inline (auto-select most-recent + auto fill + select-by-required on load) · auto-save/update template on Next convert · "Apply to TMSBill" + "Save" button với status column (OK / MATCHED_MANUAL / MATCH_BY_FILE_NO / NOT_FOUND / AMBIGUOUS / INVALID / ERROR) · compare panel 25% dưới mapped preview dùng `UITMSBillList type='selector' + onSelect` → manual match · common lib `UIFakeProgressBar` + `FakeProgressController` cho fake progress bar reusable · `UIImportedHistoryList` + Plugin pattern, popup md minHeight 500, click View → breadcrumb preview seeded initialStatus · `showImportedHistory` exported function trong Tools popover `TMSBillListPageControl` → snapshot sau Apply (rowsJson lưu `{mapped, tmsFieldKeys, mappingSummary, importStatus}`) · auto-detect numeric field → `dataType='double'` · Import mở qua `addPageContent` breadcrumb · Stable key compare panel chặn remount storm · Notification refactor dùng `.withEntityOpNotification` chained · **Rules mới**: backend.md §2.6 (Repository package + `@EnableJpaRepositories.basePackages`), §2.7 (`MapObject.getXxx(key, def)` HARD RULE), frontend.md §3.4.3 (notification 3 cấp ưu tiên) | manual test | ⏳ **pushed, chờ dev merge PR** |
