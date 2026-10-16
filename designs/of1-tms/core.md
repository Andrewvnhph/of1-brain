# Design — core (hiện trạng)

Module nền tảng dùng chung cho toàn bộ OF1 TMS. Cung cấp domain entities + hạ tầng DAO;
mọi Logic class ở các module khác extends `TMSDAOService` từ đây.

## Boundary

- Package gốc `cloud.datatp.tms.core` (+ `net.datatp.logistics.*`).
- Chứa domain entity nền tảng (`TMSEmployee`, `TMSCompany`, các enum/constant), auth hook, cấu hình chung.
- Là dependency của mọi module khác (`bill`, `fleet`, `vendor`, `ops`, `integration`, `notification`).

## Sub-packages

| Package | Trách nhiệm |
|---|---|
| `entity` | Domain entity nền: `TMSEmployee` (với các flag như `excludeFromReports`), `TMSCompany`, enum nghiệp vụ |
| `db` | DAO hạ tầng: `TMSDAOService` (base cho mọi Logic), SQL query manager, Groovy SQL loader |
| `groovy` | Groovy SQL script động cho query phức tạp — dùng `SqlMapRecord` (auto snake_case ↔ camelCase) |
| `auth` | Keycloak integration, permission check, ClientContext |
| `config` | TMS system config, company config, feature flags |
| `common` | Enum/constant chung: `TMSBillType` (IMS/FORWARDER), `TMSBillProcessStatus`, `TransportationMode`, `ContainerType`… |
| `sequence` | `TMSSequenceService` cho code generation (bill code, HBL no...) |

## Data model chính

- `TMSEmployee` — nhân viên TMS; có flag `excludeFromReports` (ẩn khỏi BillReport/BillApiLogReport khi deactivated).
- `TMSCompany` — tenant / tổ chức; mọi entity nghiệp vụ có `company_id`.
- Các enum nghiệp vụ: `TMSBillType {IMS, FORWARDER}`, `TMSBillProcessStatus {PLAN, PENDING, PROCESSING, DONE, CANCELED}`, `TransportationMode`, `ContainerType`, `CustomsChannel {GREEN, YELLOW, RED}`.

## Luồng chính

- **DAO base**: mọi Logic ở module khác extends `TMSDAOService` → gọi `searchDbRecords(scriptFile, "QueryName", params)` để chạy Groovy SQL.
- **Snake_case ↔ camelCase**: `SqlMapRecord` tự convert khi map result row (vd `previous_fixed_charge` → `previousFixedCharge`).
- **Auth / Context**: mọi business method nhận `ClientContext client` đầu tiên; permission check dựa trên Keycloak claim.
- **Sequence**: `TMSSequenceService` sinh unique code (`<company_id>_<prefix>_<sequence>`).

## Ghi chú mở rộng

- Thêm field entity → **bắt buộc** thêm `@Column`; nếu dùng trong Groovy SQL thì khớp snake_case.
- Thêm enum/constant dùng chung → đặt ở `common`, không nhân bản trong module khác.
- Thêm permission type → cập nhật ở `auth` + Keycloak role mapping.
