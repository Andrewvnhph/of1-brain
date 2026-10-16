<!--
  MIRROR — nguồn gốc ban đầu: /Users/admin/OF1/forgejo/of1-platform/of1-tms-engineering-hub/rules/backend.md
  Last synced: 2026-10-13.
  DIVERGENCE: bản này đã divergent khỏi engineering-hub do audit code thật phát hiện drift lớn
  (Spring Boot 3.3.3 → 3.5.10, Kafka inbound/self-async, @Transactional explicit manager thắng,
  Testcontainers tạm bỏ, env config còn 1 file). Cần push ngược về engineering-hub khi có cơ hội.
-->

# Backend Rules

## 1. Preferences & Conventions

- **No Emojis**: Never use emojis in code, comments, or PRs. Write like a normal human.
- **Keep it Simple**: Do not over-engineer. Focus on readability and match the surrounding code style.
- **Formatting**: Use 2 spaces for indentation. Keep lines at a readable length (typically under 100-120 characters) to avoid horizontal scrolling.
- **Imports**: Prefer wildcard imports (`import ...;`) or block imports. Do not use fully qualified class names inline unless resolving a collision.
- **Comments**: Keep them short. Explain the *WHY* and the *FLOW*, not the *WHAT*.
- **Naming**: Use strict `camelCase` for variables/methods, `PascalCase` for classes. Interfaces should not use the `I` prefix unless matching existing patterns.
- **Annotations**: Place Spring annotations on separate lines above the declaration.
- **ClientContext**: Every business Logic, Service, or Plugin method MUST accept `ClientContext client` as its first parameter. (Confirmed consistent across the codebase.)

---

## 2. Component & Layer Rules

### 2.1. Service → Logic → Repository (layering bắt buộc)

**Flow chuẩn:**

```
Service (@Service, transaction boundary + delegation)
   → Logic (*Logic, extends TMSDAOService, business + mutation)
      → Repository (JpaRepository, @Query cho PK lookup; Groovy SQL cho query động)
         → Entity (@Entity extends CompanyEntity / PersistableEntity / CompanyPersistable)
```

**Trách nhiệm từng tầng:**

| Tầng | Có | Không |
|------|-----|-------|
| **Service** | `@Transactional("tmsTransactionManager")`, delegate sang Logic, permission wrapping | **KHÔNG** inject Repository trực tiếp (trừ facade service pure delegate); **KHÔNG** chứa business logic |
| **Logic** | Business rules, validation, mutation entity, inject Repository + Logic khác; extends `TMSDAOService` | **KHÔNG** khai `@Transactional` (transaction thuộc Service — hiện có **6 chỗ vi phạm**: `GoertekDriverTripLogic`, `TMSJobTrackingLogic` → cần cleanup) |
| **Repository** | `JpaRepository<Entity, Long>`, `@Query` cho PK/unique lookup | **KHÔNG** `@Query` cho filter/search động → dùng Groovy SQL |

**3 pattern service đồng tồn tại** (chọn theo use case):

| Pattern | Khi nào dùng | Annotation | Transaction |
|---------|-------------|-----------|-------------|
| **Business service** (dominant) | Có business + mutation DB | `@Service("TMSXxxService")` + optional extends `BaseComponent` | Bắt buộc explicit `@Transactional("tmsTransactionManager")` |
| **Facade service** | Chỉ delegate sang Logic | `@Service(value = "TMSXxxService")` | **Không khai** `@Transactional` |
| **Kafka consumer** | Nhận event bất đồng bộ | **`@Component`** | `@Transactional("tmsTransactionManager")` **trên method `@KafkaListener`** |

- **Service naming**: luôn đặt tên tường minh (`@Service("MyEntityService")`). FE map theo tên bean.
- **Service inject Logic**, không inject Repository (ngoại lệ: facade service có thể bypass Logic nếu chỉ CRUD đơn giản — hiếm).
- **Logic inject Repository + Logic khác** (vd `TMSBillLogic` inject 5 Repository + 5 Logic khác).
- **Exception**: `CronJob`, `WebhookHandler`, `Controller`, `Plugin` được phép inject Repository trực tiếp (không qua Logic) vì chúng ở ngoài flow business chính (~15 instance hiện tại).
- **Dependency Injection**: field injection (`@Autowired`) là standard. Không constructor injection trừ khi thật cần.
- **Naming drift (minor)**: `MatchPriceService → MatchPriceManager` dùng `Manager` thay `Logic`. Khi tạo mới **ưu tiên** `*Logic`; `*Manager` chỉ chấp nhận ở integration code đã tồn tại.

