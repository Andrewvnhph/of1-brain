# Research: DB Migration Tools — Liquibase, Flyway & alternatives

> **Loại**: Research only — không có code/openspec.
> **Mục tiêu**: So sánh các tool DB migration, áp dụng vào of1-tms thay thế SQL manual hiện tại.

---

## 1. Vấn đề hiện tại của of1-tms

Hiện tại of1-tms dùng pattern **SQL manual**: dev tự viết file `V__<desc>.sql` và chạy tay trên DB. Rủi ro:
- Dễ quên chạy khi deploy lên staging/prod
- Không có audit trail "ai chạy migration nào lúc mấy giờ"
- Team mới join không biết thứ tự chạy SQL
- Không rollback được nếu migration lỗi nửa chừng

---

## 2. Flyway

### Giới thiệu
Tool đơn giản nhất — convention over configuration. Đặt file SQL vào đúng thư mục, Flyway tự chạy khi app start.

### Cách hoạt động
- Scan thư mục `classpath:db/migration/`
- Chạy các file chưa được chạy theo thứ tự version
- Lưu lịch sử vào bảng `flyway_schema_history`

### Naming convention
```
V1__init_schema.sql
V2__add_booking_forwarder.sql
V2.1__add_bfs_hawb_status.sql
R__refresh_view.sql          ← repeatable (chạy lại mỗi lần thay đổi)
U2__undo_booking_forwarder.sql  ← undo (Flyway Pro)
```

### Spring Boot integration
```yaml
# application.yml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true   # cho DB đã có sẵn data
```

```gradle
// build.gradle
implementation 'org.flywaydb:flyway-core'
```

### Ưu điểm
- **Cực đơn giản** — chỉ cần đặt file SQL đúng chỗ
- Spring Boot auto-configure, chạy khi app start
- Hỗ trợ PostgreSQL, MySQL, Oracle...
- Community edition free, đủ dùng cho hầu hết case

### Nhược điểm
- Chỉ dùng SQL thuần (không có XML/YAML DSL như Liquibase)
- Rollback/Undo chỉ có ở bản Pro (trả tiền)
- Khó conditional migration (chạy khác nhau tùy môi trường)

---

## 3. Liquibase

### Giới thiệu
Mạnh hơn Flyway, hỗ trợ nhiều format (XML, YAML, JSON, SQL), có rollback built-in ở bản Community.

### Cách hoạt động
- Dùng file `changelog` định nghĩa các `changeSet`
- Mỗi changeSet có `id` + `author` unique → Liquibase track bằng hash
- Lưu lịch sử vào `databasechangelog` + `databasechangeloglock`

### Format XML (phổ biến nhất)
```xml
<!-- db/changelog/db.changelog-master.xml -->
<databaseChangeLog>
    <include file="changes/v1-init.xml"/>
    <include file="changes/v2-booking-forwarder.xml"/>
</databaseChangeLog>

<!-- changes/v2-booking-forwarder.xml -->
<databaseChangeLog>
    <changeSet id="v2-add-booking-forwarder" author="mchien">
        <addColumn tableName="lgc_tms_bill">
            <column name="bf_partner_id" type="BIGINT"/>
            <column name="bf_partner_name" type="VARCHAR(255)"/>
        </addColumn>
        <rollback>
            <dropColumn tableName="lgc_tms_bill" columnName="bf_partner_id"/>
            <dropColumn tableName="lgc_tms_bill" columnName="bf_partner_name"/>
        </rollback>
    </changeSet>
</databaseChangeLog>
```

### Format SQL (gần giống Flyway)
```sql
-- db/changelog/changes/v2-booking-forwarder.sql
--liquibase formatted sql
--changeset mchien:v2-add-booking-forwarder
ALTER TABLE lgc_tms_bill ADD COLUMN bf_partner_id BIGINT;
ALTER TABLE lgc_tms_bill ADD COLUMN bf_partner_name VARCHAR(255);
--rollback ALTER TABLE lgc_tms_bill DROP COLUMN bf_partner_id;
--rollback ALTER TABLE lgc_tms_bill DROP COLUMN bf_partner_name;
```

### Spring Boot integration
```yaml
spring:
  liquibase:
    enabled: true
    change-log: classpath:db/changelog/db.changelog-master.xml
```

