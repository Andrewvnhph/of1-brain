# of1-tms — grounding bắt buộc trước pipeline

> File này được Claude Code tự động load khi làm việc trong thư mục `brainstorms/of1-tms/`.
> AI đọc trước khi chạy bất kỳ phase nào (design/openspec/code) của pipeline cho module TMS.

## Cấu trúc file trong thư mục này (per-user)

- **Brainstorm tổ chức theo user**, không theo module. Mỗi dev có 1 file: `<user>.md` (vd `mchien.md`).
- TODO trong mỗi file **phải tag module** để AI load đúng grounding: `- [ ] [<module>] <nội dung>`.
- Module info nằm ở `../../designs/of1-tms/<module>.md` + `../../openspec/specs/of1-tms/<module>/spec.md` (không phải trong brainstorms).
- Match pattern Forgejo "group by assignee" (xem rule `../../designs/of1-tms/rules/forgejo-workflow.md`).

## ⚠️ HARD SAFETY RULE — Repo scope (write vs read-only)

AI tuyệt đối tuân thủ scope này khi làm việc với code thật:

| Repo | Path | Scope | AI được phép |
|------|------|-------|-------------|
| **`of1-tms`** | `/Users/admin/OF1/forgejo/of1-platform/of1-tms` | **WRITABLE** | grep + read + **edit + commit** (trên nhánh `ai/<slug>` off `develop`, KHÔNG push `develop`, KHÔNG merge) |
| **`of1-document`** | `/Users/admin/OF1/forgejo/of1-platform/of1-document` | **WRITABLE** | grep + read + **edit + commit** (trên nhánh `ai/<slug>` off `develop`, KHÔNG push `develop`, KHÔNG merge). Dùng cho lib document viewer share dùng các app (xlsx, pdf, ...) |
| `of1-platform` | `/Users/admin/OF1/forgejo/of1-platform/of1-platform` | **READ-ONLY** | grep + read để grounding. **KHÔNG edit, KHÔNG commit.** |
| `of1-core` | `/Users/admin/OF1/forgejo/of1-platform/of1-core` | **READ-ONLY** | grep + read để grounding. **KHÔNG edit, KHÔNG commit.** |
| `of1-webui` | `/Users/admin/OF1/forgejo/of1-platform/of1-webui` | **READ-ONLY** | grep + read để grounding. **KHÔNG edit, KHÔNG commit.** |

**Nếu phát hiện bug/cần sửa trong 3 repo read-only** (platform/core/webui):
- **KHÔNG tự modify.** Ghi finding vào design (`../../designs/of1-tms/<slug>.md` phần "Giả định" hoặc "Open questions"), nêu rõ:
  - File + line + hành vi hiện tại
  - Thay đổi cần thiết + lý do
  - Impact tới of1-tms
- Để dev handle thủ công (có thể là PR riêng ở repo đó).

**Nếu AI vô ý edit file trong 3 repo read-only** → **DỪNG NGAY, báo dev** để revert. Đây là vi phạm hard rule.

**Trước MỖI `git commit`**: PHẢI chạy `git branch --show-current` và verify output ≠ `develop` / `main` / `master` / `release`. Branch state local **không stable** qua các turn (dev merge PR + pull có thể fast-forward branch `ai/<slug>` về `develop`). Chi tiết + recovery procedure: `../../designs/of1-tms/rules/forgejo-workflow.md` §"Pre-commit safety check".

## Rules bắt buộc (load trước)

AI PHẢI đọc 4 file rule sau trước khi gen code/design TMS:

- **Backend**: `../../designs/of1-tms/rules/backend.md` — Service → Logic → Repo, save pattern, DDD Aggregate, Kafka, Testing, Env.
- **Frontend**: `../../designs/of1-tms/rules/frontend.md` — React 18 Class Components, Module Federation, bs.BB* inputs, BBRef từ of1-tms, shell app registration (§5.7).
- **Git (Forgejo)**: `../../designs/of1-tms/rules/forgejo-workflow.md` — commit scope/message, branch `ai/<slug>`, push rules (chỉ `of1-tms` writable).
- **Task tracking (OpenProject)**: `../../designs/of1-tms/rules/openproject-workflow.md` — tạo work_package trên `insight.openfreightone.com/projects/TMS`. **Hiện đang STUB** chờ dev fill cấu trúc API.

> **Nguồn gốc rules**: `/Users/admin/OF1/forgejo/of1-platform/of1-tms-engineering-hub/rules/`. Bản tại `designs/of1-tms/rules/` là MIRROR; khi engineering-hub cập nhật cần re-sync.

## Overview grounding (đọc trước mỗi TODO)

Trước khi design/openspec/code cho TODO trong thư mục này, AI PHẢI đọc:

1. `../../designs/of1-tms/overview.md` — kiến trúc tổng, tech stack, module map, port.
2. `../../openspec/specs/of1-tms/overview.md` — capabilities + ràng buộc TMS-wide.
3. Design + spec của module tương ứng với TODO (link ở header mỗi `<module>.md`).

