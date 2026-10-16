# fleet Specification

## Purpose
Module quản lý đội xe (`TMSVehicle`), tài xế (`TMSDriver`), assignment xe-driver, và integrate
GPS tracking + license expiry alert.

## Requirements

### Requirement: Plate number unique per company
`TMSVehicle.plateNo` SHALL unique trong phạm vi `company_id`.

#### Scenario: Thêm xe trùng biển số
- **WHEN** tạo `TMSVehicle` với `plateNo` đã tồn tại trong cùng company
- **THEN** service ném `ValidationException`, không persist

### Requirement: Vehicle-driver assignment không overlap thời gian
`TMSVehicleAssignment` SHALL không được overlap thời gian cho cùng vehicle hoặc driver.

#### Scenario: Overlap assignment
- **WHEN** tạo assignment driver A cho vehicle X từ `2026-01-01` đến `2026-02-01`
- **AND** đã tồn tại assignment driver A cho vehicle Y từ `2026-01-15` đến `2026-01-30`
- **THEN** service ném exception, không cho overlap

### Requirement: GPS tracking từ integration
Vehicle `currentLocation` SHALL được cập nhật từ event GPS do `integration` module push.

#### Scenario: GPS event vào
- **WHEN** `integration` push event GPS cho `vehicleId=X` với lat/lng + timestamp
- **THEN** `TMSVehicle.currentLocation` update, `lastSeenAt = timestamp`
- **AND** nếu `timestamp` cũ hơn `lastSeenAt` hiện tại → bỏ qua event

### Requirement: License expiry alert
Hệ thống SHALL cron scan `TMSDriver.licenseExpiry` và publish alert cho driver sắp hết hạn.

#### Scenario: Driver license hết hạn trong 30 ngày
- **WHEN** cron chạy daily
- **AND** phát hiện driver có `licenseExpiry < today + 30 days` và chưa có alert gần đây
- **THEN** publish notification tới dispatcher qua `notification` module
- **AND** ghi log để tránh gửi trùng trong 7 ngày
