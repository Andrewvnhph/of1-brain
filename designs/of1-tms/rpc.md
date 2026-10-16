# Design — rpc (hiện trạng)

Module đóng gói mọi lời gọi của TMS tới các service của Platform (và các integration khác)
qua RPC thay vì Kafka. Là cầu nối duy nhất TMS → `app/api` của `of1-platform`.

## Boundary

- Package gốc `cloud.datatp.tms.rpc`.
- Phụ thuộc Platform API client (`datatp-platform-app-api`) và các RPC lib dùng chung của `datatp-core`.
- **KHÔNG** gọi Kafka trực tiếp — tất cả tương tác với platform qua RPCService → `app/api`.

## Sub-packages

| Package | Trách nhiệm |
|---|---|
| `platform` | Client gọi vào Platform (`PlatformClient`): account, company, user, permission, approval |
| `communication` | Communication RPC (email/SMS/notification platform-level) |
| `storage` | Storage RPC (S3 upload, file metadata) |
| `location` | `LocationRPC` cho address/geocoding của platform |
| `jobtracking` | `JobTrackingRPC` cho tracking vehicle/shipment status |
| `bot` | `BotService` cho integration bot/automation |

## Data model chính

Không có entity DB — chỉ DTO request/response:
- `RPCRequest<T>` / `RPCResponse<T>` — generic wrapper.
- DTO cụ thể per service (ví dụ `GetAccountResponse`, `ListCompanyPermissionsResponse`).

## Luồng chính

- **Outbound call**: module nghiệp vụ (`bill`, `fleet`, `ops`…) inject bean RPC tương ứng (vd `@Autowired PlatformClient`) → gọi method → RPC lib handle serialize + HTTP transport.
- **Error / retry**: thấp hơn Platform SLA → retry theo policy mặc định; log + alert khi fail ngoài ngưỡng.
- **Context propagation**: `ClientContext` được forward qua header; permission check phía Platform.

## Ghi chú mở rộng

- Thêm RPC call mới → thêm method trong client tương ứng (vd `PlatformClient.getXxx`), không viết HTTP call tay.
- Khi platform expose service mới → sync DTO + method theo `datatp-platform-app-api` version mới nhất.
- **Tuyệt đối không** thay bằng Kafka call cho sync use case — vi phạm convention core TMS.
