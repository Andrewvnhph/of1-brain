# TMS Webhook — Tách HTTP khỏi Transaction (Option B) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Loại bỏ `ObjectOptimisticLockingFailureException` trên `VehicleTripGoodsTracking` phát sinh từ `TrackingSyncKafkaConsumer` bằng cách tách external HTTP call ra khỏi transaction JPA.

**Architecture:** Chia method `TMSWebhookLogic.syncVendorBillWithVehicleTripGoodsTrackings` thành 3 phase:
- **Phase A** (read-only `@Transactional`) — load snapshot vào DTO rồi detach.
- **Phase B** (NO transaction) — gọi webhook HTTP.
- **Phase C** (short write `@Transactional`) — bulk UPDATE 2 field `refId` + `webhookPushSuccess` qua `@Modifying` query sẵn có, bypass `@Version`.

Phase A & C đặt trong một bean riêng `TMSWebhookTxOps` để `@Transactional` không bị vô hiệu bởi Spring self-invocation. `TMSWebhookLogic` còn lại thành orchestrator, không có `@Transactional`.

**Tech Stack:** Java, Spring Boot, Hibernate/JPA, `tmsTransactionManager`, Kafka listener, JUnit 5 + Mockito.

**Spec:** Phân tích root cause trong hội thoại ngày 2026-10-26 (file này là spec duy nhất). Error reference: `ERROR 92692 ... TrackingSyncKafkaConsumer : TrackingSync fail (retry=0) count=1 err=Row was updated or deleted by another transaction : [cloud.datatp.ops.trip.entity.VehicleTripGoodsTracking#191478]`.

**Repo mục tiêu:** `/Users/admin/OF1/forgejo/of1-platform/of1-tms` (plan này sống ở `of1-brain`, implementation ở `of1-tms`).

## Global Constraints

- Transaction manager name: `tmsTransactionManager` (phải truyền vào mọi `@Transactional`).
- Entity `VehicleTripGoodsTracking` kế thừa `PersistableEntity` → có `@Version Long version`. KHÔNG được bỏ `@Version`; chỉ được bypass qua `@Modifying` bulk update cho 2 field `refId` + `webhookPushSuccess`.
- Phải tạo branch `ai/*` trước khi commit (pre-commit hook grep `^ai/` fail-fast — xem memory `feedback_git_pre_commit_branch_check`).
- Giữ nguyên behavior cho các source gọi `goodsTrackingLogic.saveVehicleTripGoodsTracking(...)` ngoài webhook consumer.
- JUnit 5 (`org.junit.jupiter.api`) — follow pattern tại `RouteOptimizeLogicUnitTest.java`.
- Build system: Gradle. Module path: `of1-tms/module/tms/ops`.
- Package base: `cloud.datatp.ops.webhook`.
- Logger: `lombok @Slf4j` (consumer đã dùng pattern này).

## Review Focus

Các vùng input/failure spec này không bao phủ bằng test đơn lẻ — đã gắn test vào task tương ứng:

1. **Retry topic + main topic chạy song song cùng tracking** — cả `receive` và `receiveRetry` cùng gọi `handle(...)`. Dù mỗi listener `concurrency=1`, nhưng là 2 listener khác nhau → 2 thread. Nếu main đang xử lý tracking X và retry pop lại chính X, có thể vẫn race. Test ở Task 6 phải cover trường hợp 2 thread song song cùng tracking.
2. **Idempotency replay** — nếu Phase C commit xong nhưng Kafka offset chưa commit → message replay → vendor nhận duplicate push. Test ở Task 4 phải assert orchestrator tolerate replay (`refId` set 2 lần với cùng giá trị không gây lỗi).
3. **Empty / null `trackings` input** — hiện tại consumer đã early-return, nhưng sau refactor orchestrator phải bảo tồn behavior này. Test ở Task 4.
4. **Vendor webhook timeout / 5xx** — Phase B throw exception → Phase C KHÔNG được chạy; message rơi về retry topic. Test ở Task 4.
5. **Partial batch failure trong Phase C** — một trong `updateRefId` fail SQL (ví dụ `refId` quá lớn). Phase C phải log + continue cho các id còn lại, không roll back toàn batch. Test ở Task 3.

---

## File Structure

