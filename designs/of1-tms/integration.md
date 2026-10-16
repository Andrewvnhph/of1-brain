# Design — integration (hiện trạng)

Module đóng gói mọi tích hợp external của TMS (BFSOne, Microsoft Graph, crypto helper).
Cầu nối duy nhất từ domain TMS ra ngoài (không kể platform RPC đã có ở `rpc`).

## Boundary

- Package gốc `cloud.datatp.tms.integration`.
- Phụ thuộc: `core`, `rpc` (nếu cần platform metadata). Được `bill`, `fleet` dùng khi cần external data.

## Sub-packages

| Package | Trách nhiệm |
|---|---|
| `bfsone` | BFSOne REST API client (cost template sync, truck template sync, employee sync, bill push) |
| `msgraph` | Microsoft Graph API client (email, calendar, user directory) |
| `crypto` | Crypto helper (encrypt API key, token signing cho webhook) |
| `tracking` | AOP tracking outbound call (log API call latency, error rate, alert) |
| `config` | External system config (base URL, API key, retry policy) |

## Data model chính

- `BFSOneCredential` — credential config per company (encrypted).
- `BFSOneApiLog` — audit mọi call BFSOne (request/response, latency, status).
- `MsGraphCredential` — Microsoft tenant credential per company.
- `ApiCallTrace` (chung với tracking) — generic outbound call trace.

## Luồng chính

- **BFSOne sync bill**: `bill` module gọi `BFSOneClient.pushBill(bill)` → integration module build request → log request → gọi BFSOne → log response → return.
- **BFSOne sync template**: cron pull cost/truck template từ BFSOne → upsert vào bảng cache local → publish event cho `bill` module invalidate.
- **BFSOne employee sync**: pull employee list → map sang `TMSEmployee` (reconcile theo `refCode`).
- **MS Graph email**: send email transactional qua Microsoft Graph (fallback / primary channel tuỳ config).
- **Tracking**: `@Tracked` AOP ở mọi method client → async lưu `ApiCallTrace` + alert khi error rate vượt ngưỡng.

## Ghi chú mở rộng

- Thêm external system mới → tạo sub-package riêng; không reuse BFSOne client cho system khác.
- Khi BFSOne thay đổi payload → cập nhật `TMSBillBFSOneLogic.convertBFSOneDataToTMSBills` (ở `bill` module) đồng bộ.
- Mọi API key / credential **phải** mã hoá qua `crypto` package khi lưu DB.
- Khi gọi external SLA quan trọng → luôn thêm `@Tracked` + alert threshold hợp lý.
