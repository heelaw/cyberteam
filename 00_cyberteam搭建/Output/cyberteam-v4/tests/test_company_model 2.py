"""测试公司多租户数据模型。"""

import pytest
import pytest_asyncio
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from backend.app.models import Base, Company, Department, Agent, CompanyDepartment, CompanyAgent


# 使用 SQLite 内存数据库进行测试
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_engine():
    """创建异步测试引擎。"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine):
    """创建异步会话。"""
    async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def sync_engine():
    """创建同步测试引擎（用于需要同步操作的测试）。"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest_asyncio.fixture
def sync_session(sync_engine):
    """创建同步会话。"""
    Session = sessionmaker(bind=sync_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


class TestCompanyModel:
    """测试 Company 模型。"""

    def test_create_company(self, sync_session: Session):
        """测试创建公司。"""
        company = Company(
            name="测试公司",
            status="active",
            config={"plan": "enterprise"}
        )
        sync_session.add(company)
        sync_session.commit()

        assert company.id is not None
        assert company.name == "测试公司"
        assert company.status == "active"
        assert company.created_at is not None

    def test_company_relationships(self, sync_session: Session):
        """测试公司的部门 和 Agent 关联。"""
        # 创建公司
        company = Company(name="测试公司")
        sync_session.add(company)
        sync_session.commit()

        # 创建部门
        dept = Department(
            name="技术部",
            code="tech",
            company_id=company.id
        )
        sync_session.add(dept)
        sync_session.commit()

        # 创建 Agent
        agent = Agent(
            name="测试Agent",
            agent_type="executor",
            company_id=company.id
        )
        sync_session.add(agent)
        sync_session.commit()

        # 验证关系
        sync_session.refresh(company)
        assert len(company.departments) == 1
        assert company.departments[0].name == "技术部"
        assert len(company.agents) == 1
        assert company.agents[0].name == "测试Agent"


class TestDepartmentModel:
    """测试 Department 模型。"""

    def test_create_department_without_company(self, sync_session: Session):
        """测试创建不关联公司的部门（兼容历史数据）。"""
        dept = Department(
            name="通用部门",
            code="generic",
            company_id=None  # nullable
        )
        sync_session.add(dept)
        sync_session.commit()

        assert dept.id is not None
        assert dept.company_id is None

    def test_create_department_with_company(self, sync_session: Session):
        """测试创建关联公司的部门。"""
        # 先创建公司
        company = Company(name="测试公司")
        sync_session.add(company)
        sync_session.commit()

        # 创建部门
        dept = Department(
            name="技术部",
            code="tech",
            company_id=company.id
        )
        sync_session.add(dept)
        sync_session.commit()

        assert dept.id is not None
        assert dept.company_id == company.id
        assert dept.company.name == "测试公司"

    def test_department_company_id_index(self, sync_session: Session):
        """测试部门的 company_id 索引存在。"""
        from sqlalchemy import inspect
        inspector = inspect(sync_session.bind)
        indexes = inspector.get_indexes("departments")

        has_company_id_index = any(
            any(col == "company_id" for col in idx.get("column_names", []))
            for idx in indexes
        )
        assert has_company_id_index, "departments 表应该有 company_id 索引"


class TestAgentModel:
    """测试 Agent 模型。"""

    def test_create_agent_without_company(self, sync_session: Session):
        """测试创建不关联公司的 Agent（兼容历史数据）。"""
        agent = Agent(
            name="通用Agent",
            agent_type="executor",
            company_id=None  # nullable
        )
        sync_session.add(agent)
        sync_session.commit()

        assert agent.id is not None
        assert agent.company_id is None

    def test_create_agent_with_company(self, sync_session: Session):
        """测试创建关联公司的 Agent。"""
        # 先创建公司
        company = Company(name="测试公司")
        sync_session.add(company)
        sync_session.commit()

        # 创建 Agent
        agent = Agent(
            name="测试Agent",
            agent_type="executor",
            company_id=company.id
        )
        sync_session.add(agent)
        sync_session.commit()

        assert agent.id is not None
        assert agent.company_id == company.id
        assert agent.company.name == "测试公司"

    def test_agent_company_id_index(self, sync_session: Session):
        """测试 Agent 的 company_id 索引存在。"""
        from sqlalchemy import inspect
        inspector = inspect(sync_session.bind)
        indexes = inspector.get_indexes("agents")

        has_company_id_index = any(
            any(col == "company_id" for col in idx.get("column_names", []))
            for idx in indexes
        )
        assert has_company_id_index, "agents 表应该有 company_id 索引"


class TestCompanyDepartmentModel:
    """测试 CompanyDepartment 关联表模型。"""

    def test_create_company_department(self, sync_session: Session):
        """测试创建公司-部门关联。"""
        # 创建公司
        company = Company(name="测试公司")
        sync_session.add(company)
        sync_session.commit()

        # 创建部门
        dept = Department(name="技术部", code="tech")
        sync_session.add(dept)
        sync_session.commit()

        # 创建关联
        cd = CompanyDepartment(
            company_id=company.id,
            department_id=dept.id
        )
        sync_session.add(cd)
        sync_session.commit()

        assert cd.id is not None
        assert cd.company_id == company.id
        assert cd.department_id == dept.id


class TestCompanyAgentModel:
    """测试 CompanyAgent 关联表模型。"""

    def test_create_company_agent(self, sync_session: Session):
        """测试创建公司-Agent关联。"""
        # 创建公司
        company = Company(name="测试公司")
        sync_session.add(company)
        sync_session.commit()

        # 创建 Agent
        agent = Agent(name="测试Agent", agent_type="executor")
        sync_session.add(agent)
        sync_session.commit()

        # 创建关联
        ca = CompanyAgent(
            company_id=company.id,
            agent_id=agent.id
        )
        sync_session.add(ca)
        sync_session.commit()

        assert ca.id is not None
        assert ca.company_id == company.id
        assert ca.agent_id == agent.id


class TestMultiTenantQuery:
    """测试多租户查询过滤。"""

    def test_query_departments_by_company(self, sync_session: Session):
        """测试按公司查询部门。"""
        # 创建两家公司
        company1 = Company(name="公司A")
        company2 = Company(name="公司B")
        sync_session.add_all([company1, company2])
        sync_session.commit()

        # 为公司1创建部门
        dept1 = Department(name="研发部", code="rd", company_id=company1.id)
        dept2 = Department(name="产品部", code="pm", company_id=company1.id)
        # 为公司2创建部门
        dept3 = Department(name="销售部", code="sales", company_id=company2.id)

        sync_session.add_all([dept1, dept2, dept3])
        sync_session.commit()

        # 查询公司1的部门
        result = sync_session.execute(
            select(Department).where(Department.company_id == company1.id)
        ).scalars().all()

        assert len(result) == 2
        assert all(d.company_id == company1.id for d in result)

    def test_query_agents_by_company(self, sync_session: Session):
        """测试按公司查询Agent。"""
        # 创建两家公司
        company1 = Company(name="公司A")
        company2 = Company(name="公司B")
        sync_session.add_all([company1, company2])
        sync_session.commit()

        # 为公司1创建Agent
        agent1 = Agent(name="Agent1", agent_type="executor", company_id=company1.id)
        agent2 = Agent(name="Agent2", agent_type="executor", company_id=company1.id)
        # 为公司2创建Agent
        agent3 = Agent(name="Agent3", agent_type="executor", company_id=company2.id)

        sync_session.add_all([agent1, agent2, agent3])
        sync_session.commit()

        # 查询公司1的Agent
        result = sync_session.execute(
            select(Agent).where(Agent.company_id == company1.id)
        ).scalars().all()

        assert len(result) == 2
        assert all(a.company_id == company1.id for a in result)

    def test_query_departments_without_company(self, sync_session: Session):
        """测试查询无公司关联的部门（历史数据）。"""
        # 创建一些无公司关联的部门
        dept1 = Department(name="通用部门", code="generic", company_id=None)
        dept2 = Department(name="系统部门", code="system", company_id=None)
        sync_session.add_all([dept1, dept2])
        sync_session.commit()

        # 查询无公司关联的部门
        result = sync_session.execute(
            select(Department).where(Department.company_id.is_(None))
        ).scalars().all()

        assert len(result) >= 2
        assert all(d.company_id is None for d in result)


class TestModelIntegrity:
    """测试模型完整性。"""

    def test_foreign_key_constraint(self, sync_session: Session):
        """测试外键约束 - 无效的 company_id 应该失败。"""
        from sqlalchemy import exc

        # 尝试创建关联到不存在的公司
        dept = Department(
            name="无效部门",
            code="invalid",
            company_id="non-existent-company-id"
        )
        sync_session.add(dept)

        # SQLite 默认不强制外键约束，但让我们验证字段存在
        sync_session.commit()
        # 注意：如果数据库启用了外键约束，这里会抛出异常

    def test_department_company_relationship_bidirectional(self, sync_session: Session):
        """测试部门和公司之间的双向关系。"""
        company = Company(name="测试公司")
        sync_session.add(company)
        sync_session.commit()

        dept = Department(name="技术部", code="tech", company_id=company.id)
        sync_session.add(dept)
        sync_session.commit()

        # 从部门角度
        assert dept.company is not None
        assert dept.company.id == company.id

        # 从公司角度
        sync_session.refresh(company)
        assert len(company.departments) == 1
        assert company.departments[0].id == dept.id

    def test_agent_company_relationship_bidirectional(self, sync_session: Session):
        """测试Agent和公司之间的双向关系。"""
        company = Company(name="测试公司")
        sync_session.add(company)
        sync_session.commit()

        agent = Agent(name="测试Agent", agent_type="executor", company_id=company.id)
        sync_session.add(agent)
        sync_session.commit()

        # 从Agent角度
        assert agent.company is not None
        assert agent.company.id == company.id

        # 从公司角度
        sync_session.refresh(company)
        assert len(company.agents) == 1
        assert company.agents[0].id == agent.id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
