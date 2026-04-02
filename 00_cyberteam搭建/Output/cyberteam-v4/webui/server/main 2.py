"""CyberTeam Studio WebUI 后端 - FastAPI CRUD API

技能管理已重构：直接读写 SKILLS/ 目录下的真实 SKILL.md 文件
不再使用 SQLite 存储技能数据
"""

import sqlite3
import json
import os
import re
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import yaml

# CyberTeam V4 根目录（用于源文件同步）
CYBERTEAM_ROOT = Path(__file__).parent.parent.parent
AGENTS_DIR = CYBERTEAM_ROOT / "AGENTS"
CONFIG_DIR = CYBERTEAM_ROOT / "config"
SKILLS_DIR = CYBERTEAM_ROOT / "SKILLS"
WEBUI_SERVER_DIR = Path(__file__).parent

# 数据库路径（仅用于部门、Agent、Team 等非技能数据）
DB_PATH = WEBUI_SERVER_DIR / "data.db"


# ═══════════════════════════════════════════════════════════════════════════════
# SKILL.md 解析器 - 直接读写 SKILLS/ 目录下的真实文件
# ═══════════════════════════════════════════════════════════════════════════════

def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """解析 YAML frontmatter，返回 (frontmatter_dict, markdown_content)"""
    if content.startswith('---'):
        parts = content[3:].split('---', 1)
        if len(parts) == 2:
            try:
                fm = yaml.safe_load(parts[0])
                return (fm or {}, parts[1].strip())
            except yaml.YAMLError:
                return ({}, content)
    return ({}, content)


def serialize_frontmatter(fm: Dict[str, Any], content: str) -> str:
    """将 frontmatter 和 markdown 内容序列化为完整 SKILL.md"""
    fm_str = yaml.dump(fm, allow_unicode=True, default_flow_style=False, sort_keys=False)
    return f"---\n{fm_str}---\n\n{content}\n"


def parse_skill_file(skill_path: Path) -> Optional[Dict[str, Any]]:
    """解析单个 SKILL.md 文件，返回技能信息字典"""
    if not skill_path.exists():
        return None

    try:
        content = skill_path.read_text(encoding='utf-8')
        fm, md_content = parse_frontmatter(content)

        skill_dir = skill_path.parent

        # 计算相对路径，确定 category
        rel_path = skill_dir.relative_to(SKILLS_DIR)
        path_parts = rel_path.parts

        # category 是第一层目录名
        # 但对于 third-party/baoyu/baoyu-xxx/ 嵌套结构，需要特殊处理
        if len(path_parts) >= 3 and path_parts[0] == "third-party":
            # 嵌套结构如 third-party/baoyu/baoyu-xxx/
            # category 使用 "third-party" 或 "third-party/baoyu"
            category = f"{path_parts[0]}/{path_parts[1]}"
        elif len(path_parts) >= 2:
            category = path_parts[0]
        else:
            category = path_parts[0] if path_parts else "uncategorized"

        # 检查 references 目录
        references_dir = skill_dir / "references"
        references = []
        if references_dir.exists():
            for ref_file in references_dir.glob("*.md"):
                references.append({
                    "name": ref_file.stem,
                    "path": str(ref_file.relative_to(SKILLS_DIR)),
                    "type": "file"
                })

        # 检查 assess 目录
        assess_dir = skill_dir / "assess"
        assess_files = []
        if assess_dir.exists():
            for f in assess_dir.glob("*.json"):
                assess_files.append({
                    "name": f.stem,
                    "path": str(f.relative_to(SKILLS_DIR))
                })

        # 检查 evals 目录
        evals_dir = skill_dir / "evals"
        evals_files = []
        if evals_dir.exists():
            for f in evals_dir.glob("*.json"):
                evals_files.append({
                    "name": f.stem,
                    "path": str(f.relative_to(SKILLS_DIR))
                })

        # 提取 markdown 内容的前几行作为 description
        md_lines = md_content.strip().split('\n')
        md_description = ""
        in_section = False
        for line in md_lines:
            if line.startswith('#'):
                if in_section:
                    break
                in_section = True
            elif in_section and line.strip() and not line.startswith('##'):
                md_description += line.strip() + " "
            elif line.startswith('##') and md_description:
                break

        # 获取技能的 name/id
        skill_name_raw = fm.get("name")
        # 处理 YAML boolean 类型 (True/False) 或 None 的情况，使用目录名
        if isinstance(skill_name_raw, bool) or skill_name_raw is None:
            skill_name = skill_dir.name
        else:
            skill_name = skill_name_raw

        return {
            "id": skill_name,
            "name": skill_name,
            "category": category,
            "description": fm.get("description", md_description.strip()[:200]),
            "trigger": fm.get("trigger", ""),
            "triggerConditions": fm.get("trigger", ""),
            "difficulty": fm.get("difficulty", ""),
            "estimated_time": fm.get("estimated_time", ""),
            "version": fm.get("version", ""),
            "author": fm.get("author", ""),
            "tags": fm.get("tags", []),
            "success_metrics": fm.get("success_metrics", {}),
            "usageGuide": md_content[:500] if md_content else "",
            "content": md_content,
            "references": references,
            "assess": assess_files,
            "evals": evals_files,
            "source_path": str(rel_path),
        }
    except Exception as e:
        print(f"[SkillParser] Error parsing {skill_path}: {e}")
        return None