**Create (in `of1-tms/module/tms/ops/src/main/java/cloud/datatp/ops/webhook/`):**
- `dto/TMSWebhookBatch.java` — detached snapshot cho 1 TMSBill (customer, bill, vendorBill, goodsTrackings MapObject list, attemptedIds).
- `dto/TMSWebhookPersistCommand.java` — kết quả Phase B dùng cho Phase C (`Map<Long,Long> idToRefId`, `Set<Long> successIds`, `Set<Long> attemptedIds`).
- `TMSWebhookTxOps.java` — bean mới chứa 2 method `@Transactional`.

**Create (in `of1-tms/module/tms/ops/src/test/java/cloud/datatp/ops/webhook/`):**
- `TMSWebhookTxOpsUnitTest.java`
- `TMSWebhookLogicOrchestrationUnitTest.java`
- `TMSWebhookRaceIntegrationTest.java` (có thể Disabled nếu infra DB thiếu — xem Task 6).

**Modify:**
- `cloud/datatp/ops/webhook/TMSWebhookLogic.java` — refactor method `syncVendorBillWithVehicleTripGoodsTrackings` (lines 90-192) thành orchestrator.
- `cloud/datatp/ops/trip/kafka/TrackingSyncKafkaConsumer.java` — bỏ `@Transactional("tmsTransactionManager")` ở line 70.

**Dùng lại không sửa:**
- `VehicleTripGoodsTrackingRepository.updateRefId(companyId, id, refId)` (line 71-73).
- `VehicleTripGoodsTrackingRepository.updateWebhookPushSuccess(companyId, ids, success)` (line 67-69).

---

### Task 1: Thêm DTO `TMSWebhookBatch` + `TMSWebhookPersistCommand`

**Files:**
- Create: `of1-tms/module/tms/ops/src/main/java/cloud/datatp/ops/webhook/dto/TMSWebhookBatch.java`
- Create: `of1-tms/module/tms/ops/src/main/java/cloud/datatp/ops/webhook/dto/TMSWebhookPersistCommand.java`

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `TMSWebhookBatch`: constructor `(TMSPartner customer, TMSBill tmsBill, TMSVendorBill vendorBill, List<MapObject> goodsTrackings, List<Long> attemptedIds)` + getters bằng Lombok `@Value` hoặc `@Data`.
  - `TMSWebhookPersistCommand`: constructor `(List<Long> attemptedIds, Map<Long,Long> idToRefId)` + getter `attemptedIds()`, `idToRefId()`, derived `successIds()` = keyset.

- [ ] **Step 1: Tạo `TMSWebhookBatch` POJO**

Dùng Lombok `@Value` (immutable) hoặc `@Data` cho đồng bộ với codebase. Field list đúng như Produces block ở trên. Không có logic.

- [ ] **Step 2: Tạo `TMSWebhookPersistCommand` POJO**

Dùng Lombok `@Value`. Field: `List<Long> attemptedIds`, `Map<Long,Long> idToRefId`. Thêm method `Set<Long> successIds() { return idToRefId.keySet(); }`.

- [ ] **Step 3: Compile check**

Run: `./gradlew :module:tms:ops:compileJava`
Expected: BUILD SUCCESSFUL.

- [ ] **Step 4: Commit**

```bash
git checkout -b ai/webhook-tx-split
git add module/tms/ops/src/main/java/cloud/datatp/ops/webhook/dto/
git commit -m "feat(webhook): add TMSWebhookBatch + TMSWebhookPersistCommand DTOs"
```

---

### Task 2: Tạo bean `TMSWebhookTxOps` + Phase A method `loadBatches`

**Files:**
- Create: `of1-tms/module/tms/ops/src/main/java/cloud/datatp/ops/webhook/TMSWebhookTxOps.java`
- Create: `of1-tms/module/tms/ops/src/test/java/cloud/datatp/ops/webhook/TMSWebhookTxOpsUnitTest.java`

**Interfaces:**
- Consumes: `TMSBillLogic`, `TMSPartnerLogic`, `VehicleTripGoodsTrackingLogic`, helper `buildTracking(...)` + `updateVendorBillByVTGTracking(...)`.
- Produces: `List<TMSWebhookBatch> loadBatches(ClientContext client, ICompany company, List<VehicleTripGoodsTracking> trackings)`.

