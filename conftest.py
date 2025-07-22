import pytest
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from common.config import Config
from common.logger import logger

@pytest.fixture(scope="session")
def config():
    """全局配置fixture"""
    return Config()

@pytest.fixture(scope="session")
def base_url(config):
    """基础URL fixture"""
    return config.get("base_url", "https://jsonplaceholder.typicode.com")

@pytest.fixture(scope="function")
def test_data():
    """测试数据fixture"""
    return {}

@pytest.fixture(autouse=True)
def setup_test(request):
    """每个测试用例的自动设置"""
    logger.info(f"开始执行测试: {request.node.name}")
    yield
    logger.info(f"测试完成: {request.node.name}")

@pytest.fixture(scope="session")
def allure_environment_info():
    """设置Allure环境信息"""
    return {
        "Python版本": sys.version,
        "pytest版本": pytest.__version__,
        "项目路径": str(project_root),
        "测试环境": os.getenv("TEST_ENV", "dev")
    } 