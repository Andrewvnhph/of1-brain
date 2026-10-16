# Design — Phase 1: Add drag-drop handler cho `UIMessageForm` attachment area

> **Status**: Design — chờ dev duyệt trước khi implement (lần đầu động code `of1-tms`).
> **TODO**: `brainstorms/of1-tms/mchien.md` — Phase 1 (FE only, no BE).
> **Prerequisite**: Research đã done (`research-outlook-attachment-dragdrop.md`).

## 1. Scope (THU HẸP sau khi dev clarify)

**FE only.** Không tạo bảng DB, không entity mới, không service mới, không migration.

- Add `onDragOver` + `onDrop` handler vào attachment area của `UIMessageForm`
- Dropped files → convert base64 → push vào `attB64DataMap` của observer (field đã có sẵn, `@Transient`, pattern có sẵn)
- Bill editor **đã** reuse `UIMessageForm` qua `UITMSBillMessage.tsx` → tự động hưởng lợi, không cần touch bill editor
- Message editor (ở các context khác) cũng tự động hưởng lợi

## 2. File duy nhất cần sửa

**`of1-tms/webui/tms/src/app/logistics/common/message/UIMessage.tsx`**

Method `UIMessageForm.buildBtnAttFile()` hiện tại (line 68-78) chỉ có file picker click. Cần wrap thêm drag-drop container.

### Trước

```tsx
buildBtnAttFile() {
  return (
    <div className='flex-grow-0 position-relative flex-vbox align-items-center justify-content-center my-1'
      style={{ width: 20, height: 20, cursor: 'pointer' }}>
      <FeatherIcon.Plus size={20} className='text-primary' />
      <input type='file' name='uploadFiles[]' multiple={true}
        onChange={this.onSelectAttachmentFiles}
        className='position-absolute opacity-0' style={{ zIndex: 1, width: 20, height: 20 }} />
    </div>
  );
}
```

### Sau (option 1 — drop zone bao bọc toàn attachment area)

Thêm handler drop vào **wrapper** chứa cả `buildBtnAttFile` + `onRenderAttachFiles` (vì user kéo thả vào vùng attachment thì tự nhiên hơn là chỉ vào nút +).

Vùng này được render ở `buildReceiverInfo` (từ line 116). Cần tìm chỗ render + thêm `onDragOver` / `onDrop` + state `isDraggingOver` cho visual feedback.

Pseudo-code add:

```typescript
// Thêm state field
state = { isDraggingOver: false };

// Handler drag
onDragOver = (e: React.DragEvent) => {
  e.preventDefault();
  e.stopPropagation();
  if (!this.state.isDraggingOver) this.setState({ isDraggingOver: true });
};

onDragLeave = (e: React.DragEvent) => {
  e.preventDefault();
  e.stopPropagation();
  this.setState({ isDraggingOver: false });
};

onDropAttachment = async (e: React.DragEvent) => {
  e.preventDefault();
  e.stopPropagation();
  this.setState({ isDraggingOver: false });

  const files = this.extractFilesFromDataTransfer(e.dataTransfer);
  if (files.length === 0) return;

  // Reuse existing logic — convert file → base64 → observer
  const { observer } = this.props;
  const dataMap: Record<string, string> = observer.getBeanProperty('attB64DataMap', {});
  for (const f of files) {
    const fileData = await util.io.createB64ObjectData(f);
    const name = String(fileData.name || '').replace(/\.{2,}/g, '.');
    dataMap[name] = fileData.data;
  }
  observer.replaceBeanProperty('attB64DataMap', dataMap);
  observer.replaceBeanProperty('attB64DataMapChanged', true);
  this.forceUpdate();
};

// Helper tách files từ DataTransfer (Outlook Desktop drag works via dataTransfer.items[].getAsFile())
extractFilesFromDataTransfer = (dt: DataTransfer): File[] => {
  const files: File[] = [];
  if (dt.items && dt.items.length) {
    for (let i = 0; i < dt.items.length; i++) {
      if (dt.items[i].kind === 'file') {
        const f = dt.items[i].getAsFile();
        if (f) files.push(f);
      }
    }
  } else if (dt.files && dt.files.length) {
    for (let i = 0; i < dt.files.length; i++) files.push(dt.files[i]);
  }
  return files;
};
```

