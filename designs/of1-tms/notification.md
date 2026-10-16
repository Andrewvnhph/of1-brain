# Design — notification (hiện trạng)

Module push notification + email alert cho TMS. Dùng Firebase Admin SDK để push lên mobile
app; email có thể qua Microsoft Graph (xem `integration`) hoặc platform communication RPC.

## Boundary

- Package gốc `cloud.datatp.tms.notification`.
- Phụ thuộc: `core`, `rpc` (platform communication cho email/SMS platform-level).

## Sub-packages

| Package | Trách nhiệm |
|---|---|
| `firebase` | Firebase Admin SDK 9.4.1 — push mobile notification (driver app, dispatcher app) |
| `email` | Email template rendering + send (via platform RPC hoặc MS Graph fallback) |
| `template` | Template message system (variable substitution, i18n) |
| `webhook` | Outbound webhook tới platform (notify event, consume event để trigger push) |

## Data model chính

- `TMSNotificationLog` — vết mọi notification gửi: `type` (push/email/sms), `recipientId`, `payload`, `status`, `error`, `sentAt`.
- `TMSNotificationTemplate` — template config per event type + company.
- `TMSDeviceToken` — Firebase device token của user (đồng bộ từ mobile app).

## Luồng chính

- **Push on bill event**: `bill` module publish event (vd `BillAssignedToDriver`) → notification module build payload → gọi Firebase Admin SDK → log result.
- **Email digest**: cron scan bill overdue → render template → send qua platform communication RPC → log.
- **Device token management**: driver app login → gửi device token lên qua service → notification lưu/update `TMSDeviceToken`.
- **Platform webhook**: subscribe event từ platform (user permission change, company config change) → trigger push nếu cần.

## Ghi chú mở rộng

- Thêm notification type mới → thêm template + handler route theo `type`.
- Thêm channel mới (SMS, Zalo...) → sub-package riêng, không gộp vào `email`/`firebase`.
- Firebase credential key phải mã hoá (dùng `integration.crypto`).
- Mọi push phải log kết quả vào `TMSNotificationLog` để debug.
