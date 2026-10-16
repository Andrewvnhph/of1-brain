<!--
  MIRROR — nguồn gốc ban đầu: /Users/admin/OF1/forgejo/of1-platform/of1-tms-engineering-hub/rules/frontend.md
  Last synced: 2026-10-13.
  DIVERGENCE: bản này đã divergent khỏi engineering-hub do audit code thật phát hiện drift
  (library name casing, filename, enhanced MF plugin v2.9, ComplexBeanObserver pattern làm rõ,
  prefer DefaultTabPane thay vì ban legacy, document backend thuộc of1-document, path của lib
  component chuyển sang of1-webui/). Cần push ngược về engineering-hub khi có cơ hội.
-->

# Frontend Rules

## 1. Preferences & Conventions

- **No Emojis**: Never use emojis in code, comments, or UI text (unless specifically requested by design).
- **Keep it Simple**: Readability + match surrounding style. Separate business logic từ view logic nếu possible.
- **Formatting**: 2 spaces indent; line length ≤ 100-120 chars.
- **TypeScript Rigor**: strict typing; `interface` cho component Props + DTO khớp BE contract. Prefer `interface` over `type`.
- **Component Naming**: `PascalCase.tsx` (vd `UITMSEmployeeList.tsx`, `CustomerList.tsx`).
- **Imports**: group theo thứ tự React → external libs → internal components → utils. Không dùng relative path > 2 cấp (`../../..` cấm); dùng alias nếu config có.
- **Comments**: ngắn gọn. Explain *WHY* và *FLOW*, không *WHAT*.

---

## 2. Architecture & Framework

- **React 18.3.1** + **TypeScript 5.3.3** + **Webpack 5.87**, package manager **pnpm**.
- **Module Federation**: `@module-federation/enhanced` **v2.9.0** (không phải standard `webpack.container.ModuleFederationPlugin`).
- **TMS FE ALWAYS embedded trong Platform FE** (phoenix host) via Module Federation.
- Port local: TMS dev-server **3006**, release **7086**; Platform **7080**; Platform FE dev **3000**.

### Dependency chính

- `react` / `react-dom` 18.3.1
- `react-router-dom` 6.29.0
- `@module-federation/enhanced` 2.9.0
- `keycloak-js` 26.2.0
- `maplibre-gl` 5.1.1 (map realtime)
- `three` 0.170.0 (3D container viz)
- `recharts` 2.15.1 (chart)
- `@dnd-kit/*` (drag-drop)
- `react-window` 1.8.10 (virtualization)
- `react-datetime` 3.2.0
- `react-feather` (icons)
- `@of1-webui/lib`, `@of1-webui/platform` (shared libs)

---

## 3. Component & UI Conventions

### 3.1. Lifecycle — Class Components only, no Hooks

- Codebase 100% Class Components: **208** `extends app.AppComponent` + **54** `extends React.Component`. **Zero `useState`/`useEffect`/functional components** (confirmed audit).
- Override `onInit`, `onPreCommit`, `onPostCommit` để quản flow.
- **Không dùng React Hooks** trừ khi thật cần thiết (và cần justify trong PR).

### 3.2. Data binding & inputs

**🚫 TUYỆT ĐỐI KHÔNG viết raw HTML input**: `<input/>`, `<select/>`, `<textarea/>`, `<checkbox/>`, … **KHÔNG được dùng** trong code TMS. Luôn dùng component wrapper từ `bs.*`:

| Kiểu field | Component |
|-----------|-----------|
| String / text | `bs.BBString` |
| Boolean / checkbox | `bs.BBBoolean` (hoặc `bs.Boolean`) |
| Number | `bs.BBNumber` |
| Date / Datetime | `bs.BBDate`, `bs.BBDateTime` |
| Select (enum) | `bs.BBSelect` |
| Textarea | `bs.BBTextArea` |

Props chuẩn mọi `bs.BB*`:
```typescript
<bs.BBString bean={bean} field="fieldName" label={T('Label')} />
<bs.BBBoolean bean={bean} field="isActive" label={T('Active')} />
```

→ 2-way binding tự động vào `bean[fieldName]`, cùng pattern validation + grid context.

**BBRef family** (reference input / foreign-key picker):

- `BBRefTMSEmployee`, `BBRefAccount`, `BBRefTMSEmployeeGroup`, `BBRefTMSCustomer`, `BBRefTMSVendor`, … — tất cả **thuộc dự án `of1-tms`**, import từ **`webui/tms/src/...`**.
- ⚠️ **KHÔNG** import `BBRef*` từ `of1-platform` repo — vi phạm scope ownership.
- Cần `BBRef*` mới (vd field reference tới entity chưa có picker) → **DỪNG, hỏi dev trước**. Không tự tạo tuỳ tiện; mỗi `BBRef*` ảnh hưởng pattern + search backend của entity đó.

**Silent update bean**: khi `bean[field] = 'xxx'` set không qua input → gọi `this.forceUpdate()` để re-render.

**Reactive field change**: handler `onInputChange = (fieldCtx: grid.FieldContext) => {...}` cho field-level change (vd disable field khác khi field này thay đổi).

### 3.3. Layout

