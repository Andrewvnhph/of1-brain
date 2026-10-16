# Design — webhook (hiện trạng)

Module xử lý webhook inbound từ external systems (BFSOne, platform event, partner feedback).
Khác với outbound webhook (xem `notification.webhook`).

## Boundary

- Package gốc `cloud.datatp.tms.webhook`.
- Phụ thuộc: `core` (ClientContext, auth), `bill` (dispatch event vào bill module), `integration` (verify signature nếu cần).

## Sub-packages

| Package | Trách nhiệm |
|---|---|
| `endpoint` | Inbound HTTP endpoint (`/webhook/<source>/<event>`) — nhận POST từ external |
| `auth` | Authentication token verification cho inbound (feature recent #422 Oct 12) |
| `dispatcher` | Route event theo `source + event type` tới handler trong module nghiệp vụ |
| `handler` | Handler implementation per event type (bill update từ BFSOne, status callback…) |
| `log` | Audit log cho mọi webhook nhận được |

## Data model chính

- `TMSWebhookEndpoint` — config endpoint: `source`, `authType`, `authSecret` (encrypted), `enabled`.
- `TMSWebhookEvent` — log event nhận được: `source`, `eventType`, `payload`, `receivedAt`, `processedAt`, `status`.
- `TMSWebhookAuthToken` — authtoken dùng để verify inbound (per source, có expiry).

## Luồng chính

- **Inbound request**: external POST tới `/webhook/<source>/<event>` → `auth` package verify token/signature → log `TMSWebhookEvent` status=RECEIVED.
- **Dispatch**: `dispatcher` lookup handler theo `(source, eventType)` → invoke → update status=PROCESSED hoặc FAILED.
- **Retry**: FAILED event có thể retry thủ công hoặc cron (optional).
- **Auth token management**: tạo/xoá/rotate authtoken qua service, không expose ra WebUI (admin-only).

## Ghi chú mở rộng

- Thêm source webhook mới → tạo endpoint route + auth strategy riêng (HMAC, OAuth, static token…).
- Thêm event type → thêm handler + register trong `dispatcher`.
- **Luôn** verify signature/token trước khi dispatch (security critical).
- Payload lưu nguyên vào `TMSWebhookEvent.payload` (JSON) để trace lỗi và replay.
