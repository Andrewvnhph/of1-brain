# Design — ops (hiện trạng)

Module operations monitoring + reporting + analytics. Read-only cross-module query qua
Groovy SQL. Là module top-level trong dependency graph.

## Boundary

- Package gốc `cloud.datatp.tms.ops`.
- Phụ thuộc: `bill`, `vendor`, `core`. Chỉ read, không mutation entity module khác.

## Sub-packages

| Package | Trách nhiệm |
|---|---|
| `report` | Report logic (BillReport, BillApiLogReport, UserErrorReport, VendorLOLOReport, TransportReport) |
| `groovy` | Groovy SQL script cross-join bill/vendor/fleet/core |
| `dashboard` | Dashboard aggregation (daily/weekly/monthly) |
| `service` | `TMSOpsService` — RPC entry point cho FE dashboard |
| `export` | XLSX export (via `TMSReportExportXLSXButton` ở FE, backend sinh data) |

## Data model chính

Chủ yếu read-only — không entity riêng. Chỉ vài entity support:
- `TMSBillTransportReport` — denormalized transport metrics (snapshot).
- `TMSBillUserErrorReport` — user error / discrepancy log.
- `TMSBillApiLog` (shared với `bill` module) — API call audit cho report filter.

## Luồng chính

- **Bill report**: `TMSBillReportLogic.searchTMSBillApiLogReport()` → Groovy SQL join bill + employee + company → filter employee có `excludeFromReports=true` (feature recent).
- **LOLO report**: cross-read vendor bill + due date → compute On-time / Overdue-Inv.Received / Overdue-Inv.Pending / None → return cho `UITMSBillVendorLOLOReport`.
- **User error report**: scan `TMSBillUserErrorReport` entries → group by user/period → chart.
- **Dashboard**: aggregate daily metrics (bill count, revenue, cost, profit) → cache ngắn hạn.
- **Export**: FE click XLSX button → gọi `TMSOpsService.exportXxx(...)` → backend build sheet → stream download.

## Ghi chú mở rộng

- Thêm report mới → viết Groovy SQL ở `groovy`, add method vào logic, expose qua service.
- Thêm filter dimension (vd theo region) → sửa SQL + service params; nhớ sync cột snake_case.
- Khi join vào module mới → read-only, không được dùng Repository mutation.
- Dashboard metric cache cần invalidate khi bill lifecycle change — hook qua `TMSBillActivity`.
