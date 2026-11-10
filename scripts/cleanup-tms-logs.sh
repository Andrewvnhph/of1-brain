#!/usr/bin/env bash
#
# cleanup-tms-logs.sh — xóa log folder cũ trên TMS server, giữ N folder mới nhất.
# DEFAULT = DRY RUN. Phải --force mới thực sự xóa.
#
# Usage:
#   ./cleanup-tms-logs.sh                       # dry run, giữ 5 folder mới nhất, prod
#   ./cleanup-tms-logs.sh --keep 3              # giữ 3 folder (dry run)
#   ./cleanup-tms-logs.sh --force               # xóa thật (hỏi confirm)
#   ./cleanup-tms-logs.sh --force --yes         # xóa thật, SKIP confirm (dangerous)
#   ./cleanup-tms-logs.sh --host beta --force   # chạy trên beta
#
# Yêu cầu: SSH tới datatp@tms-server đã work.

set -euo pipefail

# ===== Config =====
HOST_PROD="tms-server.of1-prod-platform.svc.cluster.local"
HOST_BETA="tms-server.of1-beta-platform.svc.cluster.local"
SSH_USER="datatp"
REMOTE_LOG_ROOT="/home/datatp/release-tms/server-instances/tms-server/logs"

# ===== Parse args =====
HOST="$HOST_PROD"
ENV_LABEL="prod"
KEEP=5
FORCE=0
SKIP_CONFIRM=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --keep)  KEEP="$2"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --yes)   SKIP_CONFIRM=1; shift ;;
    --host)
      case "$2" in
        prod) HOST="$HOST_PROD"; ENV_LABEL="prod" ;;
        beta) HOST="$HOST_BETA"; ENV_LABEL="beta" ;;
        *) echo "ERR: --host phải là 'prod' hoặc 'beta'"; exit 1 ;;
      esac
      shift 2
      ;;
    -h|--help) sed -n '1,15p' "$0" | sed 's/^#//'; exit 0 ;;
    *) echo "ERR: arg không hiểu '$1'. --help để xem."; exit 1 ;;
  esac
done

if ! [[ "$KEEP" =~ ^[0-9]+$ ]] || [[ "$KEEP" -lt 1 ]]; then
  echo "ERR: --keep phải là số nguyên >= 1"; exit 1
fi

SSH_TARGET="${SSH_USER}@${HOST}"

echo ">>> ENV: $ENV_LABEL ($HOST)"
echo ">>> KEEP top: $KEEP folder mới nhất"
echo ">>> MODE: $([ "$FORCE" -eq 1 ] && echo 'FORCE (sẽ xóa thật)' || echo 'DRY RUN (chỉ in, không xóa)')"
echo ""

# ===== Load remote state =====
echo ">>> Fetching folder list từ server..."
ALL_FOLDERS=$(ssh "$SSH_TARGET" "ls -1 $REMOTE_LOG_ROOT | sort -r")
TOTAL=$(echo "$ALL_FOLDERS" | wc -l | tr -d ' ')

if [[ -z "$ALL_FOLDERS" ]] || [[ "$TOTAL" -eq 0 ]]; then
  echo "Không có folder nào trong $REMOTE_LOG_ROOT"
  exit 0
fi

echo ">>> Tổng số folder trên server: $TOTAL"
echo ""

if [[ "$TOTAL" -le "$KEEP" ]]; then
  echo "✅ Tổng ($TOTAL) <= KEEP ($KEEP) — không có gì để xóa."
  echo ""
  echo "=== Folder hiện tại ==="
  echo "$ALL_FOLDERS"
  exit 0
fi

TO_KEEP=$(echo "$ALL_FOLDERS" | head -n "$KEEP")
TO_DELETE=$(echo "$ALL_FOLDERS" | tail -n +$((KEEP+1)))
DEL_COUNT=$(echo "$TO_DELETE" | wc -l | tr -d ' ')

echo "=== KEEP ($KEEP folder) ==="
echo "$TO_KEEP"
echo ""
echo "=== DELETE ($DEL_COUNT folder) ==="
echo "$TO_DELETE"
echo ""

# ===== Dung lượng ước tính =====
echo ">>> Đang tính dung lượng sẽ giải phóng..."
DEL_LIST_SPACED=$(echo "$TO_DELETE" | tr '\n' ' ')
FREED=$(ssh "$SSH_TARGET" "cd $REMOTE_LOG_ROOT && du -sch $DEL_LIST_SPACED 2>/dev/null | tail -1" | awk '{print $1}')
echo ">>> Sẽ giải phóng khoảng: $FREED"
echo ""

# ===== Dry run exit =====
if [[ "$FORCE" -ne 1 ]]; then
  echo "🧪 DRY RUN — không xóa gì. Chạy lại với --force để xóa thật."
  exit 0
fi

# ===== Confirm =====
if [[ "$SKIP_CONFIRM" -ne 1 ]]; then
  echo "⚠️  Sẽ xóa VĨNH VIỄN $DEL_COUNT folder trên $ENV_LABEL ($HOST)"
  read -p "Gõ 'yes' để confirm: " yn
  if [[ "$yn" != "yes" ]]; then
    echo "Hủy."
    exit 0
  fi
fi

# ===== Xóa =====
echo ">>> Đang xóa..."
# Dùng printf để không bị word-split tên folder có khoảng trắng (phòng hờ)
ssh "$SSH_TARGET" "cd $REMOTE_LOG_ROOT && printf '%s\n' $DEL_LIST_SPACED | xargs -I {} rm -rf {}"

echo ""
echo "✅ Xóa xong."
echo ""

# ===== Verify =====
NEW_TOTAL=$(ssh "$SSH_TARGET" "ls -1 $REMOTE_LOG_ROOT | wc -l" | tr -d ' ')
NEW_SIZE=$(ssh "$SSH_TARGET" "du -sh $REMOTE_LOG_ROOT 2>/dev/null | cut -f1")
echo "Folder còn lại: $NEW_TOTAL"
echo "Dung lượng logs/: $NEW_SIZE"
