# integration Specification

## Purpose
Module đóng gói mọi tích hợp external (BFSOne, Microsoft Graph, crypto helper, AOP tracking).
Là cầu nối duy nhất domain TMS ↔ external system (ngoài platform RPC đã có ở `rpc`).

## Requirements

### Requirement: BFSOne call đi qua integration module
Mọi call tới BFSOne từ TMS SHALL đi qua bean trong `integration.bfsone`, không viết HTTP call tay.

#### Scenario: Push bill sang BFSOne
- **WHEN** `bill` module cần push bill sang BFSOne
- **THEN** inject `BFSOneClient`, gọi `bfsOneClient.pushBill(bill)`
- **AND** request/response log vào `BFSOneApiLog` tự động qua AOP

### Requirement: Credential mã hoá khi lưu DB
Mọi credential (`BFSOneCredential`, `MsGraphCredential`) SHALL được mã hoá qua
`integration.crypto` khi persist.

#### Scenario: Lưu BFSOne API key
- **WHEN** admin cấu hình API key BFSOne cho company
- **THEN** service encrypt key qua `crypto` package trước khi save entity
- **AND** đọc ra tự decrypt, trường plaintext không bao giờ xuất hiện trong log

### Requirement: AOP tracking outbound call
Mọi method client external SHALL được annotate `@Tracked` và lưu `ApiCallTrace` bất đồng bộ.

#### Scenario: Call có latency cao
- **WHEN** `bfsOneClient.pushBill` thực thi
- **THEN** `TrackedCallAspect` lưu `ApiCallTrace` với `durationMs`, `status`, `errorMsg` (nếu có)
- **AND** khi error rate 5 phút gần nhất vượt ngưỡng → alert qua `notification` module

### Requirement: BFSOne employee sync
Employee list từ BFSOne SHALL sync vào `TMSEmployee` reconcile theo `refCode`.

#### Scenario: Cron sync employee
- **WHEN** cron pull employee từ BFSOne
- **THEN** mỗi record tìm `TMSEmployee` có `refCode = <bfsone_employee_id>`
- **AND** nếu tồn tại thì update field; nếu không thì tạo mới với `refSource = "BFSONE"`