```gradle
implementation 'org.liquibase:liquibase-core'
```

### Ưu điểm
- **Rollback built-in** (free) — cực kỳ quan trọng cho production
- Multi-format: XML/YAML/JSON/SQL — linh hoạt
- Conditional migration (`context`, `label`) — chạy khác nhau cho dev/prod
- Diff tool — so sánh 2 DB schema, tự generate changelog
- Mạnh hơn với complex migration

### Nhược điểm
- Phức tạp hơn Flyway, learning curve cao hơn
- XML verbose
- `databasechangeloglock` đôi khi bị stuck khi app crash giữa migration

---

## 4. So sánh Flyway vs Liquibase

| | Flyway | Liquibase |
|---|---|---|
| **Độ phức tạp** | Thấp | Trung bình |
| **Format** | SQL only (Community) | XML, YAML, JSON, SQL |
| **Rollback** | Pro only | Free (nếu định nghĩa) |
| **Spring Boot** | Auto-configure | Auto-configure |
| **Tracking** | Version number (`V2__`) | id + author hash |
| **Conditional** | Không | Có (context/label) |
| **Phổ biến** | Rất phổ biến | Phổ biến |
| **License** | Community free | Community free |
| **Phù hợp** | Simple project, SQL thuần | Complex migration, cần rollback |

---

## 5. Các tool khác (ít phổ biến hơn)

| Tool | Stack | Ghi chú |
|---|---|---|
| **Alembic** | Python/SQLAlchemy | Python projects |
| **Django Migrations** | Python/Django | Built-in Django |
| **ActiveRecord Migrations** | Ruby on Rails | Built-in Rails |
| **golang-migrate** | Go | CLI + library |
| **Prisma Migrate** | Node.js | ORM-based |
| **Atlas** | Go/Any | Schema-as-code, mới nổi |

→ Với Java/Spring Boot, chỉ cần quan tâm **Flyway** hoặc **Liquibase**.

---

## 6. Khuyến nghị cho of1-tms

### Lựa chọn: **Flyway**

**Lý do**:
1. of1-tms đã có convention đặt tên file `V__<desc>.sql` → **migrate sang Flyway gần như zero effort** (chỉ cần đổi naming và thêm dependency)
2. Team đang dùng SQL thuần → không cần XML/YAML DSL của Liquibase
3. Đơn giản hơn, ít config hơn, dễ onboard dev mới
4. Rollback: của1-tms có thể xử lý bằng cách viết `V__rollback_<desc>.sql` riêng thủ công nếu cần

### Migration plan từ SQL manual → Flyway

**Bước 1**: Thêm dependency vào `build.gradle` module `core`:
```gradle
implementation 'org.flywaydb:flyway-core'
implementation 'org.flywaydb:flyway-database-postgresql'
```

**Bước 2**: Config trong `application.yml`:
```yaml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: true  # QUAN TRỌNG: DB đã có data sẵn
    baseline-version: 0
    table: flyway_schema_history
```

**Bước 3**: Đặt tất cả SQL migration hiện có vào `src/main/resources/db/migration/` với naming chuẩn:
```
V1__init_baseline.sql         ← SQL dump schema hiện tại (baseline)
V2__add_booking_forwarder.sql
V3__add_bfs_hawb_status.sql
...
```

**Bước 4**: Với DB đang chạy, dùng `baseline-on-migrate: true` → Flyway sẽ coi schema hiện tại là baseline, chỉ chạy migration mới từ đây về sau.

### Lưu ý quan trọng
- **KHÔNG** chạy SQL migration thủ công nữa sau khi enable Flyway
- Mỗi migration file là **immutable** — không được sửa file đã chạy (Flyway verify bằng checksum)
- Môi trường dev/staging/prod phải chạy cùng migration files

---

## 7. Tài liệu tham khảo

- **Flyway docs**: flywaydb.org/documentation
- **Liquibase docs**: docs.liquibase.com
- **Spring Boot + Flyway guide**: docs.spring.io/spring-boot/docs/current/reference/html/howto.html#howto.data-initialization.migration-tool.flyway
- **So sánh chi tiết**: baeldung.com/flyway-vs-liquibase
