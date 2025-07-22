"""
认证管理器使用示例

这个文件展示了如何在测试中使用全局认证管理器
"""

import pytest
import allure
from common.http_client import HttpClient
from common.assertions import ApiAssertions
from common.auth_manager import auth_manager
from common.logger import logger


@allure.epic("认证使用示例")
@allure.feature("认证Token使用")
class TestAuthUsageExample:
    """认证使用示例测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置设置"""
        self.client = HttpClient("https://station-developer.aevatar.ai")
        self.assertions = ApiAssertions()
        
        # 设置默认请求头
        self.default_headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://godgpt.portkey.finance',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    @allure.story("使用全局认证Token")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_with_global_auth_token(self):
        """示例：使用全局认证token进行API调用"""
        
        # 方法1：直接获取token
        token = auth_manager.get_auth_token()
        if not token:
            pytest.skip("无法获取认证token")
        
        # 设置认证请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {token}'
        
        # 进行API调用
        endpoint = "/godgptprod-client/api/profile/user-info"
        
        with allure.step("使用全局认证token调用API"):
            try:
                response = self.client.get(endpoint, headers=auth_headers)
                
                # 验证响应
                self.assertions.assert_status_code(response, 200)
                self.assertions.assert_not_empty(response)
                
                logger.info("使用全局认证token成功调用API")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.warning("认证失败，可能需要刷新token")
                    # 强制刷新token
                    new_token = auth_manager.refresh_token()
                    if new_token:
                        auth_headers['authorization'] = f'Bearer {new_token}'
                        response = self.client.get(endpoint, headers=auth_headers)
                        self.assertions.assert_status_code(response, 200)
                        logger.info("刷新token后成功调用API")
                    else:
                        pytest.skip("无法获取有效的认证token")
                else:
                    raise e
    
    @allure.story("检查Token有效性")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_check_token_validity(self):
        """示例：检查token有效性"""
        
        with allure.step("检查当前token是否有效"):
            is_valid = auth_manager.is_token_valid()
            
        if is_valid:
            logger.info("当前token有效")
        else:
            logger.info("当前token无效或即将过期")
            # 获取新token
            new_token = auth_manager.get_auth_token()
            if new_token:
                logger.info("成功获取新token")
            else:
                logger.warning("无法获取新token")
    
    @allure.story("多API调用共享Token")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_multiple_apis_share_token(self):
        """示例：多个API调用共享同一个token"""
        
        # 获取token（所有API调用共享同一个token）
        token = auth_manager.get_auth_token()
        if not token:
            pytest.skip("无法获取认证token")
        
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {token}'
        
        # 模拟多个API调用
        endpoints = [
            "/godgptprod-client/api/profile/user-info",
            # 可以添加更多需要认证的端点
        ]
        
        with allure.step("使用同一个token调用多个API"):
            for endpoint in endpoints:
                try:
                    response = self.client.get(endpoint, headers=auth_headers)
                    self.assertions.assert_status_code(response, 200)
                    logger.info(f"成功调用API: {endpoint}")
                except Exception as e:
                    logger.warning(f"调用API失败: {endpoint}, 错误: {e}")
                    if "401" in str(e) or "403" in str(e):
                        pytest.skip("认证失败，跳过剩余测试")
                    else:
                        raise e


# 使用示例：在其他测试文件中
def example_usage_in_other_tests():
    """
    在其他测试文件中使用认证管理器的示例
    """
    
    # 1. 导入认证管理器
    from common.auth_manager import auth_manager
    
    # 2. 获取认证token
    token = auth_manager.get_auth_token()
    
    # 3. 在请求头中使用
    headers = {
        'authorization': f'Bearer {token}',
        'content-type': 'application/json'
    }
    
    # 4. 进行API调用
    # response = client.get('/api/endpoint', headers=headers)
    
    # 5. 检查token有效性
    if not auth_manager.is_token_valid():
        # token即将过期，可以强制刷新
        auth_manager.refresh_token()
    
    # 6. 清除token（如果需要）
    # auth_manager.clear_token()


if __name__ == "__main__":
    # 运行示例测试
    import pytest
    pytest.main([__file__, "-v"]) 