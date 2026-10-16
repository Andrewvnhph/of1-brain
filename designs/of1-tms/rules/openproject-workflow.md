# OpenProject Workflow (TMS task tracking)

Platform task tracking chính thức cho TMS. Thay thế Forgejo issue tracker.

- **Instance URL**: https://insight.openfreightone.com
- **UI route**: `/projects/TMS/work_packages`
- **API base** (OpenProject v3): `https://insight.openfreightone.com/api/v3`
- **Project**: `TMS` → internal ID **`75`**

## ⚠️ Hard Rule — No Confirmation

Tạo work_package / comment / update status / assign: **KHÔNG hỏi dev confirm**, chạy end-to-end. Chỉ dừng khi ambiguous fact không thể infer.

## Default values (TMS project)

Từ sample call user cung cấp (2026-10-13):

| Field | Default | API link |
|-------|---------|----------|
| **Project** | TMS | `/api/v3/projects/75` |
| **Type** | Task | `/api/v3/types/1` |
| **Status** (khi tạo) | New | `/api/v3/statuses/1` |
| **Priority** | Normal | `/api/v3/priorities/8` |
| `scheduleManually` | `true` | — |
| `_meta.validateCustomFields` | `true` | — |

Null (optional, bỏ ra khỏi body nếu không set): `startDate`, `dueDate`, `estimatedTime`, `duration`, `percentageDone`, `storyPoints`, `category`, `assignee`, `responsible`, `parent`, `version`, `sprint`, `projectPhase`, `projectPhaseDefinition`.

## 🚧 Pending — User cần cung cấp thêm

- [ ] **API token** → lưu ở `~/.openproject-token` (mode `600`). Hiện CHƯA có → AI chưa gọi API thật được.
- [ ] Danh sách **type** khác ngoài `Task` (nếu dùng Feature / Bug / User Story / Epic): tra `GET /api/v3/types` → map ID.
- [ ] Danh sách **status** workflow TMS: `New(1) → ? → ? → Closed`. Chạy `GET /api/v3/statuses` để lấy.
- [ ] Danh sách **priority**: `GET /api/v3/priorities`.
- [ ] Default **assignee** (`196phamminhchien`? cần `GET /api/v3/users?filters=...` để lấy user ID numeric).
- [ ] **Custom fields** của TMS project (nếu có — vd module tag, sprint, estimated hours).
- [ ] Parent "Main Epic" / Sprint current có cần set không? (hiện default `null`).

## Create work_package — API template

**Endpoint**: `POST /api/v3/work_packages` (hoặc nested `/api/v3/projects/75/work_packages`).

**Auth** (OpenProject v3 chuẩn): HTTP Basic `apikey:<token>` → `Authorization: Basic $(echo -n "apikey:<token>" | base64)`.

**Note về sample user cung cấp**: endpoint `/projects/TMS/work_packages` + `x-csrf-token` + session cookie là **Rails UI route**, không phải API v3. UI route chỉ dùng được qua browser (có session). AI automation phải dùng **API v3 endpoint + API token**.

**Minimal body** (chỉ required fields):

```json
{
  "subject": "<tóm tắt TODO>",
  "_links": {
    "project":  { "href": "/api/v3/projects/75" },
    "type":     { "href": "/api/v3/types/1" },
    "status":   { "href": "/api/v3/statuses/1" },
    "priority": { "href": "/api/v3/priorities/8" }
  }
}
```

**Full body template** (có description, assignee, parent):

```json
{
  "subject": "<tóm tắt TODO>",
  "description": {
    "format": "markdown",
    "raw": "<nội dung TODO đầy đủ + context>"
  },
  "scheduleManually": true,
  "_meta": { "validateCustomFields": true },
  "_links": {
    "project":  { "href": "/api/v3/projects/75" },
    "type":     { "href": "/api/v3/types/1" },
    "status":   { "href": "/api/v3/statuses/1" },
    "priority": { "href": "/api/v3/priorities/8" },
    "assignee": { "href": "/api/v3/users/<userId>" },
    "parent":   { "href": "/api/v3/work_packages/<parentWpId>" }
  }
}
```

**curl**:

```bash
TOKEN=$(cat ~/.openproject-token | tr -d '\n\r ')
BASE="https://insight.openfreightone.com/api/v3"

curl -s -X POST \
  -H "Authorization: Basic $(echo -n "apikey:$TOKEN" | base64)" \
  -H "Content-Type: application/json" \
  -d @body.json \
  "$BASE/work_packages"
```

