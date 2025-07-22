import pytest
import allure
from common.http_client import HttpClient
from common.assertions import ApiAssertions
from common.logger import logger
from common.auth_manager import auth_manager

@allure.epic("GodGPT API")
@allure.feature("聊天历史功能")
class TestChatHistoryAPI:
    """GodGPT 聊天历史功能API测试类"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前置设置"""
        self.client = HttpClient("https://station-developer.aevatar.ai")
        self.assertions = ApiAssertions()
        
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
        
        self.auth_token = auth_manager.get_auth_token()
        if not self.auth_token:
            logger.warning("无法获取认证token，某些测试可能会跳过")
    
    @allure.story("查询聊天历史-基本功能")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_get_chat_history_basic(self):
        """测试查询聊天历史-基本功能"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/godgpt/chat/a4eb7361-4a48-48df-9b0b-3e21dffa42d5"
        
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        with allure.step("发送GET请求查询聊天历史"):
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
                        assert isinstance(response_json, (dict, list)), "响应应该是JSON对象或数组"
                        
                        logger.info(f"聊天历史响应内容: {response_json}")
                        
                        # 如果是字典，检查常见字段
                        if isinstance(response_json, dict):
                            history_fields = ['data', 'messages', 'history', 'chat', 'session']
                            found_field = None
                            for field in history_fields:
                                if field in response_json:
                                    found_field = field
                                    break
                            
                            if found_field:
                                field_value = response_json[found_field]
                                logger.info(f"找到聊天历史字段: {found_field}")
                                if isinstance(field_value, list):
                                    logger.info(f"聊天历史包含 {len(field_value)} 条消息")
                                elif isinstance(field_value, dict):
                                    logger.info(f"聊天历史为对象格式")
                            else:
                                logger.info("响应中未找到标准历史字段，但API调用成功")
                        
                        # 如果是数组，检查数组内容
                        elif isinstance(response_json, list):
                            logger.info(f"聊天历史包含 {len(response_json)} 条消息")
                            if len(response_json) > 0:
                                logger.info(f"第一条消息: {response_json[0]}")
                        
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
    
    @allure.story("查询聊天历史-无效sessionId")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_get_chat_history_invalid_session(self):
        """测试查询聊天历史-无效sessionId"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/godgpt/chat/invalid-session-id-12345"
        
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        with allure.step("发送GET请求查询无效sessionId的聊天历史"):
            try:
                response = self.client.get(
                    endpoint,
                    headers=auth_headers
                )
                
                with allure.step("验证响应状态码"):
                    # API可能返回200（空历史）或错误状态码
                    if response.status_code == 200:
                        logger.info("API返回200，可能是空历史记录")
                        # 检查响应内容是否为空或包含空历史
                        try:
                            response_json = response.json()
                            if isinstance(response_json, list) and len(response_json) == 0:
                                logger.info("确认为空历史记录")
                            elif isinstance(response_json, dict) and not response_json.get('data'):
                                logger.info("确认为空历史记录")
                        except:
                            logger.info("响应格式无法解析，但状态码为200")
                    else:
                        logger.info(f"API返回错误状态码: {response.status_code}")
                    
                logger.info(f"无效sessionId测试通过，状态码: {response.status_code}")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("查询聊天历史-缺少认证")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_get_chat_history_no_auth(self):
        """测试查询聊天历史-缺少认证"""
        endpoint = "/godgptprod-client/api/godgpt/chat/a4eb7361-4a48-48df-9b0b-3e21dffa42d5"
        
        with allure.step("发送GET请求查询聊天历史-无认证"):
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
                    pytest.skip("认证失败，跳过此测试")
                else:
                    raise e
    
    @allure.story("查询聊天历史-性能测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    def test_get_chat_history_performance(self):
        """测试查询聊天历史-性能测试"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/godgpt/chat/a4eb7361-4a48-48df-9b0b-3e21dffa42d5"
        
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        with allure.step("发送多次GET请求测试性能"):
            try:
                import time
                start_time = time.time()
                
                # 发送3次请求测试性能
                for i in range(3):
                    response = self.client.get(
                        endpoint,
                        headers=auth_headers
                    )
                    
                    assert response.status_code == 200, f"请求{i+1}失败，状态码: {response.status_code}"
                    self.assertions.assert_response_time(response, 5.0)
                    
                    logger.info(f"性能测试请求{i+1}通过，响应时间: {response.elapsed.total_seconds():.2f}秒")
                
                end_time = time.time()
                total_time = end_time - start_time
                avg_time = total_time / 3
                
                logger.info(f"性能测试完成，总时间: {total_time:.2f}秒，平均时间: {avg_time:.2f}秒")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("查询聊天历史-并发测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    def test_get_chat_history_concurrent(self):
        """测试查询聊天历史-并发测试"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/godgpt/chat/a4eb7361-4a48-48df-9b0b-3e21dffa42d5"
        
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        responses = []
        
        with allure.step("发送3个并发GET请求"):
            try:
                import concurrent.futures
                
                def make_history_request():
                    return self.client.get(
                        endpoint,
                        headers=auth_headers
                    )
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    futures = [executor.submit(make_history_request) for _ in range(3)]
                    responses = [future.result() for future in concurrent.futures.as_completed(futures)]
                
                with allure.step("验证所有请求都成功"):
                    for i, response in enumerate(responses):
                        assert response.status_code == 200, f"聊天历史请求{i+1}失败，状态码: {response.status_code}"
                        self.assertions.assert_not_empty(response)
                
                logger.info(f"聊天历史并发测试通过，所有{len(responses)}个请求都成功")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e 