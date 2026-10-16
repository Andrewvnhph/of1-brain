# Design — bill (hiện trạng)

Module trung tâm của TMS: quản lý hoá đơn multi-leg shipment, cost tracking, tích hợp BFSOne.
Là hub lớn nhất (~27 entity, `TMSBillLogic` 900+ dòng).

## Boundary

- Package gốc `cloud.datatp.tms.bill`.
- Phụ thuộc: `core` (TMSDAOService, enum), `fleet` (vehicle info), `integration` (BFSOne/MS Graph).
- Companion packages: `housebill`, `document`, `ru`, `groovy`, `jobtracking`.

## Sub-packages

| Package | Trách nhiệm |
|---|---|
| `entity` | 27 entity (`TMSBill`, `TMSBillFee`, `TMSBillCostItem`, `TMSBillStopLocation`, `TMSBillActivity`, `TMSBillApiLog`, `TMSBillRating`, `TMSBillResponsibility`, `TMSBillTransport`, `TMSBillForwarderTransport`, `TMSBillGoods`, `TMSBillCustomer`, `TMSBillSender`, `TMSBillReceiver`…) |
| `repository` | JpaRepository per entity |
| `api` | Request/response model cho API |
| `models` | DTO + request classes |
| `jobtracking` | Integration với job tracking + cron task |
| `webhook` | Bill-related webhook |
| `TMSBillService` | Service facade (RPC entry point) |
| `TMSBillLogic` | Core business logic (900+ dòng) — save/search/sync, validation chéo customer-vendor |
| `TMSBillBFSOneLogic` | Integration BFSOne (`convertBFSOneDataToTMSBills` — map 25+ field, FCL/LCL/BULK_CARGO) |
| `TMSBillReportLogic` | Sinh report (`BillReport`, `BillApiLogReport`) với filter employee |

## Data model chính

### `TMSBill` (~40 cột)
- `code` (unique per company), `label` (file number ref), `type` (IMS/FORWARDER).
- `processStatus` ∈ `{PLAN, PENDING, PROCESSING, DONE, CANCELED}` — bill lifecycle.
- `bookingDate`, `deliveryPlan`, `containerNo`, `sealNo`, `customsChannel` (GREEN/YELLOW/RED).
- `isCombine` (combined shipment flag).
- `refSource` / `refCode` / `refId` — tham chiếu external system.
- Embedded: `TMSBillCustomer`, `TMSBillSender`, `TMSBillReceiver`.
- Relationship: 1:1 `TMSBillFee`, 1:n `TMSBillStopLocation`, conditional `TMSBillTransport` (IMS) hoặc `TMSBillForwarderTransport` (FORWARDER).

### Entities liên quan
- `TMSBillFee` — tổng chi phí: `fixedPayment`, `extraPayment`, `tax`, `profit`, `paymentMethod`.
- `TMSBillCostItem` — line item: `quantity`, `price`, `unit`, `totalCost`, `currency`, loại (GoodsInsurance, COD, ShipmentCharge…).
- `TMSBillResponsibility` — ai chịu trách nhiệm ở stage nào.
- `TMSBillStopLocation` — route stops.
- `TMSBillActivity` — event log state change.
- `TMSBillApiLog` — audit API call.

## Luồng chính

- **Create bill**: `saveTMSBill(client, company, bill)` → validate house bill compatibility → update customer/vendor → sync salesman → persist → tạo `TMSBillResponsibility` record.
- **Search**: `searchTMSBills(client, company, params)` → Groovy SQL (`SearchTMSBills`) → `List<SqlMapRecord>`.
- **Bulk**: `saveTMSBillModels(client, company, models)` — validate loạt bill mới cùng lúc.
- **Sync master**: `syncDataByMasterBill(client, company, masterBillId, targetBillIds, fields)` — copy field từ master sang target.
- **BFSOne sync**: `convertBFSOneDataToTMSBills()` map JSON payload BFSOne thành 25+ field entity (FCL/LCL, BULK_CARGO → container, vehicle info extraction).
- **Report**: `TMSBillReportLogic` lọc bỏ employee có `excludeFromReports=true` (recent feature).

## Ghi chú mở rộng

- Thêm cột `TMSBill` mới → thêm `@Column` + update Groovy SQL (snake_case) + `TMSBillRecordConfig.tsx` (FE).
- Thêm status mới trong `TMSBillProcessStatus` → review tất cả transition logic trong `TMSBillLogic`.
- Thêm BFSOne field mapping → `TMSBillBFSOneLogic.convertBFSOneDataToTMSBills` (map theo field name BFSOne).
- Khi thêm `TMSBillCostItem` type mới → thêm enum trong `core.common` + fee aggregation logic trong `TMSBillFee`.