- Grid: `bs.Row` + `bs.Col span={divisible_by_12}`.
- Split pane: `bs.VSplit` + `bs.VSplitPane` (có `width`, `className`, `updateOnResize`).
- Icons: `<FeatherIcon.XxxIcon size={12} className="me-1" />` (import `* as FeatherIcon from 'react-feather'`).

### 3.3.11. `createPopupPage` vs `addPageContent` — modal vs breadcrumb

Có 2 API push page content, chọn theo UX intent:

| | `pageContext.createPopupPage(name, label, create, options)` | `pageContext.addPageContent(name, label, create)` |
|---|---|---|
| UI | **Modal dialog** overlay | **Breadcrumb page** trong stack |
| Close/back | Click `×` hoặc backdrop | Click breadcrumb item trước |
| Size | `{ size: 'xs/sm/md/lg/xl/flex-lg' }` + `backdrop` option | Full page của current context |
| Isolation | AppContext + PageContext riêng | Share context với parent |
| Hierarchy | Standalone, không nest | Push vào `pageContext.breadcumbs` stack |

**Dùng `createPopupPage` khi**:
- Confirm/alert dialog (OK/Cancel)
- Quick picker (chọn vendor, chọn file)
- Isolated form editor (edit entity trong popup)
- UI tạm không cần quay lại filter trước

**Dùng `addPageContent` khi**:
- Step-by-step flow (upload → preview → confirm)
- Nested detail list (bill → bill item detail)
- Result preview mà user có thể quay lại thay đổi filter
- Deeper drill-down với breadcrumb trail hiển thị path

API reference: `of1-webui/src/app/app.tsx` — `addPageContent` push vào `Breadcrumbs.pushContent()`, `createPopupPage` tạo `PopupPageContext` + `dialogShow()`.

### 3.4. Popup / Dialog

- **Prefer `pageContext.createPopupPage(name, label, createAppPage, options)`** cho modal có sub-page (list, editor, form). Signature:
  ```typescript
  createAppPage = (appCtx, pageCtx) => <YourComponent appContext={appCtx} pageContext={pageCtx} ... />
  ```
  Options: `{ size: 'xs'|'sm'|'md'|'lg'|'flex-lg'|'xl', backdrop?: 'static'|boolean, zIndex?, dialogId? }`.
- Fallback `bs.dialogShow(title, jsx, options)` **chỉ** cho dialog tiny stateless (confirm, plain message, translation popup).
- Form hint: `bs.CssTooltip`.
- Status thực tế: `createPopupPage` dominant (326 uses) vs `dialogShow` (48 uses) ✓ compliant.

### 3.3.9. DbEntityList subclass — Props PHẢI extend `entity.DbEntityListProps`

Khi tạo subclass của `entity.DbEntityList<Props>`, Props interface **phải** extend `entity.DbEntityListProps`, không phải chỉ `app.AppComponentProps`. Lý do: base class generic yêu cầu:

```typescript
abstract class DbEntityList<
  T extends DbEntityListProps = DbEntityListProps,
  ...
> extends app.AppComponent<T, S> {}
```

**❌ Sai**:
```typescript
interface MyListProps extends app.AppComponentProps {
  rawRows: any[];
}
class MyList extends entity.DbEntityList<MyListProps> {}  // TS error (hoặc runtime nếu bypass)
```

**✅ Đúng**:
```typescript
interface MyListProps extends entity.DbEntityListProps {
  rawRows: any[];
}
```

`DbEntityListProps` include:
- `plugin: DbEntityListPlugin` (required — grid data source)
- `type?`, `storageState?`, `onSelect?`, `onMultiSelect?`, `onModifyBean?`, `onLoadData?` (optional)
- Kế thừa từ `app.AppComponentProps`: `appContext`, `pageContext`

**Hệ quả**: parent luôn phải pass `plugin` prop. Pattern: `plugin={new entity.DbEntityListPlugin(records)}`.

### 3.3.10. DbEntityList — instance var init trong constructor ordering

`DbEntityList` base ctor gọi `createVGridContext()` → `createVGridConfig()` **TRONG `super()`**. Class field initializers TypeScript biên dịch thành assignment SAU `super()`:

```typescript
// Source:
class MyList extends entity.DbEntityList {
  myBean: Record<string, any> = {};  // class field initializer
}

// Compiled:
class MyList extends entity.DbEntityList {
  constructor(props) {
    super(props);         // ← base ctor runs createVGridConfig, this.myBean undefined
    this.myBean = {};     // ← too late
  }
}
```

**Crash symptom**: `Cannot read properties of undefined (reading 'xxx')` khi code trong `createVGridConfig()` truy cập `this.myBean[k]`. Error key là value của `k` (vd `_rowNumber` nếu đó là field name đầu tiên).

**Fix**: idempotent lazy init TẠI ĐẦU `createVGridConfig()`:

```typescript
createVGridConfig(): grid.VGridConfig {
  // Lazy init — base ctor có thể gọi method này TRƯỚC khi class field initializers chạy.
  this.myBean = this.myBean || {};
  this.myMap = this.myMap || {};
  // ... rest ...
}
```

Vẫn giữ class field initializers để TS type-safe + default khi component remount (key change → new instance → field init chạy normal).

**Alternative** (nếu không muốn lazy pattern): dùng getter với `_private` backing + undefined check. Verbose hơn, không recommend trừ khi phức tạp.

