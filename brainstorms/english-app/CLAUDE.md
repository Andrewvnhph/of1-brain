# english-app — grounding bắt buộc trước pipeline

> File này được Claude Code tự động load khi làm việc trong thư mục `brainstorms/english-app/`.
> AI đọc trước khi chạy bất kỳ phase nào (design/openspec/code).

## Project overview

**english-app** — phần mềm học tiếng Anh (project cá nhân của mchien, tách khỏi workspace OF1).

**Stack**:
- **Backend**: Node.js (TBD framework: Express / Fastify / NestJS)
- **Database**: MongoDB
- **Frontend**: React.js (TBD: CRA / Vite / Next.js). Mobile responsive qua web (PWA option sau).
- **Monorepo?**: TBD (pnpm workspaces / Turborepo / Nx?) — nếu tách BE / FE / shared.

**Khác hẳn stack of1-tms/of1-document** (Spring Boot + PostgreSQL + Class Components) → KHÔNG reuse rules TMS, cần rule set riêng (sẽ fill khi dev chốt framework + convention).

## Cấu trúc file trong thư mục này (per-user)

- Brainstorm per-user: `<user>.md` (vd `mchien.md`). TODO ghi với tag scope.
- Scope ∈ `{backend, web, mongo, shared, infra, overview}`.
- Nhiều scope → `[backend,mongo]` hoặc `[web,shared]`.

## ⚠️ HARD SAFETY RULE — Repo scope

**english-app repo** nằm ở `/Users/admin/personal/english-app` (hoặc path dev chọn — personal project, ngoài workspace OF1 `/Users/admin/OF1/forgejo/of1-platform/`).

**Workflow git tương tự TMS/document** (xem `../../designs/rules/forgejo-workflow.md`):
- Branch `ai/<slug>` off `develop` / `main` (tùy convention dev chọn)
- Pre-commit `git branch --show-current | grep -qE '^ai/'` fail-fast
- KHÔNG push `main`/`develop`, KHÔNG merge
- Cleanup `ai/*` local + remote sau dev merge PR

**Khác TMS/document**:
- Có thể dùng GitHub thay Forgejo (nếu dev host personal repo trên GitHub) → auth qua SSH key cá nhân, không phải Forgejo token.
- Nếu monorepo → path trong repo (vd `apps/backend`, `apps/web`, `packages/shared`) phải tag rõ khi commit scope.

## Rules bắt buộc (load trước — 2 layer)

**Layer 1 — Shared rules** (`../../designs/rules/`):
- **Git workflow**: `../../designs/rules/forgejo-workflow.md` — áp cho mọi project (Forgejo và GitHub có pattern tương tự).

**Layer 2 — English-app rules** (`../../designs/english-app/rules/`):
- Hiện trạng: **chưa có file** — dev chốt framework trước (Express vs Fastify vs NestJS, Vite vs Next.js), AI sẽ gen rule phù hợp.
- Dự kiến các file sau khi stack rõ:
  - `backend.md` — Node convention (TS strict? async/await patterns? error handling? Mongoose vs native driver?)
  - `web.md` — React.js convention (functional vs class? hooks? state management: zustand/redux/context? styling: Tailwind / CSS Modules?)
  - `mongo.md` — schema conventions, indexing, aggregation patterns
  - `monorepo.md` — nếu dùng workspaces (shared types/utils between BE + web)

## Convention tạm thời (chờ dev chốt)

- **Language**: TypeScript cho tất cả (BE + web + shared) — khuyến nghị cho type sharing.
- **Package manager**: pnpm (consistent với OF1 workspace).
- **Node version**: >= 20 LTS.
- **MongoDB**: >= 7.0 với replicaset (hỗ trợ transactions).

## Trình tự pipeline cho english-app TODO

Khi gặp TODO chưa checked trong `brainstorms/english-app/<user>.md`:

1. **Load context**: shared git rule + (sau khi có) english-app rules.
2. **Design** → `../../designs/english-app/<slug>.md`.
3. **OpenSpec** → `/opsx:propose "<slug>"` cho feature lớn.
4. **Code** (sau khi dev confirm scaffold repo):
   - Clone repo + verify path writable.
   - Nhánh `ai/<slug>` off develop.
   - TDD: viết test fail → implement → test pass.
5. **Review** → tests pass + manual verify + lint/type check.
6. **Commit + push** → pre-commit branch check.
7. **Cleanup** → sau dev merge PR, cleanup combo.

## Chốt stack (100% decisions MVP)

- ✅ BE: **Fastify + TypeScript** (AI recommend, dev delegate)
- ✅ FE: **React.js + TypeScript + Vite** (dev chốt)
- ✅ DB: MongoDB 7+ replicaset
- ✅ Repo path: `/Users/admin/personal/english-app` (chưa tồn tại, mkdir khi scaffold)
- ✅ OCR: Tesseract.js (worker thread, parallel 4) + preprocess sharp
- ✅ Layout: L2 scan + text overlay
- ✅ TTS: Web Speech API client-side
- ✅ Dictionary: Free Dictionary API + LibreTranslate self-host EN→VN
- ✅ Queue: Redis + BullMQ, realtime socket.io
- ✅ Multi-book library + 500MB upload / Single-user / No storage limit / Mobile+desktop responsive

Full MVP design: `../../designs/english-app/book-ingestion-mvp.md`.

## Pending (secondary, chốt khi code — không block scaffold)

- [ ] Monorepo tool: pnpm workspaces (default) / Turborepo / Nx (decide khi phase 1a start)
- [ ] State management: zustand (recommend MVP, lightweight) / jotai / redux-toolkit / context
- [ ] Styling: Tailwind (recommend) / CSS Modules / styled-components
- [ ] Auth: JWT self-host (single-user MVP, có thể skip auth hoàn toàn)
- [ ] Repo host: GitHub personal (recommend)