**Circular-dep guard:** `TMSWebhookLogic` (Task 4) sẽ inject `TMSWebhookTxOps`, nên `TMSWebhookTxOps` KHÔNG được inject ngược `TMSWebhookLogic`. Có 2 cách giải quyết, chọn **Option 1**:
- **Option 1 (chọn):** `buildTracking` và `updateVendorBillByVTGTracking` là **pure transformation** (không DB write), chuyển sang `TMSWebhookTxOps` dưới dạng `private` method (copy, rồi xoá bản gốc ở `TMSWebhookLogic` sau Task 4). `TMSWebhookTxOps` inject thêm `VehicleTripLogic`, `VehicleLogic` và các dep hiện tại của 2 helper này.
- Option 2 (fallback): extract 2 helper sang class riêng `TMSWebhookPayloadBuilder @Component`.

- [ ] **Step 1: Viết test fail trước**

```java
@ExtendWith(MockitoExtension.class)
class TMSWebhookTxOpsUnitTest {
  @Mock TMSBillLogic billLogic;
  @Mock TMSPartnerLogic partnerLogic;
  @Mock VehicleTripGoodsTrackingLogic trackingLogic;
  @Mock VehicleTripLogic vehicleTripLogic;
  @Mock VehicleLogic vehicleLogic;
  // + các dep khác mà buildTracking / updateVendorBillByVTGTracking cần (xem code gốc trong TMSWebhookLogic.java:194+)
  @InjectMocks TMSWebhookTxOps txOps;

  @Test
  void loadBatches_singleBillSingleCustomer_returnsOneBatch() {
    // given: 1 tracking, 1 bill with refSource="lgc_tms_bill", 1 customer with autoPush=true
    // when: txOps.loadBatches(...)
    // then: result.size() == 1, batch.getAttemptedIds().size() == N (number of trackings for that bill)
  }

  @Test
  void loadBatches_skipsNonUpdateVendorBill() { ... }

  @Test
  void loadBatches_skipsBillWithWrongRefSource() { ... }

  @Test
  void loadBatches_dedupsSameBillAcrossTrackings() { ... }

  @Test
  void loadBatches_skipsCustomerAutoPushFalse() { ... }

  @Test
  void loadBatches_emptyInput_returnsEmptyList() { ... }
}
```

- [ ] **Step 2: Chạy test → fail do class chưa tồn tại**

Run: `./gradlew :module:tms:ops:test --tests TMSWebhookTxOpsUnitTest`
Expected: FAIL (compile error — class `TMSWebhookTxOps` not found).

- [ ] **Step 3: Implement `TMSWebhookTxOps.loadBatches(...)` tại `cloud/datatp/ops/webhook/TMSWebhookTxOps.java`**

Chuyển nguyên block `TMSWebhookLogic.java` lines 92-146 (vòng for đầu tiên) vào method này. Trả về `List<TMSWebhookBatch>` thay cho `Map<Long, TMSWebhookModel>`. Signature:

```java
@Component
public class TMSWebhookTxOps {
  @Transactional(value = "tmsTransactionManager", readOnly = true)
  public List<TMSWebhookBatch> loadBatches(ClientContext client, ICompany company,
                                           List<VehicleTripGoodsTracking> trackings) { ... }
}
```

Lưu ý khi port code:
- Thay `tmsCustomerWebhookMaps.put/get` bằng `List<TMSWebhookBatch> out`.
- Không gọi `model.processResult` ở đây.
- Giữ nguyên logic dedup `tmsBillIdDup`.
- Copy 2 helper `buildTracking` + `updateVendorBillByVTGTracking` sang `TMSWebhookTxOps` (private). Bản gốc trong `TMSWebhookLogic` sẽ xoá tại Task 4 Step 3 sau khi orchestrator không còn cần.

- [ ] **Step 4: Chạy test → pass**

Run: `./gradlew :module:tms:ops:test --tests TMSWebhookTxOpsUnitTest`
Expected: PASS tất cả 6 case.

- [ ] **Step 5: Commit**

```bash
git add module/tms/ops/src/main/java/cloud/datatp/ops/webhook/TMSWebhookTxOps.java \
        module/tms/ops/src/main/java/cloud/datatp/ops/webhook/TMSWebhookLogic.java \
        module/tms/ops/src/test/java/cloud/datatp/ops/webhook/TMSWebhookTxOpsUnitTest.java
git commit -m "feat(webhook): add TMSWebhookTxOps.loadBatches (readOnly phase A)"
```

---

### Task 3: Thêm Phase C method `persistResult` vào `TMSWebhookTxOps`

