"""
思维模型加载器

从内部目录加载100个思维模型，
转换为统一的 ThinkingModel 数据结构。
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from .models import ThinkingModel, ModelCategory


class ThinkingLoader:
    """
    思维模型加载器

    从 cyberteam/thinking_models/ 目录加载所有思维模型
    """

    def __init__(self, base_path: Optional[Path] = None):
        if base_path is None:
            # 默认路径：从 engine/thinking/ 往上三级到 cyberteam-v4，再往下一级到 cyberteam/thinking_models/
            # engine/thinking/loader.py -> engine/thinking/ -> engine/ -> cyberteam-v4/ -> cyberteam/thinking_models/
            self.base_path = Path(__file__).parent.parent.parent / "cyberteam" / "thinking_models"
        else:
            self.base_path = Path(base_path)

        self._models: dict[str, ThinkingModel] = {}
        self._keyword_index: dict[str, set[str]] = {}  # 关键词 -> 模型ID集合

    def load_all(self) -> dict[str, ThinkingModel]:
        """加载所有思维模型"""
        self._models.clear()
        self._keyword_index.clear()

        if not self.base_path.exists():
            print(f"[ThinkingLoader] 路径不存在: {self.base_path}")
            return self._models

        # 遍历所有思维模型目录
        for model_dir in self.base_path.iterdir():
            if not model_dir.is_dir():
                continue

            # 跳过非数字开头的目录（如 __pycache__）
            if not re.match(r'^\d+', model_dir.name):
                continue

            # 查找 AGENT.md 文件
            agent_file = model_dir / "AGENT.md"
            if not agent_file.exists():
                continue

            try:
                model = self._parse_agent_file(agent_file, model_dir.name)
                if model:
                    self._models[model.id] = model
                    self._index_keywords(model)
            except Exception as e:
                print(f"[ThinkingLoader] 解析失败 {model_dir.name}: {e}")

        print(f"[ThinkingLoader] 加载了 {len(self._models)} 个思维模型")
        return self._models

    def _parse_agent_file(self, file_path: Path, dir_name: str) -> Optional[ThinkingModel]:
        """解析 AGENT.md 文件"""
        content = file_path.read_text(encoding="utf-8")

        # 提取元数据 JSON（如果存在）
        metadata = self._extract_metadata(content)

        # 提取名称（优先从元数据，其次从表格）
        name = metadata.get("name") or self._extract_table_field(content, "Agent名称") or self._extract_title(content)
        if not name:
            name = self._infer_name_from_dir(dir_name)

        # 提取描述
        description = self._extract_table_field(content, "核心能力") or metadata.get("description", "")

        # 提取触发关键词（优先从元数据，其次从触发词表格）
        trigger_keywords = metadata.get("triggers", []) or self._extract_trigger_words(content)
        if not trigger_keywords:
            trigger_keywords = self._extract_keywords_from_content(content)

        # 确定分类
        category = self._infer_category(name, trigger_keywords, description)

        # 生成 ID
        model_id = metadata.get("id") or self._generate_id(name)

        # 获取优先级
        priority = self._infer_priority(name, trigger_keywords)

        return ThinkingModel(
            id=model_id,
            name=name,
            category=category,
            description=description[:200] if description else "思维分析工具",
            trigger_keywords=trigger_keywords[:10] if trigger_keywords else [],
            input_schema=metadata.get("input_schema", self._get_default_input_schema()),
            output_schema=metadata.get("output_schema", self._get_default_output_schema()),
            priority=priority
        )

    def _extract_metadata(self, content: str) -> dict:
        """提取 JSON 元数据"""
        metadata = {}

        # 查找 JSON 代码块
        json_match = re.search(r'```json\s*({\s*".*?"\s*})\s*```', content, re.DOTALL)
        if json_match:
            try:
                metadata = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        return metadata

    def _extract_table_field(self, content: str, field_name: str) -> Optional[str]:
        """从 Markdown 表格中提取字段"""
        # 查找包含字段名的行
        pattern = rf'\|\s*\*{field_name}\*\s*\|\s*([^|]+)\s*\|'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()

        # 尝试不带星号
        pattern = rf'\|\s*{field_name}\s*\|\s*([^|]+)\s*\|'
        match = re.search(pattern, content)
        if match:
            return match.group(1).strip()

        return None

    def _extract_title(self, content: str) -> Optional[str]:
        """提取标题"""
        # # 标题
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    def _extract_trigger_words(self, content: str) -> list[str]:
        """提取触发词"""
        triggers = []

        # 查找触发词表格
        lines = content.split('\n')
        in_trigger_table = False

        for line in lines:
            if '触发场景' in line or '触发词' in line:
                in_trigger_table = True
                continue

            if in_trigger_table:
                if line.startswith('|') and '---' not in line:
                    # 表格行，提取内容
                    parts = line.split('|')
                    if len(parts) >= 3:
                        trigger = parts[1].strip()
                        if trigger and '触发' not in trigger:
                            triggers.append(trigger)
                elif '---' in line or line.strip() == '':
                    if in_trigger_table and triggers:
                        break

        return triggers

    def _extract_keywords_from_content(self, content: str) -> list[str]:
        """从内容中提取关键词"""
        keywords = []

        # 提取中文词组
        found = re.findall(r'[\u4e00-\u9fff]{2,4}', content)
        keywords.extend(found[:10])

        # 去重
        keywords = list(set(keywords))[:10]
        return keywords

    def _infer_category(self, name: str, keywords: list[str], description: str) -> ModelCategory:
        """推断分类"""
        text = f"{name} {' '.join(keywords)} {description}".lower()

        if any(w in text for w in ["分析", "诊断", "检验", "还原", "偏差", "噪声", "决策"]):
            return ModelCategory.ANALYSIS
        elif any(w in text for w in ["决策", "选择", "判断", "战略", "博弈"]):
            return ModelCategory.DECISION
        elif any(w in text for w in ["创造", "创新", "设计", "发散", "六顶"]):
            return ModelCategory.CREATIVE
        elif any(w in text for w in ["评估", "评审", "检查", "审核", "扫描"]):
            return ModelCategory.EVALUATION
        else:
            return ModelCategory.SYSTEM

    def _infer_priority(self, name: str, keywords: list[str]) -> int:
        """推断优先级"""
        high_priority = ["第一性原理", "六顶思考帽", "SWOT", "TOWS", "5W1H", "二阶思维",
                        "批判性思维", "系统思维", "麦肯锡", "卡尼曼", "博弈论"]
        if any(h in name for h in high_priority):
            return 9
        return 5

    def _generate_id(self, name: str) -> str:
        """生成模型 ID"""
        # 中文名称转拼音/英文的映射
        id_map = {
            "卡尼曼决策专家": "kahneman",
            "第一性原理": "first-principle",
            "第一性原理思维专家": "first-principle",
            "六顶思考帽": "six-hats",
            "六顶思考帽专家": "six-hats",
            "SWOT/TOWS": "swot-tows",
            "SWOT": "swot-tows",
            "TOWS": "swot-tows",
            "5W1H": "fivew1h",
            "临界点": "critical-point",
            "批判性思维专家": "critical-thinking",
            "系统思维专家": "systems-thinking",
            "逆向思维专家": "reverse-thinking",
            "机会成本决策专家": "opportunity-cost",
            "沉没成本谬误专家": "sunk-cost",
            "二阶思维专家": "second-order",
            "博弈论专家": "game-theory",
            "概率思维专家": "probabilistic",
            "贝叶斯专家": "bayesian",
            "帕累托专家": "pareto",
            "麦肯锡分析专家": "mckinsey",
            "波特五力专家": "porters-five-forces",
            "PDCA专家": "pdca",
            "迭代思维专家": "iteration",
            "复利效应专家": "compound-effect",
        }

        if name in id_map:
            return id_map[name]

        # 通用转换：去除"专家"后缀，去除特殊字符，转小写
        clean = name.replace("专家", "").replace("思维", "")
        clean = re.sub(r'[^\w]', '-', clean.lower())
        return clean[:30]

    def _infer_name_from_dir(self, dir_name: str) -> str:
        """从目录名推断名称"""
        # 去掉数字前缀
        name = re.sub(r'^\d+-', '', dir_name)
        # 转换连字符为空格
        name = name.replace('-', ' ')
        # 首字母大写
        return name.title()

    def _index_keywords(self, model: ThinkingModel):
        """建立关键词索引"""
        for kw in model.trigger_keywords:
            kw_lower = kw.lower()
            if kw_lower not in self._keyword_index:
                self._keyword_index[kw_lower] = set()
            self._keyword_index[kw_lower].add(model.id)

    def _get_default_input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "任务描述"},
                "context": {"type": "string", "description": "上下文信息"},
            },
            "required": ["task"]
        }

    def _get_default_output_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "analysis": {"type": "string", "description": "分析结果"},
                "key_findings": {"type": "array", "items": {"type": "string"}},
                "recommendations": {"type": "array", "items": {"type": "string"}},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            }
        }

    def get_model(self, model_id: str) -> Optional[ThinkingModel]:
        """获取指定模型"""
        return self._models.get(model_id)

    def get_all_models(self) -> list[ThinkingModel]:
        """获取所有模型"""
        return list(self._models.values())

    def search_by_keyword(self, keyword: str) -> list[ThinkingModel]:
        """通过关键词搜索模型"""
        keyword_lower = keyword.lower()
        matched_ids = set()

        # 精确匹配
        if keyword_lower in self._keyword_index:
            matched_ids.update(self._keyword_index[keyword_lower])

        # 模糊匹配
        for kw, ids in self._keyword_index.items():
            if keyword_lower in kw or kw in keyword_lower:
                matched_ids.update(ids)

        return [self._models[mid] for mid in matched_ids if mid in self._models]

    def get_by_category(self, category: ModelCategory) -> list[ThinkingModel]:
        """获取指定分类的模型"""
        return [m for m in self._models.values() if m.category == category]
