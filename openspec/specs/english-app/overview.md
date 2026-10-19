# english-app — Capabilities overview

Phần mềm học tiếng Anh (personal project of mchien).

**Status**: bootstrap — chưa có capability nào được chốt. Dev fill scope trong `brainstorms/english-app/mchien.md` → AI gen spec khi scope rõ.

## Capabilities (dự kiến)

| Capability | Spec path | Status |
|---|---|---|
| vocabulary-flashcard | `./vocabulary-flashcard/spec.md` | TBD |
| spaced-repetition | `./spaced-repetition/spec.md` | TBD |
| grammar-check | `./grammar-check/spec.md` | TBD |
| conversation-practice | `./conversation-practice/spec.md` | TBD |
| listening-pronunciation | `./listening-pronunciation/spec.md` | TBD |
| reading-comprehension | `./reading-comprehension/spec.md` | TBD |
| progress-tracking | `./progress-tracking/spec.md` | TBD |
| auth-user-mgmt | `./auth-user-mgmt/spec.md` | TBD |

## Cross-cutting constraints

- **TypeScript strict** everywhere (BE / web / shared).
- **Shared validation schemas** (zod) giữa BE và FE (type + runtime check đồng nhất).
- **Spaced repetition algorithm**: SM-2 (SuperMemo) baseline, có thể upgrade FSRS sau.
- **i18n**: khả năng UI bilingual (Vietnamese + English learner-facing) từ đầu để không retrofit sau.
- **Mobile responsive**: web layout mobile-first; option PWA (installable, offline cache qua service worker) nếu dev muốn user cài đặt home screen.