**Files:**
- Modify: `of1-tms/module/tms/ops/src/main/java/cloud/datatp/ops/webhook/TMSWebhookTxOps.java`
- Modify: `of1-tms/module/tms/ops/src/test/java/cloud/datatp/ops/webhook/TMSWebhookTxOpsUnitTest.java`

**Interfaces:**
- Consumes: `VehicleTripGoodsTrackingRepository.updateRefId(companyId, id, refId)`, `VehicleTripGoodsTrackingRepository.updateWebhookPushSuccess(companyId, ids, success)` — đã có sẵn.
- Produces: `void persistResult(ICompany company, TMSWebhookPersistCommand cmd)`.

- [ ] **Step 1: Viết test fail trước**

```java
@Test
void persistResult_allSuccess_updatesRefIdAndWebhookTrue() {
  TMSWebhookPersistCommand cmd = new TMSWebhookPersistCommand(
      List.of(1L, 2L), Map.of(1L, 100L, 2L, 200L));
  txOps.persistResult(company, cmd);
  verify(repo).updateRefId(companyId, 1L, 100L);
  verify(repo).updateRefId(companyId, 2L, 200L);
  verify(repo).updateWebhookPushSuccess(companyId, List.of(1L, 2L), true);
  verify(repo, never()).updateWebhookPushSuccess(anyLong(), anyList(), eq(false));
}

@Test
void persistResult_partialFailure_marksFailedIds() {
  // attemptedIds = [1,2,3], idToRefId = {1:100} → failed = [2,3]
  TMSWebhookPersistCommand cmd = new TMSWebhookPersistCommand(
      List.of(1L, 2L, 3L), Map.of(1L, 100L));
  txOps.persistResult(company, cmd);
  verify(repo).updateRefId(companyId, 1L, 100L);
  verify(repo).updateWebhookPushSuccess(companyId, List.of(1L), true);
  verify(repo).updateWebhookPushSuccess(companyId, List.of(2L, 3L), false);
}

@Test
void persistResult_allFailure_marksAllFalse() { ... }

@Test
void persistResult_oneRefIdUpdateThrows_continuesOthersAndRethrows() {
  // Review Focus #5: partial failure in Phase C
  // simulate updateRefId(id=1) throws DataAccessException
  // expected: updateRefId(id=2) still called, then exception rethrown
}
```

- [ ] **Step 2: Chạy test → fail**

Run: `./gradlew :module:tms:ops:test --tests TMSWebhookTxOpsUnitTest.persistResult*`
Expected: FAIL — method chưa tồn tại.

- [ ] **Step 3: Implement `persistResult`**

```java
@Transactional("tmsTransactionManager")
public void persistResult(ICompany company, TMSWebhookPersistCommand cmd) { ... }
```

Logic: duyệt `cmd.getIdToRefId()` gọi `repo.updateRefId(...)` từng id (catch + log + rethrow sau khi xong vòng loop); gọi `repo.updateWebhookPushSuccess(success=true)` cho `cmd.successIds()`; gọi `repo.updateWebhookPushSuccess(success=false)` cho `attemptedIds - successIds`.

- [ ] **Step 4: Chạy test → pass**

Run: `./gradlew :module:tms:ops:test --tests TMSWebhookTxOpsUnitTest`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add module/tms/ops/src/main/java/cloud/datatp/ops/webhook/TMSWebhookTxOps.java \
        module/tms/ops/src/test/java/cloud/datatp/ops/webhook/TMSWebhookTxOpsUnitTest.java
git commit -m "feat(webhook): add TMSWebhookTxOps.persistResult (phase C bulk UPDATE)"
```

---

### Task 4: Refactor `TMSWebhookLogic.syncVendorBillWithVehicleTripGoodsTrackings` thành orchestrator

**Files:**
- Modify: `of1-tms/module/tms/ops/src/main/java/cloud/datatp/ops/webhook/TMSWebhookLogic.java` (lines 90-192)
- Create: `of1-tms/module/tms/ops/src/test/java/cloud/datatp/ops/webhook/TMSWebhookLogicOrchestrationUnitTest.java`

**Interfaces:**
- Consumes: `TMSWebhookTxOps.loadBatches(...)`, `TMSWebhookTxOps.persistResult(...)`.
- Produces: `void syncVendorBillWithVehicleTripGoodsTrackings(ClientContext, ICompany, List<VehicleTripGoodsTracking>)` — chữ ký không đổi, caller không bị ảnh hưởng.

- [ ] **Step 1: Viết test orchestration fail trước**

```java
@ExtendWith(MockitoExtension.class)
class TMSWebhookLogicOrchestrationUnitTest {
  @Mock TMSWebhookTxOps txOps;
  @InjectMocks TMSWebhookLogic logic;

