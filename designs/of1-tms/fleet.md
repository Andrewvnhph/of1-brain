# Design — fleet (hiện trạng)

Module quản lý đội xe và tài xế của TMS. Cung cấp dữ liệu xe/driver cho `bill` khi gán vận
chuyển, và cho `ops` khi monitoring real-time.

## Boundary

- Package gốc `cloud.datatp.tms.fleet`.
- Phụ thuộc: `core` (entity base, TMSDAOService), `integration` (external vehicle API nếu có), `rpc` (Company API từ platform).

## Sub-packages

| Package | Trách nhiệm |
|---|---|
| `entity` | `TMSVehicle`, `TMSDriver`, `TMSVehicleType`, `TMSDriverLicense`, `TMSVehicleAssignment` |
| `repository` | JpaRepository per entity |
| `service` | `TMSVehicleService`, `TMSDriverService` — RPC entry point |
| `logic` | Business logic: assignment vehicle↔driver, GPS tracking integration, license expiry monitoring |

## Data model chính

- `TMSVehicle` — xe: `plateNo`, `vehicleType`, `capacity`, `status`, `currentDriverId`, `company_id`.
- `TMSDriver` — tài xế: `fullName`, `phone`, `licenseNo`, `licenseExpiry`, `status`.
- `TMSVehicleAssignment` — gán xe-driver theo thời gian.
- `TMSVehicleType` — loại xe (container 20ft, 40ft, truck, bulk cargo…).

## Luồng chính

- **Register vehicle**: Service → Logic validate plate unique + vehicle type → persist.
- **Assign driver to vehicle**: tạo `TMSVehicleAssignment` với date range; chống overlap.
- **Vehicle tracking**: integration module push GPS → fleet cập nhật `currentLocation`.
- **License expiry alert**: cron scan driver có `licenseExpiry < today + N days` → publish alert.

## Ghi chú mở rộng

- Thêm vehicle type mới → thêm enum trong `core.common` hoặc config bảng `TMSVehicleType`.
- Thêm field driver (vd rating) → `@Column` + update Groovy SQL nếu có report.
- Khi tích hợp GPS provider mới → qua `integration` module, fleet chỉ nhận event.