## Convention tuyệt đối

### Communication với bên ngoài — 3 kênh phân biệt rõ

| Hướng | Kênh | Chi tiết |
|-------|------|---------|
| TMS **→** `of1-platform` | **RPC qua `app/api`** | Sync; dùng `RPCService` + client bean (`PlatformClient`, `CommunicationRPC`…). **TUYỆT ĐỐI không** gọi Kafka cho hướng này. |
| External (vd document service) **→** TMS | **Kafka inbound** | `@Component` + `@KafkaListener` + `@Transactional("tmsTransactionManager")` on method. Vd `InvoiceExtractedDataKafkaConsumer`. |
| TMS self-async (produce + consume own topic) | **Kafka** | Retry/decouple pattern; wrap producer trong `*KafkaProducer` class, có fallback inline khi `kafka.queue-enable=false`. Vd `TrackingSyncKafkaProducer` + `TrackingSyncKafkaConsumer`. |

### Các convention khác

- **DB column snake_case** ↔ camelCase qua `SqlMapRecord` (ví dụ `previous_fixed_charge` ↔ `previousFixedCharge`).
- **Entity Java field mới** → bắt buộc `@Column(name = "snake_case_name")`.
- **Transaction**: `@Transactional("tmsTransactionManager")` **tường minh** ở **Service** (không ở Logic). Bare `@Transactional` + `@Transactional` ở Logic là drift cần cleanup.
- **Layering**: Service → Logic → Repository → Entity. Service inject **Logic** (không Repository trực tiếp trừ facade pure delegate). Logic extends `TMSDAOService`, nhận `ClientContext client` đầu tiên.
- **Repository package convention**: Repo **phải** nằm trong `<domain>.repository.*Repository.java` **và** thêm `<domain>.repository` vào `ModuleTMSCoreConfig.@EnableJpaRepositories.basePackages` (list không recursive). Sai → Spring không tìm được bean, runtime fail. Chi tiết: `backend.md` §2.6.
- **`MapObject` numeric getters**: luôn dùng `getDouble(k, 0D)` / `getLong(k, 0L)` / `getInteger(k, null)` / `getBoolean(k, false)` — bare `getDouble(k)` / `getFloat(k)` / `getLong(k)` / `getBoolean(k)` KHÔNG tồn tại; `getInteger(k)` throws khi null. Chi tiết: `backend.md` §2.7.
- **`@RPCCall` annotation**: KHÔNG tự thêm vào service method. Chỉ thêm khi dev yêu cầu rõ (xem rule §2.1.1 trong `backend.md`). Pattern mặc định `@Service + @Transactional + public method` đủ cho FE call.
- **TypeScript — KHÔNG `as any`** để bypass TS error. Dùng explicit `let x: Type = {...}; return x;` để compile-time catch sai field name. Nếu TS error, mở source type definition xem đúng tên (vd `grid.VGridConfig` ở `of1-webui/.../IVGrid.tsx`). Rule chi tiết: `../../designs/of1-tms/rules/frontend.md` §3.4.0.
- **Save pattern (HARD RULE)**: mọi `repo.save(entity)` trong Logic **phải** preceded bằng `entity.set(client, company)` ngay trước đó (xem rule §2.3 trong `backend.md`). Thứ tự: build/enrich → `set(client, company)` → `save()`.
- **Aggregate Root** có cascade (`@OneToOne`/`@OneToMany`/`@ManyToMany`) → bắt buộc override `set(ClientContext, ICompany)` để propagate xuống child. Child extends `CompanyEntity` → `set(client, company, child)`; child chỉ `PersistableEntity` → `child.set(client)` (xem rule §3.7 trong `backend.md`).
- **Groovy SQL**: `ExecutableSqlBuilder` mới phải `register(new ...())` trong constructor của `*Sql` class, không sẽ silent fail runtime.
- **UI bill config** tập trung ở `webui/tms/src/app/logistics/tms/bill/TMSBillRecordConfig.tsx` (function `createTMSBillRecordConfig`).
- **FE call BE**: dùng `appContext.getBackendConfigs().getBackendConfig('tms').createHttpBackendCall('<Service>', '<method>', params)`.
- **DbEntityListPlugin**: `this.backend = { backend: 'tms', service: '...', searchMethod: '...' }` — nếu quên `backend: 'tms'` sẽ default về `platform` (bug ngầm).
- **Input FE**: KHÔNG viết raw `<input/>`, `<select/>`, `<textarea/>`. Luôn dùng `bs.BBString`, `bs.BBBoolean`, `bs.BBNumber`, `bs.BBDate`, `bs.BBSelect`, `bs.BBTextArea` (xem `../../designs/of1-tms/rules/frontend.md` §3.2).
- **Notification FE** (3 cấp ưu tiên): (1) API call → chain `.withEntityOpNotification(op, entityLabel, affectedCount?)` tự wire success + fail toast; (2) client-side action hoặc API success cần rich content runtime → `appContext.addOSNotification`; (3) error chi tiết / validation blocking → `bs.notificationShow` static. Chi tiết `frontend.md` §3.4.3.
- **BBRef family** (reference picker — `BBRefTMSEmployee`, `BBRefAccount`, …): **chỉ import từ `of1-tms`** (`webui/tms/src/...`), KHÔNG từ `of1-platform`. Cần `BBRef*` mới → **DỪNG, hỏi dev** trước, không tự tạo.
- **Thêm UI mới ở đâu?** Follow flow `Init.tsx` → `registerTmsShellApps` → `createTmsScreens` → 1 trong 9 Screen module (`shell/init/{Search,Report,Bill,Fleet,Ops,RU,Reconcile,Settings,Guide}Screen.tsx`). Checklist step-by-step tại `../../designs/of1-tms/rules/frontend.md` §5.7. Key files tại §10.

