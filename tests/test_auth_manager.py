import pytest
import allure
from common.auth_manager import auth_manager
from common.logger import logger


@allure.epic("认证管理")
@allure.feature("认证Token管理")
class TestAuthManager:
    """认证管理器测试类"""
    
    @allure.story("获取认证Token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_get_auth_token(self):
        """测试获取认证token"""
        with allure.step("获取认证token"):
            token = auth_manager.get_auth_token()
            
        with allure.step("验证token不为空"):
            assert token is not None, "认证token不应为空"
            assert isinstance(token, str), "认证token应该是字符串"
            assert len(token) > 0, "认证token长度应大于0"
            
        logger.info(f"成功获取认证token，长度: {len(token)}")
    
    @allure.story("Token有效性检查")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_token_validity(self):
        """测试token有效性检查"""
        with allure.step("获取认证token"):
            token = auth_manager.get_auth_token()
            
        with allure.step("检查token有效性"):
            is_valid = auth_manager.is_token_valid()
            assert is_valid, "token应该是有效的"
            
        logger.info("token有效性检查通过")
    
    @allure.story("强制刷新Token")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_force_refresh_token(self):
        """测试强制刷新token"""
        with allure.step("强制刷新认证token"):
            token = auth_manager.refresh_token()
            
        with allure.step("验证刷新后的token"):
            assert token is not None, "刷新后的认证token不应为空"
            assert isinstance(token, str), "刷新后的认证token应该是字符串"
            assert len(token) > 0, "刷新后的认证token长度应大于0"
            
        logger.info("强制刷新token成功")
    
    @allure.story("清除Token")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    def test_clear_token(self):
        """测试清除token"""
        with allure.step("获取初始token"):
            initial_token = auth_manager.get_auth_token()
            assert initial_token is not None, "初始token不应为空"
            
        with allure.step("清除token"):
            auth_manager.clear_token()
            
        with allure.step("验证token已清除"):
            is_valid = auth_manager.is_token_valid()
            assert not is_valid, "清除后token应该无效"
            
        with allure.step("重新获取token"):
            new_token = auth_manager.get_auth_token()
            assert new_token is not None, "重新获取的token不应为空"
            
        logger.info("token清除和重新获取测试通过")
    
    @allure.story("Token缓存机制")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_token_caching(self):
        """测试token缓存机制"""
        with allure.step("第一次获取token"):
            token1 = auth_manager.get_auth_token()
            assert token1 is not None, "第一次获取的token不应为空"
            
        with allure.step("第二次获取token（应该使用缓存）"):
            token2 = auth_manager.get_auth_token()
            assert token2 is not None, "第二次获取的token不应为空"
            assert token1 == token2, "缓存的token应该与第一次获取的token相同"
            
        logger.info("token缓存机制测试通过") 