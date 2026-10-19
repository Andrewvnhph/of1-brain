# designs/rules/ — Shared rules áp cho mọi project

## Scope

Rules trong thư mục này áp dụng **cho tất cả projects** AI write code trong workspace OF1 (hiện tại: `of1-tms`, `of1-document`; tương lai: `of1-crm`, `of1-wms`, ...). Khi code bất kỳ project nào, AI load các rule shared này cộng với rule project-specific.

## File hiện có

| File | Nội dung |
|---|---|
| `forgejo-workflow.md` | Git workflow với Forgejo (branch `ai/<slug>`, commit scope, pre-commit check, cleanup, PR). Repo paths cho mỗi project ghi riêng trong CLAUDE.md tương ứng |

## Nguyên tắc 2-layer (shared + project-specific)

```
designs/
├── rules/                       — Shared rules (90% dùng chung)
│   ├── README.md                — Convention + layer explain
│   └── forgejo-workflow.md
├── of1-tms/
│   └── rules/                   — TMS-specific overrides/extensions
│       ├── backend.md           — Spring/JPA + TMS layer (Service→Logic→Repo, TMSDAOService, SqlMapRecord)
│       └── frontend.md          — React + TMS-specific (BBRefTMS*, SpacePlugin, Init shell)
├── of1-document/
│   └── rules/                   — Document-specific (hiện trạng: chưa có file, reference TMS rules)
└── of1-crm/ ... (future)
```

**Loading order** trong CLAUDE.md của mỗi project (vd `brainstorms/of1-tms/CLAUDE.md`):
1. **Shared layer** — `../../designs/rules/*.md` (forgejo workflow)
2. **Project layer** — `../../designs/<project>/rules/*.md` (backend/frontend tùy project)
3. Khi 2 layer conflict → **project layer win** (project-specific override shared).

## Khi edit rule

- **Shared rule change** (vd `forgejo-workflow.md`) → verify không break workflow của bất kỳ project. Test tối thiểu: TMS + Document.
- **Project-specific rule change** → chỉ ảnh hưởng project đó, không touch shared.
- **Khi 1 pattern trở nên generic** (dùng ở 2+ projects) → promote từ project rule → shared rule.
- **Khi rule shared bị override quá nhiều ở 1 project** → có thể cần tách shared thành 2 variants hoặc demote về project rule.

## Khi thêm project mới

1. Tạo `designs/<new-project>/` + `designs/<new-project>/rules/` (nếu cần project-specific).
2. Tạo `brainstorms/<new-project>/CLAUDE.md` reference shared + project rules.
3. Tạo `openspec/specs/<new-project>/` cho capabilities.
4. Update HARD SAFETY RULE table trong CLAUDE.md các project liên quan (nếu `<new-project>` writable).

## Reference project rules hiện tại

- **of1-tms**: `../of1-tms/rules/{backend,frontend}.md` + `../of1-tms/rules/openproject-workflow.md`
- **of1-document**: chưa có rule riêng (phase 1), tham chiếu TMS rules
