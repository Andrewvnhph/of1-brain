# english-app · mchien — TODO cá nhân

> Brainstorm file của **mchien**. Mỗi TODO ghi scope rõ để AI load đúng grounding.
> Convention + HARD SAFETY RULE + rules xem `./CLAUDE.md`.

## Format TODO

```
- [ ] [<scope>] <nội dung ngắn gọn, 1 ý>
```

- `<scope>` ∈ `{backend, web, mobile, mongo, shared, infra, overview}`
- Multi scope → `[backend,mongo]` hoặc `[web,mobile]`

## TODO (dev)

<!-- Dev fill ideas tự do ở đây. AI chạy pipeline khi TODO không có `[?]` ambiguous. -->

- [ ] [overview] Chốt stack framework: Express/Fastify/NestJS? Vite/Next.js? Expo/bare RN?
- [ ] [overview] Setup repo + folder structure monorepo (apps/backend, apps/web, apps/mobile, packages/shared)
- [ ] [overview] Scope phase 1 — chốt features MVP (flashcard SRS / vocab quiz / grammar check / conversation / listening?)

## Summary (AI)
<!-- AI điền ngay dưới TODO sau khi chạy pipeline. Dev không sửa tay. -->

| TODO | scope | design | openspecs | code | review | status |
|---|---|---|---|---|---|---|
