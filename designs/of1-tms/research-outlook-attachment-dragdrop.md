# Research — Drag-drop chứng từ đính kèm từ Outlook sang TMS webui

> **Status**: Research only — kết luận feasibility + đề xuất hướng. Chưa phải design triển khai.
> **Owner**: mchien · **Scope**: TMS webui (bill/vendor-bill attachment UI) + S3 upload backend.
> **TODO gốc**: `brainstorms/of1-tms/mchien.md` — `[+ui,bill] Chứng từ đính kèm: nghiên cứu khả năng kéo-thả từ Outlook mà không cần tải file về máy`

## TL;DR

| Case | Feasible? | Chi phí triển khai |
|------|-----------|--------------------|
| Kéo **1 file đính kèm** từ Outlook Desktop (Win/Mac) → TMS | **✅ ĐƯỢC**, gần như free (code hiện tại đã handle) | Thấp — có thể dùng ngay sau khi enable UI |
| Kéo **cả email** `.msg` từ Outlook Desktop | ⚠️ Có nhận được file `.msg` nhưng là binary proprietary (OLE compound) — cần parser để lấy attachment bên trong | Cao — cần thư viện parse `.msg` (vd `msg-reader`) |
| Kéo từ **Outlook Web (OWA)** sang TMS tab khác | ❌ KHÔNG stable — browser cross-tab security chặn | — |
| Kéo từ **Outlook Web** trong iframe cùng TMS | Có thể nhưng OWA không cho embed; cần tích hợp qua Microsoft Graph (async, OAuth) | Cao |

**Kết luận**: Trường hợp "dev kéo trực tiếp 1 attachment PDF/XLSX từ Outlook Desktop vào TMS" **đã sẵn sàng** — chỉ cần enable UI attachment ở Bill editor (hiện đang commented out). Trường hợp "kéo cả email" cần đầu tư thêm (`.msg` parser).

---

## 1. Hiện trạng TMS

### 1.1. Code sẵn — S3 upload drag-drop đã có

**Component**: `S3UploadDropZone` tại `webui/tms/src/app/logistics/s3/UIS3AttachmentList.tsx:149-236`.

Dùng HTML5 DataTransfer modern API:
```typescript
// line 174-186 (tóm tắt):
onDrop(e) {
  const dt = e.dataTransfer;
  if (dt.items && dt.items.length) {
    if (dt.items[0].kind === 'file') f = dt.items[0].getAsFile();
  } else if (dt.files.length) {
    f = dt.files[0];
  }
  // upload f via S3ServiceApi
}
```

- Modern `dataTransfer.items` + fallback `dataTransfer.files`
- Call backend qua `S3ServiceApi.uploadObjects()` → `S3ApiService.uploadObjects()` ở `of1-core`
- Format: base64-encoded data URL (`data:<mime>;base64,...`), backend tự strip prefix
- Supported extensions hiện tại: image (jpg/png/gif/svg/webp), pdf, office (docx/xlsx/pptx), text (json/xml), csv

### 1.2. UI attachment ở Bill — **đang commented out**

File `webui/tms/src/app/logistics/vendor/UITMSVendorBillEditor.tsx:248-250`:
```tsx
// {/* <Button ...>File Attachment</Button> */}
```

Housebill editor **chưa có** attachment UI.

→ **Pre-requisite**: Enable (uncomment + wire up) UI attachment ở `UITMSVendorBillEditor` và các editor bill khác trước khi nói chuyện Outlook drag-drop.

### 1.3. Backend S3 — không có MIME filter

`of1-core/.../S3ApiService.java:82-83` → `uploadObjects(List<S3ObjectContent>)`.

`S3ObjectContent`:
- `bucket`, `key`, `data` (byte[]), `contentType`, `metadata`
- **Không validate MIME, extension, size** ở API level

→ Có nghĩa `.msg` / `.eml` upload được, backend không block. Decision validation ở frontend.

---

## 2. Outlook drag-drop — hành vi thực tế

### 2.1. Kéo 1 attachment riêng (phổ biến nhất)

Khi user chọn 1 file đính kèm trong email và kéo vào browser:

| OS | Browser nhận được |
|----|-------------------|
| Windows Outlook Desktop | `dataTransfer.files[0]` là File object chuẩn (MIME đúng theo file, vd `application/pdf`) |
| Mac Outlook Desktop | Tương tự — File object chuẩn |

→ **Code `S3UploadDropZone` hiện tại handle được ngay**. Không cần modify logic drop.

### 2.2. Kéo cả email (toàn message)

| OS | Browser nhận được |
|----|-------------------|
| Windows Outlook | File `.msg` binary (MIME `application/vnd.ms-outlook` hoặc `message/rfc822`) — **OLE compound document**, không plain text |
| Mac Outlook (Intel) | Tương tự Windows |
| Mac Outlook (Apple Silicon) | **wemlinktype** data (string reference) — KHÔNG phải File object. Không save được qua browser |