def scan_all_skills() -> List[Dict[str, Any]]:
    """递归扫描 SKILLS_DIR 下所有 SKILL.md 文件，返回技能列表"""
    skills = []

    # 使用 rglob 递归查找所有 SKILL.md 文件
    for skill_md in SKILLS_DIR.rglob("SKILL.md"):
        skill = parse_skill_file(skill_md)
        if skill:
            skills.append(skill)

    return skills


def get_skill_by_path(source_path: str) -> Optional[Dict[str, Any]]:
    """根据 source_path 获取技能信息"""
    skill_path = SKILLS_DIR / source_path / "SKILL.md"
    return parse_skill_file(skill_path)


def create_skill_directory(category: str, skill_name: str) -> Path:
    """创建新的技能目录及其基本 SKILL.md 文件"""
    skill_dir = SKILLS_DIR / category / skill_name
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_id = f"{category}-{skill_name}"
    fm = {
        "name": skill_id,
        "description": "新技能描述",
        "trigger": "触发条件",
        "difficulty": "medium",
        "estimated_time": "30-60分钟",
        "version": "v1.0",
        "author": "CyberTeam",
        "tags": [category],
        "success_metrics": {}
    }
    md_content = f"""# {skill_name} 技能

## 核心职责

1. **职责1**: 描述
2. **职责2**: 描述

## 工作流程

1. 步骤1
2. 步骤2
3. 步骤3
"""
    (skill_dir / "SKILL.md").write_text(serialize_frontmatter(fm, md_content), encoding='utf-8')

    # 创建辅助目录
    (skill_dir / "references").mkdir(exist_ok=True)
    (skill_dir / "assess").mkdir(exist_ok=True)
    (skill_dir / "evals").mkdir(exist_ok=True)

    return skill_dir


def update_skill_file(source_path: str, skill_data: Dict[str, Any]) -> bool:
    """更新技能文件"""
    skill_dir = SKILLS_DIR / source_path
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        return False

    try:
        content = skill_md.read_text(encoding='utf-8')
        fm, md_content = parse_frontmatter(content)

        # 更新 frontmatter
        update_fields = ["name", "description", "trigger", "difficulty", "estimated_time",
                        "version", "author", "tags", "success_metrics"]
        for field in update_fields:
            if field in skill_data:
                fm[field] = skill_data[field]

        # 如果有 content 更新 markdown 内容
        if "content" in skill_data:
            md_content = skill_data["content"]

        # 如果有 usageGuide 但没有 content，用 usageGuide 更新
        if "usageGuide" in skill_data and "content" not in skill_data:
            # usageGuide 取 markdown 的核心部分
            pass

        skill_md.write_text(serialize_frontmatter(fm, md_content), encoding='utf-8')
        return True
    except Exception as e:
        print(f"[SkillParser] Error updating {skill_md}: {e}")
        return False


def delete_skill_directory(source_path: str) -> bool:
    """删除技能目录"""
    skill_dir = SKILLS_DIR / source_path
    if skill_dir.exists() and skill_dir.is_dir():
        try:
            shutil.rmtree(skill_dir)
            return True
        except Exception as e:
            print(f"[SkillParser] Error deleting {skill_dir}: {e}")
            return False
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# 技能索引缓存
# ═══════════════════════════════════════════════════════════════════════════════

_skill_cache: List[Dict[str, Any]] = []
_cache_loaded = False


def get_skills_cache() -> List[Dict[str, Any]]:
    """获取技能缓存，必要时重新扫描"""
    global _skill_cache, _cache_loaded
    if not _cache_loaded:
        _skill_cache = scan_all_skills()
        _cache_loaded = True
    return _skill_cache


def invalidate_skill_cache():
    """使技能缓存失效"""
    global _cache_loaded
    _cache_loaded = False

app = FastAPI(title="CyberTeam Studio API", version="1.0.0")

# ── 源文件同步服务 ──

def sync_agent_to_file(agent_data: dict) -> bool:
    """同步Agent到AGENTS目录下的markdown文件"""
    try:
        dept_id = agent_data.get("departmentId", "")
        # 部门ID映射到目录名
        dept_dir_map = {
            "dept-ceo": "ceo", "dept-coo": "coo",
            "dept-ops": "growth", "dept-mkt": "growth",
            "dept-tech": "tech", "dept-design": "design",
            "dept-hr": "hr", "dept-finance": "finance",
            "dept-product": "product"
        }
        dept_dir = dept_dir_map.get(dept_id, "middle-tier")
        agent_dir = AGENTS_DIR / dept_dir
        agent_dir.mkdir(parents=True, exist_ok=True)

        # 生成markdown内容
        skills = agent_data.get("skills", [])
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except:
                skills = []

        content = f"""# {agent_data.get('name', 'Agent')}

## 基本信息

- **ID**: {agent_data.get('id', '')}
- **角色**: {agent_data.get('role', '')}
- **部门**: {dept_id}
- **级别**: L{agent_data.get('level', 3)}

## 能力标签

{agent_data.get('capabilities', '[]') or '[]'}

## 已配置技能

{', '.join([s.get('name', s) if isinstance(s, dict) else s for s in skills]) or '无'}

## 上游Agent

{agent_data.get('upstreamAgents', '[]') or '[]'}

## 下游Agent

{agent_data.get('downstreamAgents', '[]') or '[]'}

## 知识领域

{agent_data.get('knowledge', '')}

## 输出风格

{agent_data.get('outputStyle', '')}

---

*由 CyberTeam Studio 生成 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        file_path = agent_dir / f"{agent_data.get('id', 'agent')}.md"
        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"[Sync] Agent文件同步失败: {e}")
        return False

def sync_dept_rules_to_file(dept_data: dict) -> bool:
    """同步部门规则到config目录"""
    try:
        dept_id = dept_data.get("id", "")
        rules = dept_data.get("rules", "{}")
        if isinstance(rules, str):
            try:
                rules = json.loads(rules)
            except:
                rules = {}

        config_dir = CONFIG_DIR
        config_dir.mkdir(parents=True, exist_ok=True)

        content = f"""# {dept_data.get('name', '部门')} 规则配置

