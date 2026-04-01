#!/usr/bin/env python3
"""
思考天团 AutoResearch Master v2
整合 Goal-Driven + AutoResearch + PUA + 14位思维专家
"""

import asyncio
import subprocess
import time
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

# 颜色
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
NC = '\033[0m'

# 导入专家注册表
import sys
sys.path.insert(0, str(Path(__file__).parent))
from expert_registry_full import EXPERT_REGISTRY, route_experts, get_expert_info, print_expert_routing


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
    expert_name_cn: str
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
        self.reports: List[AnalysisReport] = []

    def log(self, level: str, message: str):
        color = {
            "INFO": BLUE, "SUCCESS": GREEN, "WARNING": YELLOW, 
            "ERROR": RED, "MASTER": MAGENTA, "PUA": RED, 
            "EXPERT": CYAN, "THINK": CYAN
        }.get(level, NC)
        print(f"{color}[{level}]{NC} {message}")

    def route_experts(self) -> List[str]:
        """路由专家"""
        expert_ids = route_experts(self.config.goal, self.config.max_experts)
        print_expert_routing(self.config.goal, expert_ids)
        return expert_ids

    def load_expert_agent(self, expert_id: str) -> Optional[str]:
        """加载专家Agent定义"""
        agent_path = self.expert_dir / expert_id / "AGENT.md"
        if agent_path.exists():
            return agent_path.read_text()
        return None

    def call_expert(self, expert_id: str) -> AnalysisReport:
        """调用单个专家Agent"""
        start_time = time.time()
        info = get_expert_info(expert_id)
        expert_name = info.get("name", expert_id)
        expert_name_cn = info.get("name_cn", expert_id)

        self.log("EXPERT", f"调用专家: {expert_name_cn} ({expert_id})")

        try:
            agent_prompt = self.load_expert_agent(expert_id)
            if not agent_prompt:
                return AnalysisReport(
                    expert_id=expert_id, expert_name=expert_name, expert_name_cn=expert_name_cn,
                    analysis="", success=False, duration=time.time()-start_time,
                    error=f"专家 {expert_id} 的AGENT.md不存在"
                )

            analysis_prompt = f"""# 思考天团专家分析

## 用户问题
{self.config.goal}

## 你的角色
你是{expert_name}（{expert_name_cn}），{info.get('description', '')}

## 你的专长
- 分类: {info.get('category', '未知')}
- 技能: {', '.join(info.get('skills', []))}

## 分析要求
请从你的专业角度分析这个问题，给出：
1. 问题诊断
2. 关键分析
3. 具体建议

请用中文输出结构化的分析报告。
"""

            result = self._execute_claude(analysis_prompt)
            duration = time.time() - start_time

            if result["success"]:
                self.log("SUCCESS", f"专家 {expert_name_cn} 完成 ({duration:.1f}秒)")
                return AnalysisReport(
                    expert_id=expert_id, expert_name=expert_name, expert_name_cn=expert_name_cn,
                    analysis=result["output"], success=True, duration=duration
                )
            else:
                self.log("ERROR", f"专家 {expert_name_cn} 失败")
                return AnalysisReport(
                    expert_id=expert_id, expert_name=expert_name, expert_name_cn=expert_name_cn,
                    analysis="", success=False, duration=duration, error=result.get("error")
                )

        except Exception as e:
            duration = time.time() - start_time
            self.log("ERROR", f"专家 {expert_name_cn} 异常: {e}")
            return AnalysisReport(
                expert_id=expert_id, expert_name=expert_name, expert_name_cn=expert_name_cn,
                analysis="", success=False, duration=duration, error=str(e)
            )

    def _execute_claude(self, prompt: str) -> Dict[str, Any]:
        """执行Claude分析"""
        try:
            result = subprocess.run(
                ["claude", "--print", prompt],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout (120s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def execute_parallel_analysis(self, expert_ids: List[str]) -> List[AnalysisReport]:
        """并行执行多个专家分析"""
        self.log("INFO", f"\n并行执行 {len(expert_ids)} 个专家分析...")
        results = []
        
        for expert_id in expert_ids:
            report = self.call_expert(expert_id)
            results.append(report)
            self.reports.append(report)
            
            # 间隔2秒避免API限流
            if expert_id != expert_ids[-1]:
                time.sleep(2)
        
        return results

    def integrate_results(self, reports: List[AnalysisReport]) -> str:
        """整合分析结果"""
        self.log("INFO", "\n" + "="*60)
        self.log("INFO", "📊 整合分析结果")
        self.log("INFO", "="*60)

        successful = [r for r in reports if r.success]
        failed = [r for r in reports if not r.success]

        integration = f"""
{'='*70}
                    🤖 思考天团分析报告
{'='*70}

## 用户问题
{self.config.goal}

## 分析专家
{len(successful)}/{len(reports)} 位专家成功分析

"""

        # 详细展示每个专家的分析
        for report in successful:
            integration += f"""
{'─'*70}
【{report.expert_name_cn}】{report.expert_name}
{'─'*70}
{report.analysis}

"""

        # 错误信息
        if failed:
            integration += f"""
{'─'*70}
⚠️ 未成功分析的专家
{'─'*70}
"""
            for report in failed:
                integration += f"• {report.expert_name_cn}: {report.error}\n"

        # 综合建议
        integration += f"""
{'='*70}
                    💡 综合建议
{'='*70}

基于 {len(successful)} 位专家的分析，系统给出以下建议：

"""

        # 提取关键建议
        key_suggestions = []
        for report in successful[:3]:
            # 提取前200字符作为关键点
            lines = report.analysis.split('\n')
            key_line = ""
            for line in lines:
                if line.strip() and len(line.strip()) > 10:
                    key_line = line.strip()
                    break
            if key_line:
                key_suggestions.append(f"【{report.expert_name_cn}】{key_line[:100]}...")

        for suggestion in key_suggestions:
            integration += f"\n{suggestion}"

        integration += f"""

{'='*70}
"""

        return integration

    def check_criteria(self) -> bool:
        """检查是否满足成功标准"""
        self.log("INFO", f"\n检查Criteria: {self.config.criteria}")

        criteria = self.config.criteria

        # 解析"至少N个专家"
        if "至少" in criteria and "专家" in criteria:
            match = re.search(r"至少(\d+)个专家", criteria)
            if match:
                min_experts = int(match.group(1))
                successful = len([r for r in self.reports if r.success])
                if successful >= min_experts:
                    self.log("SUCCESS", f"✓ 满足最低专家数量: {successful} >= {min_experts}")
                    return True
                else:
                    self.log("WARNING", f"专家数量不足: {successful} < {min_experts}")
                    return False

        # 默认：3次迭代认为基本满足
        if self.iteration >= 3:
            self.log("SUCCESS", "✓ 达到最低迭代次数")
            return True

        return False

    def apply_pressure(self):
        """应用PUA压力"""
        self.pressure_level += 1
        
        self.log("PUA", "\n" + "="*60)
        self.log("PUA", "🔴 PUA压力升级!")
        self.log("PUA", f"压力等级: L{self.pressure_level}")
        self.log("PUA", "="*60)

        pressure_actions = {
            1: "💡 换个角度思考问题",
            2: "🔍 搜索更多案例和数据",
            3: "📋 采用更系统的分析框架",
            4: "🚨 必须突破现有思维框架",
            5: "💀 最后的尝试"
        }

        self.log("PUA", f"动作: {pressure_actions.get(self.pressure_level, '继续')}")

    async def run_loop(self):
        """核心循环"""
        self.log("MASTER", "\n" + "="*70)
        self.log("MASTER", "🚀 思考天团 AutoResearch Master 启动")
        self.log("MASTER", "="*70)
        self.log("MASTER", f"目标: {self.config.goal}")
        self.log("MASTER", f"Criteria: {self.config.criteria}")
        self.log("MASTER", f"模式: {self.config.mode} | 最大专家: {self.config.max_experts}")
        self.log("MASTER", "="*70)

        # 主循环
        while self.iteration < self.config.max_iterations:
            self.iteration += 1

            self.log("MASTER", f"\n{'─'*70}")
            self.log("MASTER", f"📍 迭代 #{self.iteration}")
            self.log("MASTER", f"   压力等级: L{self.pressure_level}")
            self.log("MASTER", f"   已有报告: {len([r for r in self.reports if r.success])} 个")
            self.log("MASTER", f"{'─'*70}")

            # Phase 1: 路由专家
            self.log("THINK", "\n[Phase 1] 专家路由")
            expert_ids = self.route_experts()

            # Phase 2: 执行分析
            self.log("THINK", "\n[Phase 2] 专家分析")
            reports = self.execute_parallel_analysis(expert_ids)

            # Phase 3: 整合结果
            self.log("THINK", "\n[Phase 3] 整合结果")
            integration = self.integrate_results(reports)
            print(integration)

            # Phase 4: 检查Criteria
            self.log("THINK", "\n[Phase 4] 验证Criteria")
            criteria_met = self.check_criteria()

            if criteria_met:
                self.log("SUCCESS", "\n" + "="*70)
                self.log("SUCCESS", "🎉 Goal Achieved! 目标达成!")
                self.log("SUCCESS", f"总迭代次数: {self.iteration}")
                self.log("SUCCESS", f"成功分析专家: {len([r for r in self.reports if r.success])} 位")
                self.log("SUCCESS", "="*70)
                break

            # Criteria未满足，准备下一轮
            if self.pressure_level < 4:
                self.apply_pressure()
            else:
                self.log("ERROR", "\n达到最大压力等级，任务无法完成")
                break

            # 等待
            self.log("INFO", f"\n等待 {self.config.check_interval}秒...")
            await asyncio.sleep(self.config.check_interval)

        # 保存最终报告
        self.save_final_report()

        return self.check_criteria()

    def save_final_report(self):
        """保存最终报告"""
        report_file = self.result_dir / f"final_report_{int(time.time())}.md"

        successful = [r for r in self.reports if r.success]

        report = f"""# 思考天团 最终报告

## 任务
{self.config.goal}

## Criteria
{self.config.criteria}

## 执行摘要
- 总迭代次数: {self.iteration}
- 最终压力等级: L{self.pressure_level}
- 成功分析专家: {len(successful)} 位

## 专家分析汇总
"""

        for r in successful:
            report += f"""
### {r.expert_name_cn} ({r.expert_name})
{r.analysis}

"""

        report += """
---
*由思考天团 AutoResearch 系统自动生成*
"""

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        self.log("INFO", f"\n📄 最终报告已保存: {report_file}")
