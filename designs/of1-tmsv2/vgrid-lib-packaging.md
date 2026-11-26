# VGrid — Đóng gói lib tái sử dụng

## Kết quả research

### Hiện trạng

| Hạng mục | Hiện trạng |
|---|---|
| Monorepo | pnpm workspaces: `host / tms / ui` |
| Bundler | RSBuild (`@rsbuild/core ^2.2.7`) — chỉ có ở `host/` |
| `ui` workspace | **Source-only** — không có build config, không output dist |
| Path aliases | `util/*`, `app/*`, `wbootstrap/*` resolve qua tsconfig paths |

### Dependencies của `wbootstrap/grid`

**npm packages bên ngoài:**
| Package | Dùng để | Peer hay bundle? |
|---|---|---|
| `react-window` | Virtualization (VariableSizeGrid) | Bundle hoặc peer |
| `react-feather` | Icons | Peer (host inject) |
| `moment` | Date filter, GanttChart | Bundle hoặc peer |
| `bootstrap` | Modal/Popover JS API | Peer (host inject) |
| `simplebar-react` | (core) | Bundle hoặc peer |

**Internal imports cần giải quyết:**
| Import | File | Vấn đề |
|---|---|---|
| `util/text`, `util/HTML`, `util/common`... | Nhiều file trong grid | Cần bundle cùng hoặc move vào wbootstrap |
| `app/backend` (RestResponse) | `FavoriteService.ts` | **Coupling duy nhất với app layer** |
| `i18n` | Một số label string | Cần abstraction |

**Không có** coupling với `AppRegistry`, `ShellContext`, hay shell-specific code — grid core sạch.

---

## Go / No-Go

**Go** — coupling chỉ có 1 điểm (`FavoriteService → app/backend`). Phần còn lại là UI components thuần, có thể tách ra dễ dàng.

---

## Approach: Monorepo package (không tạo repo mới)

Giữ trong monorepo `of1-tmsv2`, thêm build config cho `ui` workspace.

**Lý do không tạo repo riêng:**
- Tránh version sync overhead
- CSS vars / theming không thay đổi gì
- Client dùng được qua `npm link` hoặc private registry

### Các bước thực hiện

#### 1. Abstract FavoriteService backend
Thêm interface `IGridBackend` để host inject, thay vì hardcode `app/backend`:

```ts
// wbootstrap/grid/IGridBackend.ts
export interface IGridBackend {
  call<T>(service: string, method: string, params: any): Promise<T>;
}
```

`VGridConfig` nhận optional `backend?: IGridBackend`. FavoriteService dùng `backend` từ context thay vì import trực tiếp.

#### 2. Bundle `util/*` vào wbootstrap
Move hoặc re-export `util/text`, `util/HTML`, `util/common`, `util/Arrays` vào `wbootstrap/util/` → không còn path alias dependency.

#### 3. Thêm build config cho `ui` workspace
Dùng **tsup** (đơn giản hơn rollup cho lib):

```json
// webui/ui/package.json
{
  "main": "dist/index.js",
  "module": "dist/index.mjs",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsup src/wbootstrap/grid/index.tsx --format cjs,esm --dts --external react --external react-dom --external react-feather --external bootstrap"
  }
}
```

#### 4. Peer deps vs bundle
| Package | Strategy |
|---|---|
| `react`, `react-dom` | peerDep — host inject |
| `react-feather` | peerDep — host inject |
| `bootstrap` (JS) | peerDep — host inject |
| `react-window` | Bundle (ít ai có sẵn) |
| `moment` | Bundle (hoặc peer nếu host dùng) |

#### 5. CSS / Theming
CSS vars (`--grid-*`, `--slate-*`, `--blue-*`) giữ nguyên — host chỉ cần import `dist/index.css`. Dark mode qua `.dark` class trên `<html>` vẫn hoạt động.

---

## Estimation

| Task | Effort |
|---|---|
| Abstract FavoriteService | 2h |
| Move util/* vào wbootstrap | 3h |
| Thêm tsup build config + test | 2h |
| Docs + ví dụ integration | 1h |
| **Tổng** | **~1 ngày** |

---

## Chưa làm (scope sau)

- Private npm registry setup (Verdaccio / Forgejo Packages)
- Versioning strategy (semver / calver)
- i18n abstraction (hiện tại label hardcode tiếng Việt/Anh — cần `I18nProvider`)
