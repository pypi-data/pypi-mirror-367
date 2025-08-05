"""
集成测试示例 - 真实数据库连接测试

注意: 这些测试需要真实的 PostgreSQL 数据库运行
"""
import pytest
import asyncio
import os
from dotenv import load_dotenv
from quant_async.blotter import Blotter

# Load environment variables from .env file
load_dotenv()


class TestDatabaseIntegration:
    """数据库集成测试 - 需要真实 PostgreSQL"""
    
    @pytest.mark.integration  # 标记为集成测试
    @pytest.mark.asyncio
    async def test_real_postgres_connection_success(self):
        """测试真实数据库连接成功场景"""
        # 从环境变量获取真实数据库配置
        config = {
            'dbhost': os.getenv('TEST_DB_HOST', 'localhost'),
            'dbport': os.getenv('TEST_DB_PORT', '5432'),
            'dbuser': os.getenv('TEST_DB_USER', 'test_user'),
            'dbpass': os.getenv('TEST_DB_PASS', 'test_pass'),
            'dbname': os.getenv('TEST_DB_NAME', 'test_quant_async'),
            'dbskip': False
        }
        
        blotter = Blotter(**config)
        
        try:
            # 🔥 这里没有任何 Mock！直接调用真实函数
            pool = await blotter.get_postgres_connection()
            
            # 验证连接池确实被创建
            assert pool is not None
            
            # 测试真实数据库操作
            async with pool.acquire() as conn:
                # 执行一个简单查询验证连接
                result = await conn.fetchval("SELECT 1")
                assert result == 1
                
                # 测试数据库版本查询
                version = await conn.fetchval("SELECT version()")
                assert "PostgreSQL" in version
                
        finally:
            # 清理：关闭连接池
            if hasattr(blotter, 'pool') and blotter.pool:
                await blotter.pool.close()
    
    @pytest.mark.integration
    @pytest.mark.asyncio 
    async def test_real_postgres_connection_failure(self):
        """测试真实数据库连接失败场景"""
        # 故意使用错误的配置
        config = {
            'dbhost': 'nonexistent_host',  # 不存在的主机
            'dbport': '9999',              # 错误的端口
            'dbuser': 'wrong_user',
            'dbpass': 'wrong_pass', 
            'dbname': 'wrong_db',
            'dbskip': False
        }
        
        blotter = Blotter(**config)
        
        # 验证连接失败时抛出异常
        with pytest.raises(Exception):  # 可能是 ConnectionError, TimeoutError 等
            await blotter.get_postgres_connection()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_database_schema_validation(self):
        """测试数据库 schema 是否符合预期"""
        config = {
            'dbhost': os.getenv('TEST_DB_HOST', 'localhost'),
            'dbport': os.getenv('TEST_DB_PORT', '5432'),
            'dbuser': os.getenv('TEST_DB_USER', 'test_user'),
            'dbpass': os.getenv('TEST_DB_PASS', 'test_pass'),
            'dbname': os.getenv('TEST_DB_NAME', 'test_quant_async'),
            'dbskip': False
        }
        
        blotter = Blotter(**config)
        
        try:
            pool = await blotter.get_postgres_connection()
            
            async with pool.acquire() as conn:
                # 检查必要的表是否存在
                tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                """
                
                tables = await conn.fetch(tables_query)
                table_names = [row['table_name'] for row in tables]
                
                # 验证必要的表存在
                expected_tables = ['symbols', 'bars', 'ticks', 'greeks', 'trades']
                for table in expected_tables:
                    assert table in table_names, f"Missing table: {table}"
                
        finally:
            if hasattr(blotter, 'pool') and blotter.pool:
                await blotter.pool.close()


# 如何运行集成测试的配置示例
"""
# pytest.ini 或 pyproject.toml 中添加:
[tool.pytest.ini_options]
markers = [
    "integration: marks tests as integration tests (deselect with '-m \"not integration\"')",
]

# 运行方式:
# 1. 只运行单元测试 (跳过集成测试):
pytest -m "not integration"

# 2. 只运行集成测试:
pytest -m integration

# 3. 运行所有测试:
pytest
"""