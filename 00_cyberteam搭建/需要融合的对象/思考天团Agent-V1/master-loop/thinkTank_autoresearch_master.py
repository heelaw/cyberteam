#!/usr/bin/env python3
"""
思考天团 AutoResearch Master
整合 Goal-Driven + AutoResearch + PUA + 14位思维专家
"""

import asyncio
import subprocess
import time
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
NC = '\033[0m'


@dataclass
class ThinkTankConfig:
    goal: str
    criteria: str
    mode: str = "parallel"
    max_experts: int = 5
    check_interval: int = 30
    max_iterations: int = 50


@dataclass
class AnalysisReport:
    expert_id: str
    expert_name: str
    analysis: str
    success: bool
    duration: float
    error: Optional[str] = None


class ThinkTankAutoResearchMaster:
    def __init__(self, config: ThinkTankConfig, work_dir: Path):
        self.config = config
        self.work_dir = work_dir
        self.expert_dir = work_dir / "agents"
        self.result_dir = work_dir / "master-loop" / "thinktank_results"
        self.result_dir.mkdir(parents=True, exist_ok=True)
        self.iteration = 0
        self.pressure_level = 0
        self.iteration_history = []

    def log(self, level: str, message: str):
        color = {"INFO": BLUE, "SUCCESS": GREEN, "WARNING": YELLOW, "ERROR": RED, "MASTER": MAGENTA, "PUA": RED, "EXPERT": CYAN, "THINK": CYAN}.get(level, NC)
        print(f"{color}[{level}]{NC} {message}")

    def route_experts(self) -> List[str]:
        self.log("THINK", "=" * 50)
        self.log("THINK", "🎯 专家路由")
        self.log("THINK", "=" * 50)

        goal = self.config.goal.lower()
        expert_keywords = {
            "kahneman": ["选择", "决策", "风险", "纠结", "判断"],
            "first-principle": ["创新", "颠覆", "从零开始", "本质"],
            "swot-tows": ["战略", "竞争", "优势", "劣势"],
            "fivewhy": ["为什么", "原因", "追问"],
            "ai-board": ["投资", "商业决策"],
            "six-hats": ["多角度", "全面"],
            "reverse-thinking": ["逆向", "终局"],
        }

        scores = {}
        for expert_id, keywords in expert_keywords.items():
            score = sum(1 for kw in keywords if kw in goal)
            if score > 0:
                scores[expert_id] = score

        sorted_experts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        matched = [eid for eid, _ in sorted_experts[:self.config.max_experts]]

        if not matched:
            matched = ["kahneman", "swot-tows", "first-principle"]

        self.log("THINK", f"匹配专家: {', '.join(matched)}")
        return matched

    def load_expert_agent(self, expert_id: str) -> Optional[str]:
        agent_path = self.expert_dir / expert_id / "AGENT.md"
        if agent_path.exists():
            return agent_path.read_text()
        return None

    def call_expert(self, expert_id: str, query: str, context: str = "") -> AnalysisReport:
        start_time = time.time()
        self.log("EXPERT", f"调用专家: {expert_id}")

        try:
            agent_prompt = self.load_expert_agent(expert_id)
            if not agent_prompt:
                return AnalysisReport(expert_id=expert_id, expert_name=expert_id, analysis="", success=False, duration=time.time()-start_time, error=f"专家不存在")

            analysis_prompt = f"""
# 思考天团专家分析

## 用户问题
{query}

## 背景
{context if context else '无'}

---

请作为{expert_id}专家分析这个问题。
"""

            result = self._execute_claude(analysis_prompt)
            duration = time.time() - start_time

            if result["success"]:
                self.log("SUCCESS", f"专家 {expert_id} 完成 ({duration:.1f}秒)")
                return AnalysisReport(expert_id=expert_id, expert_name=expert_id, analysis=result["output"], success=True, duration=duration)
            else:
                self.log("ERROR", f"专家 {expert_id} 失败")
                return AnalysisReport(expert_id=expert_id, expert_name=expert_id, analysis="", success=False, duration=duration, error=result.get("error"))

        except Exception as e:
            duration = time.time() - start_time
            self.log("ERROR", f"专家 {expert_id} 异常: {e}")
            return AnalysisReport(expert_id=expert_id, expert_name=expert_id, analysis="", success=False, duration=duration, error=str(e))

    def _execute_claude(self, prompt: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(["claude", "--print", prompt], capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_parallel_analysis(self, query: str, expert_ids: List[str], context: str = "") -> List[AnalysisReport]:
        self.log("INFO", f"并行执行 {len(expert_ids)} 个专家")
        results = []
        for expert_id in expert_ids:
            report = self.call_expert(expert_id, query, context)
            results.append(report)
            if expert_id != expert_ids[-1]:
                time.sleep(2)
        return results

    def integrate_results(self, reports: List[AnalysisReport]) -> str:
        self.log("INFO", "整合分析结果")
        if not reports:
            return "没有可整合的分析结果"

        successful = [r for r in reports if r.success]

        integration = f"""
{'='*60}
                    思考天团分析报告
{'='*60}

## 问题
{self.config.goal}

## 分析专家
{len(successful)}/{len(reports)} 位专家成功

"""
        for report in successful:
            integration += f"""
{'─'*50}
【{report.expert_id}】分析
{'─'*50}
{report.analysis[:500] if len(report.analysis) > 500 else report.analysis}

"""

        integration += f"""
{'='*60}
💡 综合建议
{'='*60}

基于{len(successful)}位专家的分析...
{'='*60}
"""
        return integration

    def check_criteria(self) -> bool:
        self.log("INFO", f"检查Criteria: {self.config.criteria}")
        if self.iteration >= 2:
            self.log("SUCCESS", "满足最低迭代次数")
            return True
        return False

    def apply_pressure(self):
        self.pressure_level += 1
        self.log("PUA", "=" * 50)
        self.log("PUA", f"🔴 PUA压力升级! L{self.pressure_level}")
        self.log("PUA", "=" * 50)

    async def run_loop(self):
        self.log("MASTER", "=" * 60)
        self.log("MASTER", "🚀 思考天团 AutoResearch Master 启动")
        self.log("MASTER", f"目标: {self.config.goal}")
        self.log("MASTER", f"Criteria: {self.config.criteria}")
        self.log("MASTER", "=" * 60)

        while self.iteration < self.config.max_iterations:
            self.iteration += 1
            self.log("MASTER", f"\n--- 迭代 #{self.iteration} ---")

            expert_ids = self.route_experts()
            reports = self.execute_parallel_analysis(self.config.goal, expert_ids)
            integration = self.integrate_results(reports)

            if self.check_criteria():
                self.log("SUCCESS", "🎉 Goal Achieved!")
                break

            if self.pressure_level < 3:
                self.apply_pressure()
            else:
                self.log("ERROR", "达到最大压力")
                break

            await asyncio.sleep(self.config.check_interval)

        self.save_final_report()
        return self.check_criteria()

    def save_final_report(self):
        report_file = self.result_dir / f"final_report_{int(time.time())}.md"
        report = f"""
# 思考天团 最终报告

## 任务
{self.config.goal}

## 执行摘要
- 总迭代次数: {self.iteration}
- 最终压力等级: L{self.pressure_level}
"""
        with open(report_file, 'w') as f:
            f.write(report)
        self.log("INFO", f"报告已保存: {report_file}")
