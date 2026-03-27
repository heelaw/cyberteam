#!/bin/bash
# CyberTeam Browse CLI - 持久无头浏览器命令行接口
# 用于 QA 测试、站点验证、截图、登录测试

set -e

# ─── 常量 ───────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_DIR="$(dirname "$SCRIPT_DIR")"
SKILL_DIR="$MODULE_DIR"
STATE_DIR="${HOME}/.cyberteam/browse"
STATE_FILE="${STATE_DIR}/state.json"

# ─── 依赖检查 ───────────────────────────────────────────────────
check_deps() {
    if ! command -v bun &> /dev/null; then
        echo "错误: 需要 Bun 运行时" >&2
        echo "安装: curl -fsSL https://bun.sh/install | bash" >&2
        exit 1
    fi

    if ! command -v playwright &> /dev/null && ! bun x playwright --version &> /dev/null; then
        echo "警告: Playwright 未安装" >&2
        echo "安装: bunx playwright install chromium" >&2
    fi
}

# ─── 状态管理 ───────────────────────────────────────────────────
read_state() {
    if [ -f "$STATE_FILE" ]; then
        cat "$STATE_FILE"
    else
        echo "{}"
    fi
}

write_state() {
    mkdir -p "$STATE_DIR"
    cat > "$STATE_FILE"
}

get_port() {
    read_state | grep -o '"port":[0-9]*' | cut -d':' -f2
}

get_token() {
    read_state | grep -o '"token":"[^"]*"' | cut -d'"' -f4
}

is_server_alive() {
    local port="$1"
    local pid="$2"

    # 检查进程
    if [ -n "$pid" ] && ! kill -0 "$pid" 2>/dev/null; then
        return 1
    fi

    # 检查端口
    if [ -n "$port" ]; then
        curl -s --connect-timeout 1 "http://127.0.0.1:$port/health" > /dev/null 2>&1
        return $?
    fi

    return 1
}

# ─── 服务器管理 ─────────────────────────────────────────────────
start_server() {
    echo "[browse] 启动服务器..."

    mkdir -p "$STATE_DIR"

    # 清理旧状态
    rm -f "$STATE_FILE"

    # 启动服务器
    bun run "$SKILL_DIR/src/server.ts" &
    SERVER_PID=$!

    # 等待状态文件
    local timeout=8
    while [ $timeout -gt 0 ]; do
        if [ -f "$STATE_FILE" ]; then
            local port=$(get_port)
            if [ -n "$port" ] && is_server_alive "$port" "$SERVER_PID"; then
                echo "[browse] 服务器运行在端口 $port"
                return 0
            fi
        fi
        sleep 0.5
        timeout=$((timeout - 1))
    done

    echo "错误: 服务器启动失败" >&2
    return 1
}

ensure_server() {
    local state=$(read_state)
    local port=$(echo "$state" | grep -o '"port":[0-9]*' | cut -d':' -f2)
    local pid=$(echo "$state" | grep -o '"pid":[0-9]*' | cut -d':' -f2)
    local token=$(echo "$state" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)

    if [ -z "$port" ] || [ -z "$token" ]; then
        start_server
        return $?
    fi

    if ! is_server_alive "$port" "$pid"; then
        echo "[browse] 服务器无响应，重新启动..."
        start_server
        return $?
    fi

    # 健康检查
    if curl -s "http://127.0.0.1:$port/health" > /dev/null 2>&1; then
        echo "$port:$token"
        return 0
    fi

    start_server
}

# ─── 命令发送 ───────────────────────────────────────────────────
send_command() {
    local port="$1"
    local token="$2"
    shift 2

    local command="$1"
    local args="${@:2}"

    local response=$(curl -s \
        -X POST "http://127.0.0.1:$port/command" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $token" \
        -d "{\"command\":\"$command\",\"args\":[$args]}")

    echo "$response"
}

# ─── CLI 入口 ────────────────────────────────────────────────────
show_help() {
    cat << EOF
CyberTeam Browse - 持久无头浏览器

用法: browse <命令> [参数...]

导航:
  goto <url>       打开URL
  back             后退
  forward          前进
  reload           刷新
  url              打印当前URL

内容:
  text             页面文本
  html [选择器]    HTML内容
  links            所有链接
  forms            表单字段

交互:
  click <选择器>   点击元素
  fill <选择器> <值>  填写输入
  hover <选择器>   悬停
  type <文本>      输入文本
  press <按键>     按键
  scroll [选择器]  滚动

检查:
  js <表达式>      执行JS
  css <选择器> <属性>  CSS值
  attrs <选择器>   元素属性
  is <属性> <选择器>  状态检查
  console [--errors]  控制台
  network          网络请求
  cookies          Cookie

可视化:
  screenshot [路径]  截图
  pdf [路径]       生成PDF
  responsive [前缀]  响应式截图

快照:
  snapshot [-i] [-D] [-a] [-C]
    -i    仅交互元素
    -D    与之前对比
    -a    带注释截图
    -C    光标交互元素

服务器:
  handoff [消息]   用户接管
  resume           恢复AI
  status           健康检查
  stop             关闭
  restart          重启

示例:
  browse goto example.com
  browse snapshot -i
  browse click @e1
  browse screenshot /tmp/shot.png
  browse handoff "请处理验证码"

EOF
}

# ─── 主程序 ────────────────────────────────────────────────────
main() {
    # 检查依赖
    check_deps

    # 无参数显示帮助
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi

    # 解析命令
    local command="$1"
    shift

    case "$command" in
        -h|--help|help)
            show_help
            ;;
        init)
            start_server
            ;;
        *)
            # 确保服务器运行
            local endpoint=$(ensure_server)
            if [ $? -ne 0 ]; then
                echo "错误: 无法启动服务器" >&2
                exit 1
            fi

            local port=$(echo "$endpoint" | cut -d':' -f1)
            local token=$(echo "$endpoint" | cut -d':' -f2)

            # 发送命令
            local args_json=""
            for arg in "$@"; do
                if [ -n "$args_json" ]; then
                    args_json="$args_json,"
                fi
                # 转义引号
                arg="${arg//\"/\\\"}"
                args_json="$args_json\"$arg\""
            done

            send_command "$port" "$token" "$command" $args_json
            ;;
    esac
}

main "$@"
