# Design: Liquibase Integration cho module/tms/core

> **Loại**: Design + Implementation plan
> **Scope**: `module/tms/core` only — các module khác (bill, ops...) KHÔNG nằm trong scope này.
> **Branch**: `ai/liquibase-integration` (khi implement)
> **Prereq**: research-db-migration.md

---

## 1. Hiện trạng — tms-core

4 SQL migration files hiện tại trong `module/tms/core/src/main/resources/db/migration/`:

```
V__add_goertek_driver_trip_token_indexes.sql
V__add_invoice_vat_to_tms_partner.sql
V__drop_tms_partner_account_id_constraint.sql
V__drop_tms_partner_odoo_partner_code_column.sql
```

Vấn đề hiện tại:
- Dev chạy tay, không có cơ chế tự động, dễ quên khi deploy
- Không có audit trail — không biết file nào đã chạy trên môi trường nào
- Naming `V__` không có số → không tương thích Flyway

---

## 2. Kiến trúc

### 2.1 Cấu trúc thư mục mới trong tms-core

```
module/tms/core/src/main/resources/
  db/
    changelog/
      db.changelog-master.xml       ← entry point Liquibase
      changes/
        001-goertek-driver-indexes.sql
        002-add-invoice-vat-partner.sql
        003-drop-partner-account-id.sql
        004-drop-partner-odoo-code.sql
```

Thư mục `db/migration/` cũ giữ nguyên (không xóa) để tham khảo — Liquibase dùng `db/changelog/` mới.

### 2.2 Master changelog XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.27.xsd">

    <include file="db/changelog/changes/001-goertek-driver-indexes.sql"
             relativeToChangelogFile="false"/>
    <include file="db/changelog/changes/002-add-invoice-vat-partner.sql"
             relativeToChangelogFile="false"/>
    <include file="db/changelog/changes/003-drop-partner-account-id.sql"
             relativeToChangelogFile="false"/>
    <include file="db/changelog/changes/004-drop-partner-odoo-code.sql"
             relativeToChangelogFile="false"/>

</databaseChangeLog>
```

### 2.3 SQL file format (Liquibase formatted SQL)

Thêm 2 dòng header vào đầu mỗi file — nội dung SQL **không đổi**:

```sql
--liquibase formatted sql
--changeset mchien:001-goertek-driver-indexes
CREATE INDEX IF NOT EXISTS idx_goertek_driver_trip_token ON lgc_tms_driver_trip (token);
--rollback DROP INDEX IF EXISTS idx_goertek_driver_trip_token;
```

```sql
--liquibase formatted sql
--changeset mchien:003-drop-partner-account-id
ALTER TABLE lgc_tms_partner DROP COLUMN IF EXISTS account_id;
--rollback ALTER TABLE lgc_tms_partner ADD COLUMN account_id BIGINT;
```

### 2.4 Gradle dependency

```gradle
// module/tms/core/build.gradle
implementation 'org.liquibase:liquibase-core:4.27.0'
```

### 2.5 Spring Boot config

Config trong application yml của TMS app (không phải trong `core/build.gradle`):

```yaml
spring:
  liquibase:
    enabled: true
    change-log: classpath:db/changelog/db.changelog-master.xml
    database-change-log-table: liquibase_changelog
    database-change-log-lock-table: liquibase_changelog_lock
```

---

## 3. Migration plan — từ SQL manual → Liquibase

### Bước 1 — Thêm dependency
`module/tms/core/build.gradle` thêm `liquibase-core`.

### Bước 2 — Tạo cấu trúc changelog
Tạo thư mục `db/changelog/changes/` trong `module/tms/core/src/main/resources/`.

### Bước 3 — Convert 4 SQL files
Thêm header `--liquibase formatted sql` + `--changeset` + `--rollback` vào đầu mỗi file.

### Bước 4 — Tạo master changelog XML
File `db.changelog-master.xml` include 4 changeset theo thứ tự.

### Bước 5 — Config Spring Boot
Thêm block `spring.liquibase` vào `application.yml` của TMS app.

### Bước 6 — Baseline DB đang chạy
Vì DB đã có schema sẵn, chạy 1 lần để mark tất cả changeset là "already ran":
```bash
liquibase --changelog-file=db.changelog-master.xml changelogSync
```
Hoặc dùng `runOnChange="false"` + precondition `onFail="MARK_RAN"` trong mỗi changeset.

### Bước 7 — Test local
Restart TMS app, verify bảng `liquibase_changelog` được tạo và 4 rows được insert.

---

## 4. Naming convention (từ nay về sau)

```
{yyyyMMddHHmmss}-{description}.sql

Ví dụ:
20261112163000-add-description-document-log.sql
```

- `yyyyMMddHHmmss` = **datetime thực tế** khi tạo file (không dùng `000000` hay số tuần tự)
- Nếu tạo nhiều changeset cùng ngày → dùng `HHmmss` khác nhau (giờ:phút:giây thực tế)
- **changeset id** bên trong file = tên file không có `.sql` (vd `--changeset mchien:20261112163000-add-description-document-log`)
- **author** = tên dev commit (vd `mchien`)
- **Rollback bắt buộc** với mọi changeset ALTER/ADD/CREATE.

---

## 5. Task plan

| Task | Nội dung | Effort |
|---|---|---|
| T1 | Thêm `liquibase-core` vào `core/build.gradle` | 5 phút |
| T2 | Tạo `db/changelog/changes/` structure | 5 phút |
| T3 | Convert 4 SQL files → Liquibase format (header + rollback) | 20 phút |
| T4 | Tạo `db.changelog-master.xml` include 4 files | 10 phút |
| T5 | Config `spring.liquibase` trong `application.yml` | 10 phút |
| T6 | Chạy `changelogSync` baseline DB dev | 10 phút |
| T7 | Test restart app, verify `liquibase_changelog` table | 15 phút |
| T8 | Viết convention vào `backend.md` §DB Migration | 10 phút |

**Tổng**: ~1.5 giờ

---

## 6. Rủi ro & Giải pháp

| Rủi ro | Giải pháp |
|---|---|
| DB production đã có schema, Liquibase detect "not ran" | Chạy `changelogSync` trước khi enable — mark tất cả là đã chạy |
| `liquibase_changelog_lock` bị stuck khi app crash | `liquibase releaseLocks` trước khi restart app |
| Dev quên thêm rollback | Checklist review: mọi changeset ALTER/ADD/CREATE phải có `--rollback` |

---

## 7. Đã xác nhận

- `application.yml` TMS app: **`release/`**
- Platform BE dùng Liquibase trên **DB riêng** → không conflict table name → giữ default `databasechangelog` / `databasechangeloglock`.
