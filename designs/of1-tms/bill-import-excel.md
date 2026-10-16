# Design — Import bản kê cước vận chuyển (Excel) vào TMSBill

> **Status**: Design — chờ dev duyệt scope + trả lời open questions trước khi implement.
> **TODO**: `brainstorms/of1-tms/mchien.md` — `[+ui,bill,vendor] Import bản kê cước vận chuyển (Excel) vào TMSBill`
> **Sample file**: `/Users/admin/Downloads/CƯỚC & CHI HỘ BS TUẦN 4 THÁNG 09.2026-Thầu phụ Đức Toàn Phát.xlsx`

## 1. Scope + độ phức tạp

**Scope lớn** — nhiều layer:

| Layer | Trạng thái hiện tại | Cần build |
|-------|---------------------|-----------|
| BE Excel reader | ❌ Chưa có (POI chỉ dùng export) | Thêm Excel parse service |
| BE Import service | ❌ Chưa có | `TMSBillExcelImportLogic` + `Service` |
| BE Bulk create | ✅ `TMSBillLogic.saveTMSBillModels()` exists | Reuse |
| BE Vendor lookup by name | ❌ Chưa có | Thêm `findByLabel()` repo method |
| FE Upload UI | ❌ Chưa có | Button upload + preview dialog |
| FE Preview/mapping | ❌ Chưa có | Grid preview + error display |

**Ước lượng**: ~5-7 ngày code (BE 2-3, FE 2-3, test + polish 1-2).

## 2. Cấu trúc Excel sample

### 2 sheet
- **Sheet 1 `26.09-30.09`** — bản kê chính (import target)
- **Sheet 2 `DSHĐ CẦN ĐIỀU CHỈNH`** — danh sách HĐ cần điều chỉnh (bỏ qua, không import)

### Sheet 1 layout
- **R1-R8**: metadata header (tên công ty, địa chỉ, MST, email, bảng giá 20'/40', danh sách sale)
- **R9-R10**: column headers (merged nhiều row)
- **R11+**: data rows
- **Max col 37** nhưng data chính chỉ ở col A-U (1-21)
- **Max row 845** nhưng data thật ~56 rows → 12 bills (nhiều row empty padding)

### Column mapping đề xuất

| Col | Label Excel | TMSBill field |
|-----|-------------|---------------|
| A | SỐ JOB (vd `BEE26.09.198`) | `code`? hoặc `label`? **cần dev clarify** |
| B | Ngày tháng | `bookingDate` |
| C | SỐ TK + TÊN CTY | map sang `TMSBillCustomer{taxCode, name}` qua `TMSPartner` lookup |
| D | SỐ FILE BEE (vd `BLHAN099499/26`) | `refCode` hoặc `label` **cần dev clarify** |
| E | SALE | map sang `TMSEmployee` (salesman) |
| F | CONT (20'/40') | `TMSBillForwarderTransport.containerType` |
| G | SỐ CONT (vd `STXU2046902`) | `containerNo` |
| H-I | ĐIỂM ĐI / MỚI | `TMSBillStopLocation[0]` |
| J-K | ĐIỂM ĐẾN / MỚI | `TMSBillStopLocation[last]` |
| L | TRỌNG LƯỢNG (`NHẸ` / số kg / date) | `TMSBillGoods.weight` (dạng free-text?) |
| **M** | **CƯỚC CVC** (vd 5280000) | `TMSBillCostItem{type=CVC, totalCost}` |
| **N** | **LẠCH HUYỆN** (450000) | `TMSBillCostItem{type=PortFee, totalCost}` |
| **O** | **PHÁT SINH** (400000) | `TMSBillCostItem{type=Extra, totalCost}` |
| P | TỔNG CƯỚC (sum) | **derived**, không lưu |
| Q | CHI HỘ > NỘI DUNG (`PHÍ CSHT`) | `TMSBillCostItem{type=Reimbursement, note}` |
| R | SỐ HĐ (invoice no) | metadata trên cost item |
| S | SỐ TIỀN (expense amount) | `TMSBillCostItem.totalCost` của mục chi hộ |
| T | NGÀY HĐ (invoice date) | metadata |
| U | SỐ XE (`15H-354.50`) | `TMSBillForwarderTransport.vehiclePlate` |

**Columns V-AK (22-37)**: internal tracking (sale name display, mail status, nội dung xuất HĐ…) — không import vào TMSBill, có thể hiển thị để check.

### Pattern multi-row 1 bill

Observation từ sample:
- Row 11: BEE26.09.198 (main data, 1 container)
- Row 12-13: Continuation (col C có mã TK phụ `EBARA`, `SHHPH26018296S`)
- Row 14: Empty separator

