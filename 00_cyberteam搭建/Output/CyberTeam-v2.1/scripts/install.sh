#!/usr/bin/env bash
#
# cyberteam-install.sh -- CyberTeam v2.1 安装脚本
#
# 将 CyberTeam Agents 和 Skills 安装到本地 AI 编程工具中
#
# 使用方法:
#   ./scripts/install.sh [--tool <name>] [--interactive] [--no-interactive] [--parallel] [--jobs N] [--help]
#
# 支持的工具:
#   claude-code    -- 安装到 ~/.claude/agents/
#   copilot        -- 安装到 ~/.github/agents/ 和 ~/.copilot/agents/
#   antigravity    -- 安装到 ~/.gemini/antigravity/skills/
#   gemini-cli     -- 安装扩展到 ~/.gemini/extensions/cyberteam/
#   opencode       -- 安装到 .opencode/agent/ (项目级)
#   cursor         -- 安装到 .cursor/rules/ (项目级)
#   aider          -- 安装 CONVENTIONS.md (项目级)
#   windsurf       -- 安装 .windsurfrules (项目级)
#   openclaw       -- 安装到 ~/.openclaw/cyberteam/
#   qwen           -- 安装到 ~/.qwen/agents/ 或 .qwen/agents/
#   all            -- 安装所有检测到的工具 (默认)
#
# 参数:
#   --tool <name>      仅安装指定工具
#   --interactive      显示交互式选择器 (终端模式下默认)
#   --no-interactive   跳过交互式选择器，安装所有检测到的工具
#   --parallel         并行安装各工具
#   --jobs N           并行任务数 (默认: nproc 或 4)
#   --help             显示帮助信息
#
# 平台支持:
#   Linux, macOS (需要 bash 3.2+), Windows Git Bash / WSL

set -euo pipefail

# ============================================================================
# 颜色定义 (仅在终端支持颜色时启用)
# ============================================================================
if [[ -t 1 && -z "${NO_COLOR:-}" && "${TERM:-}" != "dumb" ]]; then
  C_GREEN=$'\033[0;32m'
  C_YELLOW=$'\033[1;33m'
  C_RED=$'\033[0;31m'
  C_CYAN=$'\033[0;36m'
  C_BOLD=$'\033[1m'
  C_DIM=$'\033[2m'
  C_RESET=$'\033[0m'
else
  C_GREEN=''; C_YELLOW=''; C_RED=''; C_CYAN=''; C_BOLD=''; C_DIM=''; C_RESET=''
fi

ok()     { printf "${C_GREEN}[OK]${C_RESET}  %s\n" "$*"; }
warn()   { printf "${C_YELLOW}[!!]${C_RESET}  %s\n" "$*"; }
err()    { printf "${C_RED}[ERR]${C_RESET} %s\n" "$*" >&2; }
header() { printf "\n${C_BOLD}%s${C_RESET}\n" "$*"; }
dim()    { printf "${C_DIM}%s${C_RESET}\n" "$*"; }

# 进度条: [=======>    ] 3/8
progress_bar() {
  local current="$1" total="$2" width="${3:-20}" i filled empty
  (( total > 0 )) || return
  filled=$(( width * current / total ))
  empty=$(( width - filled ))
  printf "\r  ["
  for (( i=0; i<filled; i++ )); do printf "="; done
  if (( filled < width )); then printf ">"; (( empty-- )); fi
  for (( i=0; i<empty; i++ )); do printf " "; done
  printf "] %s/%s" "$current" "$total"
  [[ -t 1 ]] || printf "\n"
}

# ============================================================================
# 路径定义
# ============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
AGENTS_DIR="$PROJECT_ROOT/agents"
SKILLS_DIR="$PROJECT_ROOT/skills"
WORKFLOWS_DIR="$PROJECT_ROOT/workflows"
INTEGRATIONS="$PROJECT_ROOT/integrations"

ALL_TOOLS=(claude-code copilot antigravity gemini-cli opencode openclaw cursor aider windsurf qwen)

