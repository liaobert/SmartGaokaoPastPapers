#!/usr/bin/env bash
# 一键部署 SmartGaokaoPastPapers → 腾讯云
# 访问：https://gaokao.defenxiang.online/pastpapers/
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEPLOY_DIR="$ROOT/deploy"
ENV_FILE="${DEPLOY_ENV:-$DEPLOY_DIR/deploy.env}"

die() { echo "错误: $*" >&2; exit 1; }

load_env() {
  [[ -f "$ENV_FILE" ]] || die "缺少 $ENV_FILE"
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
  DEPLOY_HOST="${DEPLOY_HOST:-}"
  DEPLOY_USER="${DEPLOY_USER:-ubuntu}"
  DEPLOY_PORT="${DEPLOY_PORT:-22}"
  DEPLOY_SSH_KEY="${DEPLOY_SSH_KEY:-$HOME/.ssh/defenxiang.pem}"
  REMOTE_DIR="${REMOTE_DIR:-/opt/smart-gaokao-pastpapers}"
  BIND_PORT="${BIND_PORT:-8010}"
  APP_BASE_PATH="${APP_BASE_PATH:-/pastpapers}"
  [[ -n "$DEPLOY_HOST" ]] || die "DEPLOY_HOST 未设置"
  DEPLOY_SSH_KEY="${DEPLOY_SSH_KEY/#\~/$HOME}"
  [[ -f "$DEPLOY_SSH_KEY" ]] || die "SSH 私钥不存在: $DEPLOY_SSH_KEY"
}

SSH=()
RSYNC=()

init_tools() {
  SSH=(ssh -i "$DEPLOY_SSH_KEY" -p "$DEPLOY_PORT"
    -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ServerAliveInterval=30)
  RSYNC=(rsync -az --delete
    --exclude '._*'
    --exclude '.DS_Store'
    --exclude 'data/'
    --exclude 'output/'
    --exclude '.venv/'
    --exclude '__pycache__/'
    --exclude '*.pyc'
    --exclude 'database/*.db-wal'
    --exclude 'database/*.db-shm'
    -e "ssh -i $DEPLOY_SSH_KEY -p $DEPLOY_PORT -o BatchMode=yes -o StrictHostKeyChecking=accept-new")
}

HOST() { echo "${DEPLOY_USER}@${DEPLOY_HOST}"; }

echo "==> 加载配置"
load_env
init_tools
export COPYFILE_DISABLE=1

echo "==> 1. 远端目录 $REMOTE_DIR"
"${SSH[@]}" "$(HOST)" "sudo mkdir -p $REMOTE_DIR && sudo chown -R ubuntu:ubuntu $REMOTE_DIR"

echo "==> 2. 同步代码与数据库"
"${RSYNC[@]}" \
  "$ROOT/src/" "$(HOST):$REMOTE_DIR/src/"
"${RSYNC[@]}" \
  "$ROOT/database/" "$(HOST):$REMOTE_DIR/database/"
"${RSYNC[@]}" \
  "$ROOT/deploy/" "$(HOST):$REMOTE_DIR/deploy/"
"${RSYNC[@]}" \
  "$ROOT/requirements.txt" "$(HOST):$REMOTE_DIR/requirements.txt"
"${RSYNC[@]}" \
  "$ROOT/README.md" "$(HOST):$REMOTE_DIR/README.md"
# 媒体资源不可 --delete，避免清空服务器已转换的公式图
rsync -az --exclude '._*' --exclude '.DS_Store' \
  -e "ssh -i $DEPLOY_SSH_KEY -p $DEPLOY_PORT -o BatchMode=yes -o StrictHostKeyChecking=accept-new" \
  "$ROOT/assets/" "$(HOST):$REMOTE_DIR/assets/"

echo "==> 3. 远端安装 venv / systemd / nginx"
"${SSH[@]}" "$(HOST)" "REMOTE_DIR=$REMOTE_DIR BIND_PORT=$BIND_PORT APP_BASE_PATH=$APP_BASE_PATH" bash -s <<'REMOTE'
set -euo pipefail
REMOTE_DIR="${REMOTE_DIR:-/opt/smart-gaokao-pastpapers}"
BIND_PORT="${BIND_PORT:-8010}"
APP_BASE_PATH="${APP_BASE_PATH:-/pastpapers}"