### 3.4.0. VGrid config — explicit type annotation, KHÔNG `as any`

AI thường bị cám dỗ dùng `as any` để bypass TypeScript khi config phức tạp. ĐỪNG. `as any` nuốt mọi lỗi, bao gồm sai tên property (vd `headerRowHeight` thay vì `headerCellHeight`) → bug chạy UI mới phát hiện.

**❌ Sai**:
```typescript
createVGridConfig(): grid.VGridConfig {
  return {
    record: {
      fields: [...],
      headerRowHeight: 70,  // ← sai property name, nhưng cast nuốt
    } as any,  // ← bypass check
    toolbar: { hide: true },
    view: { ... },
  };
}
```

**✅ Đúng** — explicit typed variable để compile-time catch sai field name:
```typescript
createVGridConfig(): grid.VGridConfig {
  let config: grid.VGridConfig = {
    record: {
      fields: [...],
      headerCellHeight: 100,  // sai tên → TS error ngay
    },
    toolbar: { hide: true },
    view: { ... },
  };
  return config;
}
```

**Nguyên tắc chung**: khi gặp TS error với `grid.*` / `entity.*` types, **đừng cast `as any`** — mở source `of1-webui/src/wbootstrap/grid/IVGrid.tsx` xem đúng tên property. VD các tên dễ nhầm:
- `headerCellHeight` (không phải `headerRowHeight`)
- `rowHeight` (ok, cho data row)
- `cellClassName` (không phải `cssClass` khi dùng ở FieldConfig; `cssClass` nằm chỗ khác)

### 3.4.1. VGrid config — bắt buộc khai `view` + `toolbar`

Mọi `grid.VGridConfig` (trả từ `DbEntityList.createVGridConfig()`) PHẢI khai **cả 2** block `view` + `toolbar`, nếu không VGrid crash khi render.

**Minimum config**:

```typescript
return {
  id: 'xxx-list',
  record: { fields: [...] },
  toolbar: { hide: true },          // hoặc toolbar config đầy đủ với actions/filters
  view: {
    currentViewName: 'table',
    availables: { table: { viewMode: 'table' } },
  },
};
```

**Crashes đã gặp khi thiếu**:
- Thiếu `view` → `Cannot read properties of undefined (reading 'currentViewName')` ở `VGridToolbar.tsx:118`
- Thiếu `toolbar` → `Cannot read properties of undefined (reading 'hide')` ở `VGridToolbar.tsx:27`

**Khi nào `toolbar: { hide: true }`**: khi parent component đã có toolbar riêng (upload / search / action buttons) → tránh double toolbar. Vd dialog import Excel: dialog đã có upload + Fill buttons.

**Khi nào toolbar config đầy đủ**: khi là list page chính (vd `UITMSBillList`, `ZoneList`) → cần Search + Delete + Filter actions. Pattern:

```typescript
toolbar: {
  actions: [...entity.DbEntityListConfigTool.TOOLBAR_ACTION_DELETE(!deleteCap, T('Delete'))],
  filters: entity.DbEntityListConfigTool.TOOLBAR_FILTERS(true, 'filter'),
  filterActions: [...entity.DbEntityListConfigTool.TOOLBAR_AUTO_REFRESH('auto-refresh-xxx', T('Refresh'))],
}
```

Pattern reference: `UIWebhookInputLogList.tsx:93-105`, `ZoneList.tsx`.

### 3.4.2. VGrid refresh khi data đổi — 2 pattern

`DbEntityList` cache plugin + VGrid context internal. `setState` ở parent re-render parent **nhưng VGrid con không tự refresh** vì nó dùng cached listModel.

#### Pattern A — `key` remount (dùng cho test tool / UI tạm)

Pass `key` prop khác nhau mỗi lần data đổi → React unmount + remount child → fresh grid.

```typescript
state = { ..., gridRevision: 0 };

onDataChange = () => {
  this.setState({ ..., gridRevision: this.state.gridRevision + 1 });
};

render() {
  return <MyList key={`grid-rev-${this.state.gridRevision}`} plugin={plugin} ... />;
}
```

- ✅ Đơn giản, không cần ref hay API grid internal
- ❌ Mất scroll position + selection state + VGrid internal state (sort, filter, column resize)
- ❌ Tốn render cycle

**Dùng khi**: test tool / dialog preview tạm, không quan trọng scroll state.

#### Pattern B — `replaceWith()` + `forceUpdateView()` (production)

Giữ plugin instance, mutate records in-place, báo grid refresh.

```typescript
plugin = new entity.DbEntityListPlugin([]);
listRef = React.createRef<MyList>();

refreshGrid = () => {
  this.plugin.getListModel().replaceWith(newRecords);
  const vctx = (this.listRef.current as any)?.vgridContext;
  vctx?.getVGrid()?.forceUpdateView();
}

onDataChange = () => {
  this.setState({ ... }, this.refreshGrid);
}

render() {
  return <MyList ref={this.listRef} plugin={this.plugin} ... />;
}
```

- ✅ Giữ scroll + selection + VGrid state
- ❌ Verbose hơn, cần ref access `vgridContext` (API internal)

**Dùng khi**: production list, dev UX quan trọng scroll/selection.

#### API ListModel

