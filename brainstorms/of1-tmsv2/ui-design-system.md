## TODO (dev)
- [x] Thử chuyển đổi qua Radix Colors. Hỗ trợ theme Dark mode ✅ ai/geo-foundation commit `47f8b79`

## Summary (AI)

| TODO | design | openspecs | code | review | status |
|---|---|---|---|---|---|
| Radix Colors + Dark Mode | `../designs/of1-tmsv2/ui-design-system.md` | — | branch `ai/geo-foundation` · HEAD `47f8b79` · 9 files: `ThemeContext` + `bootstrap.tsx` Radix CSS imports + `stylesheet.scss` color overrides + `TopBar` toggle + `AppShell` bg var | build ✅ | ✅ **done** |
| Remove --phoenix-* layer (Radix direct) | — | — | branch `ai/geo-foundation` · HEAD `97a2455` · 6 files: `pxvar()` redef → Radix vars; bulk replace `var(--phoenix-*)` in grid+calendar; `stylesheet.scss` simplified; TopBar+AppShell inline vars | build ✅ | ✅ **done** |