cd "$REMOTE_DIR"
sudo find "$REMOTE_DIR" -name '._*' -delete 2>/dev/null || true

# Python venv
if [[ ! -x "$REMOTE_DIR/.venv/bin/python" ]]; then
  python3 -m venv "$REMOTE_DIR/.venv"
fi
"$REMOTE_DIR/.venv/bin/pip" install -q --upgrade pip
"$REMOTE_DIR/.venv/bin/pip" install -q -r "$REMOTE_DIR/requirements.txt"

# 权限：www-data 读库
sudo chown -R ubuntu:www-data "$REMOTE_DIR"
sudo find "$REMOTE_DIR" -type d -exec chmod 755 {} \;
sudo find "$REMOTE_DIR" -type f -exec chmod 644 {} \;
sudo chmod +x "$REMOTE_DIR/.venv/bin/"* 2>/dev/null || true
sudo chmod 664 "$REMOTE_DIR/database/gaokao.db" || true
# WAL 可能需要写权限
sudo chmod 775 "$REMOTE_DIR/database" || true

# systemd
sudo cp "$REMOTE_DIR/deploy/smart-gaokao-pastpapers.service" /etc/systemd/system/smart-gaokao-pastpapers.service
sudo systemctl daemon-reload
sudo systemctl enable smart-gaokao-pastpapers.service
sudo systemctl restart smart-gaokao-pastpapers.service

# 注入 nginx 到 gaokao 站点（幂等）
GAOKAO_CONF=/etc/nginx/sites-available/gaokao-defenxiang
SNIPPET="$REMOTE_DIR/deploy/nginx.pastpapers-location.conf"
if ! sudo grep -q 'SMART_GAOKAO_PASTPAPERS_BEGIN' "$GAOKAO_CONF"; then
  sudo python3 <<'PY'
from pathlib import Path
conf_path = Path("/etc/nginx/sites-available/gaokao-defenxiang")
snippet = Path("/opt/smart-gaokao-pastpapers/deploy/nginx.pastpapers-location.conf").read_text()
text = conf_path.read_text()
if "SMART_GAOKAO_PASTPAPERS_BEGIN" in text:
    print("already injected")
else:
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    injected_once = False
    # 在每个 server 块的第一个 location 之前注入
    while i < len(lines):
        out.append(lines[i])
        if (not injected_once or True) and "server_name gaokao.defenxiang.online" in lines[i]:
            j = i + 1
            while j < len(lines) and not lines[j].lstrip().startswith("location "):
                out.append(lines[j])
                j += 1
            # 若该 server 尚未注入
            block_start = len(out)
            # look ahead in remaining for end of this server - simpler: inject before first location after this server_name
            # Check if already in this server: we'll inject every time we see server_name (http + https)
            out.append("\n" + snippet + "\n")
            i = j - 1
        i += 1
    conf_path.write_text("".join(out))
    print("injected /pastpapers/ into gaokao conf")
PY
else
  echo "gaokao conf already has pastpapers locations"
fi

sudo nginx -t
sudo systemctl reload nginx

echo "==> 等待服务就绪"
for i in $(seq 1 20); do
  if curl -sf "http://127.0.0.1:${BIND_PORT}/health" >/dev/null; then
    echo "health ok"
    break
  fi
  sleep 0.5
done
curl -s "http://127.0.0.1:${BIND_PORT}/health" || true
echo
sudo systemctl is-active smart-gaokao-pastpapers.service
REMOTE

echo "==> 4. 公网验证"
sleep 1
echo "--- health via nginx ---"
curl -sk "https://gaokao.defenxiang.online/pastpapers/health" || curl -s "http://gaokao.defenxiang.online/pastpapers/health" || true
echo
echo "--- index title ---"
curl -sk "https://gaokao.defenxiang.online/pastpapers/" | grep -oE '<title>[^<]*</title>' || \
  curl -s "http://gaokao.defenxiang.online/pastpapers/" | grep -oE '<title>[^<]*</title>' || true
echo
echo "完成。请访问：https://gaokao.defenxiang.online/pastpapers/"