- `plugin.getListModel().replaceWith(records)` — swap in-place
- `plugin.getListModel().update(records)` — set fresh (resets internal state)
- `plugin.getListModel().addRecords(records)` — append
- `plugin.getListModel().removeRecord(record)` — remove
- `vgridContext.getVGrid().forceUpdateView()` — refresh render

**Lưu ý Pattern B**: `vgridContext` chỉ available sau khi DbEntityList mount xong. Luôn gọi trong `setState` callback để chắc commit done.

#### BB*Field onInputChange — nếu cần refresh footer counts

Khi header có `BB*Field` mà footer counts tùy thuộc bean đó, pattern tối ưu dùng ctx có sẵn (truyền từ `customHeaderRender(_ctx, ...)`):

```typescript
customHeaderRender: (_ctx: grid.VGridContext, _field, _ele) => (
  <input.BBCheckboxField
    bean={this.requiredBean}
    field={k}
    value={false}
    onInputChange={() => _ctx.getVGrid().forceUpdateView()}
  />
)
```

- ✅ Refresh **chỉ VGrid** (gồm footer render), không whole DbEntityList
- ✅ Lighter hơn `this.forceUpdate()` ở parent
- `_ctx` có sẵn trong customHeaderRender signature, không cần ref

### 3.5. Tabs — ưu tiên `bs.DefaultTabPane`

- **Ưu tiên** `bs.DefaultTabPane` + `bs.TabPaneConfig` + `bs.PanelConfig`. Mỗi tab build lazy qua `renderContent`.
- Legacy `<bs.TabPane>` + `<bs.Tab>` children: còn tồn tại trong code (~106 uses) nhưng **không viết code mới theo kiểu đó**.
- Khi touch file có legacy tab → chuyển dần sang `DefaultTabPane`.

```typescript
import { bs } from '@of1-webui/lib';

let tabs: bs.PanelConfig[] = [
  { name: 'tab1', label: T('Tab 1'), active: true,
    renderContent: (_ctx: bs.UIContext) => <Content1 /> },
  { name: 'tab2', label: T('Tab 2'),
    renderContent: (_ctx: bs.UIContext) => <Content2 /> },
];

let config: bs.TabPaneConfig = {
  tabs: tabs,
  // optional: renderCustomActions: () => <MyAction />,
};

return <bs.DefaultTabPane className="flex-vbox" config={config} />;
```

Reference: `src/app/logistics/tms/settings/jobtracking/UITMSJobTrackingTab.tsx`.

Khi 1 settings menu có nhiều list liên quan → gộp thành 1 `*Tab` component (1 nav item) thay vì 1 nav item per list.

### 3.6. ComplexBeanObserver — khi bean có nested arrays/beans con

Khi edit **entity phức tạp** (bean chứa các bean con, hoặc có nested 1-n array như `config.columns`, `bill.items`):

- **Root bean wrap trong `entity.ComplexBeanObserver`** (KHÔNG dùng `entity.BeanObserver`). Chỉ `ComplexBeanObserver` biết commit nested observer/plugin ngược về mutable bean khi save.
- **Child list editor plugin** build qua **`configOb.createVGridEntityListEditorPlugin('fieldName', [])`** — KHÔNG `new grid.ListEditorPlugin(bean.field)` cũng KHÔNG `new entity.DbEntityListPlugin(...)`.
  - Factory này **register plugin dưới observer**, nên khi `ButtonEntityCommit.commitAndGet()` chạy, mảng hiện tại được write back vào `mutableBean.fieldName` + serialize về BE.
- `VGridEntityListEditor` subclass **không cần** `onModifyBean` wiring — observer tự lo sync.
- **BE pair**: JPA `@OneToMany(cascade = ALL, orphanRemoval = true)` + force-init LAZY collection trong load service (`config.getColumns().size();`) để JSON response có array.
- Reference: `webui/tms/src/app/logistics/tms/fleet/tracking/UIVehicleTripGoodsTrackingConfig.tsx` (columns tab).

**Lưu ý quan trọng**: Khi bean **không** phức tạp (chỉ flat list, không nested bean) → vẫn dùng `new entity.DbEntityListPlugin(data)` bình thường. Rule factory chỉ áp dụng cho `ComplexBeanObserver` case.

---

## 4. Module Federation

### 4.1. Cách hoạt động

```
Host (phoenix @ 3000/7080)
  └── loads TmsModule @ localhost:3006/webui/init.js
```

1. Phoenix build với `DATATP_WEBUI_PLUGINS=tms,...`.
2. Webpack tạo remote: `TMSFederationPlugin@http://localhost:3006/webui/init.js`.
3. Browser load `init.js` → tạo `window.TMSFederationPlugin`.
4. Phoenix import `TMSFederationPlugin/init` → gọi `init()`.
5. `init()` register plugin → menu xuất hiện.

### 4.2. Library name — PHẢI khớp (CRITICAL)

| Module | Phoenix expects | Remote PHẢI export |
|--------|-----------------|-------------------|
| TMS | `TMSFederationPlugin` | `library: { type: 'var', name: 'TMSFederationPlugin' }` |

**Lưu ý casing**: `TMSFederationPlugin` all-caps prefix (không phải `TmsFederationPlugin` PascalCase).

