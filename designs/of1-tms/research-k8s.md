# Research: Kubernetes (k8s) — Concepts & Áp dụng cho of1-tms

> **Loại**: Research only — không có code/openspec.
> **Mục tiêu**: Nắm concepts cơ bản k8s + so sánh với Docker Compose + khả năng deploy of1-tms stack.

---

## 1. Kubernetes là gì?

Kubernetes (k8s) là **container orchestration platform** — tự động hóa việc deploy, scale, và quản lý container. Nếu Docker Compose là "chạy nhiều container trên 1 máy", k8s là "chạy nhiều container trên nhiều máy (cluster) và tự recover khi có máy die".

---

## 2. Core Concepts

### 2.1 Pod
- **Đơn vị nhỏ nhất** trong k8s — 1 Pod = 1 hoặc nhiều container chạy chung.
- Có IP riêng trong cluster, nhưng **không persistent** — Pod die là IP mất.
- Thông thường 1 Pod = 1 container (ví dụ: 1 Pod chạy TMS BE).

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tms-backend
spec:
  containers:
  - name: tms-backend
    image: of1/tms-backend:latest
    ports:
    - containerPort: 7086
```

### 2.2 Deployment
- **Quản lý Pod** — khai báo "tôi muốn 3 replica của TMS BE", k8s tự đảm bảo luôn có đủ.
- Tự restart Pod khi crash, rolling update khi deploy version mới.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tms-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: tms-backend
  template:
    spec:
      containers:
      - name: tms-backend
        image: of1/tms-backend:1.2.3
```

### 2.3 Service
- **Stable endpoint** trỏ vào Pod — Pod chết/đổi IP, Service vẫn ổn định.
- 3 loại chính:
  - `ClusterIP` — internal only (default), dùng cho giao tiếp giữa services.
  - `NodePort` — expose ra ngoài qua port của node (dev/test).
  - `LoadBalancer` — dùng cloud LB (GCP/AWS/Azure), production.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: tms-backend-svc
spec:
  selector:
    app: tms-backend
  ports:
  - port: 7086
    targetPort: 7086
  type: ClusterIP
```

### 2.4 Ingress
- **HTTP router** — route traffic từ ngoài vào đúng Service dựa trên host/path.
- Thay thế cho nginx/reverse proxy thủ công.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: of1-ingress
spec:
  rules:
  - host: tms.openfreightone.com
    http:
      paths:
      - path: /api
        backend:
          service:
            name: tms-backend-svc
            port:
              number: 7086
```

### 2.5 ConfigMap & Secret
- **ConfigMap**: key-value config không nhạy cảm (vd: `SPRING_PROFILES_ACTIVE=prod`).
- **Secret**: base64-encoded, dùng cho password, token, API key.
- Inject vào Pod qua env vars hoặc mount file.

```yaml
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: tms-config
data:
  SPRING_PROFILES_ACTIVE: "prod"
  TMS_PORT: "7086"

# Secret
apiVersion: v1
kind: Secret
metadata:
  name: tms-db-secret
type: Opaque
data:
  DB_PASSWORD: cGFzc3dvcmQ=  # base64("password")
```

### 2.6 PersistentVolume (PV) & PersistentVolumeClaim (PVC)
- **PV**: storage thực tế (disk trên cloud, NFS, local disk).
- **PVC**: Pod "claim" một phần storage.
- Dùng cho PostgreSQL, Kafka data — cần persistent sau khi Pod restart.

### 2.7 Namespace
- Logical partition trong cluster — tách môi trường: `dev`, `staging`, `prod`.
- Resource limit per namespace.

---

## 3. Docker Compose vs Kubernetes

| | Docker Compose | Kubernetes |
|---|---|---|
| **Scale** | 1 máy | Multi-node cluster |
| **High Availability** | Không (1 máy die = down) | Tự động (Pod reschedule sang node khác) |
| **Rolling update** | Manual (down + up) | Tự động, zero-downtime |
| **Config management** | `.env` file | ConfigMap + Secret |
| **Service discovery** | Service name trong network | DNS tự động (`<service>.<namespace>.svc`) |
| **Load balancing** | Không có sẵn | Built-in |
| **Resource limits** | Optional | Enforced (CPU/memory per Pod) |
| **Learning curve** | Thấp | Cao |
| **Dev local** | Rất phù hợp | Dùng minikube/kind |
| **Production** | Hạn chế | Tiêu chuẩn industry |