### Wire vào render

Trong `buildReceiverInfo` (hoặc chỗ render attachment area), wrap thêm:

```tsx
<div
  onDragOver={this.onDragOver}
  onDragLeave={this.onDragLeave}
  onDrop={this.onDropAttachment}
  className={`flex-vbox border p-2 ${this.state.isDraggingOver ? 'border-primary border-2' : ''}`}
  style={{ borderStyle: this.state.isDraggingOver ? 'dashed' : 'solid' }}
>
  {this.buildBtnAttFile()}
  {this.onRenderAttachFiles()}
</div>
```

→ Visual feedback: border xanh dashed khi đang drag qua, user biết target drop đúng chỗ.

## 3. Code sẽ touch

| File | Thay đổi |
|------|---------|
| `webui/tms/src/app/logistics/common/message/UIMessage.tsx` | Add 3 handler (`onDragOver`, `onDragLeave`, `onDropAttachment`) + helper `extractFilesFromDataTransfer` + wrap attachment area với drop zone |

**Không file nào khác.** Bill editor + các consumer khác của `UIMessageForm` tự động hưởng lợi.

## 4. Testing

- **Manual smoke test** (rule FE §5 không có testing framework cho TMS webui):
  - Mở Bill editor → click Send Mail → `UIMessageForm` hiện
  - Drag file PDF từ Outlook Desktop → thả vào attachment area
  - Verify: file xuất hiện trong attachment list, `attB64DataMap` có entry mới
  - Save/send → verify flow Message consumer process attachment như cũ
- **Edge cases**:
  - Drag nhiều file cùng lúc (Ctrl+click chọn multi trong Outlook rồi drag) → tất cả đổ vào map
  - Drag non-file (text, URL) → `dataTransfer.items[].kind !== 'file'` → bỏ qua silently
  - Drag file trùng tên với file đã có → ghi đè (map key = filename)
  - Mac Apple Silicon Outlook: drag cả email → wemlinktype, không có File → fallback bỏ qua (research đã note)

## 5. Pipeline nếu dev duyệt

1. Branch `ai/attachment-outlook-dragdrop` off `develop` trong `of1-tms`
2. Edit duy nhất `UIMessage.tsx` theo plan §2
3. Smoke test manual
4. Commit:
   ```
   feat(ui): add drag-drop handler cho UIMessageForm attachment area

   Hỗ trợ kéo thả file đính kèm từ Outlook Desktop (và file explorer) vào
   attachment zone. Tận dụng attB64DataMap transient có sẵn, không cần
   change BE / DB. Bill message editor tự hưởng lợi qua UITMSBillMessage.

   Refs: brainstorms/of1-tms/mchien.md TODO "[+ui,bill] Phase 1 — Enable
   attachment chứng từ cho bill: UI drag-drop add vào attB64DataMap"
   ```
5. `git push origin ai/attachment-outlook-dragdrop`
6. Dừng, dev review PR trên Forgejo

## 6. Risk / limitation

- **Chỉ Outlook Desktop + file explorer**. Outlook Web cross-tab + Mac Apple Silicon email drag → không support (đã note research).
- **Transient only** — attachment sống trong lifecycle Message send, không persist lâu dài. Nếu cần persist chứng từ Bill lâu dài → Phase 2 riêng (S3 hoặc entity mới).
- **No multi-upload progress bar** — Message editor flow sync, UI block khi `createB64ObjectData` chạy. File lớn (>10MB) UI có thể lag. Chấp nhận giới hạn này.

## 7. Dev duyệt gì

- [ ] **Approve scope**: FE only, 1 file, không BE/DB change
- [ ] **Approve wrap `buildReceiverInfo` area** với drop zone (hoặc chỉ wrap nút `buildBtnAttFile`?)
- [ ] **Approve pipeline**: branch `ai/attachment-outlook-dragdrop`, không merge, không push `develop`
- [ ] **Visual feedback**: border xanh dashed khi dragging — OK style này?
