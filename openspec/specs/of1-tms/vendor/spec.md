# vendor Specification

## Purpose
Module quản lý vendor (nhà cung cấp dịch vụ vận chuyển), aggregate chi phí thành vendor bill,
reconcile payment, và track LOLO (Lift-On/Lift-Off) status feed vào `ops` report.

## Requirements

### Requirement: Vendor code unique per company
`TMSVendor.code` SHALL unique trong `company_id`.

#### Scenario: Trùng vendor code
- **WHEN** tạo vendor với `code` đã tồn tại trong cùng company
- **THEN** service ném exception, không persist

### Requirement: Vendor bill aggregate từ cost item
`TMSVendorBill` SHALL aggregate `TMSBillCostItem` chưa invoiced theo vendor + period.

#### Scenario: Generate vendor bill monthly
- **WHEN** cron chạy đầu tháng với `vendorId=V`, `period=2026-09`
- **AND** `TMSBillCostItem` của vendor V trong tháng 9 chưa thuộc vendor bill nào
- **THEN** tạo `TMSVendorBill` draft chứa toàn bộ cost item đó, total = sum(`totalCost`)
- **AND** mark cost item đã invoiced để tránh double

### Requirement: Payment reconciliation
`TMSVendorPayment` SHALL match với `TMSVendorBill` outstanding theo amount và vendor.

#### Scenario: Thanh toán vendor bill
- **WHEN** nhập `TMSVendorPayment` amount 10000 cho `vendorId=V`
- **AND** vendor có 2 bill outstanding (6000 + 4000)
- **THEN** payment allocate đủ cho cả 2 bill, status chuyển `PAID`
- **AND** nếu amount < outstanding → bill mới nhất chuyển `PARTIALLY_PAID`

### Requirement: LOLO status feed vào report
Vendor bill overdue SHALL được mark LOLO status để `ops.VendorLOLOReport` consume.

#### Scenario: Vendor bill quá hạn
- **WHEN** `TMSVendorBill.dueDate < today` và chưa có `TMSVendorPayment` khớp
- **THEN** compute LOLO status theo invoice state:
    - Overdue + invoice received → `Overdue-Inv.Received`
    - Overdue + invoice pending → `Overdue-Inv.Pending`
    - Chưa tới hạn → `On-time`
    - Không có bill → `None`
