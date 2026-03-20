#!/bin/zsh
set -euo pipefail

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RUNTIME_BASE="${MAIL_LISTENER_BASE_DIR:-$HOME/.cache/mail-listener}"
RUNTIME_DIR="${MAIL_LISTENER_RUNTIME_DIR:-$RUNTIME_BASE/run}"
LOG_DIR="${MAIL_LISTENER_LOG_DIR:-$RUNTIME_BASE/logs}"
PID_FILE="${MAIL_LISTENER_PID_FILE:-$RUNTIME_DIR/gmail_imap_idle.pid}"
LOG_FILE="${MAIL_LISTENER_LOG_FILE:-$LOG_DIR/gmail_imap_idle.log}"
CTL_STDOUT_FILE="${MAIL_LISTENER_CTL_STDOUT_FILE:-$LOG_DIR/ctl.stdout.log}"
CTL_STDERR_FILE="${MAIL_LISTENER_CTL_STDERR_FILE:-$LOG_DIR/ctl.stderr.log}"

mkdir -p "$RUNTIME_DIR" "$LOG_DIR"

run_module() {
  "$PYTHON_BIN" -m mail_listener "$@"
}

is_running() {
  [[ -f "$PID_FILE" ]] || return 1
  local pid
  pid="$(head -n 1 "$PID_FILE" 2>/dev/null | tr -d '[:space:]')"
  [[ -n "$pid" ]] || return 1
  kill -0 "$pid" 2>/dev/null
}

cmd="${1:-}"
case "$cmd" in
  check)
    run_module --check
    ;;
  start)
    if is_running; then
      echo "mail-listener already running"
      exit 0
    fi
    nohup "$PYTHON_BIN" -m mail_listener >"$CTL_STDOUT_FILE" 2>"$CTL_STDERR_FILE" &
    sleep 1
    if is_running; then
      echo "mail-listener started"
    else
      echo "mail-listener failed to start"
      exit 1
    fi
    ;;
  stop)
    if ! is_running; then
      echo "mail-listener not running"
      exit 0
    fi
    local_pid="$(head -n 1 "$PID_FILE" | tr -d '[:space:]')"
    kill "$local_pid"
    echo "mail-listener stopped"
    ;;
  restart)
    "$0" stop || true
    "$0" start
    ;;
  status)
    if is_running; then
      echo "mail-listener is running"
    else
      echo "mail-listener is not running"
      exit 1
    fi
    ;;
  logs)
    touch "$LOG_FILE"
    tail -f "$LOG_FILE"
    ;;
  *)
    echo "Usage: $0 {check|start|stop|restart|status|logs}"
    exit 1
    ;;
esac