## 基本信息

- **部门ID**: {dept_id}
- **上级部门**: {dept_data.get('parentId', '无')}
- **级别**: L{dept_data.get('level', 1)}

## 规章制度

{yaml_dump(rules) if rules else '无规则配置'}

---

*由 CyberTeam Studio 生成 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        file_path = config_dir / f"dept_{dept_id}_rules.md"
        file_path.write_text(content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"[Sync] 部门规则同步失败: {e}")
        return False

def yaml_dump(data: dict) -> str:
    """简单的dict转yaml格式"""
    lines = []
    for k, v in data.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{k}: {v}")
    return '\n'.join(lines) if lines else '{}'

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 数据库初始化 ──

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()

    # 部门表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            parentId TEXT,
            description TEXT,
            rules TEXT,
            level INTEGER DEFAULT 1,
            createdAt TEXT,
            updatedAt TEXT
        )
    """)

    # Agent表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT,
            departmentId TEXT,
            level INTEGER DEFAULT 3,
            capabilities TEXT,
            skills TEXT,
            upstreamAgents TEXT,
            downstreamAgents TEXT,
            knowledge TEXT,
            outputStyle TEXT,
            createdAt TEXT,
            updatedAt TEXT
        )
    """)

    # Skill表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            description TEXT,
            triggerConditions TEXT,
            usageGuide TEXT,
            createdAt TEXT,
            updatedAt TEXT
        )
    """)

    # Agent-Skill关联表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_skills (
            agentId TEXT,
            skillId TEXT,
            PRIMARY KEY (agentId, skillId)
        )
    """)

    # Team表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            agentIds TEXT,
            coordinationMode TEXT,
            reportingCycle TEXT,
            createdAt TEXT,
            updatedAt TEXT
        )
    """)

    # Template表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            teamConfig TEXT,
            usageCount INTEGER DEFAULT 0,
            createdAt TEXT,
            updatedAt TEXT
        )
    """)

    conn.commit()
    conn.close()

    # 初始化预设数据
    init_preset_data()