### 2.1.1. `@RPCCall` annotation — chỉ thêm khi dev yêu cầu

**AI KHÔNG tự thêm `@RPCCall(allowedPaths = {...})`** vào service method. Pattern mặc định: `@Service` + `@Transactional` + method public là đủ cho FE call qua `createHttpBackendCall`.

**Khi nào thêm `@RPCCall`**: chỉ khi dev **yêu cầu rõ ràng** (vd muốn restrict scope cụ thể, expose public API, hoặc business requirement). Không tự assume cần.

**Lý do**: `@RPCCall(allowedPaths = { AccessPath.Private })` ngầm restrict access scope. Nếu set sai scope hoặc không cần, có thể block call hợp lệ hoặc expose nhầm. Dev biết context tốt hơn AI → để dev quyết định.

### 2.2. Transaction Management

- **Chỉ có 1 transaction manager**: `tmsTransactionManager` (defined ở `net.datatp.module.data.db.TMSJpaConfiguration`).
- **Rule**: Mọi `@Transactional` **phải khai tường minh** `"tmsTransactionManager"`:

  ```java
  // Write
  @Transactional("tmsTransactionManager")
  public void saveTMSBill(ClientContext client, TMSBill bill) { ... }

  // Read
  @Transactional(value = "tmsTransactionManager", readOnly = true)
  public List<SqlMapRecord> searchTMSBills(ClientContext client, ...) { ... }
  ```

- **Bare `@Transactional`** (không có manager) **là drift cần cleanup dần** — hiện codebase có ~50 chỗ còn bare (vs ~342 chỗ explicit). Khi touch code có bare, đồng thời sửa về explicit.

### 2.3. Save pattern — luôn `set(client, company)` trước `save()`

**🚫 HARD RULE**: trong Logic class, **mọi** `repo.save(entity)` **phải** được preceded bằng `entity.set(client, company)` ngay trước đó. Lý do: để propagate `companyId` + `ClientContext` xuống tất cả child cascade; `CompanyEntity.set()` enforce `@NotNull companyId` không null trước khi persist.

**✅ Pattern đúng:**
```java
public void saveTMSBill(ClientContext client, ICompany company, TMSBill bill) {
  // validate, enrich bill ...
  bill.set(client, company);              // ← bắt buộc trước save
  tmsBillRepo.save(bill);
}
```

**❌ Vi phạm hiện tại** cần cleanup (TMSBillLogic.java):
- Line **1070**: `setContainerNo()` + save (thiếu `.set(client, company)`)
- Line **1124**: `setDocumentCount()` + save (thiếu)
- Line **1131**: `setDocumentCount()` + save (thiếu)
- Line **1138**: `setDocumentSetId()` + save (thiếu)

Khi touch các method này, **đồng thời** sửa về đúng pattern.

**Base class helper**: hiện **chưa có** `TMSDAOService.saveEntity(client, company, entity)` wrapper. Mỗi Logic method tự gọi `set + save` thủ công. (Nếu refactor sau: cân nhắc thêm helper vào `TMSDAOService` để enforce rule compile-time.)

**Thứ tự call đúng**:
1. Build/enrich entity (set các field nghiệp vụ).
2. `entity.set(client, company)` — enforce company context + propagate xuống cascade children (xem §3.7).
3. `repo.save(entity)` — Hibernate persist root + cascade children.

### 2.4. Query Layer — Groovy SQL First

- **Default**: viết query ở `*Sql.groovy` dưới `<module>/groovy/`. Logic gọi qua `searchDbRecords(client, scriptDir, scriptFile, "ClassName", params)`, return `List<SqlMapRecord>`. Dùng helper macro có sẵn (`FILTER_BY_OPTION`, `AND_FILTER_BY_PARAM`, `AND_SEARCH_BY_PARAMS`, `MAX_RETURN`, …) cho filter company / storage_state / search params.