HOẶC:
- Row 15: BEE26.09.236 (40', container MRKU4135923)
- Row 16: **không có job code**, nhưng có container MRSU4398265 → **container thứ 2 của cùng bill?** Hay **bill mới**?

→ **Open question #2** cho dev.

### Vendor identification

File là của "ĐỨC TOÀN PHÁT" (thầu phụ). Tên công ty + MST ở R1-R4 metadata header, không trong data row.

→ **Open question #3**: hardcode vendor per upload (user chọn vendor trước khi upload) hay auto-detect từ metadata header?

## 3. Open questions (BẮT BUỘC dev trả lời trước khi code)

1. **Bill code**: `TMSBill.code` dùng col A `SỐ JOB` (`BEE26.09.198`) hay col D `SỐ FILE BEE` (`BLHAN099499/26`)? Hoặc 1 cái là `code`, 1 cái là `label` / `refCode`?
2. **Multi-row interpretation**: R15 có job code `BEE26.09.236`, R16 không có job code nhưng có container number khác. Đây là:
    - **a.** 1 bill với 2 container (TMSBill có 2 StopLocation hoặc 2 ForwarderTransport?)
    - **b.** 2 bill riêng biệt cùng job code
    - **c.** Khác (dev cho ví dụ khác)
3. **Vendor matching**: Mỗi file 1 vendor. User chọn vendor trước khi upload (dropdown TMSVendor list) hay AI auto-detect từ header R1-R4?
4. **Column mapping có hardcode không**: Template Excel này sẽ dùng mãi mãi (cùng vendor Đức Toàn Phát + vendor khác dùng template giống hệt), hay mỗi vendor template khác → cần UI chọn mapping?
5. **Cost item type**: Có enum sẵn trong `core.common` không? (`CVC`, `LạchHuyện`, `PhátSinh`, `ChiHộ`). Hay dùng free-text `note`?
6. **Date trong col L**: cột `TRỌNG LƯỢNG` nhưng data đôi khi là date (`2026-08-08 00:00:00`), đôi khi `NHẸ`, đôi khi số. Dev confirm interpretation?
7. **Customer lookup qua MST (col C)**: Nếu TMSPartner không có MST khớp → tạo mới hay reject row?
8. **Duplicates**: Nếu `TMSBill.code` đã tồn tại → skip, update, hay reject?
9. **Multi-sheet**: Chỉ sheet đầu tiên hay cho user chọn sheet?
10. **Scope lần đầu**: 
    - **a.** Full import (preview + validate + bulk save + error report)
    - **b.** MVP phase 1: parse Excel → gen `MapObject[]` cho user review tay trên UI → nhấn save → saveTMSBillModels

## 4. Đề xuất kiến trúc (nếu dev approve)

### BE

**Flow**:
```
FE upload Excel (MultipartFile) 
  → TMSBillImportService.parseExcel(client, company, bytes, vendorId)
    → ExcelParser (Apache POI) → List<MapObject> rows
    → TMSBillImportLogic.convertRowsToModels(client, company, rows, vendorId)
      → Lookup TMSVendor by id (hardcode user-provided)
      → Lookup TMSPartner (customer) by MST
      → Lookup TMSEmployee (salesman) by name
      → Build TMSBillModel per bill (handle multi-row grouping)
    → Return List<TMSBillImportPreview>{model, errors, warnings}

FE user review preview → click confirm
  → TMSBillService.importBills(client, company, models)
    → TMSBillLogic.saveTMSBillModels(client, company, models) ← reuse existing
```

**New files**:
- `module/tms/bill/src/main/java/.../import/TMSBillExcelImportService.java` (facade)
- `module/tms/bill/src/main/java/.../import/TMSBillExcelImportLogic.java` (parse + convert)
- `module/tms/bill/src/main/java/.../import/TMSBillImportRow.java` (DTO per Excel row)
- `module/tms/bill/src/main/java/.../import/TMSBillImportPreview.java` (DTO: model + errors)

**Dependency**: `org.apache.poi:poi-ooxml` (có khả năng đã có qua transitive của BillExport service).

### FE

**Flow**:
1. `UITMSVendorBillList` → thêm button **"Import Excel"**
2. Click → popup chọn vendor + chọn file `.xlsx`
3. Upload → BE parse → trả preview list
4. UI hiển thị grid: mỗi row = 1 bill với error/warning status
5. User xoá row bị lỗi, hoặc fix inline, hoặc OK
6. Click Confirm → save
7. Toast success + navigate về bill list

**New files**:
- `webui/tms/src/app/logistics/tms/bill/import/UITMSBillImportDialog.tsx`
- `webui/tms/src/app/logistics/tms/bill/import/UITMSBillImportPreview.tsx`

## 5. MVP Phase 1 (gợi ý nếu dev muốn phân phase)

**MVP**: Chỉ parse + save, không preview UI phức tạp:
1. Button upload trong vendor bill list
2. Dialog: chọn vendor dropdown + file picker
3. Backend parse Excel → trả `{ success: count, failed: [{row, error}] }`
4. Hiển thị summary ra toast

Scope: ~2-3 ngày. Preview UI (Phase 2) khi dev duyệt pattern.

## 6. Risk / limitation

- **Template Excel biến động**: Nếu vendor khác đổi column order, cần config mapping động → thiết kế rigid hiện tại fail.
- **File size**: 845 row x 37 col = ~30k cells. POI load full workbook, ~5-10MB RAM. Chấp nhận cho mỗi file <5MB.
- **Encoding**: Excel VN có dấu — POI đọc UTF-16 OK.
- **Date parsing**: col B date có `2026-09-21 00:00:00` dễ, nhưng col L mix date + text (`NHẸ`) → cần try-parse.
- **Vendor Đức Toàn Phát**: hiện chưa chắc đã có trong `TMSVendor` của system. Dev cần confirm vendor exists hoặc tạo trước.

## 7. Dev cần trả lời

**10 open questions ở §3** — trả lời xong tôi:
- Thu hẹp scope → design chi tiết column mapping cố định
- Tách TODO phase 1 (MVP) + phase 2 (preview UI) nếu cần
- Chạy pipeline: branch `ai/bill-import-excel` → BE + FE → review → push

**Nếu dev chọn MVP phase 1** (recommend để tránh over-engineer): trả lời Q1-Q4, Q7-Q10 là đủ, Q5-Q6 edge có thể decide trong code.