Response trả `id` work_package mới → lưu vào brainstorm Summary + dùng cho `Refs #<id>` trong commit.

## Update work_package — status / assignee

```bash
# Lấy lockVersion trước (bắt buộc với OpenProject optimistic locking)
curl -s -H "Authorization: Basic ..." "$BASE/work_packages/<wpId>" | jq .lockVersion

# PATCH với lockVersion
curl -s -X PATCH -H "Authorization: Basic ..." -H "Content-Type: application/json" \
  -d '{"lockVersion": <n>, "_links": {"status": {"href": "/api/v3/statuses/<newStatusId>"}}}' \
  "$BASE/work_packages/<wpId>"
```

## Add comment / activity

```bash
curl -s -X POST \
  -H "Authorization: Basic ..." -H "Content-Type: application/json" \
  -d '{"comment": {"raw": "<comment markdown>"}}' \
  "$BASE/work_packages/<wpId>/activities"
```

## Linking commit ↔ work_package

- Commit message chứa `Refs #<wp-id>` → nếu OpenProject có repository integration plugin, auto-link về work_package.
- Nếu plugin chưa cài → AI phải manual add comment work_package reference commit SHA sau khi push.

## Pipeline integration với brainstorm

Khi dev viết TODO mới trong `brainstorms/of1-tms/<user>.md`:

```markdown
- [ ] [bill] Thêm field deliveryContact vào TMSBill
```

AI flow:
1. **Tạo work_package** qua `POST /api/v3/work_packages` với:
   - `subject`: `[bill] Thêm field deliveryContact vào TMSBill`
   - `description.raw`: full context từ brainstorm (nếu có thêm context ngoài TODO line)
   - `_links.assignee`: map user owner của brainstorm file (`mchien` → user ID numeric)
   - Default type/status/priority như bảng trên
2. **Lưu `wpId`** vào Summary table (cột mới `wp` hoặc append `OP#<id>` vào status).
3. **Commit code** reference `Refs #<wpId>` để auto-link.
4. Khi code review done → **PATCH status** sang `In review` / `Closed` (chờ dev fill mapping status workflow).
5. **Add activity comment** tóm tắt progress + link branch `ai/<slug>`.

## API Cheatsheet (quick ref)

```bash
TOKEN=$(cat ~/.openproject-token | tr -d '\n\r ')
BASE="https://insight.openfreightone.com/api/v3"
AUTH="Authorization: Basic $(echo -n "apikey:$TOKEN" | base64)"

# List types / statuses / priorities (chạy 1 lần để map ID)
curl -s -H "$AUTH" "$BASE/types"
curl -s -H "$AUTH" "$BASE/statuses"
curl -s -H "$AUTH" "$BASE/priorities"

# Get project TMS detail
curl -s -H "$AUTH" "$BASE/projects/75"

# Create work_package
curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" -d @body.json "$BASE/work_packages"

# Get work_package (lấy lockVersion)
curl -s -H "$AUTH" "$BASE/work_packages/<id>"

# Update
curl -s -X PATCH -H "$AUTH" -H "Content-Type: application/json" -d @patch.json "$BASE/work_packages/<id>"

# Comment
curl -s -X POST -H "$AUTH" -H "Content-Type: application/json" \
  -d '{"comment": {"raw": "..."}}' "$BASE/work_packages/<id>/activities"
```

## Gotchas

- **lockVersion**: OpenProject dùng optimistic locking. Mỗi PATCH phải include `lockVersion` lấy từ GET gần nhất, nếu không trả 409 Conflict.
- **Rails UI route ≠ API v3**: endpoint `/projects/TMS/work_packages` + CSRF token là UI route (dùng session cookie), KHÔNG dùng cho automation. AI phải dùng `/api/v3/work_packages` + Basic auth với API token.
- **Build JSON body**: dùng `python3 -c 'import json; print(json.dumps({...}))'` hoặc file `body.json`, không inline `-d "..."` (escape hell).
- **Custom field IDs**: nếu TMS có custom field → ID là `customField<N>` trong body + href dạng `/api/v3/custom_fields/<N>` trong _links. Chạy `GET /api/v3/work_packages/schema` của project TMS để liệt kê schema đầy đủ.
