# of1-tms rules — Project-specific

Rules áp **chỉ** cho project `of1-tms` (repo `/Users/admin/OF1/forgejo/of1-platform/of1-tms`).

**Shared rules** load trước từ `../../rules/*.md` (xem `../../rules/README.md` cho convention 2-layer).

## File

| File | Scope |
|---|---|
| `backend.md` | Java/Spring/JPA + TMS layer convention (Service → Logic → Repo, TMSDAOService, SqlMapRecord, DDD aggregate `set(ClientContext, ICompany)`, Repository package `.repository`, MapObject accessors, Kafka inbound patterns) |
| `frontend.md` | React class components + TMS-specific (`BBRefTMS*` reference pickers, SpacePlugin + Init shell flow, DbEntityList patterns, VGrid config, notification 3 cấp, scroll viewer flex pattern, bs.Button convention) |
| `openproject-workflow.md` | Task tracking qua OpenProject `insight.openfreightone.com` (hiện STUB — chờ dev fill API cấu trúc) |

## Nguyên tắc

- Rule generic (không chứa `TMSBill` / `TMSEmployee` / shell/init-tms) **không** đặt ở đây — promote lên `../../rules/`.
- Rule có pattern chỉ xuất hiện trong TMS stack → giữ ở đây.
- Khi `of1-document` / `of1-crm` cần rule tương tự → copy sang project đó HOẶC promote lên shared nếu identical.