### 4.3. Webpack config TMS

```typescript
import { ModuleFederationPlugin } from '@module-federation/enhanced/webpack';

const federationConfig = new ModuleFederationPlugin({
  name: 'tms-module',
  library: { type: 'var', name: 'TMSFederationPlugin' },
  filename: 'webui/init.js',          // path có subdirectory
  exposes: { './init': './src/Init.tsx' },
  shared: {
    react: { singleton: true, requiredVersion: '18.3.1' },
    'react-dom': { singleton: true, requiredVersion: '18.3.1' },
    '@of1-webui/platform': { singleton: true },
    // ... các shared singleton khác
  },
});
```

- **Shared singleton** đảm bảo host + remote dùng chung instance React / platform lib (tránh double-mount, state loss).
- Dev-server port: **3006**.

### 4.4. Profile

| Profile | TMS URL | Use case |
|---------|---------|----------|
| `--profile=dev-ui` | `localhost:3006` | Dev với dev-servers |
| (default) | `localhost:7086` | Release build |

---

## 5. SpacePlugin / Init.tsx

### 5.1. Init.tsx template (TMS hiện tại)

```typescript
import { app } from '@of1-webui/lib';
import { module } from '@of1-webui/platform';
import { BACKEND_CONFIGS, BackendConfig } from '@of1-dev01/core';

import { registerTmsShellApps } from './app/logistics/shell';
import { init as vendorInit } from './app/logistics/vendor/init';
import { UITMSBillPrintApiPlugin } from 'app/logistics/tms/api/TMSBillPrintPlugin';
import { UITMSBillReportByVendorApiPlugin } from 'app/logistics/tms/chart/TMSBillVendorReport';

import UIApiPluginManager = module.security.UIApiPluginManager;

export function init() {
  // Register TMS backend
  const baseUrl = '/platform/plugin/tms';
  const tmsBackend = new BackendConfig(`${baseUrl}`, `${baseUrl}/rest/v1.0.0`, `${baseUrl}/api`);
  BACKEND_CONFIGS.add('tms', tmsBackend);

  // API plugins
  UIApiPluginManager.register(new UITMSBillPrintApiPlugin());
  UIApiPluginManager.register(new UITMSBillReportByVendorApiPlugin());

  // Shell apps + sub-modules
  registerTmsShellApps();
  vendorInit();
}
```

**Lưu ý thay đổi vs rule cũ:**

- `BACKEND_CONFIGS` + `BackendConfig` import từ **`@of1-dev01/core`** (không phải `app.host`).
- Entry point: **`registerTmsShellApps()`** (thay cho `tmsBasicInit()` cũ).
- **Không register `document` backend** ở TMS Init — document là module riêng (`of1-document`), tự lo init của nó.

### 5.2. ScreenConfig interface

```typescript
interface ScreenConfig {
  id: string;
  label: string;
  icon: React.ComponentType;
  checkPermission: {
    feature: { module: string; name: string };
    requiredCapability: string;  // app.READ, app.WRITE, app.ADMIN
  };
  renderUI: (appCtx, pageCtx) => JSX.Element;
  screens?: ScreenConfig[];      // nested screens = horizontal menu
}
```

### 5.3. Shell app registration flow — **WHERE new UI gets wired**

Flow từ `Init.tsx` xuống menu item cuối:

```
Init.tsx
  └─ registerTmsShellApps()                              [shell/registerShellApps.tsx]
       └─ ShellAppRegistry.register({ id:'tms', ..., getNav: createTmsScreens })
            └─ createTmsScreens()                        [shell/init/index.ts]
                 └─ merge 9 top-level menu groups:
                      searchScreens, reportScreens, billScreens, fleetScreens,
                      opsScreens, ruScreens, reconcileScreens, settingsScreens,
                      guideScreens
```

**9 top-level menu groups** (mỗi group 1 file ở `shell/init/<Group>Screen.tsx`):

| Group | File | Feature permission (module/name) | Số screens |
|-------|------|----------------------------------|-----------|
| Search | `shell/init/SearchScreen.tsx` | `tms/tms-basic` | 1 |
| Report | `shell/init/ReportScreen.tsx` | `tms/tms-report` | 1 |
| **Bill** | `shell/init/BillScreen.tsx` | `tms/tms-bill` | 1 parent + 2 children |
| **Fleet** | `shell/init/FleetScreen.tsx` | `tms/tms-fleet-basic` | 1 parent + 7 children |
| OPS | `shell/init/OpsScreen.tsx` | `tms/tms-ops` | 1 parent + 2 children |
| RU | `shell/init/RUScreen.tsx` | `tms/tms-round-used` | 1 parent + 2 children |
| Reconcile | `shell/init/ReconcileScreen.tsx` | `tms/tms-bill-reconcile` | 1 parent + 3 children |
| **Settings** | `shell/init/SettingsScreen.tsx` | `tms/tms-settings` | 1 parent + 11 children |
| Guide | `shell/init/GuideScreen.tsx` | (public) | 1 |

**Settings sub-screens (11)**: customer, carrier, employee, pricing, location-settings, name_fee, fee-setting, table-col-config, job-tracking-project, ops-service-config, webhook-log.

