# Design: Radix Colors + Dark Mode

## Goal
Thay thế hardcoded hex fallbacks trong `phoenix-tokens.scss` bằng Radix Colors scale,
thêm dark mode toggle dùng `.dark` class trên `<html>`.

## Approach

**Giữ nguyên abstraction layer `--phoenix-*`** — không đổi tên vars ở bất cứ đâu.
Chỉ thay "giá trị bên dưới" của `--phoenix-*` vars bằng Radix scales.

### Lý do

```
Radix CSS vars  →  --phoenix-* remapping  →  pxvar()  →  components
(light/dark auto)     (radix-tokens.scss)
```

- Code component, grid stylesheet không đổi dòng nào
- Radix tự swap `--slate-1` (near-white) ↔ (near-black) khi `.dark` active

## Color Mapping

| Phoenix var | Light (slate) | Dark (slate auto) | Semantic |
|---|---|---|---|
| `--phoenix-body-bg` | `--slate-2` | auto | page background |
| `--phoenix-secondary-bg` | `--slate-3` | auto | subtle bg, odd rows |
| `--phoenix-secondary-bg-subtle` | `--slate-3` | auto | hover, subtle |
| `--phoenix-emphasis-bg` | `white` / `--slate-1` | `--slate-2` | card surface |
| `--phoenix-border-color-translucent` | `--slate-5` | auto | hairline |
| `--phoenix-border-color` | `--slate-6` | auto | default border |
| `--phoenix-gray-200` | `--slate-6` | auto | |
| `--phoenix-gray-300` | `--slate-7` | auto | |
| `--phoenix-gray-400` | `--slate-8` | auto | |
| `--phoenix-gray-500` | `--slate-9` | auto | muted text |
| `--phoenix-gray-600` | `--slate-10` | auto | |
| `--phoenix-gray-700` | `--slate-11` | auto | secondary text |
| `--phoenix-body-color` | `--slate-12` | auto | primary text |
| `--phoenix-primary` | `--blue-9` | `--blue-10` | brand |
| `--phoenix-primary-bg-subtle` | `--blue-3` | auto | |
| `--phoenix-success` | `--green-9` | auto | |
| `--phoenix-danger` | `--red-9` | auto | |
| `--phoenix-warning` | `--orange-9` | auto | |
| `--phoenix-info` | `--cyan-9` | auto | |

## Files

| Action | File | Nội dung |
|---|---|---|
| INSTALL | `webui/ui/package.json` + `webui/host/package.json` | `@radix-ui/colors` |
| CREATE | `webui/ui/src/scss/radix-tokens.scss` | Import Radix CSS + map → `--phoenix-*` |
| EDIT | `webui/ui/src/scss/configuration.scss` | import radix-tokens |
| CREATE | `webui/host/src/theme/ThemeContext.tsx` | React context: `theme`, `toggleTheme` |
| EDIT | `webui/host/src/layout/TopBar.tsx` | Thêm dark mode toggle button |
| EDIT | `webui/host/src/layout/AppShell.tsx` | Dùng CSS class thay inline hardcoded bg |
| CREATE/EDIT | `webui/host/src/stylesheet.scss` | Dark mode overrides cho shell layout |

## Dark Mode Toggle logic

```tsx
// ThemeContext: lưu 'light'|'dark' vào localStorage
// apply bằng: document.documentElement.classList.toggle('dark', isDark)
```

Radix dark vars defined on `.dark, .dark-theme` class → đặt `.dark` trên `<html>` là xong.

## Assumption

- Chỉ implement dark mode cho shell layout (TopBar, Sidebar, AppShell) + VGrid.
  Các Phoenix Bootstrap components khác (Button, Modal...) chưa dark-mode-aware — cần `data-bs-theme="dark"` riêng, để TODO sau.
