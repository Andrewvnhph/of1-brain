# bill Specification

## Purpose
Module trung tâm: quản lý hoá đơn vận chuyển multi-leg, cost item, BFSOne sync, LOLO tracking,
và report filter. Hub phụ thuộc của `vendor` + `ops`.

## Requirements

### Requirement: Bill lifecycle
`TMSBill.processStatus` SHALL theo lifecycle `PLAN → PENDING → PROCESSING → DONE` (hoặc chuyển
sang `CANCELED` từ bất kỳ state nào trước `DONE`).

#### Scenario: Tạo bill mới
- **WHEN** `TMSBillLogic.saveTMSBill` tạo bill lần đầu
- **THEN** `processStatus = PLAN`, `code` sinh từ `TMSSequenceService`

#### Scenario: Chuyển sang PROCESSING
- **WHEN** vendor được assign và vehicle sẵn sàng
- **THEN** `processStatus` chuyển từ `PENDING → PROCESSING`
- **AND** ghi `TMSBillActivity` event state change

#### Scenario: Huỷ bill
- **WHEN** user cancel bill đang ở `PLAN/PENDING/PROCESSING`
- **THEN** `processStatus = CANCELED`, không được chuyển lại trạng thái sống

### Requirement: Bill type IMS vs FORWARDER
`TMSBill.type` SHALL là `IMS` hoặc `FORWARDER` và relationship transport tương ứng.

#### Scenario: Bill type IMS
- **WHEN** `type = IMS`
- **THEN** bill có relationship 1:1 với `TMSBillTransport` (xe nội bộ, driver trong hệ thống)

#### Scenario: Bill type FORWARDER
- **WHEN** `type = FORWARDER`
- **THEN** bill có relationship 1:1 với `TMSBillForwarderTransport` (forwarder, container, HBL)

### Requirement: Fee aggregation
`TMSBillFee` (1:1 với bill) SHALL aggregate các khoản `fixedPayment`, `extraPayment`, `tax`,
`profit` + list `TMSBillCostItem`.

#### Scenario: Tính tổng phí
- **WHEN** bill có 3 cost item (ShipmentCharge 1000, GoodsInsurance 50, COD 200)
- **THEN** `TMSBillFee.fixedPayment = 1250` + các khoản `extraPayment`/`tax` theo cấu hình
- **AND** `profit = finalPayment - cost`

### Requirement: Cost item line
Mỗi `TMSBillCostItem` SHALL có `quantity`, `price`, `unit`, `totalCost`, `currency`, loại
(enum như `GoodsInsurance`, `COD`, `ShipmentCharge`…).

#### Scenario: Thêm cost item
- **WHEN** thêm cost item type `GoodsInsurance`, quantity 1, price 50 USD
- **THEN** `totalCost = quantity * price = 50`, `currency = USD`
- **AND** aggregate ngược vào `TMSBillFee`

### Requirement: BFSOne sync
`TMSBillBFSOneLogic.convertBFSOneDataToTMSBills` SHALL map payload BFSOne thành entity TMS với
25+ field mapping, xử lý container mode `FCL/LCL/BULK_CARGO`.

#### Scenario: Sync bill từ BFSOne
- **WHEN** BFSOne push payload chứa `hbl_no`, `container_type`, `vehicle_info`
- **THEN** map thành `TMSBill` + `TMSBillForwarderTransport` tương ứng
- **AND** container mode `BULK_CARGO` map sang container type chuẩn trong `core.common`

### Requirement: Report filter employee flag
`TMSBillReportLogic` SHALL lọc bỏ các bill/log liên quan đến employee có
`excludeFromReports = true`.

#### Scenario: Employee deactivated được flag exclude
- **WHEN** `TMSEmployee.excludeFromReports = true`
- **THEN** `BillReport` và `BillApiLogReport` không trả về bất kỳ record nào liên quan employee đó
- **AND** filter áp dụng ở Groovy SQL query, không post-filter trong Java
