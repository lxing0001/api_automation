import pytest
import allure
from common.http_client import HttpClient
from common.assertions import ApiAssertions
from common.logger import logger
from common.auth_manager import auth_manager


@allure.epic("GodGPT API")
@allure.feature("用户Profile管理")
class TestUserProfileAPI:
    """GodGPT 用户Profile API测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置设置"""
        # 使用实际的API地址
        self.client = HttpClient("https://station-developer.aevatar.ai")
        self.assertions = ApiAssertions()
        
        # 设置默认请求头
        self.default_headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://godgpt.portkey.finance',
            'priority': 'u=1, i',
            'referer': 'https://godgpt.portkey.finance/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        
        # 获取全局认证token
        self.auth_token = auth_manager.get_auth_token()
        if not self.auth_token:
            logger.warning("无法获取认证token，某些测试可能会跳过")
    
    @allure.story("查询用户Profile信息")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    @pytest.mark.login
    def test_get_user_profile(self):
        """测试查询用户Profile信息"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/profile/user-info"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        with allure.step("发送GET请求查询用户Profile"):
            try:
                response = self.client.get(
                    endpoint,
                    headers=auth_headers
                )
                
                with allure.step("验证响应状态码"):
                    self.assertions.assert_status_code(response, 200)
                
                with allure.step("验证响应不为空"):
                    self.assertions.assert_not_empty(response)
                
                with allure.step("验证响应时间"):
                    self.assertions.assert_response_time(response, 10.0)
                
                with allure.step("验证响应格式"):
                    try:
                        response_json = response.json()
                        # 验证响应是JSON对象
                        assert isinstance(response_json, dict), "响应应该是JSON对象"
                        
                        # 检查是否包含用户信息字段
                        if 'username' in response_json:
                            assert isinstance(response_json['username'], str), "username应该是字符串"
                        
                        if 'email' in response_json:
                            assert isinstance(response_json['email'], str), "email应该是字符串"
                        
                        if 'roles' in response_json:
                            assert isinstance(response_json['roles'], list), "roles应该是数组"
                        
                        logger.info(f"用户Profile信息: {response_json}")
                        
                    except Exception as e:
                        logger.warning(f"响应格式验证失败: {e}")
                        pytest.fail("响应格式验证失败")
                        
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("查询用户Profile-无效Token")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_get_user_profile_invalid_token(self):
        """测试查询用户Profile-无效Token"""
        endpoint = "/godgptprod-client/api/profile/user-info"
        
        # 设置无效的认证token
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = 'Bearer invalid_token_here'
        
        with allure.step("发送GET请求查询用户Profile-无效Token"):
            try:
                response = self.client.get(
                    endpoint,
                    headers=auth_headers
                )
                
                with allure.step("验证响应状态码为401"):
                    self.assertions.assert_status_code(response, 401)
                    
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.info("预期的认证失败")
                    pytest.fail("认证失败，测试失败")
                else:
                    raise e
    
    @allure.story("查询用户Profile-缺少Token")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_get_user_profile_missing_token(self):
        """测试查询用户Profile-缺少Token"""
        endpoint = "/godgptprod-client/api/profile/user-info"
        
        with allure.step("发送GET请求查询用户Profile-缺少Token"):
            try:
                response = self.client.get(
                    endpoint,
                    headers=self.default_headers
                )
                
                with allure.step("验证响应状态码为401"):
                    self.assertions.assert_status_code(response, 401)
                    
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.info("预期的认证失败")
                    pytest.fail("认证失败，测试失败")
                else:
                    raise e
    
    @allure.story("查询用户Profile-无效的请求方法")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    def test_get_user_profile_invalid_method(self):
        """测试查询用户Profile-使用POST方法"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/profile/user-info"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        with allure.step("发送POST请求到查询Profile端点"):
            try:
                response = self.client.post(
                    endpoint,
                    headers=auth_headers
                )
                
                with allure.step("验证响应状态码为405"):
                    self.assertions.assert_status_code(response, 405)
                    
            except Exception as e:
                if "405" in str(e):
                    logger.info("预期的405错误")
                    pytest.skip("方法不允许，跳过此测试")
                else:
                    raise e
    
    @allure.story("查询用户Profile-性能测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    def test_get_user_profile_performance(self):
        """测试查询用户Profile-性能测试"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/profile/user-info"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        with allure.step("发送GET请求查询用户Profile"):
            try:
                response = self.client.get(
                    endpoint,
                    headers=auth_headers
                )
                
                with allure.step("验证响应状态码"):
                    self.assertions.assert_status_code(response, 200)
                
                with allure.step("验证响应时间不超过5秒"):
                    self.assertions.assert_response_time(response, 5.0)
                    
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("查询用户Profile-并发测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    def test_get_user_profile_concurrent(self):
        """测试查询用户Profile-并发测试"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/profile/user-info"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        responses = []
        
        with allure.step("发送3个并发Profile查询请求"):
            try:
                import concurrent.futures
                
                def make_profile_request():
                    return self.client.get(
                        endpoint,
                        headers=auth_headers
                    )
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    futures = [executor.submit(make_profile_request) for _ in range(3)]
                    responses = [future.result() for future in concurrent.futures.as_completed(futures)]
                
                with allure.step("验证所有请求都成功"):
                    for i, response in enumerate(responses):
                        assert response.status_code == 200, f"Profile查询请求{i+1}失败，状态码: {response.status_code}"
                        self.assertions.assert_not_empty(response)
                
                logger.info(f"Profile并发测试通过，所有{len(responses)}个请求都成功")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e 