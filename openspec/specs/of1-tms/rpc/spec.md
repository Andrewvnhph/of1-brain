# rpc Specification

## Purpose
Module cầu nối duy nhất của TMS tới các service của Platform (và các RPC lib dùng chung) qua
RPC chứ không qua Kafka. Đóng gói `PlatformClient`, `CommunicationRPC`, `StorageRPC`,
`LocationRPC`, `JobTrackingRPC`, `BotService`.

## Requirements

### Requirement: Mọi call ra Platform đi qua RPC module
Mọi lời gọi TMS → Platform SHALL đi qua bean RPC trong module này, **không** gọi Kafka trực tiếp
và không gọi HTTP tay.

#### Scenario: Lấy account từ platform
- **WHEN** module `bill` cần get account info của customer
- **THEN** inject `PlatformClient`, gọi `platformClient.getAccount(accountId)`, không viết HTTP call manual

#### Scenario: Vi phạm — gọi Kafka trực tiếp
- **WHEN** module nghiệp vụ cố gắng publish message Kafka tới platform
- **THEN** đây là vi phạm convention; **phải** refactor sang gọi RPC tương ứng (hoặc expose RPC mới nếu platform chưa có)

### Requirement: Context propagation qua header
`ClientContext` SHALL được propagate sang Platform qua header khi RPC call.

#### Scenario: Call sang Platform có permission
- **WHEN** TMS gọi `platformClient.listCompanyPermissions()` cho user hiện tại
- **THEN** header request chứa JWT / client context để Platform verify permission độc lập

### Requirement: Retry policy mặc định
Mỗi RPC client SHALL có retry policy mặc định (3 lần, backoff exponential) với timeout hợp lý
theo SLA của Platform.

#### Scenario: Platform tạm thời unavailable
- **WHEN** RPC call fail do network / 5xx tạm thời
- **THEN** retry theo policy, log attempts, trả error sau cùng nếu vẫn fail
- **AND** không retry với 4xx client error (validation, permission)
