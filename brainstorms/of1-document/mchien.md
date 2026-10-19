# of1-document · mchien — TODO cá nhân

> Brainstorm file của **mchien** (`196phamminhchien`). Mỗi TODO phải ghi rõ **scope ảnh hưởng** để AI load đúng grounding.
> Convention + HARD SAFETY RULE (write/read-only scope) + rules xem `./CLAUDE.md`.

## Format TODO

```
- [ ] [<scope>] <nội dung ngắn gọn, 1 ý>
```

- `<scope>` ∈ `{xlsx, docx, pdf, img, s3, accounting, inv, fee, tms, receipt, overview}`
- Multi scope → `[xlsx,s3]`
- UI touch → thêm tag `[+ui]`

## TODO (dev)

- [x] [+ui,xlsx,s3] Replace Office Online Viewer (`view.officeapps.live.com`) bằng self-host xlsx viewer. Research stack final: ExcelJS parse style + SheetJS SSF format number + custom React renderer. Fidelity ~90% Excel (font/fill/border/alignment/numFmt/column widths/row heights/merged cells). Features: multi-sheet tabs, zoom 25%-400% + Ctrl+wheel, drag range selection + auto-scroll ra ngoài edges, Ctrl+C copy range (text/html + text/plain TSV paste Excel giữ format), Download file xlsx gốc. Prototype Univer presets rollback do kéo `@grpc/grpc-js` + `moment` server-side vào bundle. S3DocumentView swap SPREADSHEET_EXT branch dùng `UIXlsxViewer`. Status: merged qua PR, branch `ai/xlsx-viewer` + `ai/xlsx-download` đã cleanup local
- [ ] [+ui,xlsx,docx,s3] `S3DocumentView` thêm **toggle 2 option chọn viewer** cho các file office. Current logic: `SPREADSHEET_EXT ⊂ supportedOfficeExt` → cells xlsx/xls/csv/ods thuộc **cả 2 set** nhưng branch `if-else` chỉ dùng `UIXlsxViewer`. **Yêu cầu**: thêm select/toggle UI để user chọn runtime:
    - **Option A — Office Online** (`view.officeapps.live.com`, DEFAULT priority, fidelity ~99% khi work; stuck "fetching your file" khi fail)
    - **Option B — Self-host** (`UIXlsxViewer` cho spreadsheet, fallback native `<object>`/`<iframe>` cho docx/pptx; fidelity ~90% xlsx + 0% docx/pptx)
    
    **File-type matrix**:
    | Ext | Chỉ trong set nào | Toggle hiển thị? | Default |
    |---|---|---|---|
    | xlsx / xls / csv / ods | SPREADSHEET + supportedOffice | ✅ 2 options | Office Online |
    | docx / doc / rtf / odt | supportedOffice | ❌ chỉ Office Online (chưa có self-host) | Office Online |
    | pptx / ppt / odp | supportedOffice | ❌ chỉ Office Online | Office Online |
    
    **UX**: dropdown/radio ở header `DocumentView` khi mở file office; remember chọn qua `storage.diskPut('document-viewer-pref', 'office-online' | 'self-host')` để persist giữa sessions. Fallback khi Office Online stuck: nút "Switch to self-host" visible sau N giây loading.

## Summary (AI)
<!-- AI điền ngay dưới TODO sau khi chạy pipeline. Dev không sửa tay. -->

| TODO | scope | design | openspecs | code | review | status |
|---|---|---|---|---|---|---|
| Xlsx readonly viewer thay Office Online | `+ui,xlsx,s3` | — (incremental, inline doc trong `webui/document/src/app/document/xlsx/README.md`) | — | branch `ai/xlsx-viewer` merged qua develop · HEAD `cf4b53e5` khi merge · 20+ commits iterate (SheetJS→ExcelJS swap, SSF numFmt, zoom + wheel, range selection + autoscroll, copy clipboard, download, Univer prototype rollback) · `webui/document/package.json` thêm `exceljs 4.4.0` + giữ `xlsx 0.18.5` · `S3DocumentView.tsx` swap SPREADSHEET_EXT branch | manual verified | ✅ **merged → develop** · local branches cleaned |
