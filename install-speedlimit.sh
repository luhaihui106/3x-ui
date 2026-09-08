#!/usr/bin/env bash
set -euo pipefail

# 3X-UI Real Speed Limit V1 - 中文一键管理入口
# 仅用于 feature/real-client-speed-limit-v1 测试构建。

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PLAIN='\033[0m'

REPO='luhaihui106/3x-ui'
BRANCH='feature/real-client-speed-limit-v1'
ROLLING_TAG='dev-latest'
SELF_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/install-speedlimit.sh"
UPSTREAM_INSTALLER_URL="https://raw.githubusercontent.com/${REPO}/${BRANCH}/install.sh"
BACKUP_ROOT='/root/3x-ui-speedlimit-backups'
MARKER='/usr/local/x-ui/bin/REAL_SPEEDLIMIT_V1'

log()  { echo -e "${GREEN}[✓]${PLAIN} $*"; }
info() { echo -e "${BLUE}[i]${PLAIN} $*"; }
warn() { echo -e "${YELLOW}[!]${PLAIN} $*"; }
die()  { echo -e "${RED}[✗]${PLAIN} $*" >&2; exit 1; }

need_root() {
  [[ ${EUID:-$(id -u)} -eq 0 ]] || die '请使用 root 权限运行。'
}

arch_name() {
  case "$(uname -m)" in
    x86_64|amd64|x64) echo amd64 ;;
    *) echo unsupported ;;
  esac
}

ensure_supported_arch() {
  [[ "$(arch_name)" == 'amd64' ]] || die 'V1 安装包当前只发布 amd64。其他架构会在实机验收通过后补齐。'
}

panel_version_text() {
  if command -v x-ui >/dev/null 2>&1; then
    x-ui version 2>&1 || true
  elif [[ -x /usr/local/x-ui/x-ui ]]; then
    /usr/local/x-ui/x-ui version 2>&1 || true
  else
    true
  fi
}

is_xpanel() {
  local v
  v="$(panel_version_text)"
  echo "$v" | grep -Eqi 'x-panel|xpanel|xeefei'
}

has_existing_panel() {
  [[ -d /usr/local/x-ui || -d /etc/x-ui || -x /usr/bin/x-ui ]]
}

