# core Specification

## Purpose
Module nền tảng dùng chung cho toàn bộ OF1 TMS: domain entity nền (`TMSEmployee`, `TMSCompany`),
DAO base, auth, enum/constant nghiệp vụ, convention `SqlMapRecord` snake_case ↔ camelCase, và
sequence generator.

## Requirements

### Requirement: DAO base cho mọi Logic
Mọi Logic class trong các module khác SHALL extends `TMSDAOService` và chạy query Groovy SQL
qua `searchDbRecords`.

#### Scenario: Chạy Groovy SQL script
- **WHEN** một Logic gọi `searchDbRecords(scriptFile, "SearchXxx", sqlParams)`
- **THEN** SQL manager thực thi script và trả về `List<SqlMapRecord>` với key đã auto-convert sang camelCase

### Requirement: Convention snake_case ↔ camelCase
`SqlMapRecord` SHALL tự động convert tên cột snake_case trong SQL thành key camelCase khi map
result row.

#### Scenario: Map column `previous_fixed_charge`
- **WHEN** một Groovy SQL select cột `previous_fixed_charge`
- **THEN** record trả về có key `previousFixedCharge`
- **AND** entity Java tương ứng phải có `@Column(name = "previous_fixed_charge")`

### Requirement: Entity field luôn có @Column
Mọi field mới trên entity Java SHALL có `@Column` annotation tương ứng (bắt buộc, không optional).

#### Scenario: Thêm field mới trên `TMSBill`
- **WHEN** developer thêm field `excludeFromReports` vào `TMSEmployee`
- **THEN** field có `@Column(name = "exclude_from_reports")` để Groovy SQL dùng được
- **AND** nếu field xuất hiện trong report SQL, cột tương ứng phải tồn tại hoặc được migrate thêm

### Requirement: ClientContext là tham số đầu tiên
Mọi business method ở Logic/Service SHALL nhận `ClientContext client` làm tham số đầu tiên.

#### Scenario: Gọi service từ FE
- **WHEN** FE gọi `createHttpBackendCall('TMSBillService', 'searchTMSBills', { params })`
- **THEN** framework inject `ClientContext` cho method; FE không truyền tham số này
- **AND** permission check dựa trên `client.getPermissions()` từ Keycloak JWT

### Requirement: Sequence code generator
`TMSSequenceService` SHALL sinh unique code theo pattern `<company_id>_<prefix>_<sequence>`.

#### Scenario: Tạo bill code mới
- **WHEN** `TMSBillLogic.saveTMSBill` cần sinh `code` cho bill mới
- **THEN** gọi `TMSSequenceService.next(company_id, "BILL")` trả về code unique per company