  @Test
  void sync_emptyInput_doesNothing() {
    // Review Focus #3
    logic.syncVendorBillWithVehicleTripGoodsTrackings(client, company, List.of());
    verifyNoInteractions(txOps);
  }

  @Test
  void sync_nullInput_doesNothing() { ... }

  @Test
  void sync_happyPath_callsLoadThenHttpThenPersist() {
    when(txOps.loadBatches(any(), any(), any())).thenReturn(List.of(sampleBatch(bill1, List.of(10L, 11L))));
    // stub webhookModelFactory to return result with id 10 -> refId 999
    logic.syncVendorBillWithVehicleTripGoodsTrackings(client, company, inputTrackings);
    InOrder order = inOrder(txOps);
    order.verify(txOps).loadBatches(any(), any(), any());
    order.verify(txOps).persistResult(eq(company), argThat(cmd ->
        cmd.getIdToRefId().equals(Map.of(10L, 999L)) &&
        cmd.getAttemptedIds().equals(List.of(10L, 11L))));
  }

  @Test
  void sync_httpThrows_persistNotCalled_rethrows() {
    // Review Focus #4: vendor timeout/5xx → consumer sẽ retry message, Phase C KHÔNG được chạy
    when(txOps.loadBatches(any(), any(), any())).thenReturn(List.of(batch));
    // stub HTTP to throw
    assertThrows(WebhookException.class, () ->
        logic.syncVendorBillWithVehicleTripGoodsTrackings(client, company, inputTrackings));
    verify(txOps, never()).persistResult(any(), any());
  }

  @Test
  void sync_replaySameMessage_idempotentPersist() {
    // Review Focus #2: gọi 2 lần với cùng input + stub HTTP trả cùng refId → persistResult được gọi 2 lần với cùng payload, không exception
  }

  @Test
  void sync_multipleBatches_oneFailsHttp_othersStillPersist() {
    // batch1 HTTP throws → batch1 persist skip; batch2 HTTP ok → batch2 persist called
    // choice: dùng try/catch per-batch trong orchestrator để 1 customer fail không ảnh hưởng customer khác
  }
}
```

- [ ] **Step 2: Chạy test → fail**

Run: `./gradlew :module:tms:ops:test --tests TMSWebhookLogicOrchestrationUnitTest`
Expected: FAIL — orchestrator chưa gọi `txOps`.

- [ ] **Step 3: Rewrite `syncVendorBillWithVehicleTripGoodsTrackings`**

Thay toàn bộ body (lines 90-192) bằng orchestration logic (xem design đã mô tả trong turn trước). Pseudocode:

```java
public void syncVendorBillWithVehicleTripGoodsTrackings(ClientContext client, ICompany company,
    List<VehicleTripGoodsTracking> trackings) {
  if (Collections.isEmpty(trackings)) return;

  List<TMSWebhookBatch> batches = txOps.loadBatches(client, company, trackings);  // Phase A, read-only TX đóng tại đây
  if (batches.isEmpty()) return;

  for (TMSWebhookBatch batch : batches) {
    TMSWebhookPersistCommand cmd;
    try {
      cmd = callWebhook(batch);  // Phase B, no TX
    } catch (Exception e) {
      logger.error("[phase=B] webhook HTTP failed customerId={}, billId={}", 
                   batch.getCustomer().getId(), batch.getTmsBill().getId(), e);
      throw e;  // orchestrator fail → consumer retry (acceptable); hoặc continue nếu muốn best-effort per-batch
    }
    txOps.persistResult(company, cmd);  // Phase C, short write TX
  }
}

