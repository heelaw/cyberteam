#!/usr/bin/env python3
"""
CyberTeam V4 - Git 命令封装
实现 Git Worktree 的创建、提交、合并、清理
"""

import subprocess
from pathlib import Path
from typing import Optional


class GitWorktreeError(Exception):
    """Git Worktree 操作异常"""
    pass


def _run_git(cmd: list, cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """执行 git 命令"""
    result = subprocess.run(
        ["git"] + cmd,
        capture_output=True,
        text=True,
        cwd=cwd or Path.cwd(),
        check=False
    )
    if check and result.returncode != 0:
        raise GitWorktreeError(f"Git command failed: {' '.join(cmd)}\n{result.stderr}")
    return result


def is_worktree_path(worktree_path: Path) -> bool:
    """检查路径是否为 worktree"""
    result = _run_git(["worktree", "list", "--porcelain"], check=False)
    if result.returncode != 0:
        return False

    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            wt_path = line[9:].strip()
            if Path(wt_path).resolve() == worktree_path.resolve():
                return True
    return False


def create_worktree(
    repo_root: Path,
    worktree_path: Path,
    branch: str,
    base_ref: str = "HEAD"
) -> None:
    """
    创建 Git Worktree

    Args:
        repo_root: 仓库根目录
        worktree_path: worktree 路径
        branch: 新分支名
        base_ref: 基准引用 (默认 HEAD)
    """
    # 确保仓库根目录是 git 仓库
    result = _run_git(["rev-parse", "--is-inside-work-tree"], cwd=repo_root, check=False)
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise GitWorktreeError(f"Not a git repository: {repo_root}")

    # 创建 worktree (自动创建分支)
    result = _run_git(
        ["worktree", "add", "-b", branch, str(worktree_path), base_ref],
        cwd=repo_root,
        check=False
    )

    if result.returncode != 0:
        # 可能分支已存在，尝试检出
        if "already exists" in result.stderr:
            raise GitWorktreeError(f"Branch already exists: {branch}")
        raise GitWorktreeError(f"Failed to create worktree: {result.stderr}")

    return None


def remove_worktree(repo_root: Path, worktree_path: Path, force: bool = True) -> None:
    """
    删除 Git Worktree

    Args:
        repo_root: 仓库根目录
        worktree_path: worktree 路径
        force: 是否强制删除
    """
    cmd = ["worktree", "remove", str(worktree_path)]
    if force:
        cmd.append("--force")

    result = _run_git(cmd, cwd=repo_root, check=False)
    if result.returncode != 0:
        raise GitWorktreeError(f"Failed to remove worktree: {result.stderr}")


def delete_branch(repo_root: Path, branch: str, force: bool = True) -> None:
    """
    删除分支

    Args:
        repo_root: 仓库根目录
        branch: 分支名
        force: 是否强制删除
    """
    cmd = ["branch", "-D" if force else "-d", branch]
    result = _run_git(cmd, cwd=repo_root, check=False)
    if result.returncode != 0:
        raise GitWorktreeError(f"Failed to delete branch: {result.stderr}")


def commit_all(worktree_path: Path, message: str) -> str:
    """
    提交所有更改

    Args:
        worktree_path: worktree 路径
        message: 提交信息

    Returns:
        提交 hash
    """
    # git add -A
    _run_git(["add", "-A"], cwd=worktree_path, check=False)

    # 检查是否有更改
    result = _run_git(["status", "--porcelain"], cwd=worktree_path, check=False)
    if not result.stdout.strip():
        return ""  # 没有更改

    # git commit
    _run_git(["commit", "-m", message], cwd=worktree_path)

    # 获取 commit hash
    result = _run_git(["rev-parse", "HEAD"], cwd=worktree_path)
    return result.stdout.strip()


def merge_branch(repo_root: Path, branch: str, target: str = "main", no_ff: bool = True) -> None:
    """
    将分支合并到目标分支

    Args:
        repo_root: 仓库根目录
        branch: 要合并的分支
        target: 目标分支
        no_ff: 是否禁用 fast-forward
    """
    # 切换到目标分支
    _run_git(["checkout", target], cwd=repo_root)

    # 合并
    cmd = ["merge"]
    if no_ff:
        cmd.append("--no-ff")
    cmd.append(branch)

    result = _run_git(cmd, cwd=repo_root, check=False)
    if result.returncode != 0:
        raise GitWorktreeError(f"Failed to merge branch: {result.stderr}")


def get_current_branch(worktree_path: Path) -> str:
    """获取当前分支名"""
    result = _run_git(["branch", "--show-current"], cwd=worktree_path)
    return result.stdout.strip()


def list_worktrees(repo_root: Path) -> list:
    """列出所有 worktree"""
    result = _run_git(["worktree", "list", "--porcelain"], cwd=repo_root)
    worktrees = []
    current = {}

    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line[9:].strip()}
        elif line.startswith("branch "):
            current["branch"] = line[7:].strip()
        elif line.startswith("HEAD "):
            current["head"] = line[5:].strip()

    if current:
        worktrees.append(current)

    return worktrees


def fetch_all(repo_root: Path) -> None:
    """fetch 所有远程"""
    _run_git(["fetch", "--all"], cwd=repo_root, check=False)


def get_worktree_info(repo_root: Path, worktree_path: Path) -> dict:
    """获取 worktree 详细信息"""
    branch = get_current_branch(worktree_path)
    result = _run_git(["status", "--porcelain"], cwd=worktree_path, check=False)

    return {
        "path": str(worktree_path),
        "branch": branch,
        "is_dirty": bool(result.stdout.strip()),
        "has_changes": bool(result.stdout.strip())
    }


if __name__ == "__main__":
    # 测试
    print("Git Worktree 模块测试")
    print("=" * 50)

    # 列出 worktrees
    repo = Path(__file__).parent.parent
    try:
        trees = list_worktrees(repo)
        print(f"\n当前仓库: {repo}")
        print(f"Worktree 数量: {len(trees)}")
        for wt in trees:
            print(f"  - {wt}")
    except GitWorktreeError as e:
        print(f"错误: {e}")