- **MUST register every new `ExecutableSqlBuilder` class** trong constructor của `*Sql` class (vd `register(new SearchTMSBill())`). Class chưa register sẽ im lặng fail runtime — **lỗi #1 khi thêm query mới**. Checklist: (1) class extends `ExecutableSqlBuilder`, (2) **register trong constructor**, (3) Logic gọi bằng string tên class khớp chính xác.

- **JPA `@Query` on Repository**: chỉ cho PK / unique-key lookup hoặc single-row mutation (`getById`, `getByLicensePlate`, `setVehiclesState`). **KHÔNG** dùng `@Query` cho: filterable search, multi-criteria sort, join entity, dynamic params → tất cả vào Groovy.

- **Logic signature**: return `List<SqlMapRecord>` (không `List<Entity>`) để FE/consumer đọc theo key auto-converted snake→camel.

- **Composable helpers trong `*Sql.groovy`** (pattern mới): method private trong `ExecutableSqlBuilder` trả `String` fragment hoặc `MapObject{selectFields, selectRuFields, joinQuery}` để compose join phức tạp. Vd `JOIN_TMS_BILL_JOB_TRACKING()`, `AND_FILTER_BY_PUSH_BFS_ONE_COST()`, `AND_FILTER_BY_LIST_VALUE()` trong `TMSBillSql.groovy`.

### 2.5. Entities & DTOs

- **Lombok**: `@Getter`, `@Setter`, `@NoArgsConstructor`. **Tránh `@Data`** (gây side-effect `equals`/`hashCode`).
- **Fields (Data Types)**: luôn dùng wrapper (`Long`, `Double`, `Integer`, `Boolean`) thay vì primitive — xử lý `null` sạch sẽ.
- **`@Column`**: luôn khai snake_case tường minh — `@Column(name = "job_tracking_id") private Long jobTrackingId;`. `SqlMapRecord` tự convert sang camelCase khi map result row.
- **Table indexes** (pattern mới): khai `@Index` trong `@Table(indexes = {...})` cho cột tra cứu nhiều — vd `TMSBill`:
  ```java
  @Table(name = TABLE_NAME, indexes = {
    @Index(name = TABLE_NAME + "_code_idx", columnList = "code"),
    @Index(name = TABLE_NAME + "_customer_id_idx", columnList = "customer_id"),
    ...
  })
  ```
- **Mapping từ `SqlMapRecord`**: đặt mapping logic ở static factory/helper trong DTO:
  ```java
  public static List<MyReport> computeFromMapRecords(List<SqlMapRecord> records) {
    // group, sum, transform
  }
  ```

### 2.6. Repository package & Spring scan registration (HARD RULE)

**Vấn đề**: `ModuleTMSCoreConfig.@EnableJpaRepositories.basePackages` (và các `Module*Config` khác) list **cụ thể từng package, KHÔNG recursive**. Repo đặt sai chỗ → Spring không scan thành bean → runtime fail:
```
Field repo in <Logic> required a bean of type '<Repository>' that could not be found.
```
Error chỉ xuất hiện khi khởi động BE, không bị TS/compile catch — rất dễ miss nếu không chạy BE.

**Convention bắt buộc khi thêm domain mới**:

1. **Package layout**: Repository **phải** nằm trong sub-package `<domain>.repository`.
   ```
   cloud.datatp.core.<domain>/
   ├── <Domain>Service.java
   ├── <Domain>Logic.java
   ├── entity/
   │   └── <Entity>.java
   └── repository/              ← Repository bắt buộc ở đây
       └── <Entity>Repository.java
   ```
   Không được đặt repo cùng level với Service/Logic (vd `cloud.datatp.core.xlsx.FooRepository` ❌).

2. **Register `@EnableJpaRepositories.basePackages`**: thêm `"cloud.datatp.core.<domain>.repository"` vào list trong `ModuleTMSCoreConfig` (hoặc `Module*Config` tương ứng với module chứa domain mới).
   ```java
   @EnableJpaRepositories(
     basePackages = {
       "cloud.datatp.core.employee.repository",
       ...
       "cloud.datatp.core.<domain>.repository",   // ← MỚI
     },
     ...
   )
   ```

