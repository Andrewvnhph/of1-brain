#!/usr/bin/env bash
#
# fetch-tms-logs.sh — kéo logs từ TMS server về local qua SSH + tar streaming.
# Dùng tar vì server không có rsync. 1 SSH connection, nén gzip trên đường truyền.
#
# Usage:
#   ./fetch-tms-logs.sh                      # tải cả thư mục logs/ (prod)
#   ./fetch-tms-logs.sh --latest             # chỉ folder MỚI NHẤT
#   ./fetch-tms-logs.sh --folder 20261030_132709   # 1 folder cụ thể
#   ./fetch-tms-logs.sh --host beta          # chuyển beta
#   ./fetch-tms-logs.sh --list               # chỉ liệt kê folder có trên server
#
# Log lưu vào: of1-brain/logs-local/<env>/

set -euo pipefail

# ===== Config =====
HOST_PROD="tms-server.of1-prod-platform.svc.cluster.local"
HOST_BETA="tms-server.of1-beta-platform.svc.cluster.local"
SSH_USER="datatp"
REMOTE_LOG_ROOT="/home/datatp/release-tms/server-instances/tms-server/logs"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_LOG_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)/logs-local"
mkdir -p "$LOCAL_LOG_ROOT"

# ===== Parse args =====
HOST="$HOST_PROD"
ENV_LABEL="prod"
MODE="all"   # all | latest | folder | list
FOLDER=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --list)   MODE="list"; shift ;;
    --latest) MODE="latest"; shift ;;
    --folder) MODE="folder"; FOLDER="$2"; shift 2 ;;
    --host)
      case "$2" in
        prod) HOST="$HOST_PROD"; ENV_LABEL="prod" ;;
        beta) HOST="$HOST_BETA"; ENV_LABEL="beta" ;;
        *) echo "ERR: --host phải là 'prod' hoặc 'beta'"; exit 1 ;;
      esac
      shift 2
      ;;
    -h|--help) sed -n '1,15p' "$0" | sed 's/^#//'; exit 0 ;;
    *) echo "ERR: arg không hiểu '$1'. Dùng --help để xem."; exit 1 ;;
  esac
done

SSH_TARGET="${SSH_USER}@${HOST}"
LOCAL_DIR="$LOCAL_LOG_ROOT/$ENV_LABEL"
mkdir -p "$LOCAL_DIR"

echo ">>> ENV: $ENV_LABEL ($HOST)"
echo ">>> MODE: $MODE"
echo ">>> Target local: $LOCAL_DIR/"
echo ""

# ===== List mode =====
if [[ "$MODE" == "list" ]]; then
  echo ">>> Folder trên server (mới nhất ở trên):"
  ssh "$SSH_TARGET" "ls -1 $REMOTE_LOG_ROOT | sort -r | head -30"
  exit 0
fi

# ===== Resolve folder cho latest =====
if [[ "$MODE" == "latest" ]]; then
  echo ">>> Detect folder mới nhất..."
  FOLDER=$(ssh "$SSH_TARGET" "ls -1 $REMOTE_LOG_ROOT | sort -r | head -1")
  echo ">>> Latest: $FOLDER"
fi

# ===== Build tar command =====
# Dùng 1 SSH connection: ssh server "tar czf - <path>" | tar xzf - -C local
#  -c create, -z gzip, -f - stdout
# Server-side cd vào parent để tar không bake absolute path
if [[ "$MODE" == "all" ]]; then
  echo ">>> tar stream CẢ thư mục logs..."
  ssh "$SSH_TARGET" "cd $REMOTE_LOG_ROOT && tar czf - ." | tar xzf - -C "$LOCAL_DIR"
elif [[ "$MODE" == "latest" || "$MODE" == "folder" ]]; then
  if [[ -z "$FOLDER" ]]; then
    echo "ERR: Không xác định được folder"; exit 1
  fi
  if ! ssh "$SSH_TARGET" "test -d $REMOTE_LOG_ROOT/$FOLDER"; then
    echo "ERR: Folder '$FOLDER' không có trên server"
    exit 1
  fi
  echo ">>> tar stream folder: $FOLDER"
  mkdir -p "$LOCAL_DIR/$FOLDER"
  ssh "$SSH_TARGET" "cd $REMOTE_LOG_ROOT/$FOLDER && tar czf - ." | tar xzf - -C "$LOCAL_DIR/$FOLDER"
fi

echo ""
echo "✅ Done."
echo ""
echo "Dung lượng:"
du -sh "$LOCAL_DIR"
echo ""
echo "Folders mới nhất ở local:"
ls -1t "$LOCAL_DIR" 2>/dev/null | head -5
echo ""
echo "💡 Paste path cho Claude:"
echo "   $LOCAL_DIR"
