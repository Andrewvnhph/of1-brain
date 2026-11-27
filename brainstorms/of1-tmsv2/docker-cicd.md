## TODO (dev)
- [ ] [docker] **Thực hành CI/CD pipeline — Docker → Harbor → k8s** — mô phỏng lại quy trình production: build image → push registry → deploy k8s. Lộ trình 5 bước:
    - Bước 1 ✅ Docker cơ bản — build image, chạy local (`docker-local.sh up-native` đã chạy được, `status: UP`)
    - Bước 2 — Registry: push/pull image với Docker Registry local (hoặc Harbor)
    - Bước 3 — k8s cơ bản: deploy image lên minikube, hiểu Pod/Deployment/Service
    - Bước 4 — CI/CD: Forgejo Actions tự build + push khi push code
    - Bước 5 — Full flow: code push → CI build → push Harbor → k8s auto deploy

## Summary (AI)

| TODO | design | openspecs | code | review | status |
|---|---|---|---|---|---|
| Docker full pipeline local (`docker-local.sh`) | — | — | branch `ai/geo-foundation` · `Dockerfile` 3-stage FE+BE · `SpaController` · `docker-local.sh` · `docker-compose.native-db.yml` standalone | `status: UP` ✅ | ✅ **done** |