private TMSWebhookPersistCommand callWebhook(TMSWebhookBatch batch) {
  TMSWebhookModel model = new TMSWebhookModel(webhookBaseRestUrl, batch.getCustomer().getWebhookConfig(),
      "logistics", "sync-vehicle-trip");
  MapObject rec = new MapObject();
  rec.add("billId",        batch.getTmsBill().getRefId());
  rec.add("billCode",      batch.getTmsBill().getRefCode());
  rec.add("label",         batch.getTmsBill().getLabel());
  rec.add("billTrackings", batch.getVendorBill().getBillTrackings());
  rec.add("trackings",     batch.getGoodsTrackings());
  model.addRecord(rec);

  InputDataProcessResult result = model.processResult(
      "sync-vehicle-trip-" + DateUtil.asCompactDateTimeId(new Date()),
      "Sync Vehicle Trip "  + DateUtil.asCompactDate(new Date()), false);

  Map<Long, Long> idToRefId = new HashMap<>();
  if (result.getProcessStatus() == InputProcessStatus.SUCCESS) {
    for (InputRecordProcessResult pr : result.getInputRecordProcessResults()) {
      if (pr.getStatus() != InputProcessStatus.SUCCESS || StringUtil.isBlank(pr.getJsonResult())) continue;
      MapObject map = DataSerializer.JSON.fromString(pr.getJsonResult(), MapObject.class);
      for (String key : map.keySet()) {
        Long refId = map.getLong(key, null);
        if (refId == null) continue;
        idToRefId.put(Long.parseLong(key), refId);
      }
    }
  }
  return new TMSWebhookPersistCommand(batch.getAttemptedIds(), idToRefId);
}
```

Quyết định: HTTP fail có **throw** không? → **throw** để consumer đẩy message vào retry topic (giữ semantics cũ). Nhưng per-batch: wrap try/catch quanh `callWebhook` + `persistResult` để 1 customer lỗi không chặn customer khác → test case thứ 6.

- [ ] **Step 4: Chạy test → pass**

Run: `./gradlew :module:tms:ops:test --tests TMSWebhookLogicOrchestrationUnitTest`
Expected: PASS.

- [ ] **Step 5: Chạy toàn bộ test module để không regress**

Run: `./gradlew :module:tms:ops:test`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add module/tms/ops/src/main/java/cloud/datatp/ops/webhook/TMSWebhookLogic.java \
        module/tms/ops/src/test/java/cloud/datatp/ops/webhook/TMSWebhookLogicOrchestrationUnitTest.java
git commit -m "refactor(webhook): orchestrator pattern — HTTP outside transaction"
```

---

### Task 5: Bỏ `@Transactional` ở `TrackingSyncKafkaConsumer.process()`

**Files:**
- Modify: `of1-tms/module/tms/ops/src/main/java/cloud/datatp/ops/trip/kafka/TrackingSyncKafkaConsumer.java` (line 70)

**Interfaces:**
- Consumes: refactored `TMSWebhookLogic.syncVendorBillWithVehicleTripGoodsTrackings` từ Task 4 (chữ ký không đổi).
- Produces: nothing.

- [ ] **Step 1: Xoá annotation `@Transactional("tmsTransactionManager")` tại line 70**

Phương thức `process` bây giờ:
```java
public void process(TrackingSyncMessage msg) {
  if (msg == null || msg.getTrackings() == null || msg.getTrackings().isEmpty()) return;
  ClientContext client = msg.getClient();
  ICompany company = client.getCompany();
  webhookLogic.syncVendorBillWithVehicleTripGoodsTrackings(client, company, msg.getTrackings());
}
```

- [ ] **Step 2: Chạy toàn bộ unit test module**

Run: `./gradlew :module:tms:ops:test`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add module/tms/ops/src/main/java/cloud/datatp/ops/trip/kafka/TrackingSyncKafkaConsumer.java
git commit -m "fix(webhook): remove outer @Transactional from Kafka consumer"
```

---

### Task 6: Integration test race condition

**Files:**
- Create: `of1-tms/module/tms/ops/src/test/java/cloud/datatp/ops/webhook/TMSWebhookRaceIntegrationTest.java`

**Interfaces:**
- Consumes: refactored stack từ Task 1-5 cộng Spring context thật.
- Produces: nothing.

Mục tiêu: chứng minh fix hoạt động — khi external thread update tracking row trong lúc Phase B đang HTTP, consumer vẫn commit thành công Phase C mà không throw `ObjectOptimisticLockingFailureException`.

- [ ] **Step 1: Check xem project có `@SpringBootTest` config + embedded DB (H2 / Testcontainers Postgres)**

Run: `grep -rn "@SpringBootTest\|Testcontainers\|@DataJpaTest" of1-tms/module/tms/ops/src/test/`
Nếu không có infra → **Disabled** test này với `@Disabled("Pending integration test harness")` và tạo issue riêng. Document trong test javadoc.

- [ ] **Step 2: Nếu có infra, viết test**

```java
@SpringBootTest
class TMSWebhookRaceIntegrationTest {

