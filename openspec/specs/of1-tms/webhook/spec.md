# webhook Specification

## Purpose
Module xử lý inbound webhook từ external systems (BFSOne, platform event, partner feedback).
Verify authentication token/signature, dispatch theo (source, event type), log mọi event.

## Requirements

### Requirement: Authentication token verify trước dispatch
Mọi inbound webhook SHALL verify authentication token hoặc signature trước khi dispatch handler.

#### Scenario: Request có token hợp lệ
- **WHEN** POST tới `/webhook/<source>/<event>` với header `Authorization: Bearer <token>` khớp `TMSWebhookAuthToken`
- **THEN** verify pass, chuyển sang dispatcher

#### Scenario: Request không có / sai token
- **WHEN** POST tới webhook endpoint mà thiếu header hoặc token không khớp
- **THEN** trả HTTP 401, không dispatch handler, log event với status `AUTH_FAILED`

### Requirement: Dispatcher theo (source, event type)
`dispatcher` SHALL route event tới handler dựa trên tuple `(source, eventType)`.

#### Scenario: BFSOne gửi bill update
- **WHEN** POST tới `/webhook/bfsone/bill_updated` với payload hợp lệ
- **THEN** dispatcher tìm handler đăng ký cho `(bfsone, bill_updated)` → invoke handler
- **AND** nếu không có handler → log `UNHANDLED`, không ném exception ra ngoài

### Requirement: Log mọi webhook event
Mọi inbound event SHALL được log vào `TMSWebhookEvent` với payload nguyên gốc để trace/replay.

#### Scenario: Nhận event
- **WHEN** webhook endpoint nhận POST
- **THEN** tạo `TMSWebhookEvent` với `source`, `eventType`, `payload` (JSON gốc), `receivedAt`
- **AND** sau khi xử lý: update `processedAt` + `status` (PROCESSED / FAILED / UNHANDLED)

### Requirement: Authtoken rotate
`TMSWebhookAuthToken` SHALL có expiry và có thể rotate không downtime.

#### Scenario: Rotate token
- **WHEN** admin rotate token cho source `BFSONE`
- **THEN** tạo token mới + mark token cũ `expiresAt = now + grace_period`
- **AND** trong `grace_period` cả 2 token đều verify pass, sau đó chỉ token mới valid
