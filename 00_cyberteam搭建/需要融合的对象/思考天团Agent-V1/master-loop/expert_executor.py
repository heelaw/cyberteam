#!/usr/bin/env python3
"""
专家执行器 - 调用专家Agent进行分析
"""

import subprocess
import time
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
NC = '\033[0m'


@dataclass
class ExpertResult:
    expert_id: str
    expert_name: str
    analysis: str
    success: bool
    duration: float
    error: Optional[str] = None


class ExpertExecutor:
    def __init__(self, work_dir: Path):
        self.work_dir = work_dir
        self.expert_dir = work_dir / "agents"
        self.result_dir = work_dir / "master-loop" / "expert_results"
        self.result_dir.mkdir(parents=True, exist_ok=True)

    def log(self, level: str, message: str):
        color = {"INFO": BLUE, "SUCCESS": GREEN, "WARNING": YELLOW, "ERROR": RED, "EXPERT": CYAN}.get(level, NC)
        print(f"{color}[{level}]{NC} {message}")

    def load_expert_prompt(self, expert_id: str) -> Optional[str]:
        expert_path = self.expert_dir / expert_id / "AGENT.md"
        if expert_path.exists():
            return expert_path.read_text()
        return None

    def call_expert(self, expert_id: str, query: str, context: str = "") -> ExpertResult:
        start_time = time.time()
        self.log("EXPERT", f"调用专家: {expert_id}")

        try:
            prompt = self.load_expert_prompt(expert_id)
            if not prompt:
                return ExpertResult(expert_id=expert_id, expert_name=expert_id, analysis="", success=False, duration=time.time()-start_time, error=f"专家 {expert_id} 不存在")

            full_prompt = f"""
# 专家任务

## 用户问题
{query}

## 背景信息
{context}

## 专家提示词
{prompt}

请按照专家的框架进行分析。
"""

            result = self._execute_claude_analysis(full_prompt)
            duration = time.time() - start_time

            if result["success"]:
                self.log("SUCCESS", f"专家 {expert_id} 完成 ({duration:.1f}秒)")
                return ExpertResult(expert_id=expert_id, expert_name=expert_id, analysis=result["output"], success=True, duration=duration)
            else:
                self.log("ERROR", f"专家 {expert_id} 失败")
                return ExpertResult(expert_id=expert_id, expert_name=expert_id, analysis="", success=False, duration=duration, error=result["error"])

        except Exception as e:
            duration = time.time() - start_time
            self.log("ERROR", f"专家 {expert_id} 异常: {e}")
            return ExpertResult(expert_id=expert_id, expert_name=expert_id, analysis="", success=False, duration=duration, error=str(e))

    def _execute_claude_analysis(self, prompt: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(["claude", "--print", prompt], capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_parallel(self, query: str, expert_ids: List[str], context: str = "") -> List[ExpertResult]:
        self.log("INFO", f"并行执行 {len(expert_ids)} 个专家分析")
        results = []
        for expert_id in expert_ids:
            result = self.call_expert(expert_id, query, context)
            results.append(result)
            if expert_id != expert_ids[-1]:
                time.sleep(2)
        return results
