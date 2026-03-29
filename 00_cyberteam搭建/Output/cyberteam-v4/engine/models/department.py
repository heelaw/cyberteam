# engine/models/department.py
"""Department - Modern Corporate Governance Terms"""

from enum import Enum


class Department(Enum):
    """
    Departments using modern corporate governance terminology.

    Replaces historical terms:
    - 吏部 → HR (Human Resources)
    - 户部 → FIN (Finance)
    - 礼部 → ADMIN (Administration)
    - 兵部 → OPS (Operations)
    - 刑部 → LEGAL (Legal/Compliance)
    - 工部 → ENG (Engineering)
    """

    HR = "hr"  # 人力资源部 - 招聘、培训、绩效、考核
    FIN = "finance"  # 财务部 - 预算、成本、结算、报销
    ADMIN = "admin"  # 行政部 - 制度、文化、行政事务
    OPS = "operations"  # 运营部 - 日常运营、流程管理
    LEGAL = "legal"  # 法务部 - 合规、风控、法务咨询
    ENG = "engineering"  # 工程部 - 技术开发、系统建设

    @classmethod
    def from_string(cls, value: str) -> "Department":
        """Convert string to Department enum."""
        mapping = {
            "hr": cls.HR,
            "finance": cls.FIN,
            "fin": cls.FIN,
            "admin": cls.ADMIN,
            "administration": cls.ADMIN,
            "operations": cls.OPS,
            "ops": cls.OPS,
            "legal": cls.LEGAL,
            "engineering": cls.ENG,
            "eng": cls.ENG,
        }
        normalized = value.lower().strip()
        if normalized not in mapping:
            raise ValueError(f"Unknown department: {value}")
        return mapping[normalized]
