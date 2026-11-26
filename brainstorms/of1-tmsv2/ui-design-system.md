## TODO (dev)
- [x] Thử chuyển đổi qua Radix Colors. Hỗ trợ theme Dark mode ✅ ai/geo-foundation commit `47f8b79`
- [x] [+ui] Thử khả năng kéo thả sắp xếp col trên VGrid — drag grip hiện khi hover header, kéo để reorder trong cùng container (fixed-left/default/fixed-right), drop indicator line dọc, ghost header floating. Dùng raw mouse events (pattern cũ của startColumnResize). ✅ ai/geo-foundation commit `c4ede56`

## Summary (AI)

| TODO | design | openspecs | code | review | status |
|---|---|---|---|---|---|
| VGrid column header menu — sort, inline filter, pin, hide; status icons; default sortable+filterable | — | — | branch `ai/geo-foundation` · HEAD `e1d3a56` · 3 files: `TableHeaderCell` ColMenuBtn+InlineFilter+hover status icons; `ListModel` sortField/sortDesc tracking; `VGridConfigModel` default sortable=true dataType='string' | build ✅ | ✅ **done** |
| Radix Colors + Dark Mode | `../designs/of1-tmsv2/ui-design-system.md` | — | branch `ai/geo-foundation` · HEAD `47f8b79` · 9 files: `ThemeContext` + `bootstrap.tsx` Radix CSS imports + `stylesheet.scss` color overrides + `TopBar` toggle + `AppShell` bg var | build ✅ | ✅ **done** |
| Remove --phoenix-* layer (Radix direct) | — | — | branch `ai/geo-foundation` · HEAD `97a2455` · 6 files: `pxvar()` redef → Radix vars; bulk replace `var(--phoenix-*)` in grid+calendar; `stylesheet.scss` simplified; TopBar+AppShell inline vars | build ✅ | ✅ **done** |
| Lighten dark mode — semantic surface vars | — | — | branch `ai/geo-foundation` · HEAD `8aab3fa` · 4 files: `stylesheet.scss` add `--of1-bg/surface/border/border-mid` `:root` + `.dark` overrides (slate-4/5); `grid/stylesheet.scss` `.dark .v-grid` shift rows/header to slate-4/5/7; `AppShell` → `var(--of1-bg)`; `TopBar` → `var(--of1-surface/border)` | build ✅ | ✅ **done** |
| Sync all hardcoded colors to CSS vars | — | — | branch `ai/geo-foundation` · HEAD `1fba4cb` · 7 files: `stylesheet.scss` add `--of1-sidebar-*` vars (light=orange, dark=slate-4/5/6); `Sidebar.tsx` C object → CSS vars; `BreadcrumbBar` + `AppTile` + `PopupRenderer` → `--of1-surface/border/slate-*`; `App.tsx` loading bg → `--of1-bg`; `TopBar` badge border → `--of1-surface` | build ✅ | ✅ **done** |
| VGrid drag-and-drop column reorder — DragGrip + startColumnDrag + indicator line + reorderField | `+ui` | — | — | branch `ai/geo-foundation` · HEAD `c4ede56` · 3 files: `TableHeaderCell.tsx` DragGrip SVG (6-dot grip, hover-only), startColumnDrag() raw mousemove pattern (ghost floating+rotate, full-height indicator line+triangle tip, elementsFromPoint target detection); `IVGrid.tsx` hideColMenuBtn flag; `VGridConfigModel.tsx` reorderField(dragName,targetName,insertBefore) splice+updateVisibleFieldModels | build ✅ | ✅ **done** |
