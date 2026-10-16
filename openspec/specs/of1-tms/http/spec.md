# http Specification

## Purpose
Module expose Spring `@Service` bean cho WebUI qua RPC-style HTTP (`createHttpBackendCall`),
cấu hình HTTP server (Jetty 12), security filter (Keycloak OAuth2), và global error handling.

## Requirements

### Requirement: RPC-style exposure cho FE
Hệ thống SHALL expose tất cả `@Service` bean của TMS qua endpoint HTTP chung
`POST /<serviceName>/<methodName>`.

#### Scenario: FE gọi service
- **WHEN** FE gọi `createHttpBackendCall('TMSBillService', 'searchTMSBills', params)`
- **THEN** request POST tới endpoint, routing lookup bean `TMSBillService` + method `searchTMSBills`
- **AND** params map vào method parameter **theo tên** (compile `-parameters`)

### Requirement: OAuth2 Keycloak filter
Mọi request vào TMS BE SHALL được xác thực qua Spring Security + Keycloak JWT trước khi vào routing.

#### Scenario: Request không có JWT
- **WHEN** request đến endpoint TMS mà không có `Authorization: Bearer <jwt>`
- **THEN** filter trả về HTTP 401, không invoke service

#### Scenario: JWT hợp lệ
- **WHEN** request có JWT hợp lệ (verify qua Keycloak public key)
- **THEN** filter inject claim vào `SecurityContext`
- **AND** `ClientContext` được build từ claim và forward vào method

### Requirement: Global error handling
Mọi exception từ service SHALL được chuẩn hoá thành response format
`{ success: false, error: { code, message, traceId } }`.

#### Scenario: Service ném exception
- **WHEN** `TMSBillService.saveTMSBill` ném `ValidationException`
- **THEN** global handler log kèm trace ID, trả response error với `code`/`message`/`traceId`
- **AND** HTTP status phù hợp (4xx cho user error, 5xx cho system error)
