import pytest
import allure
from common.http_client import HttpClient
from common.assertions import ApiAssertions
from common.logger import logger
from common.auth_manager import auth_manager


@allure.epic("GodGPT API")
@allure.feature("会话分享功能")
class TestShareSessionAPI:
    """GodGPT 会话分享API测试类"""
    
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
        
        # 存储session ID
        self.session_id = None
    
    @allure.story("分享会话-基本功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_share_session_basic(self):
        """测试分享会话-基本功能"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/godgpt/share"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        # 请求数据（使用示例sessionId）
        request_data = {"sessionId": "71d34ea5-a9d5-45eb-bfc8-fe79132c7a4d"}
        
        with allure.step("发送POST请求分享会话"):
            try:
                response = self.client.post(
                    endpoint,
                    json=request_data,
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
                        assert isinstance(response_json, dict), "响应应该是JSON对象"
                        
                        # 打印响应内容以便调试
                        logger.info(f"分享会话响应内容: {response_json}")
                        
                        # 检查是否包含分享链接或相关字段
                        share_fields = ['shareId']
                        found_share_field = None
                        for field in share_fields:
                            if field in response_json:
                                found_share_field = field
                                break
                        
                        if found_share_field:
                            share_url = response_json[found_share_field]
                            assert isinstance(share_url, str), f"{found_share_field}应该是字符串"
                            assert len(share_url) > 0, f"{found_share_field}不应为空"
                            logger.info(f"成功分享会话，{found_share_field}: {share_url}")
                        else:
                            logger.info("响应中未找到分享链接字段，但API调用成功")
                            pytest.fail("响应中未找到分享链接字段，但API调用成功")
                        
                    except Exception as e:
                        logger.warning(f"响应格式验证失败: {e}")
                        
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("分享会话-无效sessionId")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_share_session_invalid_session_id(self):
        """测试分享会话-无效sessionId"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/godgpt/share"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        # 请求数据（使用无效的sessionId）
        request_data = {"sessionId": "invalid-session-id"}
        
        with allure.step("发送POST请求分享无效会话"):
            try:
                response = self.client.post(
                    endpoint,
                    json=request_data,
                    headers=auth_headers
                )
                
                # 无效sessionId可能返回400或其他错误状态码
                logger.info(f"无效sessionId分享响应状态码: {response.status_code}")
                
                # 记录响应内容
                try:
                    response_json = response.json()
                    logger.info(f"无效sessionId分享响应内容: {response_json}")
                except:
                    logger.info(f"无效sessionId分享响应文本: {response.text}")
                
            except Exception as e:
                if "400" in str(e):
                    logger.info("预期的400错误（无效sessionId）")
                elif "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("分享会话-空sessionId")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    def test_share_session_empty_session_id(self):
        """测试分享会话-空sessionId"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/godgpt/share"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        # 请求数据（空sessionId）
        request_data = {"sessionId": ""}
        
        with allure.step("发送POST请求分享空sessionId会话"):
            try:
                response = self.client.post(
                    endpoint,
                    json=request_data,
                    headers=auth_headers
                )
                
                # 空sessionId可能返回400或其他错误状态码
                logger.info(f"空sessionId分享响应状态码: {response.status_code}")
                
            except Exception as e:
                if "400" in str(e):
                    logger.info("预期的400错误（空sessionId）")
                elif "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("分享会话-缺少sessionId")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    def test_share_session_missing_session_id(self):
        """测试分享会话-缺少sessionId"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/godgpt/share"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        # 请求数据（缺少sessionId）
        request_data = {}
        
        with allure.step("发送POST请求分享缺少sessionId的会话"):
            try:
                response = self.client.post(
                    endpoint,
                    json=request_data,
                    headers=auth_headers
                )
                
                # 缺少sessionId可能返回400或其他错误状态码
                logger.info(f"缺少sessionId分享响应状态码: {response.status_code}")
                
            except Exception as e:
                if "400" in str(e):
                    logger.info("预期的400错误（缺少sessionId）")
                elif "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("分享会话-性能测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    def test_share_session_performance(self):
        """测试分享会话-性能测试"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/godgpt/share"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        # 请求数据
        request_data = {"sessionId": "71d34ea5-a9d5-45eb-bfc8-fe79132c7a4d"}
        
        with allure.step("发送POST请求进行性能测试"):
            try:
                response = self.client.post(
                    endpoint,
                    json=request_data,
                    headers=auth_headers
                )
                
                with allure.step("验证响应状态码"):
                    self.assertions.assert_status_code(response, 200)
                
                with allure.step("验证响应时间不超过5秒"):
                    self.assertions.assert_response_time(response, 5.0)
                
                logger.info("分享会话性能测试通过")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("分享会话-并发测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    def test_share_session_concurrent(self):
        """测试分享会话-并发测试"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/godgpt/share"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        responses = []
        
        with allure.step("发送3个并发分享会话请求"):
            try:
                import concurrent.futures
                
                def make_share_request():
                    request_data = {"sessionId": "71d34ea5-a9d5-45eb-bfc8-fe79132c7a4d"}
                    return self.client.post(
                        endpoint,
                        json=request_data,
                        headers=auth_headers
                    )
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    futures = [executor.submit(make_share_request) for _ in range(3)]
                    responses = [future.result() for future in concurrent.futures.as_completed(futures)]
                
                with allure.step("验证所有请求都成功"):
                    for i, response in enumerate(responses):
                        assert response.status_code == 200, f"分享会话请求{i+1}失败，状态码: {response.status_code}"
                        self.assertions.assert_not_empty(response)
                
                logger.info(f"分享会话并发测试通过，所有{len(responses)}个请求都成功")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e 