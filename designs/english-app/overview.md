# english-app — Overview

Phần mềm học tiếng Anh. Project cá nhân của mchien.

## Stack

| Layer | Tech | Notes |
|---|---|---|
| Backend | **Node.js** (TBD: Express / Fastify / NestJS) | TypeScript, Node 20 LTS |
| Database | **MongoDB** (>= 7.0 replicaset) | Transactions support |
| Frontend web | **React.js** (TBD: CRA / Vite / Next.js) | SPA hoặc SSR tùy need SEO |
| Frontend mobile | **React Native** (TBD: Expo / bare) | iOS + Android |
| Shared | Types + utils + validation schemas | Giữa BE, web, mobile |
| Monorepo | pnpm workspaces (default) / Turborepo (?) | TBD |

**Khác hẳn OF1 stack** (Spring Boot + PostgreSQL + Class Components) → độc lập repo + rules.

## Architecture dự kiến

```
┌────────────────────┐  ┌────────────────────┐
│  Web (React.js)    │  │  Mobile (RN)       │
└──────────┬─────────┘  └──────────┬─────────┘
           │                       │
           └─────────┬─────────────┘
                     ↓
         ┌───────────────────────┐
         │  BE API (Node.js)     │
         │  + Auth               │
         │  + Business logic     │
         │  + Spaced repetition  │
         └───────────┬───────────┘
                     ↓
         ┌───────────────────────┐
         │  MongoDB              │
         │  users / cards /      │
         │  reviews / vocab / ... │
         └───────────────────────┘
```

## Features (phase 1 — TBD, dev fill)

Khả năng cân nhắc:
- **Vocabulary flashcards** với spaced repetition (SM-2 algorithm)
- **Grammar check** / correction (có thể dùng LanguageTool API hoặc tự implement)
- **Vocabulary quiz** (multiple choice, fill-in-blank, matching)
- **Conversation practice** (chatbot — có thể gọi OpenAI/Claude API)
- **Listening** + pronunciation (speech-to-text, text-to-speech)
- **Reading comprehension** (articles + quiz)
- **Progress tracking** + stats
- **Social**: leaderboard, friends, challenges
- **Dictionary lookup** inline (dùng free dict API)

**Scope MVP phase 1** → dev chốt sau trong `brainstorms/english-app/mchien.md`.

## Repo structure (dự kiến monorepo)

```
english-app/
├── apps/
│   ├── backend/        — Node.js API
│   ├── web/            — React.js web client
│   └── mobile/         — React Native app
├── packages/
│   ├── shared/         — Types + utils + validation (zod schemas)
│   └── config/         — ESLint, TS config, Prettier shared
├── pnpm-workspace.yaml
├── package.json
└── README.md
```

## Nguồn tham chiếu

- Code gốc: `/Users/admin/personal/english-app` (TBD path)
- Rules: `./rules/README.md` (chưa có file override; shared `../rules/forgejo-workflow.md`)
- Specs: `../../openspec/specs/english-app/overview.md`

## Pending decisions

- [ ] Chốt framework BE
- [ ] Chốt framework web (SSR cần không?)
- [ ] Chốt Expo vs bare RN
- [ ] Chốt monorepo tool
- [ ] Chốt auth strategy (JWT self-host / Auth0 / Clerk / Supabase)
- [ ] Chốt scope MVP features phase 1
- [ ] Setup repo + initial scaffold