**Fleet sub-screens (7)**: fleet-planning, vendor (5 tabs trong), vehicles (2 tabs trong), transporters, report-fcl, driver-operation-report, driver-salary-report (2 tabs trong).

### 5.4. UIApiPluginManager — Resource endpoint plugins

Khác với shell screens (menu-item có UI), **plugin** là resource endpoint cho:
- Print/PDF rendering (vd bill POD print)
- External chart renderer
- Tracking widget

**4 plugin đang register:**

| Plugin | Resource ID | Vai trò | File |
|--------|-------------|---------|------|
| `UITMSBillPrintApiPlugin` | `resource:tms-bill-print` | Render bill POD print | `app/logistics/tms/api/TMSBillPrintPlugin.tsx:205` |
| `UITMSBillReportByVendorApiPlugin` | `resource:tms-bill-report-by-vendor` | Vendor performance chart | `app/logistics/tms/chart/TMSBillVendorReport.tsx:339` |
| `UIApiPluginTMSGoodsTracking` | `resource:tms-goods-tracking` | Real-time goods tracking + GPS | `app/logistics/tms/api/TMSTrackingPlugin.tsx:223` |
| `UITMSVendorBillPlugin` | (partner space) | Vendor bill view | `app/logistics/vendor/init.tsx` |

### 5.5. shellKit `page()` wrapper + permission

File: `shell/shellKit.tsx:33-57`.

```typescript
page(label: string, feature: ScreenFeature, functionCode: string, renderFn)
  → wrap render trong <FunctionPermissionRenderUI> → check (feature.name + functionCode)
    → chỉ render nếu canRead || canWrite
  → cũng setBackendServer('tms') automatic
```

**`FunctionPermissionDTO`** (từ `app/logistics/permission/FunctionPermissionTypes.tsx:1-43`):

```typescript
type FunctionPermissionDTO = {
  functionCode: string;              // vd 'tms-bill', 'tms-fleet-planning'
  dataScope: FunctionDataScope;      // NONE | SELF_ONLY | CUSTOM | COMPANY_ONLY | GROUP_ALL
  canRead/canWrite/canDelete/canApprove/canPrint/canExport: boolean;
  accessibleAccountIds: number[];
  accessibleCompanyBranchIds: number[];
}
```

Permission được resolve runtime theo user context, không hard-code trong screen config.

### 5.6. Feature directory layout convention

Khi làm feature mới, follow pattern:

```
app/logistics/tms/<feature>/
├── UI<Feature>List.tsx          — main grid component, extends entity.DbEntityList
├── UI<Feature>ListPlugin.tsx    — DataPlugin cho list query, extends entity.DbEntityListPlugin
├── UI<Feature>.tsx              — detail/form (nếu cần)
├── <Feature>RecordConfig.tsx    — VGrid field definitions (tương tự TMSBillRecordConfig)
├── init.tsx                     — export root component class
├── api/<Feature>Plugin.tsx      — UIApiPlugin (optional, nếu cần resource endpoint)
└── <subfolder>/                 — chia sub-feature nếu lớn (vd fleet/gps/, fleet/vendor/)
```

### 5.7. 🔧 Checklist — Adding a new UI screen (step-by-step)

Khi dev / AI cần thêm feature mới (vd "Booking Management"):

**Phase 1 — Feature module** (`app/logistics/tms/<feature>/`)
1. Tạo thư mục `app/logistics/tms/booking/` (hoặc nest dưới module tương ứng vd `bill/`, `fleet/`).
2. `UIBookingList.tsx` extends `entity.DbEntityList` hoặc `app.AppComponent`.
3. `UIBookingListPlugin.tsx` extends `entity.DbEntityListPlugin` + `backend: 'tms'`.
4. `BookingRecordConfig.tsx` với VGrid field definitions (dùng `bs.BBString`, `bs.BBBoolean`, `BBRef*`).
5. `init.tsx` export root class.

**Phase 2 — Shell screen** (`shell/init/<Feature>Screen.tsx`)
1. Tạo `shell/init/BookingScreen.tsx`.
2. Khai `ScreenFeature`: `const TMS_BOOKING = { module: 'tms', name: 'tms-booking' };`
3. Khai `functionCode`: `const CODE_BOOKING = 'tms-booking';`
4. Render function wrap bằng helper `page(label, feature, functionCode, renderFn)`:
   ```typescript
   render: page('Booking', TMS_BOOKING, CODE_BOOKING,
     (a, p) => <UIBookingList appContext={a} pageContext={p} plugin={new UIBookingListPlugin()} />
   )
   ```
5. Export function `bookingScreens(): TmsNavItem[]` return array `[{ id, label, icon, feature, functionCode, render, children? }]`.

**Phase 3 — Register vào shell index**
1. Mở `shell/init/index.ts`.
2. Add import: `import { bookingScreens } from './BookingScreen';`
3. Add vào `createTmsScreens()` return array: `...bookingScreens(),`

**Phase 4 — Backend wiring** (không thuộc FE scope nhưng cần biết)
1. Backend tạo `TMSBookingService.searchBookings(...)` theo rule backend (xem `backend.md`).
2. Thêm `functionCode` 'tms-booking' + capability vào Platform permission DB (xem security section §7).