backup_now() {
  need_root
  mkdir -p "$BACKUP_ROOT"
  local ts archive list=()
  ts="$(date +%Y%m%d-%H%M%S)"
  archive="${BACKUP_ROOT}/speedlimit-backup-${ts}.tar.gz"

  [[ -e /etc/x-ui ]] && list+=(etc/x-ui)
  [[ -e /usr/local/x-ui ]] && list+=(usr/local/x-ui)
  [[ -e /etc/systemd/system/x-ui.service ]] && list+=(etc/systemd/system/x-ui.service)
  [[ -e /etc/default/x-ui ]] && list+=(etc/default/x-ui)
  [[ -e /etc/sysconfig/x-ui ]] && list+=(etc/sysconfig/x-ui)
  [[ -e /etc/conf.d/x-ui ]] && list+=(etc/conf.d/x-ui)
  [[ -e /root/cert ]] && list+=(root/cert)

  if [[ ${#list[@]} -eq 0 ]]; then
    warn '没有发现可备份的现有 3X-UI/X-Panel 文件。'
    return 0
  fi

  tar -C / -czf "$archive" "${list[@]}"
  chmod 600 "$archive"
  log "备份完成：$archive"
  echo "$archive"
}

patch_and_run_installer() {
  local tmp
  tmp="$(mktemp /tmp/3x-ui-speedlimit-install.XXXXXX.sh)"
  trap 'rm -f "$tmp"' RETURN

  curl -fsSL --retry 5 --retry-delay 2 "$UPSTREAM_INSTALLER_URL" -o "$tmp" || die '下载安装器失败，请检查 VPS 到 GitHub 的网络。'

  # 保留官方成熟安装逻辑，只把 Release 来源切到当前 Fork。
  # install.sh 原生支持参数 dev -> dev-latest，因此无需维护第二套安装器。
  sed -i \
    -e 's#github.com/MHSanaei/3x-ui#github.com/luhaihui106/3x-ui#g' \
    -e 's#github.com/mhsanaei/3x-ui#github.com/luhaihui106/3x-ui#g' \
    -e 's#api.github.com/repos/MHSanaei/3x-ui#api.github.com/repos/luhaihui106/3x-ui#g' \
    -e 's#api.github.com/repos/mhsanaei/3x-ui#api.github.com/repos/luhaihui106/3x-ui#g' \
    "$tmp"

  bash "$tmp" dev
  rm -f "$tmp"
  trap - RETURN
}

install_manager_command() {
  mkdir -p /usr/local/bin
  curl -fsSL --retry 3 "$SELF_URL" -o /usr/local/bin/xui-speedlimit || true
  if [[ -s /usr/local/bin/xui-speedlimit ]]; then
    chmod 755 /usr/local/bin/xui-speedlimit
    log '已安装中文快捷命令：xui-speedlimit'
  fi
}

verify_install() {
  local failed=0
  [[ -x /usr/local/x-ui/x-ui ]] || { warn '未找到面板二进制 /usr/local/x-ui/x-ui'; failed=1; }
  [[ -x /usr/local/x-ui/bin/xray-linux-amd64 ]] || { warn '未找到自定义 Xray 二进制'; failed=1; }
  [[ -f "$MARKER" ]] || { warn '未找到 REAL_SPEEDLIMIT_V1 构建标记；不要把它当成已验证的限速构建。'; failed=1; }

  if command -v systemctl >/dev/null 2>&1; then
    if systemctl is-active --quiet x-ui; then
      log 'x-ui 服务运行中。'
    else
      warn 'x-ui 服务当前不是 active，请查看：journalctl -u x-ui -n 100 --no-pager'
      failed=1
    fi
  fi

  if [[ -f "$MARKER" ]]; then
    echo
    info '构建标记：'
    cat "$MARKER"
    echo
  fi

  [[ $failed -eq 0 ]] || return 1
  log '自定义面板 + 自定义 Xray 文件校验通过。'
}

cmd_install() {
  need_root
  ensure_supported_arch

  if has_existing_panel; then
    if is_xpanel && [[ "${ALLOW_XPANEL_MIGRATION:-0}" != '1' ]]; then
      die '检测到 X-Panel。为避免数据库/自定义字段不兼容，V1 一键安装默认禁止直接覆盖。请先在独立测试 VPS 验证；后续迁移走专用 migration 流程。'
    fi
    warn '检测到现有 x-ui 数据，将先自动备份，再进行覆盖安装/升级。'
    backup_now >/dev/null
  fi

  patch_and_run_installer
  install_manager_command
  verify_install
  log '安装完成。限速字段：0=不限速；单位 Mbps；同一客户端所有并发连接共享总额度。'
}

cmd_update() {
  need_root
  ensure_supported_arch
  has_existing_panel || die '没有检测到现有面板，请使用 install。'
  if is_xpanel && [[ "${ALLOW_XPANEL_MIGRATION:-0}" != '1' ]]; then
    die '检测到 X-Panel，拒绝直接 update。请使用独立测试机或专用迁移流程。'
  fi
  backup_now >/dev/null
  patch_and_run_installer
  install_manager_command
  verify_install
  log '更新完成，并已保留更新前备份。'
}

cmd_status() {
  echo -e "${BLUE}=== 3X-UI 真限速 V1 状态 ===${PLAIN}"
  echo "架构：$(uname -m)"
  echo "面板版本：$(panel_version_text | head -n 3 | tr '\n' ' ' || true)"
  if [[ -f "$MARKER" ]]; then
    echo '构建标记：存在'
    cat "$MARKER"
  else
    echo '构建标记：不存在'
  fi
  if command -v systemctl >/dev/null 2>&1; then
    echo "服务：$(systemctl is-active x-ui 2>/dev/null || true)"
  fi
  if [[ -x /usr/local/x-ui/bin/xray-linux-amd64 ]]; then
    echo 'Xray：'
    /usr/local/x-ui/bin/xray-linux-amd64 version 2>/dev/null | head -n 3 || true
  fi
}

cmd_doctor() {
  need_root
  local failed=0 warned=0 menu_file db='/etc/x-ui/x-ui.db'

  echo -e "${BLUE}================================================${PLAIN}"
  echo -e "${GREEN}  3X-UI 真限速 V1 · 一键体检${PLAIN}"
  echo -e "${BLUE}================================================${PLAIN}"

  if [[ "$(arch_name)" == 'amd64' ]]; then
    log "架构支持：$(uname -m)"
  else
    warn "当前架构尚未纳入 V1 发布：$(uname -m)"
    failed=1
  fi

  if [[ -x /usr/local/x-ui/x-ui ]]; then
    log '面板二进制存在。'
  else
    warn '面板二进制缺失：/usr/local/x-ui/x-ui'
    failed=1
  fi

  if [[ -x /usr/local/x-ui/bin/xray-linux-amd64 ]]; then
    log '自定义 Xray 二进制存在。'
    /usr/local/x-ui/bin/xray-linux-amd64 version 2>/dev/null | head -n 3 || true
  else
    warn '自定义 Xray 二进制缺失。'
    failed=1
  fi

  if [[ -f "$MARKER" ]]; then
    log 'REAL_SPEEDLIMIT_V1 构建标记存在。'
    for required in \
      'build=real-client-speed-limit-v1' \
      'xray_commit=05f4c02c8a5ab773a0c8c5bfab79759cced08fe7' \
      'limits=aggregate-per-client-upload-download-mbps'; do
      if grep -Fq "$required" "$MARKER"; then
        log "构建标记匹配：$required"
      else
        warn "构建标记不匹配：$required"
        failed=1
      fi
    done
  else
    warn 'REAL_SPEEDLIMIT_V1 构建标记不存在。'
    failed=1
  fi

  if command -v systemctl >/dev/null 2>&1; then
    if systemctl is-active --quiet x-ui; then
      log 'x-ui 服务：active'
    else
      warn 'x-ui 服务不是 active。最近日志如下：'
      journalctl -u x-ui -n 20 --no-pager 2>/dev/null || true
      failed=1
    fi
  else
    warn '系统没有 systemctl，跳过 systemd 状态检查。'
    warned=1
  fi

  menu_file='/usr/local/x-ui/x-ui.sh'
  [[ -f "$menu_file" ]] || menu_file='/usr/bin/x-ui'
  if [[ -f "$menu_file" ]]; then
    if grep -Fq 'REAL_SPEEDLIMIT_V1_MENU_GUARD' "$menu_file"; then
      log '普通 x-ui 菜单已启用自定义更新保护。'
    else
      warn "菜单缺少限速版更新保护标记：$menu_file"
      failed=1
    fi
    if grep -Eq 'MHSanaei/3x-ui/main/update.sh|MHSanaei/3x-ui/raw/main/x-ui.sh' "$menu_file"; then
      warn '菜单仍存在官方更新逃生口，禁止继续正式限速测试。'
      failed=1
    else
      log '菜单未发现官方更新逃生口。'
    fi
  else
    warn '未找到 x-ui 菜单脚本。'
    failed=1
  fi

  if [[ -f "$db" ]]; then
    log "SQLite 数据库存在：$db"
    if command -v sqlite3 >/dev/null 2>&1; then
      local cols
      cols="$(sqlite3 "$db" "PRAGMA table_info(clients);" 2>/dev/null || true)"
      if echo "$cols" | grep -q 'speed_limit_up_mbps' && echo "$cols" | grep -q 'speed_limit_down_mbps'; then
        log '数据库限速字段已完成迁移。'
      else
        warn '数据库尚未发现上下行限速字段；请确认面板已用当前测试版成功启动过。'
        failed=1
      fi
      local integrity
      integrity="$(sqlite3 "$db" 'PRAGMA integrity_check;' 2>/dev/null || true)"
      if [[ "$integrity" == 'ok' ]]; then
        log 'SQLite integrity_check：ok'
      else
        warn "SQLite 完整性检查结果：${integrity:-无法读取}"
        failed=1
      fi
    else
      warn '未安装 sqlite3，跳过数据库字段/完整性深度检查。'
      warned=1
    fi
  else
    # PostgreSQL installations do not use the default SQLite file.
    if grep -Rqs '^XUI_DB_TYPE=postgres' /etc/default/x-ui /etc/sysconfig/x-ui /etc/conf.d/x-ui 2>/dev/null; then
      info '检测到 PostgreSQL 模式；V1 doctor 当前只做文件/服务/构建检查，不直接读取 PostgreSQL。'
      warned=1
    else
      warn '未找到默认 SQLite 数据库。'
      failed=1
    fi
  fi

  if [[ -f /usr/local/x-ui/bin/config.json ]]; then
    if /usr/local/x-ui/bin/xray-linux-amd64 run -test -config /usr/local/x-ui/bin/config.json >/tmp/xui-speedlimit-xray-test.log 2>&1; then
      log '当前 Xray config.json 语法测试通过。'
    else
      warn '当前 Xray config.json 测试失败：'
      tail -n 20 /tmp/xui-speedlimit-xray-test.log 2>/dev/null || true
      failed=1
    fi
    rm -f /tmp/xui-speedlimit-xray-test.log
  else
    warn '未发现 /usr/local/x-ui/bin/config.json，跳过 Xray 配置测试。'
    warned=1
  fi

  echo
  if [[ $failed -eq 0 ]]; then
    if [[ $warned -eq 0 ]]; then
      log '体检结论：PASS，可以进入 Reality/Vision 实机限速验收。'
    else
      log '体检结论：PASS（有跳过项），可以进入实机测试；建议先处理上面的黄色提示。'
    fi
    return 0
  fi

  warn '体检结论：FAIL。请先修复红/黄项，不要在生产节点上继续测试。'
  return 1
}

cmd_rollback() {
  need_root
  local archive="${1:-}"
  if [[ -z "$archive" ]]; then
    archive="$(find "$BACKUP_ROOT" -maxdepth 1 -type f -name 'speedlimit-backup-*.tar.gz' 2>/dev/null | sort | tail -n 1 || true)"
  fi
  [[ -n "$archive" && -f "$archive" ]] || die '没有找到可用备份。可传入备份文件路径：xui-speedlimit rollback /path/file.tar.gz'

  warn "准备还原：$archive"
  if [[ -t 0 ]]; then
    read -r -p '确认覆盖当前面板文件？输入 YES 继续：' ans
    [[ "$ans" == 'YES' ]] || die '已取消。'
  else
    [[ "${FORCE_ROLLBACK:-0}" == '1' ]] || die '非交互模式回滚需显式设置 FORCE_ROLLBACK=1。'
  fi

  systemctl stop x-ui 2>/dev/null || true
  tar -C / -xzf "$archive"
  systemctl daemon-reload 2>/dev/null || true
  systemctl start x-ui 2>/dev/null || true
  log '文件已还原。请立即检查面板、Xray 和客户端连通性。'
}

show_menu() {
  echo -e "${BLUE}================================================${PLAIN}"
  echo -e "${GREEN}  3X-UI 真限速 V1 · 中文一键管理${PLAIN}"
  echo '  基于 3X-UI v3.7.0 + Xray v26.7.28 改造'
  echo -e "${BLUE}================================================${PLAIN}"
  echo '1. 安装测试版（新 VPS 推荐）'
  echo '2. 更新测试版（自动备份）'
  echo '3. 查看状态'
  echo '4. 一键体检（Doctor）'
  echo '5. 立即备份'
  echo '6. 回滚最近备份'
  echo '0. 退出'
  echo
  read -r -p '请选择 [0-6]：' choice
  case "$choice" in
    1) cmd_install ;;
    2) cmd_update ;;
    3) cmd_status ;;
    4) cmd_doctor ;;
    5) backup_now ;;
    6) cmd_rollback ;;
    0) exit 0 ;;
    *) die '无效选项。' ;;
  esac
}

case "${1:-menu}" in
  install) cmd_install ;;
  update) cmd_update ;;
  status) cmd_status ;;
  doctor) cmd_doctor ;;
  backup) backup_now ;;
  rollback) shift; cmd_rollback "${1:-}" ;;
  menu|'') show_menu ;;
  help|-h|--help)
    echo '用法：xui-speedlimit {install|update|status|doctor|backup|rollback|menu}'
    ;;
  *) die "未知命令：${1}" ;;
esac