3. **Component scan**: nhớ thêm `cloud.datatp.core.<domain>` vào `@ComponentScan.basePackages` cùng file (chỉ cần package gốc, scan recursive).

4. **Entity scan tự động**: `TMSJpaConfiguration.setPackagesToScan("cloud.datatp.core", ...)` **recursive**, nên entity ở `<domain>.entity.*` tự được pick up. KHÔNG cần register entity package.

**Pre-flight checklist khi thêm domain BE mới**:
- [ ] Repository ở `<domain>.repository.*Repository.java`?
- [ ] `ModuleTMSCoreConfig.basePackages` (JPA) đã thêm `<domain>.repository`?
- [ ] `ModuleTMSCoreConfig.basePackages` (ComponentScan) đã thêm `<domain>`?
- [ ] Khởi động BE thành công, không có `could not be found` error?

### 2.7. `MapObject` accessors — luôn dùng form có defaultVal (HARD RULE)

`net.datatp.util.ds.MapObject` dùng khắp Service/Logic cho request/response động. Các getter numeric/boolean **chỉ có overload `(key, defaultVal)`** — form bare `(key)` KHÔNG tồn tại hoặc **throw RuntimeException khi value null**:

| Method | Bare `(key)` | Có `(key, default)` |
|---|---|---|
| `getDouble` | ❌ không tồn tại | ✅ `getDouble(key, 0D)` / `null` |
| `getFloat`  | ❌ không tồn tại | ✅ `getFloat(key, 0F)` / `null` |
| `getLong`   | ❌ không tồn tại | ✅ `getLong(key, 0L)` / `null` |
| `getBoolean`| ❌ không tồn tại | ✅ `getBoolean(key, false)` / `null` |
| `getInteger`| ⚠ throw nếu null | ✅ `getInteger(key, 0)` / `null` |
| `getString` | ✅ wrapper `getString(key, null)` | ✅ `getString(key, "")` |

**Rule**: với **numeric** (`Double`, `Float`, `Long`, `Integer`, `Boolean`), **luôn** dùng form `getXxx(key, defaultValue)`. `defaultValue = null` nếu caller cần phân biệt absent vs 0, hoặc `0D`/`0L`/`false` nếu safe-default.

```java
// ❌ FAIL — getDouble(String) không tồn tại, compile error
Double cost = row.getDouble("fixedCost");

// ❌ RISK — getInteger(String) throws nếu value null
Integer rowNum = row.getInteger("_rowNumber");

// ✅ ĐÚNG
Double cost = row.getDouble("fixedCost", 0D);
Integer rowNum = row.getInteger("_rowNumber", null);  // allow null khi upstream chưa gửi
```

**String**: `getString(key)` an toàn (wrapper `getString(key, null)`) — dùng được, không bắt buộc default.

Khi thêm Service method nhận `MapObject`, grep lại pass code mới để verify 100% numeric getter đều có default.

---

## 3. Database & Entity Design (Domain-Driven Design)

Thống nhất nguyên tắc Aggregate (đang được áp dụng thật, không aspirational):

1. **Tách Database & Model**:
   - *Database* = nơi lưu trữ (schema, table, constraints) tối ưu đọc/ghi + integrity.
   - *Model (Entity)* = phản ánh logic nghiệp vụ, không bắt buộc map 1-1 table.

2. **Aggregate & Aggregate Root**:
   - *Aggregate* = cụm dữ liệu thống nhất (vd `TMSBill` + `TMSBillStopLocation` + `TMSBillFee` + `TMSBillCostItem`). Thao tác con **phải** đi qua root.

3. **Unidirectional Mapping**:
   - Entity con **không** chứa ref đối tượng cha. Nếu cần query, dùng Virtual Property read-only:
     `@Column(name = "goods_declaration_id", updatable = false, insertable = false)`.
   - Root chủ động map List con bằng `@JoinColumn`, **không** `mappedBy`.

4. **Parent-Controlled Save**:
   - **TUYỆT ĐỐI KHÔNG** `save()` entity con ở Service/Repository con.
   - Thêm/sửa/xoá child item qua helper của parent (`addItem()`, `clear()`, …) rồi `save()` **root**. Hibernate cascade lo phần còn lại.