  @Autowired TMSWebhookLogic logic;
  @Autowired VehicleTripGoodsTrackingRepository repo;
  @Autowired TransactionTemplate tx;
  @MockBean TMSWebhookModelFactory modelFactory; // or stub HTTP via WireMock

  @Test
  void concurrentExternalUpdate_doesNotCauseOptimisticLockException() {
    // 1. Seed tracking row (id=X, version=V, webhookPushSuccess=null, refId=null)
    // 2. Stub webhookModel.processResult to:
    //    - sleep 2s (simulate slow HTTP)
    //    - return success with map {X: 999}
    // 3. Spawn thread T2 that waits 500ms then updates tracking X: setDeliveryNote("changed") + save (via TX)
    //    → version V → V+1
    // 4. Call logic.syncVendorBillWithVehicleTripGoodsTrackings(...) with [X] in main thread
    // 5. Assert:
    //    - No exception thrown
    //    - Row X in DB: refId=999, webhookPushSuccess=true, version=V+2 (incremented twice)
    //    - deliveryNote="changed" preserved (T2's write not lost)
  }

  @Test
  void retryTopicParallelWithMainTopic_sameTracking_noOptimisticLock() {
    // Review Focus #1
    // Simulate: main handle(X) chạy; đồng thời retry handle(X) chạy → cả 2 complete
  }
}
```

- [ ] **Step 3: Chạy test**

Run: `./gradlew :module:tms:ops:integrationTest` (hoặc `test` nếu không tách)
Expected: PASS (hoặc SKIPPED nếu Disabled).

- [ ] **Step 4: Commit**

```bash
git add module/tms/ops/src/test/java/cloud/datatp/ops/webhook/TMSWebhookRaceIntegrationTest.java
git commit -m "test(webhook): integration test for concurrent update race"
```

---

### Task 7: Observability — structured log per phase

**Files:**
- Modify: `of1-tms/module/tms/ops/src/main/java/cloud/datatp/ops/webhook/TMSWebhookLogic.java`
- Modify: `of1-tms/module/tms/ops/src/main/java/cloud/datatp/ops/webhook/TMSWebhookTxOps.java`

**Interfaces:**
- Consumes: `lombok @Slf4j` logger đã có.
- Produces: log keys `[phase=A|B|C]` + `batches=`, `customerId=`, `billId=`, `attemptedIds=`, `successIds=`, `failedIds=`, `durationMs=`.

- [ ] **Step 1: Thêm log mốc đầu/cuối mỗi phase**

Tại `loadBatches`:
```java
long t0 = System.currentTimeMillis();
...
log.info("[phase=A] loaded batches={} durationMs={}", out.size(), System.currentTimeMillis() - t0);
```

Tại orchestrator `callWebhook`:
```java
log.info("[phase=B] customerId={} billId={} attempts={}", batch.getCustomer().getId(), batch.getTmsBill().getId(), batch.getAttemptedIds().size());
```

Tại `persistResult`:
```java
log.info("[phase=C] attempts={} success={} failed={}", cmd.getAttemptedIds().size(), cmd.successIds().size(), cmd.getAttemptedIds().size() - cmd.successIds().size());
```

- [ ] **Step 2: Compile + unit test**

Run: `./gradlew :module:tms:ops:test`
Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add module/tms/ops/src/main/java/cloud/datatp/ops/webhook/
git commit -m "chore(webhook): structured logs per phase (A/B/C)"
```

---

## Rollout checklist (sau khi merge)

- [ ] Deploy staging — chạy load test với fake vendor webhook ~5s latency + 10 concurrent REST update lên cùng tracking.
- [ ] Grep production log `ObjectOptimisticLockingFailureException.*VehicleTripGoodsTracking` 7 ngày sau release → kỳ vọng 0 hit từ `TrackingSyncKafkaConsumer`. Nếu còn từ source khác (REST, Goertek callback) → ngoài scope plan này, mở ticket riêng.
- [ ] Grep `[phase=B].*customerId=.*attempts=` để xác nhận flow mới active trong prod.
