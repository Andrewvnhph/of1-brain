# OF1 TMS — Specs Overview

Tập hợp capability spec phản ánh **hiện trạng đã implement** của dự án `of1-tms`. Mỗi module
= một capability, spec tại `of1-tms/<module>/spec.md`. Đây là trạng thái ổn định (specs/),
không phải proposal đang chạy (changes/).

## Capabilities

| Capability | Spec | Vai trò |
|---|---|---|
| core | `of1-tms/core/spec.md` | Domain entity nền, DAO base, auth, enum/constant, `SqlMapRecord` convention |
| http | `of1-tms/http/spec.md` | HTTP routing, OAuth2 filter, exposure Spring `@Service` cho FE qua `createHttpBackendCall` |
| rpc | `of1-tms/rpc/spec.md` | Inter-service RPC → platform (`PlatformClient`, `CommunicationRPC`, `StorageRPC`, `LocationRPC`, `JobTrackingRPC`) — **không** Kafka trực tiếp |
| bill | `of1-tms/bill/spec.md` | Hoá đơn multi-leg: lifecycle, type IMS/FORWARDER, cost item, BFSOne sync, report filter |
| fleet | `of1-tms/fleet/spec.md` | Vehicle, driver, assignment, GPS tracking, license expiry alert |
| vendor | `of1-tms/vendor/spec.md` | Vendor master, vendor bill, payment reconciliation, LOLO status |
| ops | `of1-tms/ops/spec.md` | Reports (BillReport, BillApiLogReport, UserErrorReport, VendorLOLOReport), dashboard, XLSX export |
| integration | `of1-tms/integration/spec.md` | BFSOne (cost/truck/employee sync), Microsoft Graph, crypto, AOP tracking outbound |
| notification | `of1-tms/notification/spec.md` | Firebase push, email digest, device token, template rendering |
| webhook | `of1-tms/webhook/spec.md` | Inbound webhook endpoint, authtoken verify, dispatcher theo (source,event) |

## Ràng buộc chung (toàn hệ TMS)

- Backend RPC-style: FE map vào `@Service` bean qua `createHttpBackendCall('<ServiceName>', '<methodName>', params)`, không REST controller riêng cho business logic.
- Phân tầng Service → Logic → Repository → Entity; mọi Logic extends `TMSDAOService`.
- Mọi business method nhận `ClientContext client` đầu tiên (FE không truyền).
- Transaction tường minh; read dùng `@Transactional(readOnly = true)`.
- **RPC-only**: TMS → Platform qua `RPCService` tới `app/api` của `of1-platform`. **KHÔNG** gọi Kafka trực tiếp.
- DB column snake_case ↔ camelCase qua `SqlMapRecord` (vd `previous_fixed_charge` ↔ `previousFixedCharge`).
- Thêm field entity Java → **bắt buộc** `@Column` annotation.
- Frontend bill UI config tập trung ở `webui/tms/src/app/logistics/tms/bill/TMSBillRecordConfig.tsx` (function `createTMSBillRecordConfig`).
- Design feature mới follow OpenSpec workflow; engineering specs lưu riêng ở `of1-tms-engineering-hub/openspec/`.

Design chi tiết: `../../designs/of1-tms/`. Nguồn gốc: `of1-tms/CLAUDE.md`, `of1-tms-engineering-hub/`.