5. **Transaction Integrity**:
   - Vòng đời Aggregate nguyên khối. Mọi thay đổi trong 1 `@Transactional("tmsTransactionManager")` với root → ACID + tránh Null FK.

6. **Thứ tự khai báo trong Entity Class**:
   - Fields (`@Column`, `@ManyToOne`, `@OneToMany`, …) **trước**.
   - Override methods (`@Override`) **sau fields** (sau vùng Lombok sinh getter/setter).
   - Helper methods (`addXxx()`, `removeXxx()`, `clearXxx()`, `withXxx()`) **cuối cùng**.

7. **Propagate Context qua `set(ClientContext, ICompany)` (bắt buộc, 15 entity đã implement)**:

   **Rule**: khi Aggregate Root có `@OneToOne` / `@OneToMany` / `@ManyToMany` cascade đến child entity, **phải override** `set(ClientContext, ICompany)` ở root để propagate xuống child. Logic propagate nằm trong **Entity**, không ở Service/Logic.

   **3 case propagate** tuỳ theo base class của child:

   | Child extends | Call tại parent |
   |--------------|-----------------|
   | `CompanyEntity` / `CompanyPersistable` / `PartnerCompanyEntity` | `set(client, company, child)` — propagate đầy đủ (company + client) |
   | `PersistableEntity<Long>` (không có companyId) | `child.set(client)` — chỉ client context, không có company |
   | `Collection<CompanyEntity>` (OneToMany/ManyToMany) | `set(client, company, collection)` — iterate hộ |

   **Helper có sẵn** trong `CompanyEntity` base class:
   - `set(ClientContext, ICompany, Collection<T> children)` — iterate + call child.set
   - `set(ClientContext, ICompany, T child)` — single entity

   **Ví dụ chuẩn** (`TMSBill.java:712-719`) — có cả 2 kiểu child:
   ```java
   @Override
   public void set(ClientContext client, ICompany company) {
     super.set(client, company);
     this.companyLabel = company.getLabel();
     set(client, company, stopLocations);           // @OneToMany<CompanyPersistable> — full propagate
     // Child extends chỉ PersistableEntity → không có companyId → set(client) only:
     if (tmsBillForwarderTransport != null) tmsBillForwarderTransport.set(client);
     if (tmsBillTransport != null) tmsBillTransport.set(client);
     if (tmsBillFee != null) tmsBillFee.set(client);
   }
   ```

   **Edge case** (TMSBillForwarderTransport): entity này extends `PersistableEntity<Long>` (**không** CompanyEntity), nên không có `companyId` cần propagate. Parent chỉ gọi `.set(client)` — **không phải bug**, là pattern chuẩn cho child không có company context.

   **Quy trình khi thêm cascade mới**:
   1. Kiểm child entity extends gì (`CompanyEntity` / `PersistableEntity` / …).
   2. Nếu extends `CompanyEntity` family → thêm `set(client, company, child)` vào override.
   3. Nếu chỉ `PersistableEntity` → thêm `child.set(client)` (không company).
   4. Nếu `@OneToMany` → dùng helper `set(client, company, collection)` cho toàn list.

   **Số liệu hiện tại**: `@OneToMany`: 30 instances; `@ManyToMany`: 1 (commented out). 15 entity đã override `set(client, company)`:
   `TMSBill`, `TMSPartner`, `TMSCustomer`, `TMSTableColumnConfig`, `TMSJobTracking`, `CustomerTransportPricing`, `CustomerTransportPricingBatch`, `ContainerDeposit`, `VehicleTrip`, `VehicleTripGoodsTracking`, `TMSOperations`, `TMSVendorRouteTarget`, `TMSVendorProfile`, `TMSVendorProfileStep2`, `TMSVendorBill`.

---

## 4. Kafka Pattern (TMS self-async + inbound)

**Scope Kafka trong TMS** — không phải "RPC-only" như rule cũ:

| Hướng | Dùng | Lý do |
|-------|------|-------|
| TMS → `of1-platform` | **RPC** qua `app/api` | Sync, cần response trực tiếp |
| External → TMS (vd document service) | **Kafka inbound** | Async, decouple |
| TMS self-async (produce + consume own topic) | **Kafka** | Retry pattern, async processing |