# ============================================================================
# 使用说明
# ============================================================================
usage() {
  sed -n '3,35p' "$0" | sed 's/^# \{0,1\}//'
  exit 0
}

# 默认并行任务数
parallel_jobs_default() {
  local n
  n=$(nproc 2>/dev/null) && [[ -n "$n" ]] && echo "$n" && return
  n=$(sysctl -n hw.ncpu 2>/dev/null) && [[ -n "$n" ]] && echo "$n" && return
  echo 4
}

# ============================================================================
# 预检
# ============================================================================
check_dependencies() {
  echo "检查依赖..."

  # 检查 Python 3
  if ! command -v python3 >/dev/null 2>&1; then
    err "需要 Python 3"
    exit 1
  fi

  ok "依赖检查通过"
}

# ============================================================================
# 工具检测
# ============================================================================
detect_claude_code()  { [[ -d "${HOME}/.claude" ]]; }
detect_copilot()      { command -v code >/dev/null 2>&1 || [[ -d "${HOME}/.github" || -d "${HOME}/.copilot" ]]; }
detect_antigravity()  { [[ -d "${HOME}/.gemini/antigravity/skills" ]]; }
detect_gemini_cli()   { command -v gemini >/dev/null 2>&1 || [[ -d "${HOME}/.gemini" ]]; }
detect_cursor()       { command -v cursor >/dev/null 2>&1 || [[ -d "${HOME}/.cursor" ]]; }
detect_opencode()     { command -v opencode >/dev/null 2>&1 || [[ -d "${HOME}/.config/opencode" ]]; }
detect_aider()        { command -v aider >/dev/null 2>&1; }
detect_openclaw()     { command -v openclaw >/dev/null 2>&1 || [[ -d "${HOME}/.openclaw" ]]; }
detect_windsurf()     { command -v windsurf >/dev/null 2>&1 || [[ -d "${HOME}/.codeium" ]]; }
detect_qwen()         { command -v qwen >/dev/null 2>&1 || [[ -d "${HOME}/.qwen" ]]; }

is_detected() {
  case "$1" in
    claude-code) detect_claude_code ;;
    copilot)     detect_copilot     ;;
    antigravity) detect_antigravity ;;
    gemini-cli)  detect_gemini_cli ;;
    opencode)    detect_opencode    ;;
    openclaw)    detect_openclaw    ;;
    cursor)      detect_cursor     ;;
    aider)       detect_aider      ;;
    windsurf)    detect_windsurf   ;;
    qwen)        detect_qwen       ;;
    *)           return 1 ;;
  esac
}

# 工具标签
tool_label() {
  case "$1" in
    claude-code)  printf "%-14s  %s" "Claude Code"  "(~/.claude/agents)"      ;;
    copilot)      printf "%-14s  %s" "Copilot"      "(~/.github + ~/.copilot)" ;;
    antigravity) printf "%-14s  %s" "Antigravity"  "(~/.gemini/antigravity)" ;;
    gemini-cli)  printf "%-14s  %s" "Gemini CLI"   "(gemini extension)"      ;;
    opencode)    printf "%-14s  %s" "OpenCode"     "(.opencode/agents)"      ;;
    openclaw)    printf "%-14s  %s" "OpenClaw"     "(~/.openclaw)"           ;;
    cursor)      printf "%-14s  %s" "Cursor"       "(.cursor/rules)"         ;;
    aider)       printf "%-14s  %s" "Aider"        "(CONVENTIONS.md)"         ;;
    windsurf)    printf "%-14s  %s" "Windsurf"    "(.windsurfrules)"         ;;
    qwen)        printf "%-14s  %s" "Qwen Code"    "(~/.qwen/agents)"          ;;
  esac
}

