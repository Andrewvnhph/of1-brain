## TODO (dev)
- [x] Security foundation: Liquibase schema (core + security tables) + SecurityConfig JWT + ClientContext ThreadLocal

## Summary (AI)

| TODO | design | openspecs | code | review | status |
|---|---|---|---|---|---|
| VGrid agg/bucket rows transparent + aggPanelWidth separate from treeWidth | `+ui` | — | — | branch `ai/geo-foundation` · HEAD `3ea4065` · 6 files: `TableDataCell`+`FillerDataCell` transparent for agg/bucket; `TableAggregationViewModel` `maxWidth=55`+`getFieldContainerWidthCustom()`; `TableView` `aggPanelWidth` wrapper div | — | ✅ **done** |
| Security foundation | — | — | `of1-tmsv2/module/core/` | tests ✓ | ✅ done |
| Geo reference tables + VN 2025 seed data + JPA audit auto-fill | — | — | branch `ai/geo-foundation` · HEAD `e5f017c` · 14 files | — | ✅ **done** |
| `@of1-tms/ui` workspace — extract Group 1 wbootstrap core from of1-webui | — | — | branch `ai/geo-foundation` · HEAD `a2cc9c2` · 98 files · `webui/ui/src/{wbootstrap/core,wbootstrap/grid,wbootstrap/input,util,i18n.tsx}` + stubs `app/host` + `server` + `package.json` + `tsconfig.json` + alias in `rsbuild.config.ts` | build ✅ | ✅ **done** |
| VGrid render code review — 9-point fix | — | — | branch `ai/geo-foundation` · HEAD `ac5a33a` · 6 files | build ✅ | ✅ **done** |
| CoreLocationService + SqlBuilder/SqlQueryManager + Groovy SQL pattern | — | — | branch `ai/geo-foundation` · HEAD `1671ef2` · 9 files · `SqlBuilder` (FILTER helpers) + `SqlQueryManager` (Groovy compile+cache) + `CoreLocationService` (search/CRUD) + `LocationSearchSql.groovy` + 8 IT cases | build ✅ | ✅ **done** |
| AppContext/PageContext/AppRegistry + shell breadcrumb navigation + VGrid FieldDataType fix | — | — | branch `ai/geo-foundation` · HEAD `f499071` · 27 files · `ui/src/app/{AppContext,AppRegistry,PageContext,backend/}` + `host/src/layout/{AppPage,BreadcrumbBar,PopupRenderer}` + AppShell/Sidebar/AppTile wired; rsbuild alias bug fixed (use `tools.rspack.resolve.alias`) | build ✅ | ✅ **done** |
| GeoPage UI + CoreGeoService — country/province/ward/location tabs + CoreLocationServiceIT 8 cases | — | — | branch `ai/geo-foundation` · HEAD `7c48b1c` · 12 files · `CoreGeoService` (searchCountries/Provinces/Wards) + `GeoPage` tab switcher + 4 list views + `DbEntityList`/`AppComponent` base + `CoreLocationServiceIT` integration test | build ✅ | ✅ **done** |
| Build fix: port missing wbootstrap deps (calendar, graphic, lexical stub, JsonView, scss) + react-window/marked/dompurify/popperjs install + CoreGeoService Groovy SQL scripts (CountrySearchSql/ProvinceSearchSql/WardSearchSql) + `exportsPresence: warn` for Bootstrap ESM linking | — | — | branch `ai/geo-foundation` · HEAD `16863d9` · 31 files | build ✅ | ✅ **done** |

**Deliverables** (branch `ai/xuong-phim-ai`, project `/Users/admin/OF1/forgejo/of1-tmsv2/`):

**Liquibase migrations** (`module/core/src/main/resources/db/changelog/changes/`):
- `20261119093432-core-tables.yaml` — `core_account`, `core_company`, `core_account_company`
- `20261119093433-security-tables.yaml` — `security_module`, `security_permission`, `security_role`, `security_role_permission`, `security_account_role` + seed data
- `20261119135340-core-company-keycloak-org.yaml` — `keycloak_org_id` column
- `20261119150917-core-account-username.yaml` — `username` column

**Security layer** (`module/core/src/main/java/com/of1/tms/core/security/`):
- `SecurityConfig` — stateless JWT resource server, `ClientContextFilter` after `BearerTokenAuthenticationFilter`
- `ClientContext` — ThreadLocal, fields: `keycloakSub`, `keycloakOrgId`, `accountId`, `companyId`, `username`, `fullName`, `coarseRoles`, `permissions`
- `TmsJwtGrantedAuthoritiesConverter` — extract roles + Keycloak 26 Organizations claim (`OrgClaim`)
- `filter/ClientContextFilter` — 4 bước: resolve account → resolve company → load permissions → build context
- `service/AccountResolver` — `@Cacheable("accountId")` 30 min + auto-provision + `syncProfile` cache-aware
- `service/CompanyResolver` — partner auto-detect via `keycloak_org_id`, internal validate `X-Company-Id` header
- `service/PermissionLoader` — `@Cacheable("permissions")` 5 min, native query join `security_*` tables
- `config/CacheConfig` — `@EnableCaching` + Caffeine: `accountId` 30m, `permissions` 5m, `profileSync` 10m

**Tests** (`module/core/src/test/`):
- `AccountResolverTest` — 5 cases (provision internal/partner, existing, syncProfile)
- `CompanyResolverTest` — 5 cases (partner auto/not-found, internal null/valid/invalid)
- `ClientContextFilterTest` — 6 cases (internal/partner/403/no-auth/context-cleared)
