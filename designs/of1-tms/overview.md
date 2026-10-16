# Design — OF1 TMS (overview hiện trạng)

Tài liệu phản ánh **hiện trạng** của dự án `of1-tms` (Transport Management System cho OF1
Logistics Platform). Dùng làm điểm vào cho các design per-module trong cùng thư mục.

## Kiến trúc tổng

- **Backend**: Java 21, Spring Boot 3.5.10, Gradle 9.2.x multi-module.
- **Frontend**: React 18.3.1 + TypeScript 5.3.3 + Webpack 5.87 + Module Federation 2.9 (`@of1-webui/*` micro-frontend).
- **Database**: PostgreSQL (JDBC 42.7.3, Hibernate 6.4.4). H2 cho test.
- **Security**: Spring Security 6.3.3 + Keycloak 26.2.0 (OAuth2 Resource Server).
- **Server**: Jetty 12.0.31.
- **Messaging**: KHÔNG dùng Kafka trực tiếp — of1-tms gọi platform qua `RPCService` → `app/api` của `of1-platform`.
- Port local: TMS BE `7086`, TMS FE dev-server `3006`, Platform BE `7080`, Platform FE `3000`.

## Module map (Gradle)

| Module | projectDir | Vai trò |
|---|---|---|
| `core` | `module/tms/core` | Domain entities (`TMSEmployee`, `TMS*`), auth, convention `SqlMapRecord` snake_case ↔ camelCase |
| `http` | `module/tms/http` | REST controllers, HTTP routing (lớp exposure cho FE/UI, phụ thuộc `rpc`) |
| `rpc` | `module/tms/rpc` | Inter-service RPC → Platform (`datatp-platform-app-api`), communication, storage |
| `bill` | `module/tms/bill` | Hoá đơn multi-leg: 27 entity (`TMSBill`, `TMSBillFee`, `TMSBillCostItem`…), lifecycle `PLAN → PENDING → PROCESSING → DONE`, type IMS/FORWARDER, LOLO tracking, BFSOne sync |
| `fleet` | `module/tms/fleet` | Vehicle/driver fleet, phụ thuộc `core` + `integration` |
| `vendor` | `module/tms/vendor` | Vendor payment, phụ thuộc `bill` |
| `ops` | `module/tms/ops` | Operations monitoring + reports (`BillReport`, `BillApiLogReport`, `UserErrorReport`, `VendorLOLOReport`) |
| `integration` | `module/tms/integration` | BFSOne (cost template, truck template, employee sync), Microsoft Graph, crypto |
| `notification` | `module/tms/notification` | Firebase Admin SDK 9.4.1 push, platform webhooks |
| `webhook` | `module/tms/webhook` | Inbound webhook handling + authtoken |
| `app/cli` | `app/cli` | Spring Shell CLI (Groovy) — admin/migration tool |
| `release` | `release` | Spring Boot assembly, đóng gói deploy archive |
| `webui/tms` | `webui/tms` | React 18 + TS frontend, Module Federation share với platform UI |

Package gốc: `cloud.datatp.tms.<module>` (+ `net.datatp.logistics.*`). Mọi Logic class
extends `TMSDAOService` ở module `core`.

## Kiến trúc backend RPC-style (không REST controller cho WebUI)

Frontend không gọi REST endpoint; nó map thẳng vào Spring `@Service` bean qua
`appContext.getBackendConfigs().getBackendConfig('tms').createHttpBackendCall('TMSService', 'methodName', params)`. Phân tầng:

```
Service (@Service, transaction + permission/context)
   → Logic (*Logic, pure business, extends TMSDAOService, no transaction)
      → Repository (JpaRepository, @Query)
         → Entity (@Entity)
```

- Mọi business method nhận `ClientContext client` làm tham số **đầu tiên** (FE không truyền).
- Params FE match với tham số Java **theo tên** (compile `-parameters`).
- Transaction tường minh; read dùng `@Transactional(readOnly = true)`.
- RPC ra ngoài: of1-tms → platform đi qua `RPCService` tới `app/api` của `of1-platform`. **KHÔNG** gọi Kafka trực tiếp từ TMS.

## Quan hệ liên module

```
http ──(exposure UI)──▶ rpc, core
bill ──(cost/BFSOne sync)──▶ integration
fleet ──(vehicle)──▶ core, integration
vendor ──(payment)──▶ bill
ops ──(report cross-read)──▶ bill, vendor, core (Groovy SQL, read-only)
notification ──(push)──▶ Firebase + Platform webhook
webhook ──(inbound)──▶ core (authtoken)
mọi module ──(RPC ra ngoài)──▶ rpc → Platform/FMS
```

## DB schema change (quy ước)

- Entity Java mới / sửa field → **phải** thêm `@Column` tương ứng (bắt buộc, không optional).
- Groovy SQL: dùng cột **snake_case** khớp với `@Column`.
- `SqlMapRecord` tự convert snake_case ↔ camelCase (ví dụ: `previous_fixed_charge` → `previousFixedCharge`).
- Khi tạo field mới trên entity → kiểm tra tất cả Groovy SQL + `TMSBillRecordConfig.tsx` tương ứng.

## Frontend convention

- UI column config cho `TMSBillList`: tập trung ở `webui/tms/src/app/logistics/tms/bill/TMSBillRecordConfig.tsx`, function `createTMSBillRecordConfig`.
- Khi sửa UI (TSX) phải check pattern trong cùng file trước khi thêm code mới (tránh style/convention drift).
- State management: Grid context (từ `@of1-webui/lib`) + local component state, không Redux.
- API client: không có service layer riêng — gọi trực tiếp qua `createHttpBackendCall('<ServiceName>', '<methodName>', params)`.

## Workflow design mới (từ 2026-10-09)

- Tất cả design feature mới → OpenSpec: `of1-tms-engineering-hub/openspec/changes/<change-name>/` với `proposal.md`, `tasks.md`, `specs/<capability>/spec.md`.
- Legacy design specs: `of1-tms-engineering-hub/specs/YYYY-MM-DD-<topic>-design.md` — immutable, migrate theo `openspec/MIGRATION_PLAN.md`.

## Nguồn tham chiếu

- Master index: `of1-tms/CLAUDE.md`
- Engineering hub (source of truth cho docs): `of1-tms-engineering-hub/`
  - Architecture: `of1-tms-engineering-hub/architecture.md`
  - Rules: `of1-tms-engineering-hub/rules/{backend,frontend,forgejo-workflow}.md`
  - Patterns + business decisions: `of1-tms-engineering-hub/patterns.md`, `business/decisions.md`
  - Quick reference (ports, endpoints): `of1-tms-engineering-hub/quick-reference.md`
  - OpenSpec config: `of1-tms-engineering-hub/openspec/config.yaml`