### 4.1. Consumer

- **Annotation**: `@Component` (**không** `@Service`) + `@KafkaListener(topics, id, concurrency, containerFactory)` trên method listener.
- **Transaction**: `@Transactional("tmsTransactionManager")` **trên chính method listener**.
- **Example**: `InvoiceExtractedDataKafkaConsumer.java`:
  ```java
  @Component
  public class InvoiceExtractedDataKafkaConsumer {
    @KafkaListener(
      topics = "${kafka.document.topic.invoice-extracted-data}",
      id = "...", concurrency = "...", containerFactory = "..."
    )
    @Transactional("tmsTransactionManager")
    public void receive(ConsumerRecord<String, String> record) { ... }
  }
  ```

### 4.2. Producer

- Wrap `KafkaTemplate.send(topic, msg)` trong class dedicated `*KafkaProducer` (vd `TrackingSyncKafkaProducer`).
- Logic class inject producer, gọi `producer.send(...)`.
- **Fallback inline**: nếu `kafka.queue-enable=false` (mặc định), producer fallback chạy logic consumer inline (không qua Kafka). Vd `TrackingSyncKafkaProducer:44-46`.

### 4.3. Topic naming + config

- Topic format: `datatp.${env.name}.tms.<purpose>` (vd `datatp.prod.tms.tracking-sync`).
- Config ở `addon-tms-config.yaml` section `kafka:` với toggle enable/disable per topic (xem #6).

### 4.4. Current consumers / producers inventory

- **Inbound** (external → TMS):
  - `InvoiceExtractedDataKafkaConsumer` — topic `tms.invoice-extracted-data` (từ document service).
- **Self-async** (TMS produce + consume own):
  - `TrackingSyncKafkaProducer` → `TrackingSyncKafkaConsumer.receive()` — topic `tms.tracking-sync`.
  - Retry: `TrackingSyncKafkaConsumer.receiveRetry()` — topic `tms.tracking-sync-retry`.

---

## 5. Testing Conventions

- **Test Naming**: class **phải** đặt tên `*UnitTest` hoặc `*IntegrationTest` để task `test` mặc định pick lên.
- **Test Tags**: `@Tag("unit")` cho unit, `@Tag("integration")` cho integration. Tránh naming mâu thuẫn tag (vd `*UnitTest` tag `integration`).
- **Unit test pattern (dominant hiện tại)**:
  - **Mockito** (không `@SpringBootTest`).
  - Setup qua `ReflectionTestUtils.setField(target, "fieldName", mock)` để inject mock vào field `@Autowired`.
  - `@BeforeEach` tạo instance + inject mock.
  - Vd: `NotificationServiceUnitTest`, `TMSLocationSettingsLogicUnitTest`.
- **Testcontainers**: **tạm thời chưa dùng**. Khi reintroduce (PostgreSQL/Kafka/MSSQL), update rule này.

---

## 6. Architecture & Framework

- **Java 21** (`VERSION_21`).
- **Spring Boot 3.5.10** / Spring Framework **6.2.15**.
- **Hibernate 6.4.4.Final**.
- **Jetty 12.0.31**.
- **Lombok 1.18.42**.
- **Gradle multi-module** (9.2.x).
- **PostgreSQL** (JDBC 42.7.3) + **Kafka** (xem #4).
- **Debezium (CDC)**: có trong platform stack, TMS consume event qua Kafka khi cần.

---

## 7. Environment Configuration

**Chỉ còn 1 file**: `release/src/app/server/addons/tms/config/addon-tms-config.yaml`. (Các layer `env.sh` / `application-env.yaml` legacy đã không còn trong scope TMS.)

### Pattern config

- Khai các giá trị default + per-environment override trong cùng file.
- Dùng placeholder `${env.name}` để resolve env name.

### Example — Kafka toggle

```yaml
kafka:
  queue-enable: false                   # Default: fallback inline, không gọi Kafka
  document:
    invoice-extracted-consumer-enable: false
    topic:
      invoice-extracted-data: "datatp.${env.name}.tms.invoice-extracted-data"
  topic:
    tracking-sync:       "datatp.${env.name}.tms.tracking-sync"
    tracking-sync-retry: "datatp.${env.name}.tms.tracking-sync-retry"
```

Trong `beta` profile → bật `invoice-extracted-consumer-enable`. Trong `prod` → bật cả 2 consumer.

### Thêm config mới

1. Thêm key dưới section tương ứng (vd `kafka.<domain>.<key>`).
2. Khai per-environment override ở section env tương ứng trong cùng file.
3. Inject vào bean qua `@Value("${kafka.xxx}")` hoặc `@ConfigurationProperties`.

---

## 8. Facade Service Pattern (bổ sung)

Khi tạo service **chỉ delegate** (không business, không transaction), dùng pattern này:

- `@Service(value = "TMSXxxService")` — tên tường minh để FE map vào bean.
- **KHÔNG** extends `BaseComponent`.
- **KHÔNG** `@Transactional` ở service — transaction nằm trong Logic/Repository được gọi.
- Field inject dependency như thường.

**Example**: `TMSPrintService` chỉ nhận request `createLetterOfAuthorizationPrint(client, …)` và delegate sang Logic để build PDF — không có DB mutation ở service layer.

---

## 9. Quick Reference — Checklist khi thêm feature mới

### Layering
- [ ] Service tên tường minh `@Service("TMSXxxService")` + `@Transactional("tmsTransactionManager")` (nếu business) hoặc không khai transaction (nếu facade).
- [ ] Service inject **Logic** (không inject Repository trực tiếp, trừ facade pure delegate).
- [ ] Logic extends `TMSDAOService`, inject Repository + Logic khác, **KHÔNG** khai `@Transactional` ở method.
- [ ] Repository `JpaRepository<Entity, Long>`, `@Query` chỉ cho PK/unique-key lookup.
- [ ] Mọi business method nhận `ClientContext client` **đầu tiên** (write) hoặc `(ClientContext client, ICompany company)` khi save.
- [ ] Repository đặt ở `<domain>.repository.*Repository.java` **và** đã register `<domain>.repository` vào `ModuleTMSCoreConfig.@EnableJpaRepositories.basePackages` (xem §2.6).
- [ ] Mọi `MapObject.getDouble/Float/Long/Integer/Boolean(...)` dùng form `(key, defaultValue)` — bare form KHÔNG tồn tại hoặc throw khi null (xem §2.7).

### Entity
- [ ] `@Getter/@Setter/@NoArgsConstructor` + wrapper types (`Long`, `Boolean`) + `@Column(name = "snake_case")` + `@Index` nếu cần tra cứu nhiều.
- [ ] Aggregate Root có cascade (`@OneToOne`/`@OneToMany`/`@ManyToMany`):
  - Override `set(ClientContext, ICompany)` ở root.
  - Child extends `CompanyEntity` family → `set(client, company, child)` hoặc `set(client, company, collection)`.
  - Child chỉ extends `PersistableEntity` → `child.set(client)` (không company).

### Save pattern (HARD RULE)
- [ ] **Mọi `repo.save(entity)` trong Logic PHẢI preceded bằng `entity.set(client, company)`** ngay trước đó.
- [ ] Thứ tự: build/enrich → `entity.set(client, company)` → `repo.save(entity)`.

### Query
- [ ] Filter/search động → Groovy SQL ở `<module>/groovy/*Sql.groovy`, **register trong constructor**, Logic gọi `searchDbRecords(client, scriptDir, scriptFile, "ClassName", params)`.
- [ ] Return `List<SqlMapRecord>` (không entity).
- [ ] PK/unique lookup → JPA `@Query` trên Repository.

### Kafka
- [ ] Consumer: `@Component` + `@KafkaListener` + `@Transactional("tmsTransactionManager")` trên method.
- [ ] Producer: wrap trong `*KafkaProducer` class, fallback inline khi `queue-enable=false`.

### Config
- [ ] Config mới → thêm vào `addon-tms-config.yaml` + per-env override.

### Testing
- [ ] Unit test `*UnitTest.java` + `@Tag("unit")` + Mockito + `ReflectionTestUtils.setField(...)`, không `@SpringBootTest`.
