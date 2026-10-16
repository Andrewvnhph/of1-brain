# notification Specification

## Purpose
Module push mobile notification (Firebase) và email alert (via platform RPC hoặc MS Graph).
Quản lý device token, template, và log mọi notification đã gửi.

## Requirements

### Requirement: Firebase push qua Admin SDK
Hệ thống SHALL gửi push notification cho mobile app qua Firebase Admin SDK 9.4.1.

#### Scenario: Push khi bill assigned
- **WHEN** `bill` module publish event `BillAssignedToDriver` với `driverId=D`
- **THEN** notification module lookup `TMSDeviceToken` của driver D
- **AND** gọi Firebase Admin SDK gửi push, log kết quả vào `TMSNotificationLog`

### Requirement: Device token management
Mobile app SHALL gửi `TMSDeviceToken` qua service login/refresh; hệ thống lưu/update theo userId.

#### Scenario: Driver app login
- **WHEN** driver app login và gửi `deviceToken` + `platform` (iOS/Android)
- **THEN** service upsert `TMSDeviceToken` theo `(userId, platform)`
- **AND** token cũ của cùng user+platform bị invalidate

### Requirement: Template rendering với i18n
`TMSNotificationTemplate` SHALL support variable substitution và i18n (vi/en).

#### Scenario: Render template vi
- **WHEN** build push với template `BILL_ASSIGNED` + user locale `vi`
- **THEN** render variable (`{billCode}`, `{driverName}`) + lấy text locale `vi`
- **AND** fallback về `en` nếu locale user chưa có bản dịch

### Requirement: Log mọi notification
Mọi push/email/sms SHALL được log vào `TMSNotificationLog` với status.

#### Scenario: Push fail do token invalid
- **WHEN** Firebase trả error `UNREGISTERED` cho token
- **THEN** `TMSNotificationLog.status = FAILED`, `error = "UNREGISTERED"`
- **AND** `TMSDeviceToken` tương ứng mark `invalid = true`, không gửi tiếp