**Phase 5 — API plugin** (CHỈ khi cần resource endpoint — print, chart, tracking widget)
1. Tạo `app/logistics/tms/booking/api/BookingPrintPlugin.tsx` extends `UIApiPlugin`.
2. Define `resourceId = 'resource:tms-booking-print'`.
3. Implement `render(props)` return component.
4. Register trong `Init.tsx`: `UIApiPluginManager.register(new UIBookingPrintApiPlugin());`

**→ Thường chỉ cần Phase 1-3** cho screen bình thường. Phase 5 chỉ dành cho print/report/widget.

---

## 6. Backend Configuration

### 6.1. Registry

```
BACKEND_CONFIGS:
  'platform'  → BackendConfig(localhost:7080)   ← DEFAULT
  'tms'       → BackendConfig(localhost:7086)
  // 'document' thuộc of1-document module, không register ở TMS
```

### 6.2. Gọi API

**Pattern chuẩn** (dùng config namespace):

```typescript
appContext.getBackendConfigs().getBackendConfig('tms')
  .createHttpBackendCall('TMSBillService', 'search', params)
  .withSuccessData((data) => { ... })
  .call();
```

**Variant** dùng khi context đã biết default backend:

```typescript
appContext.createHttpBackendCall('TMSBillService', 'search', params)
  .withSuccessData((data) => { ... })
  .call();
```

Nhưng khi gọi vào TMS từ context mặc định `platform` → **phải** qua `.getBackendConfig('tms')`.

### 6.3. `DbEntityListPlugin` — set `backend: 'tms'`

```typescript
export class MyListPlugin extends entity.DbEntityListPlugin {
  constructor() {
    super([]);
    this.backend = {
      backend: 'tms',  // REQUIRED — thiếu sẽ default về 'platform' (bug ngầm)
      service: 'TMSBillService',
      searchMethod: 'searchTMSBills',
    };
  }
}
```

---

## 7. Security & Authorization

Platform owns security. Permission check ở Platform host (phoenix), **không** ở TMS backend.

### 7.1. Key tables (Platform DB)

- `security_app_feature` — feature definition (module, name, label, capability)
- `security_user_app_feature` — user assignment (company_id, app_id, account_id, capability)

### 7.2. Capability levels

| Capability | Description |
|------------|-------------|
| `app.READ` | View only |
| `app.WRITE` | View + modify |
| `app.ADMIN` | Full access |

### 7.3. Best practice

**Option 1 (Recommended)**: dùng feature có sẵn:

```typescript
checkPermission: {
  feature: { module: 'tms', name: 'tms-bill' },
  requiredCapability: app.READ,
},
```

**Option 2**: tạo feature custom (chỉ khi thực sự cần):

```sql
INSERT INTO security_app_feature (module, name, label, required_capability, company_app, storage_state)
VALUES ('tms', 'tms-custom-feature', 'TMS Custom Feature', 'Read', true, 'ACTIVE');
```

---

## 8. UI Components — API tổng hợp

### 8.1. App Component base

```typescript
import { app } from '@of1-webui/lib';

interface MyComponentProps extends app.AppComponentProps {}

export class MyComponent extends app.AppComponent<MyComponentProps> {
  render() {
    const { appContext, pageContext } = this.props;
    return <div>...</div>;
  }
}
```

### 8.2. i18n

Dùng function `T('key')` (import từ shared utils) để translate text. Vd `label: T('Tab 1')`, `title: T('Create Employee')`.

### 8.3. React Portal — inject vào DOM ngoài module

```typescript
import ReactDOM from 'react-dom';

class UINavbarInjector extends React.Component {
  private containerElement: HTMLDivElement | null = null;

  componentDidMount() {
    const navbar = document.querySelector('nav.navbar-slim');
    this.containerElement = document.createElement('div');
    navbar.appendChild(this.containerElement);
    this.forceUpdate();
  }

  componentWillUnmount() {
    if (this.containerElement?.parentNode)
      this.containerElement.parentNode.removeChild(this.containerElement);
  }

  render() {
    if (!this.containerElement) return null;
    return ReactDOM.createPortal(<MyComponent />, this.containerElement);
  }
}
```

---

## 9. Do / Don't

| Do | Don't |
|----|-------|
| Dùng `bs.BBString`, `bs.BBBoolean`, `bs.BBNumber`, … cho mọi input | Viết raw `<input/>`, `<select/>`, `<textarea/>` HTML |
| Import `BBRef*` từ `of1-tms` (`webui/tms/src/...`) | Import `BBRef*` từ `of1-platform` |
| Cần `BBRef*` mới → **hỏi dev** trước | Tự tạo `BBRef*` mới không ai biết |
| Set `backend: 'tms'` trong `DbEntityListPlugin` | Omit backend (default về `platform` — bug) |
| Dùng `createPopupPage` cho modal có sub-page | Dùng `dialogShow` cho popup có stateful content |
| **Ưu tiên** `bs.DefaultTabPane` + `TabPaneConfig` cho tab | Viết code mới với legacy `<bs.TabPane>` + `<bs.Tab>` |
| Wrap root bean trong `ComplexBeanObserver` khi có nested arrays/beans | Dùng `BeanObserver` cho complex bean (nested không commit đúng) |
| Dùng `createVGridEntityListEditorPlugin` cho child list dưới `ComplexBeanObserver` | Dùng `new entity.DbEntityListPlugin()` cho child dưới `ComplexBeanObserver` |
| Dùng `checkPermission` với feature có sẵn | Tạo custom feature không check Platform DB trước |
| Build Phoenix với `DATATP_WEBUI_PLUGINS=tms` | Build Platform mà không có tms plugin |
| Class Component extends `app.AppComponent` | Dùng Hooks (`useState`/`useEffect`) trừ khi justify kỹ |