→ Để lấy attachment từ `.msg` cần parser browser-side (vd `msg-reader`, `@kenjiuno/msgreader`). Chi phí: thêm dependency ~100KB, parse CPU-intensive với email lớn.

### 2.3. Outlook Web (OWA)

- Cross-tab drag (OWA tab → TMS tab): **không reliable** — browser security chặn
- Nếu embed OWA trong iframe: Microsoft không cho embed trực tiếp (X-Frame-Options)
- Workaround duy nhất: dùng **Microsoft Graph API** (OAuth scope `Mail.Read`) để fetch attachment theo email ID. Nhưng flow không phải drag-drop — user phải chọn email + attachment từ UI phụ

### 2.4. Metadata email

**Không khả dụng** qua DataTransfer: subject, sender, date, body text — chỉ có binary `.msg` (phải parse) hoặc file attachment riêng (không có context email).

---

## 3. Đề xuất hướng triển khai (3 phase)

### Phase 1 — Quick win: Enable UI + verify flow (ưu tiên)

**Scope**: Cho dev kéo-thả **1 attachment** từ Outlook Desktop vào TMS Bill editor.

Việc cần làm:
1. Uncomment + wire `UITMSVendorBillEditor.tsx:248-250` để show File Attachment button → mở popup `UIS3AttachmentList` (đã có sẵn).
2. Thêm attachment UI tương tự cho `UITMSHouseBillEditor`.
3. Verify E2E: Outlook Desktop → drag PDF attachment → S3UploadDropZone → S3 upload → bill persist link.

**Chi phí**: thấp (chỉ wire UI đã code sẵn). Có thể làm trong 1 TODO scope nhỏ.
**Lợi ích**: cover ~80% use case thực tế (dev chỉ kéo file đính kèm, không kéo cả email).

### Phase 2 — Enhancement: Multi-file drop

**Scope**: Cho phép kéo nhiều attachment cùng lúc.

Hiện `S3UploadDropZone:174-186` chỉ xử lý `dt.items[0]` / `dt.files[0]`. Loop qua all items để support multi-file.

**Chi phí**: thấp, chỉ sửa 1 component.
**Lợi ích**: UX tốt hơn khi email có nhiều file đính kèm.

### Phase 3 — Advanced (optional): Parse `.msg`

**Scope**: Nhận file `.msg` → extract attachments bên trong → upload từng cái.

**Approach**: thêm `@kenjiuno/msgreader` (hoặc tương đương) vào `webui/tms`. Khi drop file có extension `.msg` → parse browser-side → extract attachment stream → feed vào `S3UploadDropZone` existing logic.

**Chi phí**:
- Thêm dependency ~100-200KB
- Edge case: email có attachment lớn (>50MB) → browser memory issue
- Mac Apple Silicon: không nhận được `.msg` file, chỉ wemlinktype → không support được

**Lợi ích**: cover case dev lazy kéo cả email, nhưng % use case thấp.

**Khuyên**: hoãn Phase 3 cho tới khi có nhu cầu rõ ràng từ dev/business.

### Không khuyến khích

- **Outlook Web (OWA) integration** — cross-tab security chặn; Microsoft Graph OAuth flow phức tạp, không phải drag-drop thật.
- **Outlook Add-in / COM**: cài đặt phức tạp, chỉ Windows, không browser-native.

---

## 4. Giả định (assumptions) cần dev confirm

- [ ] Dev chủ yếu dùng **Outlook Desktop** (Windows hoặc Mac Intel), không phải Outlook Web.
- [ ] Use case 80%+ là kéo **1 attachment đã có trong email** (PDF, Excel), không phải kéo cả email để parse.
- [ ] Mac Apple Silicon Outlook users: không có hoặc chấp nhận không support kéo cả email.
- [ ] Backend S3 bucket + ACL cho bill attachment đã configure (chưa verify, cần confirm với infra team).

---

## 5. Open questions

1. **Attachment entity model**: hiện tại `UIS3AttachmentList` link attachment với entity nào? Có bảng `tms_bill_attachment` link `bill_id ↔ s3_object_key` không? Hay chỉ upload S3 generic, bill editor tự quản link?
2. **Permission**: ai được upload attachment vào bill nào? Theo `TMSBillResponsibility`? Có check qua `checkPermission` không?
3. **Preview**: sau upload, UI có cần preview inline (dùng `S3DocumentPreview`) hay chỉ list file + download link?
4. **Delete**: dev được xoá attachment đã upload không? Audit log?

Cần dev trả lời 1-4 trước khi vào Phase 1 implementation.

---

## 6. Next step (nếu dev approve Phase 1)

→ Tạo TODO follow-up trong `brainstorms/of1-tms/mchien.md`:
```
- [ ] [+ui,bill] Enable File Attachment UI ở UITMSVendorBillEditor + UITMSHouseBillEditor (reuse UIS3AttachmentList, drag-drop Outlook Desktop OK)
```

Pipeline chạy tiếp: design chi tiết → openspec → code → review → commit `ai/bill-enable-attachment-ui` → push → OpenProject work_package.
