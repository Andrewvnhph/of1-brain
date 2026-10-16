<!--
  DIVERGED từ: /Users/admin/OF1/forgejo/of1-platform/of1-tms-engineering-hub/rules/forgejo-workflow.md
  Last synced: 2026-10-13.
  SCOPE ĐÃ THU HẸP: file này giờ chỉ cover **git workflow** (commit/push/branch).
  Issue/task tracking đã chuyển sang `openproject-workflow.md` (OpenProject thay Forgejo issue).
-->

# Forgejo Git Workflow

Thao tác git với Forgejo (`git.datatp.cloud`) — chỉ repo `of1-tms/of1-tms` (writable). 3 repo khác (`of1-platform`, `of1-core`, `of1-webui`) là read-only, không commit (xem HARD SAFETY RULE trong `brainstorms/of1-tms/CLAUDE.md`).

## ⚠️ Hard Rule — No Confirmation

Commit / push / tạo branch trên `of1-tms`: **KHÔNG hỏi dev confirm**, chạy end-to-end. Hard constraint: **KHÔNG** `merge`, **KHÔNG** `push origin develop`.

## Branch convention

- Tạo branch mới cho mỗi TODO: `ai/<slug>` off `develop`.
- `<slug>` match slug trong brainstorms (vd TODO `[bill] thêm field X` → branch `ai/bill-add-field-x`).
- Multi-TODO cùng feature → 1 branch chung, nhiều commit.

## 🚨 Pre-commit safety check (BẮT BUỘC)

**Trước MỖI `git commit`**, phải chạy:

```bash
git branch --show-current
```

và verify output **KHÔNG phải** `develop` / `main` / `master` / `release`.

### Vì sao bắt buộc

Scenario thực tế đã xảy ra (2026-10-14):
1. AI tạo branch `ai/<slug>`, commit, push, dev merge PR vào `develop` trên Forgejo.
2. Dev local `git pull` → kéo `develop` forward, branch `ai/<slug>` local **mất khác biệt với `develop`** (đã merge).
3. Khi AI quay lại edit tiếp, **HEAD trỏ `develop`** (do một thao tác fast-forward hoặc checkout trước đó).
4. AI commit tiếp → landed trên `develop` local → suýt push vi phạm HARD SAFETY.

Branch state của AI **không stable** qua các turn (sau dev interaction, merge, fetch), nên verify thủ công mỗi lần.

### Checklist pre-commit

```bash
# 1. Check branch — PHẢI khác develop/main
CURRENT=$(git branch --show-current)
if [[ "$CURRENT" == "develop" || "$CURRENT" == "main" || "$CURRENT" == "master" || "$CURRENT" == "release" ]]; then
  echo "⛔ TRÊN BRANCH SHARED — DỪNG, tạo feature branch trước"
  exit 1
fi

# 2. Check staged file đúng scope TODO (không add nhầm file khác)
git diff --cached --stat

# 3. Mới commit
git commit -m "..."
```

### Recovery khi lỡ commit trên develop (chưa push)

Nếu commit đã landed local trên `develop` mà **chưa push** (`git status` nói `ahead of origin/develop by N commits`), fix non-destructive:

```bash
# 1. Tạo branch mới trỏ vào commit hiện tại (preserve work)
git branch ai/<new-slug>

# 2. Reset local develop về origin/develop
git reset --hard origin/develop

# 3. Checkout branch mới + push
git checkout ai/<new-slug>
git push origin ai/<new-slug>
```

Nếu commit **đã lỡ push origin develop** → **STOP, báo dev ngay**. Dev sẽ cần revert trên Forgejo + có thể force-push origin develop (chỉ dev được làm, không phải AI).

## Commit scope + message

**Scope**: chỉ file thuộc TODO đang xử lý, không mix sang TODO khác.

**Format commit message**:
```
<type>(<module>): <tóm tắt TODO, lowercase, imperative, ≤72 chars>

Refs: brainstorms/of1-tms/<user>.md TODO "<nội dung TODO đầy đủ>"
Refs: #<openproject-wp-id> (nếu đã có work_package tracking)
```

- `<type>`: `feat` / `fix` / `refactor` / `chore` / `docs` / `test`
- `<module>`: tag module trong TODO (`bill`, `fleet`, `ops`, `core`…)
- Line 2 `Refs: brainstorms/...` để trace về TODO gốc
- Line 3 `Refs: #<wp-id>` để OpenProject auto-link (nếu task đã có work_package)

**Ví dụ**:
```
feat(bill): add deliveryContact field to TMSBill

Refs: brainstorms/of1-tms/mchien.md TODO "[bill] Thêm field deliveryContact vào TMSBill"
Refs: #1234
```

## Push

```bash
git push origin ai/<slug>
```

**KHÔNG**:
- `git push origin develop` / `main`
- `git merge` vào `develop`
- `--force` push lên branch dev khác (chỉ force lên `ai/<slug>` của chính mình nếu cần amend)

## Sau khi push

1. Update brainstorm Summary table (check `[x]` TODO + append link branch + status).
2. Update OpenProject work_package: xem `openproject-workflow.md` → add comment progress + set status.
3. **Dừng**. Dev review branch + tạo PR / merge thủ công.

## 🧹 Cleanup local branch sau khi dev merge PR

Khi dev đã merge `ai/<slug>` trên Forgejo UI, chạy cleanup trước khi start TODO mới để tránh accumulate junk local branches.

### Pattern an toàn (chỉ xoá merged branch)

```bash
cd <path-to-of1-tms>

# 1. Fetch + prune remote tracking refs đã bị xoá trên remote
git fetch --prune

# 2. Switch sang develop để check merged state
git checkout develop
git pull origin develop

# 3. List các ai/* đã merged (safe scan)
git branch --merged origin/develop | grep '^  ai/'

# 4. Xoá từng branch merged (git -d check lại, từ chối xoá nếu chưa merge)
for b in $(git branch --merged origin/develop | grep '^  ai/' | sed 's/^  //'); do
  git branch -d "$b"
done

# 5. (Optional) Quay về feature branch đang work tiếp theo
git checkout ai/<next-slug>
```

### Rule vàng

- **Dùng `-d` lowercase**: git từ chối xoá branch chưa merged → an toàn, không mất code.
- **TUYỆT ĐỐI tránh `-D` capital**: force xoá cả branch chưa merged → mất commit nếu chưa push remote.
- **Không xoá branch đang checkout**: git tự block (lỗi "cannot delete branch currently checked out").
- **Chỉ xoá `ai/*` prefix**: không đụng branch của dev khác (`chien`, `nhat`, `document`...).

### Nếu `-d` từ chối vì "not fully merged"

Nghĩa là branch có commit chưa vào `develop`. 2 khả năng:
1. PR chưa thực sự merged → check Forgejo UI, nếu merged thì `git fetch --prune` lại rồi retry.
2. Dev merged bằng squash commit → `-d` không nhận ra; dùng `git branch -D` **chỉ khi** đã xác nhận PR đã merge trên UI.

Khi nghi ngờ: dừng, báo dev. Branch local không gây hại (chỉ chiếm ref), xoá sau cũng được.

## Auth

- Token: `~/.forgejo-token` (mode `600`). Chỉ cần cho `git push` qua HTTPS (nếu dùng SSH thì không cần).
- Base URL: `https://git.datatp.cloud` · Repo: `of1-tms/of1-tms`.
