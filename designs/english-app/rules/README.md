# english-app rules — Project-specific

Rules áp **chỉ** cho project `english-app`. Shared rules load trước từ `../../rules/*.md`.

**Diverges from of1-tms**: hoàn toàn khác stack (Node.js + MongoDB + React.js vs Spring Boot + PostgreSQL + Class Components) → KHÔNG reuse rules TMS.

## Status

**Phase bootstrap** — chờ dev chốt framework trước, AI gen rule phù hợp. Chưa có file override.

## Rules dự kiến (gen sau khi stack chốt)

| File | Scope | Depends on |
|---|---|---|
| `backend.md` | Node convention: TS strict mode, async/await patterns, error handling, request validation (zod?), middleware structure, logger convention | Chọn Express/Fastify/NestJS |
| `web.md` | React.js convention: functional components, hooks, state management, routing, data fetching (React Query? SWR?), styling (CSS modules / Tailwind?) | Chọn CRA/Vite/Next.js |
| `mongo.md` | Schema conventions, indexing, aggregation patterns, migrations (migrate-mongo?), transactions usage | — |
| `monorepo.md` | pnpm workspaces, Turborepo cache, shared types/utils (zod schemas BE+FE) | Chọn workspace tool |
| `auth.md` | JWT self-host / Auth0 / Clerk / Supabase integration | Chọn auth provider |
| `testing.md` | Jest/Vitest cho BE+Web, Playwright/Cypress E2E, test coverage targets | — |

## Convention đã chốt (sẽ update khi dev confirm)

- **Language**: TypeScript (strict mode) cho tất cả apps + packages.
- **Package manager**: pnpm.
- **Node version**: >= 20 LTS.
- **MongoDB**: >= 7.0 replicaset (transactions).

## Khi english-app diverge hoặc promote lên shared

- **Pattern xuất hiện lần 2** (vd nếu có `english-admin-cms` project cùng stack) → promote lên `../../rules/` shared.
- **Pattern TMS/document có mà english-app cần giống** (vd forgejo-workflow) → reuse direct từ `../rules/` (shared).