def init_preset_data():
    """初始化预设数据"""
    conn = get_db()
    cursor = conn.cursor()

    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM departments")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    now = datetime.now().isoformat()

    # 预设部门
    departments = [
        ("dept-ceo", "CEO", None, "首席执行官", "{}", 1, now, now),
        ("dept-coo", "COO", "dept-ceo", "首席运营官", "{}", 2, now, now),
        ("dept-ops", "运营部", "dept-coo", "用户增长、内容运营、活动策划", "{}", 2, now, now),
        ("dept-mkt", "营销部", "dept-coo", "品牌营销、渠道推广、广告投放", "{}", 2, now, now),
        ("dept-tech", "技术部", "dept-coo", "技术方案、架构设计、开发实现", "{}", 2, now, now),
        ("dept-design", "设计部", "dept-coo", "UI设计、用户体验、品牌视觉", "{}", 2, now, now),
        ("dept-hr", "人力部", "dept-coo", "招聘方案、团队激励、文化建设", "{}", 2, now, now),
        ("dept-finance", "财务部", "dept-coo", "预算规划、成本控制、投资分析", "{}", 2, now, now),
        ("dept-product", "产品部", "dept-coo", "需求分析、产品设计、功能规划", "{}", 2, now, now),
    ]

    for d in departments:
        cursor.execute("""
            INSERT INTO departments (id, name, parentId, description, rules, level, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, d)

    # 预设Skills
    skills = [
        ("skill-growth", "增长黑客", "growth", "用户增长、裂变营销、病毒式传播", "用户增长遇到瓶颈时", "AARRR模型应用", now, now),
        ("skill-content", "内容营销", "content", "内容策划、文案撰写、SEO优化", "需要内容产出时", "AIDA模型应用", now, now),
        ("skill-data", "数据分析", "analytics", "数据挖掘、趋势分析、转化追踪", "需要数据支撑决策时", "漏斗分析方法", now, now),
        ("skill-social", "社交媒体运营", "social", "双微一抖、小红书运营、粉丝互动", "社交媒体推广时", "内容矩阵策略", now, now),
        ("skill-event", "活动策划", "event", "线上活动、线下活动、节日营销", "大促/活动时", "PDCA管理循环", now, now),
        ("skill-brand", "品牌建设", "brand", "品牌定位、VI设计、品牌故事", "品牌建设/升级时", "品牌金字塔模型", now, now),
        ("skill-aws", "AWS架构", "tech", "AWS云服务架构设计、DevOps", "云架构设计时", "Well-Architected框架", now, now),
        ("skill-react", "React开发", "tech", "React前端开发、组件化设计、状态管理", "前端开发时", "组件设计原则", now, now),
        ("skill-ux", "用户体验设计", "design", "用户研究、交互设计、可用性测试", "产品设计时", "用户体验五要素", now, now),
        ("skill-figma", "Figma设计", "design", "Figma原型设计、UI设计、设计系统", "UI设计时", "原子设计理论", now, now),
        ("skill-finance", "财务规划", "finance", "预算编制、成本分析、投资回报", "财务决策时", "DCF现金流折现", now, now),
        ("skill-hr", "人才发展", "hr", "招聘策略、培训体系、绩效管理", "人力资源规划时", "MBO目标管理", now, now),
        ("skill-product", "产品规划", "product", "需求分析、Roadmap规划PRD撰写", "产品规划时", "Kano模型应用", now, now),
    ]

    for s in skills:
        cursor.execute("""
            INSERT INTO skills (id, name, category, description, triggerConditions, usageGuide, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, s)

    # 预设Agents
    agents = [
        ("agent-ceo", "CEO", "首席执行官", "dept-ceo", 1, "[]", "[]", "[]", "[]", "[]", "战略眼光、决策果断", now, now),
        ("agent-coo", "COO", "首席运营官", "dept-coo", 2, "[]", "[]", "[]", "[]", "[]", "运营专家、协调能力强", now, now),
        ("agent-ops-dir", "运营总监", "运营部负责人", "dept-ops", 2, "[]", "[]", "[]", "[]", "[]", "运营专家、数据驱动", now, now),
        ("agent-mkt-dir", "营销总监", "营销部负责人", "dept-mkt", 2, "[]", "[]", "[]", "[]", "[]", "营销专家、创意丰富", now, now),
        ("agent-tech-dir", "技术总监", "技术部负责人", "dept-tech", 2, "[]", "[]", "[]", "[]", "[]", "技术专家、架构师", now, now),
        ("agent-design-dir", "设计总监", "设计部负责人", "dept-design", 2, "[]", "[]", "[]", "[]", "[]", "设计专家、审美出色", now, now),
        ("agent-hr-dir", "人力总监", "人力部负责人", "dept-hr", 2, "[]", "[]", "[]", "[]", "[]", "HR专家、识人善任", now, now),
        ("agent-finance-dir", "财务总监", "财务部负责人", "dept-finance", 2, "[]", "[]", "[]", "[]", "[]", "财务专家、风险控制", now, now),
        ("agent-product-dir", "产品总监", "产品部负责人", "dept-product", 2, "[]", "[]", "[]", "[]", "[]", "产品专家、用户思维", now, now),
        ("agent-content", "内容文案专家", "内容创作", "dept-mkt", 3, "[]", "[]", "[]", "[]", "[]", "文案功底深厚", now, now),
        ("agent-growth", "增长专家", "用户增长", "dept-ops", 3, "[]", "[]", "[]", "[]", "[]", "增长黑客思维", now, now),
    ]

    for a in agents:
        cursor.execute("""
            INSERT INTO agents (id, name, role, departmentId, level, capabilities, skills, upstreamAgents, downstreamAgents, knowledge, outputStyle, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, a)

    # CEO-Agent关联（CEO配置了部分基础技能）
    agent_skills_ceo = [
        ("agent-ceo", "skill-growth"),
        ("agent-ceo", "skill-product"),
    ]
    for ag, sk in agent_skills_ceo:
        cursor.execute("INSERT OR IGNORE INTO agent_skills (agentId, skillId) VALUES (?, ?)", (ag, sk))

    # COO-Agent关联
    agent_skills_coo = [
        ("agent-coo", "skill-data"),
        ("agent-coo", "skill-growth"),
    ]
    for ag, sk in agent_skills_coo:
        cursor.execute("INSERT OR IGNORE INTO agent_skills (agentId, skillId) VALUES (?, ?)", (ag, sk))

    # 运营总监-增长专家关联
    agent_skills_ops = [
        ("agent-ops-dir", "skill-growth"),
        ("agent-ops-dir", "skill-data"),
        ("agent-ops-dir", "skill-event"),
        ("agent-growth", "skill-growth"),
        ("agent-growth", "skill-social"),
    ]
    for ag, sk in agent_skills_ops:
        cursor.execute("INSERT OR IGNORE INTO agent_skills (agentId, skillId) VALUES (?, ?)", (ag, sk))

    # 营销总监关联
    agent_skills_mkt = [
        ("agent-mkt-dir", "skill-content"),
        ("agent-mkt-dir", "skill-brand"),
        ("agent-mkt-dir", "skill-social"),
        ("agent-content", "skill-content"),
        ("agent-content", "skill-aws"),
    ]
    for ag, sk in agent_skills_mkt:
        cursor.execute("INSERT OR IGNORE INTO agent_skills (agentId, skillId) VALUES (?, ?)", (ag, sk))

    conn.commit()
    conn.close()

# ── 启动时初始化 ──
init_db()

# ── Pydantic Models ──

class Department(BaseModel):
    id: str
    name: str
    parentId: Optional[str] = None
    description: Optional[str] = ""
    rules: Optional[str] = "{}"
    level: int = 1

class Agent(BaseModel):
    id: str
    name: str
    role: Optional[str] = ""
    departmentId: Optional[str] = None
    level: int = 3
    capabilities: Optional[str] = "[]"
    skills: Optional[list] = []
    upstreamAgents: Optional[str] = "[]"
    downstreamAgents: Optional[str] = "[]"
    knowledge: Optional[str] = ""
    outputStyle: Optional[str] = ""

class Skill(BaseModel):
    id: Optional[str] = ""
    name: str
    category: Optional[str] = ""
    description: Optional[str] = ""
    triggerConditions: Optional[str] = ""
    usageGuide: Optional[str] = ""
    difficulty: Optional[str] = "medium"
    version: Optional[str] = "v1.0.0"
    author: Optional[str] = "CyberTeam"
    tags: Optional[List[str]] = []
    trigger: Optional[str] = ""  # 别名字段

class Team(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    agentIds: Optional[list] = []
    coordinationMode: Optional[str] = "sequential"
    reportingCycle: Optional[str] = "daily"

class Template(BaseModel):
    id: str
    name: str
    description: Optional[str] = ""
    teamConfig: Optional[str] = "{}"
    usageCount: int = 0

# ── API Routes: Departments ──

@app.get("/api/departments")
async def get_departments():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM departments ORDER BY level, name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/departments/{dept_id}")
async def get_department(dept_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM departments WHERE id = ?", (dept_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "部门不存在")
    return dict(row)

@app.post("/api/departments")
async def create_department(dept: Department):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    try:
        cursor.execute("""
            INSERT INTO departments (id, name, parentId, description, rules, level, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (dept.id, dept.name, dept.parentId, dept.description, dept.rules or "{}", dept.level, now, now))
        conn.commit()
        result = dict(dept)
        result["createdAt"] = now
        result["updatedAt"] = now
        conn.close()
        return result
    except Exception as e:
        conn.close()
        raise HTTPException(400, str(e))

@app.put("/api/departments/{dept_id}")
async def update_department(dept_id: str, dept: Department):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        UPDATE departments SET name=?, parentId=?, description=?, rules=?, level=?, updatedAt=?
        WHERE id=?
    """, (dept.name, dept.parentId, dept.description, dept.rules or "{}", dept.level, now, dept_id))
    conn.commit()
    conn.close()
    return {"id": dept_id, **dept.model_dump(), "updatedAt": now}

@app.delete("/api/departments/{dept_id}")
async def delete_department(dept_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM departments WHERE id = ?", (dept_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# ── API Routes: Skills (基于真实 SKILL.md 文件) ──

@app.get("/api/skills")
async def get_skills():
    """获取所有技能列表"""
    skills = get_skills_cache()
    # 返回简化版信息（用于列表展示）
    return [{
        "id": s.get("id", ""),
        "name": s.get("name", ""),
        "category": s.get("category", ""),
        "description": s.get("description", ""),
        "triggerConditions": s.get("triggerConditions", ""),
        "usageGuide": s.get("usageGuide", "")[:200] if s.get("usageGuide") else "",
        "trigger": s.get("trigger", ""),
        "difficulty": s.get("difficulty", ""),
        "version": s.get("version", ""),
        "author": s.get("author", ""),
        "tags": s.get("tags", []),
        "source_path": s.get("source_path", ""),
    } for s in skills]

@app.get("/api/skills/{skill_id}")
async def get_skill(skill_id: str):
    """获取单个技能详细信息"""
    # skill_id 可能是 id 或 source_path
    skills = get_skills_cache()
    skill = None

    # 先尝试按 id 匹配
    for s in skills:
        if s.get("id") == skill_id or s.get("source_path") == skill_id:
            skill = s
            break

    if not skill:
        # 尝试模糊匹配
        for s in skills:
            if skill_id in s.get("source_path", "") or skill_id in s.get("id", ""):
                skill = s
                break

    if not skill:
        raise HTTPException(404, f"技能不存在: {skill_id}")

    return skill

@app.post("/api/skills")
async def create_skill(skill: Skill):
    """创建新技能（在 SKILLS/ 目录下创建真实文件）"""
    try:
        category = skill.category or "uncategorized"
        # 生成安全的目录名
        safe_name = re.sub(r'[^\w\-]', '-', skill.name)
        safe_name = re.sub(r'-+', '-', safe_name).strip('-')

        skill_dir = create_skill_directory(category, safe_name)

        # 更新基本信息
        skill_data = {
            "name": skill.name,
            "description": skill.description or "",
            "trigger": skill.triggerConditions or "",
            "tags": [category],
            "success_metrics": {}
        }
        update_skill_file(f"{category}/{safe_name}", skill_data)

        invalidate_skill_cache()

        return {
            "id": f"{category}-{safe_name}",
            "name": skill.name,
            "category": category,
            "description": skill.description or "",
            "triggerConditions": skill.triggerConditions or "",
            "source_path": f"{category}/{safe_name}",
            "createdAt": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(400, f"创建技能失败: {str(e)}")

@app.put("/api/skills/{category}/{skill_id}")
async def update_skill_v2(category: str, skill_id: str, skill: Skill):
    """更新技能信息（支持 category/skill_id 路径格式）"""
    skills = get_skills_cache()

    # 找到技能
    target_skill = None
    source_path = None
    for s in skills:
        if s.get("id") == skill_id or s.get("source_path") == f"{category}/{skill_id}":
            target_skill = s
            source_path = s.get("source_path", f"{category}/{skill_id}")
            break

    if not target_skill:
        raise HTTPException(404, f"技能不存在: {skill_id}")

    # 构建更新数据
    update_data = {
        "name": skill.name,
        "description": skill.description or "",
        "trigger": skill.triggerConditions or "",
        "tags": [skill.category] if skill.category else [],
        "difficulty": getattr(skill, 'difficulty', 'medium'),
        "version": getattr(skill, 'version', 'v1.0.0'),
        "author": getattr(skill, 'author', 'CyberTeam'),
    }

    # 如果有 usageGuide（markdown 内容），更新它
    if skill.usageGuide:
        update_data["content"] = skill.usageGuide

    success = update_skill_file(source_path, update_data)

    if not success:
        raise HTTPException(500, "更新技能文件失败")

    invalidate_skill_cache()

    return {
        "id": skill_id,
        "name": skill.name,
        "category": category,
        "description": skill.description or "",
        "triggerConditions": skill.triggerConditions or "",
        "source_path": source_path,
        "updatedAt": datetime.now().isoformat(),
    }


@app.put("/api/skills/{skill_id}")
async def update_skill(skill_id: str, skill: Skill):
    """更新技能信息（兼容旧版格式）"""
    skills = get_skills_cache()

    # 找到技能
    target_skill = None
    source_path = None
    for s in skills:
        if s.get("id") == skill_id or s.get("source_path") == skill_id:
            target_skill = s
            source_path = s.get("source_path", "")
            break

    if not target_skill:
        raise HTTPException(404, f"技能不存在: {skill_id}")

    # 构建更新数据
    update_data = {
        "name": skill.name,
        "description": skill.description or "",
        "trigger": skill.triggerConditions or "",
        "tags": [skill.category] if skill.category else [],
    }

    # 如果有 usageGuide（markdown 内容），更新它
    if skill.usageGuide:
        update_data["content"] = skill.usageGuide

    success = update_skill_file(source_path, update_data)

    if not success:
        raise HTTPException(500, "更新技能文件失败")

    invalidate_skill_cache()

    return {
        "id": skill_id,
        "name": skill.name,
        "category": skill.category,
        "description": skill.description or "",
        "triggerConditions": skill.triggerConditions or "",
        "source_path": source_path,
        "updatedAt": datetime.now().isoformat(),
    }

@app.delete("/api/skills/{skill_id}")
async def delete_skill(skill_id: str):
    """删除技能（删除真实目录）"""
    skills = get_skills_cache()

    # 找到技能
    target_skill = None
    source_path = None
    for s in skills:
        if s.get("id") == skill_id or s.get("source_path") == skill_id:
            target_skill = s
            source_path = s.get("source_path", "")
            break

    if not target_skill:
        raise HTTPException(404, f"技能不存在: {skill_id}")

    success = delete_skill_directory(source_path)

    if not success:
        raise HTTPException(500, "删除技能目录失败")

    invalidate_skill_cache()

    return {"success": True, "message": f"技能 {skill_id} 已删除"}

@app.get("/api/skills/{skill_id}/content")
async def get_skill_content(skill_id: str):
    """获取技能的完整 markdown 内容"""
    skills = get_skills_cache()

    for s in skills:
        if s.get("id") == skill_id or s.get("source_path") == skill_id:
            content = s.get("content", "")
            return {"content": content}

    raise HTTPException(404, f"技能不存在: {skill_id}")

@app.get("/api/skills/{skill_id}/references")
async def get_skill_references(skill_id: str):
    """获取技能的参考文档列表"""
    skills = get_skills_cache()

    for s in skills:
        if s.get("id") == skill_id or s.get("source_path") == skill_id:
            return {"references": s.get("references", [])}

    raise HTTPException(404, f"技能不存在: {skill_id}")

# ── API Routes: Agents ──

@app.get("/api/agents")
async def get_agents():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, GROUP_CONCAT(ags.skillId) as skillIds
        FROM agents a
        LEFT JOIN agent_skills ags ON a.id = ags.agentId
        GROUP BY a.id
        ORDER BY a.level, a.name
    """)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        d = dict(row)
        # 解析skillIds和skillNames -> 返回字符串数组给前端
        if d.get("skillIds"):
            d["skills"] = d["skillIds"].split(",")  # 前端期望 string[]
        else:
            d["skills"] = []
        # 转换 level: int -> string
        d["level"] = f"L{d.get('level', 3)}"
        # 解析 capabilities 和 knowledge: JSON string -> array
        import json
        try:
            d["capabilities"] = json.loads(d.get("capabilities") or "[]")
        except:
            d["capabilities"] = []
        try:
            d["knowledge"] = json.loads(d.get("knowledge") or "[]")
        except:
            d["knowledge"] = []
        # 删除不需要的字段
        for field in ["skillIds", "skillNames", "upstreamAgents", "downstreamAgents"]:
            d.pop(field, None)
        result.append(d)
    return result

@app.get("/api/agents/{agent_id}")
async def get_agent(agent_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, GROUP_CONCAT(ags.skillId) as skillIds
        FROM agents a
        LEFT JOIN agent_skills ags ON a.id = ags.agentId
        WHERE a.id = ?
        GROUP BY a.id
    """, (agent_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(404, "Agent不存在")

    d = dict(row)
    # 解析skillIds -> 返回字符串数组给前端
    if d.get("skillIds"):
        d["skills"] = d["skillIds"].split(",")  # 前端期望 string[]
    else:
        d["skills"] = []
    # 转换 level: int -> string
    d["level"] = f"L{d.get('level', 3)}"
    # 解析 capabilities 和 knowledge: JSON string -> array
    import json
    try:
        d["capabilities"] = json.loads(d.get("capabilities") or "[]")
    except:
        d["capabilities"] = []
    try:
        d["knowledge"] = json.loads(d.get("knowledge") or "[]")
    except:
        d["knowledge"] = []
    # 删除不需要的字段
    for field in ["skillIds", "skillNames", "upstreamAgents", "downstreamAgents"]:
        d.pop(field, None)
    return d

@app.post("/api/agents")
async def create_agent(agent: Agent):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    try:
        cursor.execute("""
            INSERT INTO agents (id, name, role, departmentId, level, capabilities, skills, upstreamAgents, downstreamAgents, knowledge, outputStyle, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (agent.id, agent.name, agent.role, agent.departmentId, agent.level,
              agent.capabilities or "[]", "[]",
              agent.upstreamAgents or "[]", agent.downstreamAgents or "[]",
              agent.knowledge or "", agent.outputStyle or "", now, now))
        conn.commit()
        conn.close()

        # 同步到源文件
        agent_data = agent.model_dump()
        agent_data["skills"] = []
        sync_agent_to_file(agent_data)

        return {**agent.model_dump(), "createdAt": now, "updatedAt": now, "skills": []}
    except Exception as e:
        conn.close()
        raise HTTPException(400, str(e))

@app.put("/api/agents/{agent_id}")
async def update_agent(agent_id: str, agent: Agent):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    # 使用 INSERT OR REPLACE：Agent 不存在时插入，存在时更新
    cursor.execute("""
        INSERT OR REPLACE INTO agents (id, name, role, departmentId, level, capabilities, skills, upstreamAgents, downstreamAgents, knowledge, outputStyle, createdAt, updatedAt)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (agent_id, agent.name, agent.role, agent.departmentId, agent.level,
          agent.capabilities or "[]", "[]",
          agent.upstreamAgents or "[]", agent.downstreamAgents or "[]",
          agent.knowledge or "", agent.outputStyle or "", now, now))

    # 更新Agent-Skill关联
    if agent.skills is not None:
        cursor.execute("DELETE FROM agent_skills WHERE agentId = ?", (agent_id,))
        for skill in agent.skills:
            skill_id = skill if isinstance(skill, str) else skill.get("id")
            if skill_id:
                cursor.execute("INSERT INTO agent_skills (agentId, skillId) VALUES (?, ?)", (agent_id, skill_id))

    conn.commit()

    # 获取完整的agent数据用于同步
    # 注意：不再JOIN skills表，因为agent_skills存储的是真实SKILL.md的ID
    cursor.execute("""
        SELECT a.*, GROUP_CONCAT(ags.skillId) as skillIds
        FROM agents a
        LEFT JOIN agent_skills ags ON a.id = ags.agentId
        WHERE a.id = ?
        GROUP BY a.id
    """, (agent_id,))
    row = cursor.fetchone()
    conn.close()

    # 同步到源文件
    if row:
        agent_data = dict(row)
        if agent_data.get("skillIds"):
            # skillIds 是真实SKILL.md的ID列表（如 growth-operations）
            agent_data["skills"] = agent_data["skillIds"].split(",")
        else:
            agent_data["skills"] = []
        sync_agent_to_file(agent_data)

    return {**agent.model_dump(), "updatedAt": now}

@app.delete("/api/agents/{agent_id}")
async def delete_agent(agent_id: str):
    conn = get_db()
    cursor = conn.cursor()

    # 获取agent信息用于删除源文件
    cursor.execute("SELECT departmentId FROM agents WHERE id = ?", (agent_id,))
    row = cursor.fetchone()

    cursor.execute("DELETE FROM agent_skills WHERE agentId = ?", (agent_id,))
    cursor.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
    conn.commit()
    conn.close()

    # 删除源文件
    if row:
        dept_dir_map = {
            "dept-ceo": "ceo", "dept-coo": "coo",
            "dept-ops": "growth", "dept-mkt": "growth",
            "dept-tech": "tech", "dept-design": "design",
            "dept-hr": "hr", "dept-finance": "finance",
            "dept-product": "product"
        }
        dept_dir = dept_dir_map.get(row[0], "middle-tier")
        file_path = AGENTS_DIR / dept_dir / f"{agent_id}.md"
        if file_path.exists():
            file_path.unlink()

    return {"success": True}

@app.get("/api/agents/{agent_id}/skills")
async def get_agent_skills(agent_id: str):
    """获取 Agent 关联的技能（从真实 SKILLS_DIR 读取）

    预设 skillId → category 映射，然后从 SKILLS_DIR 找到对应真实技能
    """
    conn = get_db()
    cursor = conn.cursor()
    # 从 agent_skills 表获取该 agent 关联的所有 skillId
    cursor.execute("SELECT skillId FROM agent_skills WHERE agentId = ?", (agent_id,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    # 预设 skillId → category 映射
    SKILL_ID_TO_CATEGORY = {
        "skill-growth": "growth",
        "skill-content": "content",
        "skill-data": "analytics",
        "skill-social": "social",
        "skill-event": "event",
        "skill-brand": "brand",
        "skill-aws": "tech",
        "skill-react": "tech",
        "skill-ux": "design",
        "skill-figma": "design",
        "skill-finance": "finance",
        "skill-hr": "hr",
        "skill-product": "product",
        # 中文名映射（部分预设技能用中文名存储）
        "增长黑客": "growth",
        "内容营销": "content",
        "数据分析": "analytics",
        "社交媒体运营": "social",
        "活动策划": "event",
        "品牌建设": "brand",
        "AWS架构": "tech",
        "React开发": "tech",
        "用户体验设计": "design",
        "Figma设计": "design",
        "财务规划": "finance",
        "人才发展": "hr",
        "产品规划": "product",
    }

    # 获取所有真实技能
    all_skills = get_skills_cache()

    # 按 category 分组真实技能
    skills_by_category = {}
    for s in all_skills:
        cat = s.get("category", "")
        if cat not in skills_by_category:
            skills_by_category[cat] = []
        skills_by_category[cat].append(s)

    result = []
    for row in rows:
        skill_id = row[0]
        # 映射到 category
        category = SKILL_ID_TO_CATEGORY.get(skill_id, "")

        if category and category in skills_by_category:
            # 如果 category 下有技能，取第一个（按 name 排序）
            cat_skills = sorted(skills_by_category[category], key=lambda x: x.get("name", ""))
            if cat_skills:
                result.append(cat_skills[0])
        else:
            # 尝试按名称直接匹配
            for s in all_skills:
                if s.get("name") == skill_id or s.get("id") == skill_id:
                    result.append(s)
                    break

    return result

@app.post("/api/agents/{agent_id}/skills/{skill_id}")
async def add_agent_skill(agent_id: str, skill_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO agent_skills (agentId, skillId) VALUES (?, ?)", (agent_id, skill_id))
    conn.commit()
    conn.close()
    return {"success": True}

@app.delete("/api/agents/{agent_id}/skills/{skill_id}")
async def remove_agent_skill(agent_id: str, skill_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM agent_skills WHERE agentId = ? AND skillId = ?", (agent_id, skill_id))
    conn.commit()
    conn.close()
    return {"success": True}

# ── API Routes: Teams ──

@app.get("/api/teams")
async def get_teams():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams ORDER BY createdAt DESC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["agentIds"] = json.loads(d.get("agentIds", "[]"))
        result.append(d)
    return result

@app.post("/api/teams")
async def create_team(team: Team):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    try:
        cursor.execute("""
            INSERT INTO teams (id, name, description, agentIds, coordinationMode, reportingCycle, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (team.id, team.name, team.description, json.dumps(team.agentIds or []),
              team.coordinationMode, team.reportingCycle, now, now))
        conn.commit()
        conn.close()
        return {**team.model_dump(), "createdAt": now, "updatedAt": now}
    except Exception as e:
        conn.close()
        raise HTTPException(400, str(e))

@app.put("/api/teams/{team_id}")
async def update_team(team_id: str, team: Team):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        UPDATE teams SET name=?, description=?, agentIds=?, coordinationMode=?, reportingCycle=?, updatedAt=?
        WHERE id=?
    """, (team.name, team.description, json.dumps(team.agentIds or []),
          team.coordinationMode, team.reportingCycle, now, team_id))
    conn.commit()
    conn.close()
    return {**team.model_dump(), "updatedAt": now}

@app.delete("/api/teams/{team_id}")
async def delete_team(team_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# ── API Routes: Templates ──

@app.get("/api/templates")
async def get_templates():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM templates ORDER BY usageCount DESC")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        d = dict(row)
        d["teamConfig"] = json.loads(d.get("teamConfig", "{}"))
        result.append(d)
    return result

@app.post("/api/templates")
async def create_template(template: Template):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    try:
        cursor.execute("""
            INSERT INTO templates (id, name, description, teamConfig, usageCount, createdAt, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (template.id, template.name, template.description,
              json.dumps(template.teamConfig or {}), template.usageCount or 0, now, now))
        conn.commit()
        conn.close()
        return {**template.model_dump(), "createdAt": now, "updatedAt": now}
    except Exception as e:
        conn.close()
        raise HTTPException(400, str(e))

@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
    conn.commit()
    conn.close()
    return {"success": True}

# ── 健康检查 ──

@app.get("/api/health")
async def health():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)