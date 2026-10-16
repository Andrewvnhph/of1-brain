# ops Specification

## Purpose
Module operations monitoring, reporting, analytics qua read-only Groovy SQL cross-module.
Expose dashboard aggregation và XLSX export cho FE.

## Requirements

### Requirement: Read-only cross-module query
`ops` module SHALL chỉ đọc entity của các module khác (`bill`, `vendor`, `fleet`, `core`),
không mutation.

#### Scenario: Thêm metric mới
- **WHEN** cần cross-join bill + vendor + driver
- **THEN** viết Groovy SQL trong `ops.groovy`, không import Repository của module khác để mutation
- **AND** nếu cần aggregated metric nên cache bảng riêng dưới module `ops`, không ghi ngược entity nguồn

### Requirement: Report filter employee flag
Mọi report liên quan employee (BillReport, BillApiLogReport, UserErrorReport) SHALL filter bỏ
employee có `excludeFromReports = true`.

#### Scenario: Filter trong SQL
- **WHEN** Groovy SQL join `TMSEmployee`
- **THEN** `WHERE employee.exclude_from_reports = false` được thêm vào query, không post-filter trong Java
- **AND** report hiển thị cho user cuối không chứa record của employee bị flag

### Requirement: LOLO report format
`VendorLOLOReport` SHALL trả về aggregate theo vendor + period với 4 status
`On-time | Overdue-Inv.Received | Overdue-Inv.Pending | None`.

#### Scenario: Request report monthly
- **WHEN** FE gọi `TMSOpsService.getVendorLOLOReport(period=2026-09)`
- **THEN** service aggregate `TMSVendorBill` theo vendor, compute LOLO status (theo spec `vendor`)
- **AND** trả record list: `{vendor, totalBills, onTime, overdueInvRecv, overdueInvPending, none}`

### Requirement: XLSX export
`ops` service SHALL expose method export XLSX cho mỗi report, data stream xuống FE.

#### Scenario: Export BillReport sang XLSX
- **WHEN** FE click `TMSReportExportXLSXButton` cho BillReport filter đã chọn
- **THEN** backend build XLSX với header + row data theo filter
- **AND** trả stream byte array cho FE download, filename format `BillReport_<period>_<timestamp>.xlsx`

### Requirement: Dashboard metric caching
Dashboard daily metric (bill count, revenue, cost, profit) SHALL cache theo ngày và invalidate
khi bill lifecycle thay đổi.

#### Scenario: Bill chuyển sang DONE
- **WHEN** `TMSBill.processStatus` chuyển sang `DONE`
- **THEN** `TMSBillActivity` event trigger invalidation cho dashboard metric của ngày tương ứng
- **AND** request dashboard tiếp theo recompute metric ngày đó
