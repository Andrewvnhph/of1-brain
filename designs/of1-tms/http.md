# Design — http (hiện trạng)

Module expose Spring `@Service` bean cho WebUI qua `createHttpBackendCall()` (RPC-style, không
REST controller riêng cho business logic). Chứa cấu hình HTTP routing + exposure cho FE.

## Boundary

- Package gốc `cloud.datatp.tms.http`.
- Phụ thuộc `rpc` (để forward call tới platform khi cần) và `core` (ClientContext, auth).
- Không chứa business logic — chỉ là lớp HTTP routing/exposure.

## Sub-packages

| Package | Trách nhiệm |
|---|---|
| `config` | HTTP server config (Jetty 12), CORS, request/response filter |
| `route` | Routing map từ `<ServiceName>.<methodName>` tới Spring `@Service` bean |
| `security` | HTTP-level security filter (OAuth2 Resource Server, Keycloak JWT) |
| `error` | Global exception handler, error response format cho FE |

## Data model chính

Không có entity riêng — chỉ DTO request/response wrapper:
- `BackendCallRequest {serviceName, methodName, params}` — map từ FE call.
- `BackendCallResponse {success, data, error}` — chuẩn hoá cho FE.

## Luồng chính

- **FE call** `createHttpBackendCall('TMSBillService', 'searchTMSBills', {...})` → HTTP POST.
- **Routing**: `http.route` nhận request, giải mã `serviceName/methodName`, lookup Spring bean, invoke method với `ClientContext` + params.
- **Security**: filter chain xác thực JWT (Keycloak) trước khi vào routing.
- **Error**: exception trong service → `error` package wrap thành response chuẩn, log kèm trace ID.

## Ghi chú mở rộng

- Thêm `@Service` bean mới → **không cần sửa gì** trong `http` (routing tự lookup theo tên bean).
- Thêm filter mới → thêm vào `security` package, giữ thứ tự chain.
- Khi thêm endpoint non-RPC (webhook, OAuth callback) → vẫn qua `http.route` nhưng dùng `@RestController` riêng.