## Ports / Endpoints

| Service | Port | Endpoint |
|---------|------|----------|
| Platform BE | 7080 | http://localhost:7080 |
| TMS BE | 7086 | http://localhost:7086 |
| TMS FE (dev) | 3006 | http://localhost:3006 |
| Platform FE (dev) | 3000 | http://localhost:3000 |

## Source of truth cho code TMS

- Code gốc: `/Users/admin/OF1/forgejo/of1-platform/of1-tms/`
- Engineering hub (docs source of truth): `/Users/admin/OF1/forgejo/of1-platform/of1-tms-engineering-hub/`
  - `architecture.md`, `patterns.md`, `quick-reference.md`, `troubleshooting.md`
  - `rules/{backend,frontend,forgejo-workflow}.md` (đã mirror sang `designs/of1-tms/rules/`)
  - `business/decisions.md`
  - `openspec/config.yaml` + `openspec/changes/<name>/`

## Trình tự pipeline cho TMS TODO

Khi gặp TODO chưa checked trong `brainstorms/of1-tms/<user>.md`:

1. **Load context** (bắt buộc):
   - 3 rules (`../../designs/of1-tms/rules/{backend,frontend,forgejo-workflow}.md`)
   - Overview design + overview spec
   - **Parse tag `[<module>]`** trong TODO → load `../../designs/of1-tms/<module>.md` + `../../openspec/specs/of1-tms/<module>/spec.md` tương ứng
   - Nhiều module tag (vd `[bill,vendor]`) → load tất cả module liên quan
2. **Design** → cập nhật/tạo `../../designs/of1-tms/<slug>.md` (hoặc per-module file nếu TODO thuộc module).
3. **OpenSpec** → `/opsx:propose "<slug>"` ở workspace của1-brain, hoặc tạo change ở `of1-tms-engineering-hub/openspec/changes/` nếu TODO ảnh hưởng code thật.
4. **Code** (tuân thủ HARD SAFETY RULE ở đầu file):
   - Code thật trên **`of1-tms` (writable)**: tạo nhánh `ai/<slug>` off `develop`, commit, KHÔNG merge, KHÔNG push `develop`, dừng để dev duyệt.
   - Cần modify **`of1-platform` / `of1-core` / `of1-webui` (read-only)**: **KHÔNG tự sửa**. Ghi finding vào design để dev xử lý thủ công.
   - Pipeline hiện tại chưa chốt (xem TODO 1 trong `brainstorms/setup.md`) → nếu TODO động vào code thật lần đầu, STOP ask dev confirm scope.
5. **Review** → chạy tests + `/code-review`; fix CRITICAL/HIGH trước khi báo done.
6. **Commit + push** → khi TODO done, commit scope đúng + push nhánh `ai/<slug>` (xem `../../designs/of1-tms/rules/forgejo-workflow.md`). **KHÔNG** merge, **KHÔNG** push `develop`.
7. **Update OpenProject** → sync status work_package tương ứng + append comment progress (xem `../../designs/of1-tms/rules/openproject-workflow.md` — hiện stub, bỏ qua step này cho tới khi dev fill cấu trúc API).
8. **Cleanup `ai/*` branches** (local + remote) → khi start session mới / TODO mới / sau khi dev confirm merged, chạy cleanup combo: `git fetch --prune` + `git branch -d` local merged + `git push origin --delete` remote merged. Script auto 1-liner + rule chi tiết: `../../designs/of1-tms/rules/forgejo-workflow.md` §"Cleanup `ai/*` branches sau khi dev merge PR". Dùng `-d` lowercase, không bao giờ `-D` trừ khi dev confirm squash merge trên UI.

Sau mỗi TODO: check `[x]` + cập nhật Summary table với link + status + cột `module` ghi tag module đã parse.

## Thêm user mới

Khi có dev mới join:
1. Tạo file mới `<user>.md` trong thư mục này (copy template từ `mchien.md`).
2. Dev đó bắt đầu thêm TODO vào file của mình, không ghi chung với dev khác.
3. Không cần sửa `CLAUDE.md` này — file auto-load cho mọi `<user>.md`.