---

## 10. Key Files

### App registration & bootstrap

| Component | Path |
|-----------|------|
| TMS Init (bootstrap entry) | `/of1-tms/webui/tms/src/Init.tsx` |
| TMS Webpack | `/of1-tms/webui/tms/webpack.config.ts` |
| **Shell app register** | `/of1-tms/webui/tms/src/shell/registerShellApps.tsx` |
| **Nav screens index (merge 9 groups)** | `/of1-tms/webui/tms/src/shell/init/index.ts` |
| **`page()` wrapper + permission** | `/of1-tms/webui/tms/src/shell/shellKit.tsx` |
| TMS Main App | `/of1-tms/webui/tms/src/app/logistics/tms/init.tsx` |

### Shell screen modules (9 top-level menu groups)

| Group | Path |
|-------|------|
| Search | `/of1-tms/webui/tms/src/shell/init/SearchScreen.tsx` |
| Report | `/of1-tms/webui/tms/src/shell/init/ReportScreen.tsx` |
| Bill | `/of1-tms/webui/tms/src/shell/init/BillScreen.tsx` |
| Fleet | `/of1-tms/webui/tms/src/shell/init/FleetScreen.tsx` |
| OPS | `/of1-tms/webui/tms/src/shell/init/OpsScreen.tsx` |
| RU | `/of1-tms/webui/tms/src/shell/init/RUScreen.tsx` |
| Reconcile | `/of1-tms/webui/tms/src/shell/init/ReconcileScreen.tsx` |
| Settings | `/of1-tms/webui/tms/src/shell/init/SettingsScreen.tsx` |
| Guide | `/of1-tms/webui/tms/src/shell/init/GuideScreen.tsx` |

### Config & plugins

| Component | Path |
|-----------|------|
| TMS Bill Record Config | `/of1-tms/webui/tms/src/app/logistics/tms/bill/TMSBillRecordConfig.tsx` |
| Bill Print Plugin | `/of1-tms/webui/tms/src/app/logistics/tms/api/TMSBillPrintPlugin.tsx` |
| Bill Vendor Report Plugin | `/of1-tms/webui/tms/src/app/logistics/tms/chart/TMSBillVendorReport.tsx` |
| Goods Tracking Plugin | `/of1-tms/webui/tms/src/app/logistics/tms/api/TMSTrackingPlugin.tsx` |
| Partner Vendor init | `/of1-tms/webui/tms/src/app/logistics/vendor/init.tsx` |
| Function Permission Types | `/of1-tms/webui/tms/src/app/logistics/permission/FunctionPermissionTypes.tsx` |

### Shared lib

| Component | Path |
|-----------|------|
| SpacePlugin (lib) | `/of1-webui/src/app/space/plugin.tsx` |
| Shared lib root | `/of1-webui/` — package `@of1-webui/lib`, `@of1-webui/platform` |

**Note**: Phoenix host (`of1-build/webui/phoenix/`) không trong workspace hiện tại — thuộc repo khác hoặc build system. Khi cần reference phoenix behavior, hỏi dev biết repo đó.

---

## 11. Quick Reference — Checklist khi thêm feature FE mới

- [ ] Component `PascalCase.tsx` extends `app.AppComponent` (Class Component).
- [ ] Props typed `interface` (strict TS).
- [ ] Imports grouped: React → external → internal → utils; không `../../..`.
- [ ] **KHÔNG viết raw `<input/>`, `<select/>`, `<textarea/>`** — dùng `bs.BBString`, `bs.BBBoolean`, `bs.BBNumber`, …
- [ ] Field reference entity khác → dùng `BBRef*` từ `of1-tms` (không import từ `of1-platform`). Cần `BBRef*` mới → **hỏi dev trước**.
- [ ] FE call BE: `appContext.getBackendConfigs().getBackendConfig('tms').createHttpBackendCall(...)`.
- [ ] `DbEntityListPlugin` có `backend: 'tms'`.
- [ ] Entity phức tạp (nested arrays/beans con) → `ComplexBeanObserver` + `createVGridEntityListEditorPlugin`.
- [ ] Entity đơn giản (flat list) → `BeanObserver` + `DbEntityListPlugin` thường.
- [ ] Modal có sub-page → `createPopupPage`; tiny dialog → `dialogShow`.
- [ ] Tab mới → `bs.DefaultTabPane` + `TabPaneConfig`, không legacy.
- [ ] Icons → `<FeatherIcon.XxxIcon size={12} className="me-1" />`.
- [ ] i18n text → wrap `T('key')`.
- [ ] Permission check → `checkPermission` với `app.READ/WRITE/ADMIN`.
- [ ] Bill UI mới → update `TMSBillRecordConfig.tsx`.
- [ ] Shared dep mới cần sync Platform → khai `shared.<name>.singleton: true` trong webpack.
