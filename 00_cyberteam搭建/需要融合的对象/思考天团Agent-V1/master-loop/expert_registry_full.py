#!/usr/bin/env python3
"""
14个思维专家完整注册表
"""

EXPERT_REGISTRY = {
    "kahneman": {
        "name": "Kahneman",
        "name_cn": "卡尼曼",
        "category": "决策",
        "triggers": ["选择", "决策", "风险", "纠结", "判断", "不确定性", "认知偏差", "高薪", "低薪", "offer"],
        "skills": ["认知偏差识别", "噪声评估", "决策辅助", "损失厌恶"],
        "description": "决策心理学专家，帮你识别认知偏差和决策陷阱"
    },
    "first-principle": {
        "name": "FirstPrinciple",
        "name_cn": "第一性原理",
        "category": "创意",
        "triggers": ["创新", "颠覆", "从零开始", "本质", "根本原因", "底层逻辑"],
        "skills": ["本质分析", "假设挑战", "创新重构"],
        "description": "第一性原理专家，从根本重新思考问题"
    },
    "six-hats": {
        "name": "SixHats",
        "name_cn": "六顶思考帽",
        "category": "分析",
        "triggers": ["多角度", "全面思考", "思考帽", "六顶", "各个角度"],
        "skills": ["平行思考", "角度切换", "全面覆盖"],
        "description": "六顶思考帽专家，全面分析问题的各个角度"
    },
    "swot-tows": {
        "name": "SWOTTOWS",
        "name_cn": "SWOT分析",
        "category": "分析",
        "triggers": ["战略", "竞争", "优势", "劣势", "机会", "威胁", "SWOT", "竞争力"],
        "skills": ["SWOT分析", "TOWS策略", "战略规划"],
        "description": "战略分析专家，系统评估内外部环境"
    },
    "fivewhy": {
        "name": "FiveWhy",
        "name_cn": "5Why分析",
        "category": "分析",
        "triggers": ["为什么", "原因", "追问", "溯源", "根因", "深入挖掘"],
        "skills": ["根因分析", "连续追问", "问题溯源"],
        "description": "5Why分析专家，追问根本原因"
    },
    "goldlin": {
        "name": "Goldlin",
        "name_cn": "吉德林法则",
        "category": "分析",
        "triggers": ["定义问题", "聚焦", "核心问题", "关键", "本质"],
        "skills": ["问题定义", "聚焦分析", "本质识别"],
        "description": "吉德林法则专家，帮你聚焦核心问题"
    },
    "grow": {
        "name": "GROW",
        "name_cn": "GROW模型",
        "category": "执行",
        "triggers": ["目标", "路径", "规划", "实现", "步骤", "计划"],
        "skills": ["目标设定", "路径规划", "行动计划"],
        "description": "GROW模型专家，帮你规划实现路径"
    },
    "kiss": {
        "name": "KISS",
        "name_cn": "KISS复盘",
        "category": "管理",
        "triggers": ["复盘", "总结", "回顾", "经验", "教训"],
        "skills": ["经验总结", "改进点识别", "复盘框架"],
        "description": "KISS复盘专家，总结经验教训"
    },
    "mckinsey": {
        "name": "McKinsey",
        "name_cn": "麦肯锡",
        "category": "分析",
        "triggers": ["框架", "方法论", "提炼", "结构化", "逻辑"],
        "skills": ["框架分析", "结构化思维", "信息提炼"],
        "description": "麦肯锡方法专家，用框架结构化分析"
    },
    "ai-board": {
        "name": "AIBoard",
        "name_cn": "AI私董会",
        "category": "决策",
        "triggers": ["投资", "商业决策", "董事会", "风险评估", "回报"],
        "skills": ["投资分析", "商业模式评估", "风险评估"],
        "description": "AI私董会，从投资人视角审视决策"
    },
    "reverse-thinking": {
        "name": "ReverseThinking",
        "name_cn": "逆向思维",
        "category": "创意",
        "triggers": ["终局", "逆向", "预防", "避免", "倒推", "失败"],
        "skills": ["逆向推理", "终局思维", "风险预防"],
        "description": "逆向思维专家，从结果倒推解决方案"
    },
    "five-dimension": {
        "name": "FiveDimension",
        "name_cn": "五维思考",
        "category": "分析",
        "triggers": ["五维", "商业", "市场", "盈利", "竞争", "价值"],
        "skills": ["五维分析", "商业洞察", "市场定位"],
        "description": "五维思考专家，从商业多维度分析"
    },
    "wbs": {
        "name": "WBS",
        "name_cn": "任务分解",
        "category": "执行",
        "triggers": ["任务分解", "执行", "计划", "WBS", "分解", "落地"],
        "skills": ["任务分解", "工作细化", "执行规划"],
        "description": "WBS任务分解专家，帮你拆解可执行的任务"
    },
    "manager-leap": {
        "name": "ManagerLeap",
        "name_cn": "管理者跃升",
        "category": "管理",
        "triggers": ["管理", "领导", "团队", "跃升", "晋升", "职业发展"],
        "skills": ["管理跃升", "领导力", "团队建设"],
        "description": "管理者跃升专家，帮你提升管理能力"
    }
}


def route_experts(query: str, max_experts: int = 5) -> list:
    """
    根据问题路由最匹配的专家
    
    Args:
        query: 用户问题
        max_experts: 最大专家数量
    
    Returns:
        匹配的专家ID列表
    """
    query_lower = query.lower()
    scores = {}

    for expert_id, expert in EXPERT_REGISTRY.items():
        score = 0
        
        # 触发词匹配
        for trigger in expert["triggers"]:
            if trigger.lower() in query_lower:
                score += 10
        
        # 技能匹配
        for skill in expert["skills"]:
            if skill.lower() in query_lower:
                score += 5
        
        # 分类匹配
        category_keywords = {
            "决策": ["选择", "决定", "应该", "还是", "风险", "回报"],
            "分析": ["分析", "评估", "为什么", "原因"],
            "创意": ["创新", "颠覆", "新"],
            "执行": ["实现", "完成", "执行", "计划"],
            "管理": ["团队", "领导", "管理", "发展"]
        }
        for kw in category_keywords.get(expert["category"], []):
            if kw in query_lower:
                score += 3

        if score > 0:
            scores[expert_id] = score

    # 按分数排序
    sorted_experts = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # 取前N个
    matched = [eid for eid, _ in sorted_experts[:max_experts]]
    
    # 如果没有匹配，返回默认专家
    if not matched:
        matched = ["kahneman", "grow", "swot-tows"]
    
    return matched


def get_expert_info(expert_id: str) -> dict:
    """获取专家信息"""
    return EXPERT_REGISTRY.get(expert_id, {})


def print_expert_routing(query: str, matched_experts: list):
    """打印专家路由结果"""
    print("\n" + "="*60)
    print("🎯 专家路由结果")
    print("="*60)
    print(f"问题: {query[:50]}..." if len(query) > 50 else f"问题: {query}")
    print(f"\n匹配到 {len(matched_experts)} 位专家:")
    
    for i, eid in enumerate(matched_experts, 1):
        info = get_expert_info(eid)
        print(f"\n{i}. {info.get('name_cn', eid)} ({info.get('name', eid)})")
        print(f"   分类: {info.get('category', '未知')}")
        print(f"   专长: {info.get('description', '')}")
    
    print("\n" + "="*60)
