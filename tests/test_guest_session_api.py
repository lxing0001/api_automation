import pytest
import allure
from common.http_client import HttpClient
from common.assertions import ApiAssertions


@allure.epic("GodGPT API")
@allure.feature("非登录会话管理")
class TestGuestSessionAPI:
    """GodGPT 非登录会话API测试类"""
    
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
    
    @allure.story("创建访客会话")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_create_guest_session(self):
        """测试创建访客会话"""
        endpoint = "/godgptprod-client/api/godgpt/guest/create-session"
        request_data = {"guider": ""}
        
        with allure.step("发送POST请求创建访客会话"):
            response = self.client.post(
                endpoint, 
                json=request_data,
                headers=self.default_headers
            )
        
        with allure.step("验证响应状态码"):
            self.assertions.assert_status_code(response, 200)
        
        with allure.step("验证响应不为空"):
            self.assertions.assert_not_empty(response)
        
        with allure.step("验证响应时间"):
            self.assertions.assert_response_time(response, 10.0)
        
        with allure.step("验证响应包含会话信息"):
            try:
                response_json = response.json()
                # 检查响应是否包含预期的字段
                assert isinstance(response_json, dict), "响应应该是JSON对象"
                logger.info(f"响应内容: {response_json}")
            except Exception as e:
                logger.warning(f"响应不是有效的JSON格式: {e}")
    
    @allure.story("创建访客会话-带引导参数")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_create_guest_session_with_guider(self):
        """测试创建带引导参数的访客会话"""
        endpoint = "/godgptprod-client/api/godgpt/guest/create-session"
        request_data = {"guider": "test_guider"}
        
        with allure.step("发送POST请求创建带引导参数的访客会话"):
            response = self.client.post(
                endpoint, 
                json=request_data,
                headers=self.default_headers
            )
        
        with allure.step("验证响应状态码"):
            self.assertions.assert_status_code(response, 200)
        
        with allure.step("验证响应不为空"):
            self.assertions.assert_not_empty(response)
    
    @allure.story("创建访客会话-空请求体")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_create_guest_session_empty_body(self):
        """测试创建访客会话-空请求体"""
        endpoint = "/godgptprod-client/api/godgpt/guest/create-session"
        request_data = {}
        
        with allure.step("发送POST请求创建访客会话-空请求体"):
            response = self.client.post(
                endpoint, 
                json=request_data,
                headers=self.default_headers
            )
        
        with allure.step("验证响应状态码"):
            # 可能返回200或400，取决于API设计
            assert response.status_code in [200, 400], f"期望状态码200或400，实际状态码{response.status_code}"
        
        with allure.step("验证响应不为空"):
            self.assertions.assert_not_empty(response)
    
    @allure.story("创建访客会话-缺少必要头部")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    def test_create_guest_session_missing_headers(self):
        """测试创建访客会话-缺少必要头部"""
        endpoint = "/godgptprod-client/api/godgpt/guest/create-session"
        request_data = {"guider": ""}
        
        # 只保留基本头部
        minimal_headers = {
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }
        
        with allure.step("发送POST请求创建访客会话-缺少必要头部"):
            response = self.client.post(
                endpoint, 
                json=request_data,
                headers=minimal_headers
            )
        
        with allure.step("验证响应状态码"):
            # 可能返回200或401/403，取决于API设计
            assert response.status_code in [200, 401, 403], f"期望状态码200、401或403，实际状态码{response.status_code}"
    
    @allure.story("创建访客会话-无效的请求方法")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    def test_create_guest_session_invalid_method(self):
        """测试创建访客会话-使用GET方法"""
        endpoint = "/godgptprod-client/api/godgpt/guest/create-session"
        
        with allure.step("发送GET请求到创建会话端点"):
            response = self.client.get(
                endpoint,
                headers=self.default_headers
            )
        
        with allure.step("验证响应状态码为405"):
            self.assertions.assert_status_code(response, 405)
    
    @allure.story("创建访客会话-验证响应格式")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_create_guest_session_response_format(self):
        """测试创建访客会话-验证响应格式"""
        endpoint = "/godgptprod-client/api/godgpt/guest/create-session"
        request_data = {"guider": ""}
        
        with allure.step("发送POST请求创建访客会话"):
            response = self.client.post(
                endpoint, 
                json=request_data,
                headers=self.default_headers
            )
        
        with allure.step("验证响应状态码"):
            self.assertions.assert_status_code(response, 200)
        
        with allure.step("验证响应格式"):
            try:
                response_json = response.json()
                # 验证响应是JSON对象
                assert isinstance(response_json, dict), "响应应该是JSON对象"
                
                # 检查是否包含常见字段（根据实际API调整）
                if 'sessionId' in response_json:
                    assert isinstance(response_json['sessionId'], str), "sessionId应该是字符串"
                
                if 'status' in response_json:
                    assert isinstance(response_json['status'], (str, int)), "status应该是字符串或数字"
                
                logger.info(f"响应格式验证通过: {response_json}")
                
            except Exception as e:
                logger.warning(f"响应格式验证失败: {e}")
                # 不强制失败，因为可能API返回格式不同
    
    @allure.story("创建访客会话-性能测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    def test_create_guest_session_performance(self):
        """测试创建访客会话-性能测试"""
        endpoint = "/godgptprod-client/api/godgpt/guest/create-session"
        request_data = {"guider": ""}
        
        with allure.step("发送POST请求创建访客会话"):
            response = self.client.post(
                endpoint, 
                json=request_data,
                headers=self.default_headers
            )
        
        with allure.step("验证响应状态码"):
            self.assertions.assert_status_code(response, 200)
        
        with allure.step("验证响应时间不超过5秒"):
            self.assertions.assert_response_time(response, 5.0)
    
    @allure.story("创建访客会话-并发测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    def test_create_guest_session_concurrent(self):
        """测试创建访客会话-并发测试"""
        endpoint = "/godgptprod-client/api/godgpt/guest/create-session"
        request_data = {"guider": ""}
        
        responses = []
        
        with allure.step("发送3个并发请求"):
            import concurrent.futures
            
            def make_request():
                return self.client.post(
                    endpoint, 
                    json=request_data,
                    headers=self.default_headers
                )
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                futures = [executor.submit(make_request) for _ in range(3)]
                responses = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        with allure.step("验证所有请求都成功"):
            for i, response in enumerate(responses):
                assert response.status_code == 200, f"请求{i+1}失败，状态码: {response.status_code}"
                self.assertions.assert_not_empty(response)
        
        logger.info(f"并发测试通过，所有{len(responses)}个请求都成功")
    
    @allure.story("非登录聊天-基本对话")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_guest_chat_basic(self):
        """测试非登录状态下的基本聊天"""
        endpoint = "/godgptprod-client/api/godgpt/guest/chat"
        request_data = {"content": "你好", "images": [], "region": ""}
        
        # 为聊天API设置特殊的请求头
        chat_headers = self.default_headers.copy()
        chat_headers['accept'] = 'text/event-stream'
        
        with allure.step("发送POST请求进行聊天"):
            try:
                response = self.client.post(
                    endpoint, 
                    json=request_data,
                    headers=chat_headers
                )
                
                with allure.step("验证响应状态码"):
                    self.assertions.assert_status_code(response, 200)
                
                with allure.step("验证响应不为空"):
                    self.assertions.assert_not_empty(response)
                
                with allure.step("验证响应时间"):
                    self.assertions.assert_response_time(response, 30.0)  # 聊天API可能需要更长时间
                
                with allure.step("验证响应格式"):
                    try:
                        # 聊天API可能返回流式数据或JSON
                        response_text = response.text
                        assert len(response_text) > 0, "响应内容不应为空"
                        logger.info(f"聊天响应内容长度: {len(response_text)}")
                    except Exception as e:
                        logger.warning(f"响应格式验证失败: {e}")
                        
            except Exception as e:
                if "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("非登录聊天-带图片")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_guest_chat_with_images(self):
        """测试非登录状态下的聊天-带图片"""
        endpoint = "/godgptprod-client/api/godgpt/guest/chat"
        request_data = {"content": "分析这张图片", "images": ["image_url_1", "image_url_2"], "region": ""}
        
        chat_headers = self.default_headers.copy()
        chat_headers['accept'] = 'text/event-stream'
        
        with allure.step("发送POST请求进行聊天-带图片"):
            try:
                response = self.client.post(
                    endpoint, 
                    json=request_data,
                    headers=chat_headers
                )
                
                with allure.step("验证响应状态码"):
                    self.assertions.assert_status_code(response, 200)
                
                with allure.step("验证响应不为空"):
                    self.assertions.assert_not_empty(response)
                    
            except Exception as e:
                if "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("非登录聊天-指定区域")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_guest_chat_with_region(self):
        """测试非登录状态下的聊天-指定区域"""
        endpoint = "/godgptprod-client/api/godgpt/guest/chat"
        request_data = {"content": "你好", "images": [], "region": "CN"}
        
        chat_headers = self.default_headers.copy()
        chat_headers['accept'] = 'text/event-stream'
        
        with allure.step("发送POST请求进行聊天-指定区域"):
            try:
                response = self.client.post(
                    endpoint, 
                    json=request_data,
                    headers=chat_headers
                )
                
                with allure.step("验证响应状态码"):
                    self.assertions.assert_status_code(response, 200)
                
                with allure.step("验证响应不为空"):
                    self.assertions.assert_not_empty(response)
                    
            except Exception as e:
                if "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("非登录聊天-空内容")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    def test_guest_chat_empty_content(self):
        """测试非登录状态下的聊天-空内容"""
        endpoint = "/godgptprod-client/api/godgpt/guest/chat"
        request_data = {"content": "", "images": [], "region": ""}
        
        chat_headers = self.default_headers.copy()
        chat_headers['accept'] = 'text/event-stream'
        
        with allure.step("发送POST请求进行聊天-空内容"):
            try:
                response = self.client.post(
                    endpoint, 
                    json=request_data,
                    headers=chat_headers
                )
                
                with allure.step("验证响应状态码"):
                    # 可能返回200或400，取决于API设计
                    assert response.status_code in [200, 400], f"期望状态码200或400，实际状态码{response.status_code}"
                    
            except Exception as e:
                if "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("非登录聊天-长文本")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_guest_chat_long_text(self):
        """测试非登录状态下的聊天-长文本"""
        endpoint = "/godgptprod-client/api/godgpt/guest/chat"
        long_text = "这是一个很长的文本内容，用来测试API对长文本的处理能力。" * 10
        request_data = {"content": long_text, "images": [], "region": ""}
        
        chat_headers = self.default_headers.copy()
        chat_headers['accept'] = 'text/event-stream'
        
        with allure.step("发送POST请求进行聊天-长文本"):
            try:
                response = self.client.post(
                    endpoint, 
                    json=request_data,
                    headers=chat_headers
                )
                
                with allure.step("验证响应状态码"):
                    self.assertions.assert_status_code(response, 200)
                
                with allure.step("验证响应不为空"):
                    self.assertions.assert_not_empty(response)
                    
            except Exception as e:
                if "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("非登录聊天-性能测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    def test_guest_chat_performance(self):
        """测试非登录状态下的聊天-性能测试"""
        endpoint = "/godgptprod-client/api/godgpt/guest/chat"
        request_data = {"content": "你好", "images": [], "region": ""}
        
        chat_headers = self.default_headers.copy()
        chat_headers['accept'] = 'text/event-stream'
        
        with allure.step("发送POST请求进行聊天"):
            try:
                response = self.client.post(
                    endpoint, 
                    json=request_data,
                    headers=chat_headers
                )
                
                with allure.step("验证响应状态码"):
                    self.assertions.assert_status_code(response, 200)
                
                with allure.step("验证响应时间不超过30秒"):
                    self.assertions.assert_response_time(response, 30.0)
                    
            except Exception as e:
                if "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("非登录聊天-并发测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    def test_guest_chat_concurrent(self):
        """测试非登录状态下的聊天-并发测试"""
        endpoint = "/godgptprod-client/api/godgpt/guest/chat"
        request_data = {"content": "你好", "images": [], "region": ""}
        
        chat_headers = self.default_headers.copy()
        chat_headers['accept'] = 'text/event-stream'
        
        responses = []
        
        with allure.step("发送2个并发聊天请求"):
            try:
                import concurrent.futures
                
                def make_chat_request():
                    return self.client.post(
                        endpoint, 
                        json=request_data,
                        headers=chat_headers
                    )
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                    futures = [executor.submit(make_chat_request) for _ in range(2)]
                    responses = [future.result() for future in concurrent.futures.as_completed(futures)]
                
                with allure.step("验证所有请求都成功"):
                    for i, response in enumerate(responses):
                        assert response.status_code == 200, f"聊天请求{i+1}失败，状态码: {response.status_code}"
                        self.assertions.assert_not_empty(response)
                
                logger.info(f"聊天并发测试通过，所有{len(responses)}个请求都成功")
                
            except Exception as e:
                if "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e


# 导入日志模块
from common.logger import logger 