---

## 4. of1-tms Stack → Kubernetes Mapping

Hiện tại stack của1-tms (ước từ port config):

| Service | Port | K8s Object |
|---|---|---|
| Platform BE (Spring Boot) | 7080 | Deployment + ClusterIP Service |
| TMS BE (Spring Boot) | 7086 | Deployment + ClusterIP Service |
| Platform FE (React) | 3000 | Deployment + ClusterIP Service |
| TMS FE (React) | 3006 | Deployment + ClusterIP Service |
| PostgreSQL | 5432 | StatefulSet + ClusterIP Service + PVC |
| Kafka | 9092 | StatefulSet + ClusterIP Service + PVC |

**Ingress** route traffic HTTP/HTTPS từ ngoài vào FE + BE theo domain/path.

**Sơ đồ**:
```
Internet → Ingress → tms-fe-svc (3006)
                   → platform-fe-svc (3000)
                   → tms-be-svc (7086)
                   → platform-be-svc (7080)

tms-be-svc ←→ platform-be-svc (internal RPC)
tms-be-svc → postgres-svc (5432)
tms-be-svc → kafka-svc (9092)
```

---

## 5. Tools cần biết

| Tool | Dùng để |
|---|---|
| `kubectl` | CLI tương tác với cluster (apply, get, logs, exec) |
| `helm` | Package manager cho k8s — deploy app phức tạp bằng "chart" |
| `k9s` | Terminal UI để browse cluster, xem Pod logs realtime |
| `minikube` | Chạy k8s local trên 1 máy (dev/test) |
| `kind` | k8s in Docker — nhẹ hơn minikube, CI-friendly |
| `k3s` | Lightweight k8s — phù hợp VPS nhỏ / edge |

---

## 6. Lộ trình học đề xuất

1. **Tuần 1** — Concepts + kubectl cơ bản
   - Đọc: [kubernetes.io/docs/concepts](https://kubernetes.io/docs/concepts/)
   - Thực hành: cài `minikube` + deploy 1 app Spring Boot đơn giản
   - Lệnh cần nhớ: `kubectl get pods/svc/deploy`, `kubectl logs`, `kubectl exec -it`, `kubectl apply -f`

2. **Tuần 2** — ConfigMap, Secret, PVC, Ingress
   - Deploy PostgreSQL với PVC
   - Inject config TMS BE từ ConfigMap + Secret
   - Setup nginx Ingress controller

3. **Tuần 3** — Helm + thực chiến
   - Viết Helm chart cho TMS BE
   - Dùng `helm install/upgrade/rollback`
   - Thử rolling update + rollback

4. **Tuần 4** — Production readiness
   - Resource requests/limits
   - Liveness + Readiness probes
   - Horizontal Pod Autoscaler (HPA)
   - Namespace + RBAC cơ bản

---

## 7. Quick Reference — Lệnh kubectl hay dùng

```bash
# Xem tất cả
kubectl get all -n <namespace>

# Xem logs
kubectl logs -f <pod-name>

# SSH vào pod
kubectl exec -it <pod-name> -- /bin/sh

# Apply config
kubectl apply -f deployment.yaml

# Scale
kubectl scale deployment tms-backend --replicas=3

# Xem events (debug)
kubectl describe pod <pod-name>

# Port-forward để test local
kubectl port-forward svc/tms-backend-svc 7086:7086
```

---

## 8. Kết luận

- **Ngắn hạn**: Docker Compose vẫn ổn cho dev local và small deployment.
- **Trung hạn**: Khi of1-tms scale lên, k8s cho phép HA + zero-downtime deploy.
- **Điểm bắt đầu**: Học `kubectl` + `minikube` + deploy TMS BE đơn giản trước khi nghĩ đến full stack.
- **M80Q** (i5-10500T, 16GB RAM): đủ để chạy `minikube` local cho học tập, nhưng sẽ nặng nếu chạy full stack trên đó.
