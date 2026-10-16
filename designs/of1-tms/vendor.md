# Design — vendor (hiện trạng)

Module quản lý vendor (nhà cung cấp dịch vụ vận chuyển ngoài) và payment cho vendor. Phụ
thuộc trực tiếp vào `bill` để aggregate cost per vendor.

## Boundary

- Package gốc `cloud.datatp.tms.vendor`.
- Phụ thuộc: `bill` (bill cost items), `core` (entity base), `rpc` (Partner API từ platform).

## Sub-packages

| Package | Trách nhiệm |
|---|---|
| `entity` | `TMSVendor`, `TMSVendorBill`, `TMSVendorPayment`, `TMSVendorContract` |
| `repository` | JpaRepository per entity |
| `service` | `TMSVendorService` — RPC entry point |
| `logic` | Business logic: aggregate cost từ bill, generate vendor bill, payment reconciliation |

## Data model chính

- `TMSVendor` — vendor master: `code`, `name`, `taxCode`, `contactInfo`, `bankAccount`, `company_id`.
- `TMSVendorBill` — hoá đơn phải trả vendor: aggregate `TMSBillCostItem` theo vendor + period.
- `TMSVendorPayment` — chi trả vendor (bank transfer, cheque…).
- `TMSVendorContract` — hợp đồng + rate card với vendor.

## Luồng chính

- **Aggregate vendor bill**: cron hoặc trigger thủ công → scan `TMSBillCostItem` theo `vendorId` + period chưa invoiced → tạo `TMSVendorBill` draft.
- **Reconcile payment**: match `TMSVendorPayment` với `TMSVendorBill` outstanding → cập nhật status.
- **Rate lookup**: khi tạo cost item, lookup rate từ `TMSVendorContract` current.
- **LOLO status**: khi vendor bill overdue → mark LOLO (Lift-On/Lift-Off) status, feed vào `ops.VendorLOLOReport`.

## Ghi chú mở rộng

- Thêm payment method mới → enum trong `core.common` + handler trong logic.
- Thêm field contract (vd SLA penalty) → `@Column` + logic penalty computation.
- Vendor bill number format phải unique per company — dùng `TMSSequenceService`.
