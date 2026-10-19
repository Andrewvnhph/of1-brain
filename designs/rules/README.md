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
- **of1-document**: **reuse of1-tms rules trực tiếp** (same stack). Mapping naming trong `../of1-document/rules/README.md`. Chưa có file override — khi diverge sẽ tạo `of1-document/rules/<topic>.md`.

## Pattern reuse giữa projects

Khi 2 projects same stack (vd TMS + Document đều Spring Boot + React), có 2 cách tổ chức:

**(A) Project B reuse project A rules** (hiện tại):
- Pros: zero duplicate, dễ sync; project B chỉ cần CLAUDE.md trỏ sang A's rules + readme mapping naming.
- Cons: project B rely vào A có rule đúng; khi A refactor rule, B phải follow.

**(B) Promote rules lên shared `designs/rules/`** (phase sau):
- Pros: ownership rõ (shared ≠ project A); cả 2 ngang hàng.
- Cons: content TMS-specific (TMSDAOService, BBRefTMS*) phải rename sang generic hoặc split thành 2 files (shared base + project overrides).

Hiện tại dùng (A) vì phase bootstrap, chuyển sang (B) khi có project thứ 3 (vd of1-crm) dùng same rules → promote lúc đó justified.
