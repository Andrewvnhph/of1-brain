# english-app — grounding bắt buộc trước pipeline

> File này được Claude Code tự động load khi làm việc trong thư mục `brainstorms/english-app/`.
> AI đọc trước khi chạy bất kỳ phase nào (design/openspec/code).

## Project overview

**english-app** — phần mềm học tiếng Anh (project cá nhân của mchien, tách khỏi workspace OF1).

**Stack**:
- **Backend**: Node.js (TBD framework: Express / Fastify / NestJS)
- **Database**: MongoDB
- **Frontend web**: React.js (TBD: CRA / Vite / Next.js)
- **Frontend mobile**: React Native (TBD: bare / Expo)
- **Monorepo?**: TBD (pnpm workspaces / Turborepo / Nx?)

**Khác hẳn stack of1-tms/of1-document** (Spring Boot + PostgreSQL + Class Components) → KHÔNG reuse rules TMS, cần rule set riêng (sẽ fill khi dev chốt framework + convention).

## Cấu trúc file trong thư mục này (per-user)

- Brainstorm per-user: `<user>.md` (vd `mchien.md`). TODO ghi với tag scope.
- Scope ∈ `{backend, web, mobile, mongo, shared, infra, overview}`.
- Nhiều scope → `[backend,mongo]` hoặc `[web,mobile]`.

## ⚠️ HARD SAFETY RULE — Repo scope

**english-app repo** nằm ở `/Users/admin/personal/english-app` (hoặc path dev chọn — personal project, ngoài workspace OF1 `/Users/admin/OF1/forgejo/of1-platform/`).

**Workflow git tương tự TMS/document** (xem `../../designs/rules/forgejo-workflow.md`):
- Branch `ai/<slug>` off `develop` / `main` (tùy convention dev chọn)
- Pre-commit `git branch --show-current | grep -qE '^ai/'` fail-fast
- KHÔNG push `main`/`develop`, KHÔNG merge
- Cleanup `ai/*` local + remote sau dev merge PR

**Khác TMS/document**:
- Có thể dùng GitHub thay Forgejo (nếu dev host personal repo trên GitHub) → auth qua SSH key cá nhân, không phải Forgejo token.
- Nếu monorepo → path trong repo (vd `apps/backend`, `apps/web`, `apps/mobile`) phải tag rõ khi commit scope.

## Rules bắt buộc (load trước — 2 layer)

**Layer 1 — Shared rules** (`../../designs/rules/`):
- **Git workflow**: `../../designs/rules/forgejo-workflow.md` — áp cho mọi project (Forgejo và GitHub có pattern tương tự).

**Layer 2 — English-app rules** (`../../designs/english-app/rules/`):
- Hiện trạng: **chưa có file** — dev chốt framework trước (Express vs Fastify vs NestJS, Vite vs Next.js, Expo vs bare RN), AI sẽ gen rule phù hợp.
- Dự kiến các file sau khi stack rõ:
  - `backend.md` — Node convention (TS strict? async/await patterns? error handling? Mongoose vs native driver?)
  - `web.md` — React.js convention (functional vs class? hooks? state management: zustand/redux/context?)
  - `mobile.md` — React Native convention (Expo vs bare? navigation: react-navigation? state sync web-mobile?)
  - `mongo.md` — schema conventions, indexing, aggregation patterns
  - `monorepo.md` — nếu dùng workspaces (shared types/utils between web + mobile)

## Convention tạm thời (chờ dev chốt)

- **Language**: TypeScript cho tất cả (BE + web + mobile) — khuyến nghị cho type sharing.
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

## Pending — dev cần chốt trước khi code

- [ ] Framework BE: Express / Fastify / NestJS?
- [ ] Framework web: CRA / Vite / Next.js (SSR cần không?)
- [ ] Mobile: Expo (nhanh) hay bare RN (control)?
- [ ] Monorepo tool: pnpm workspaces / Turborepo / Nx?
- [ ] State management shared: zustand / jotai / redux-toolkit?
- [ ] Auth: JWT self-host / Auth0 / Clerk / Supabase?
- [ ] Repo host: GitHub personal / Forgejo khác?
- [ ] Repo path exact: `/Users/admin/personal/english-app`?