# ============================================================================
# 交互式选择器
# ============================================================================
interactive_select() {
  declare -a selected=()
  declare -a detected_map=()

  local t
  for t in "${ALL_TOOLS[@]}"; do
    if is_detected "$t" 2>/dev/null; then
      selected+=(1); detected_map+=(1)
    else
      selected+=(0); detected_map+=(0)
    fi
  done

  while true; do
    printf "\n"
    printf "  ====================================================\n"
    printf "  ${C_BOLD}  CyberTeam v2.1 -- 工具安装器${C_RESET}\n"
    printf "  ====================================================\n"
    printf "\n"
    printf "  ${C_DIM}系统扫描:  [*] = 在本机检测到${C_RESET}\n"
    printf "\n"

    local i=0
    for t in "${ALL_TOOLS[@]}"; do
      local num=$(( i + 1 ))
      local label
      label="$(tool_label "$t")"
      local dot chk
      if [[ "${detected_map[$i]}" == "1" ]]; then
        dot="${C_GREEN}[*]${C_RESET}"
      else
        dot="${C_DIM}[ ]${C_RESET}"
      fi
      if [[ "${selected[$i]}" == "1" ]]; then
        chk="${C_GREEN}[x]${C_RESET}"
      else
        chk="${C_DIM}[ ]${C_RESET}"
      fi
      printf "  %s  %s)  %s  %s\n" "$chk" "$num" "$dot" "$label"
      (( i++ )) || true
    done

    printf "\n"
    printf "  ------------------------------------------------\n"
    printf "  ${C_CYAN}[1-%s]${C_RESET} 切换   ${C_CYAN}[a]${C_RESET} 全选   ${C_CYAN}[n]${C_RESET} 全不选   ${C_CYAN}[d]${C_RESET} 检测到的\n" "${#ALL_TOOLS[@]}"
    printf "  ${C_GREEN}[Enter]${C_RESET} 安装   ${C_RED}[q]${C_RESET} 退出\n"
    printf "\n"
    printf "  >> "
    read -r input </dev/tty

    case "$input" in
      q|Q)
        printf "\n"; ok "已取消."; exit 0 ;;
      a|A)
        for (( j=0; j<${#ALL_TOOLS[@]}; j++ )); do selected[$j]=1; done ;;
      n|N)
        for (( j=0; j<${#ALL_TOOLS[@]}; j++ )); do selected[$j]=0; done ;;
      d|D)
        for (( j=0; j<${#ALL_TOOLS[@]}; j++ )); do selected[$j]="${detected_map[$j]}"; done ;;
      "")
        local any=false
        for s in "${selected[@]}"; do [[ "$s" == "1" ]] && any=true && break; done
        if $any; then
          break
        else
          printf "  ${C_YELLOW}未选择任何工具 -- 请选择或按 q 退出.${C_RESET}\n"
          sleep 1
        fi ;;
      *)
        local toggled=false
        for num in $input; do
          if [[ "$num" =~ ^[0-9]+$ ]]; then
            local idx=$(( num - 1 ))
            if (( idx >= 0 && idx < ${#ALL_TOOLS[@]} )); then
              if [[ "${selected[$idx]}" == "1" ]]; then
                selected[$idx]=0
              else
                selected[$idx]=1
              fi
              toggled=true
            fi
          fi
        done
        if ! $toggled; then
          printf "  ${C_RED}无效输入. 请输入 1-%s 之间的数字.${C_RESET}\n" "${#ALL_TOOLS[@]}"
          sleep 1
        fi ;;
    esac

    local lines=$(( ${#ALL_TOOLS[@]} + 14 ))
    local l
    for (( l=0; l<lines; l++ )); do printf '\033[1A\033[2K'; done
  done

  SELECTED_TOOLS=()
  local i=0
  for t in "${ALL_TOOLS[@]}"; do
    [[ "${selected[$i]}" == "1" ]] && SELECTED_TOOLS+=("$t")
    (( i++ )) || true
  done
}

# ============================================================================
# 安装器函数
# ============================================================================

install_claude_code() {
  local dest="${HOME}/.claude/agents"
  local count=0
  mkdir -p "$dest"

  if [[ -d "$AGENTS_DIR" ]]; then
    while IFS= read -r f; do
      cp "$f" "$dest/"
      (( count++ )) || true
    done < <(find "$AGENTS_DIR" -name "*.md" -type f -print0)
  fi

  ok "Claude Code: $count agents -> $dest"
}

install_copilot() {
  local dest_github="${HOME}/.github/agents"
  local dest_copilot="${HOME}/.copilot/agents"
  local count=0
  mkdir -p "$dest_github" "$dest_copilot"

  if [[ -d "$AGENTS_DIR" ]]; then
    while IFS= read -r f; do
      cp "$f" "$dest_github/"
      cp "$f" "$dest_copilot/"
      (( count++ )) || true
    done < <(find "$AGENTS_DIR" -name "*.md" -type f -print0)
  fi

  ok "Copilot: $count agents -> $dest_github"
}

install_antigravity() {
  local src="$SKILLS_DIR"
  local dest="${HOME}/.gemini/antigravity/skills/cyberteam"
  local count=0

  [[ -d "$src" ]] || { err "skills/ 目录不存在"; return 1; }
  mkdir -p "$dest"

  local d
  while IFS= read -r -d '' d; do
    local name; name="$(basename "$d")"
    mkdir -p "$dest/$name"
    cp "$d/SKILL.md" "$dest/$name/SKILL.md" 2>/dev/null || cp "$d"/*.md "$dest/$name/" 2>/dev/null || true
    (( count++ )) || true
  done < <(find "$src" -mindepth 1 -maxdepth 1 -type d -print0)

  ok "Antigravity: $count skills -> $dest"
}

install_gemini_cli() {
  local dest="${HOME}/.gemini/extensions/cyberteam"
  mkdir -p "$dest/skills"

  # 复制 skills
  local count=0
  if [[ -d "$SKILLS_DIR" ]]; then
    local d
    while IFS= read -r -d '' d; do
      local name; name="$(basename "$d")"
      mkdir -p "$dest/skills/$name"
      cp "$d"/*.md "$dest/skills/$name/" 2>/dev/null || true
      (( count++ )) || true
    done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d -print0)
  fi

  ok "Gemini CLI: $count skills -> $dest"
}

install_opencode() {
  local src="$AGENTS_DIR"
  local dest="${PWD}/.opencode/agents"
  local count=0
  [[ -d "$src" ]] || { err "agents/ 目录不存在"; return 1; }
  mkdir -p "$dest"

  while IFS= read -r -d '' f; do
    cp "$f" "$dest/"; (( count++ )) || true
  done < <(find "$src" -maxdepth 1 -name "*.md" -print0)

  ok "OpenCode: $count agents -> $dest"
  warn "OpenCode: 项目级安装. 请在项目根目录运行."
}

install_openclaw() {
  local src="$AGENTS_DIR"
  local dest="${HOME}/.openclaw/cyberteam"
  local count=0
  [[ -d "$src" ]] || { err "agents/ 目录不存在"; return 1; }
  mkdir -p "$dest"

  local d
  while IFS= read -r -d '' d; do
    local name; name="$(basename "$d")"
    mkdir -p "$dest/$name"
    cp "$d/SOUL.md" "$dest/$name/SOUL.md" 2>/dev/null || true
    cp "$d/AGENTS.md" "$dest/$name/AGENTS.md" 2>/dev/null || true
    cp "$d/IDENTITY.md" "$dest/$name/IDENTITY.md" 2>/dev/null || true
    (( count++ )) || true
  done < <(find "$src" -mindepth 1 -maxdepth 1 -type d -print0)

  ok "OpenClaw: $count workspaces -> $dest"
}

install_cursor() {
  local src="$AGENTS_DIR"
  local dest="${PWD}/.cursor/rules"
  local count=0
  [[ -d "$src" ]] || { err "agents/ 目录不存在"; return 1; }
  mkdir -p "$dest"

  while IFS= read -r -d '' f; do
    local name; name="$(basename "$f" .md)"
    cp "$f" "$dest/${name}.mdc"; (( count++ )) || true
  done < <(find "$src" -maxdepth 1 -name "*.md" -print0)

  ok "Cursor: $count rules -> $dest"
  warn "Cursor: 项目级安装. 请在项目根目录运行."
}

install_aider() {
  local dest="${PWD}/CONVENTIONS.md"
  [[ -d "$AGENTS_DIR" ]] || { err "agents/ 目录不存在"; return 1; }

  {
    echo "# CyberTeam v2.1 -- AI Agent 规范"
    echo ""
    echo "本文件为 Aider 提供完整的 CyberTeam Agent 列表。"
    echo "要激活某个 agent，请在 Aider 会话提示中引用其名称。"
    echo ""
    find "$AGENTS_DIR" -name "*.md" -type f | while IFS= read -r f; do
      echo "---"
      cat "$f"
      echo ""
    done
  } > "$dest"

  ok "Aider: installed -> $dest"
  warn "Aider: 项目级安装. 请在项目根目录运行."
}

install_windsurf() {
  local dest="${PWD}/.windsurfrules"
  [[ -d "$AGENTS_DIR" ]] || { err "agents/ 目录不存在"; return 1; }

  {
    echo "# CyberTeam v2.1 -- AI Agent 规则"
    echo ""
    echo "CyberTeam Agent 完整列表。激活某个 agent 时，在 Windsurf 对话中引用其名称。"
    echo ""
    find "$AGENTS_DIR" -name "*.md" -type f | while IFS= read -r f; do
      echo "================================================================================"
      cat "$f"
      echo ""
    done
  } > "$dest"

  ok "Windsurf: installed -> $dest"
  warn "Windsurf: 项目级安装. 请在项目根目录运行."
}

install_qwen() {
  local src="$AGENTS_DIR"
  local dest="${PWD}/.qwen/agents"
  local count=0

  [[ -d "$src" ]] || { err "agents/ 目录不存在"; return 1; }
  mkdir -p "$dest"

  while IFS= read -r -d '' f; do
    cp "$f" "$dest/"; (( count++ )) || true
  done < <(find "$src" -maxdepth 1 -name "*.md" -print0)

  ok "Qwen Code: $count agents -> $dest"
  warn "Qwen Code: 项目级安装. 请在项目根目录运行."
}

install_tool() {
  case "$1" in
    claude-code)  install_claude_code  ;;
    copilot)      install_copilot      ;;
    antigravity)  install_antigravity ;;
    gemini-cli)   install_gemini_cli   ;;
    opencode)     install_opencode     ;;
    openclaw)     install_openclaw     ;;
    cursor)       install_cursor       ;;
    aider)        install_aider        ;;
    windsurf)     install_windsurf     ;;
    qwen)         install_qwen         ;;
  esac
}

# ============================================================================
# 主入口
# ============================================================================
main() {
  local tool="all"
  local interactive_mode="auto"
  local use_parallel=false
  local parallel_jobs
  parallel_jobs="$(parallel_jobs_default)"

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --tool)            tool="${2:?'--tool 需要一个值'}"; shift 2; interactive_mode="no" ;;
      --interactive)     interactive_mode="yes"; shift ;;
      --no-interactive)  interactive_mode="no"; shift ;;
      --parallel)        use_parallel=true; shift ;;
      --jobs)            parallel_jobs="${2:?'--jobs 需要一个值'}"; shift 2 ;;
      --help|-h)         usage ;;
      *)                 err "未知选项: $1"; usage ;;
    esac
  done

  # 预检
  check_dependencies

  # 验证工具名称
  if [[ "$tool" != "all" ]]; then
    local valid=false t
    for t in "${ALL_TOOLS[@]}"; do [[ "$t" == "$tool" ]] && valid=true && break; done
    if ! $valid; then
      err "未知工具 '$tool'. 可用: ${ALL_TOOLS[*]}"
      exit 1
    fi
  fi

  # 决定是否使用交互模式
  local use_interactive=false
  if   [[ "$interactive_mode" == "yes" ]]; then
    use_interactive=true
  elif [[ "$interactive_mode" == "auto" && -t 0 && -t 1 && "$tool" == "all" ]]; then
    use_interactive=true
  fi

  SELECTED_TOOLS=()

  if $use_interactive; then
    interactive_select
  elif [[ "$tool" != "all" ]]; then
    SELECTED_TOOLS=("$tool")
  else
    # 非交互模式: 自动检测
    header "CyberTeam v2.1 -- 扫描已安装的工具..."
    printf "\n"
    local t
    for t in "${ALL_TOOLS[@]}"; do
      if is_detected "$t" 2>/dev/null; then
        SELECTED_TOOLS+=("$t")
        printf "  ${C_GREEN}[*]${C_RESET}  %s  ${C_DIM}已检测${C_RESET}\n" "$(tool_label "$t")"
      else
        printf "  ${C_DIM}[ ]  %s  未找到${C_RESET}\n" "$(tool_label "$t")"
      fi
    done
  fi

  if [[ ${#SELECTED_TOOLS[@]} -eq 0 ]]; then
    warn "没有选择或检测到任何工具."
    printf "\n"
    dim "  提示: 使用 --tool <name> 强制安装特定工具."
    dim "  可用工具: ${ALL_TOOLS[*]}"
    exit 0
  fi

  # 工作进程模式 (用于并行安装)
  if [[ -n "${CYBERTEAM_INSTALL_WORKER:-}" ]]; then
    for t in "${SELECTED_TOOLS[@]}"; do
      install_tool "$t"
    done
    return 0
  fi

  printf "\n"
  header "CyberTeam v2.1 -- 安装 Agent"
  printf "  项目目录: %s\n" "$PROJECT_ROOT"
  local n_selected=${#SELECTED_TOOLS[@]}
  printf "  安装目标: %s\n" "${SELECTED_TOOLS[*]}"
  if $use_parallel; then
    ok "将并行安装 $n_selected 个工具 (输出可能交错)."
  fi
  printf "\n"

  local installed=0 t i=0
  if $use_parallel; then
    local install_out_dir
    install_out_dir="$(mktemp -d)"
    export CYBERTEAM_INSTALL_OUT_DIR="$install_out_dir"
    export CYBERTEAM_INSTALL_SCRIPT="$SCRIPT_DIR/install.sh"
    printf '%s\n' "${SELECTED_TOOLS[@]}" | xargs -P "$parallel_jobs" -I {} sh -c 'CYBERTEAM_INSTALL_WORKER=1 "$CYBERTEAM_INSTALL_SCRIPT" --tool "{}" --no-interactive > "$CYBERTEAM_INSTALL_OUT_DIR/{}" 2>&1'
    for t in "${SELECTED_TOOLS[@]}"; do
      [[ -f "$install_out_dir/$t" ]] && cat "$install_out_dir/$t"
    done
    rm -rf "$install_out_dir"
    installed=$n_selected
  else
    for t in "${SELECTED_TOOLS[@]}"; do
      (( i++ )) || true
      progress_bar "$i" "$n_selected"
      printf "\n"
      printf "  ${C_DIM}[%s/%s]${C_RESET} %s\n" "$i" "$n_selected" "$t"
      install_tool "$t"
      (( installed++ )) || true
    done
  fi

  # 完成
  printf "\n"
  printf "  ====================================================\n"
  printf "  ${C_GREEN}${C_BOLD}  完成! 已安装 $installed 个工具.${C_RESET}\n"
  printf "  ====================================================\n"
  printf "\n"
  dim "  下一步:"
  dim "    1. 运行: cyberteam init"
  dim "    2. 查看文档: cyberteam docs"
  printf "\n"
}

main "$@"
