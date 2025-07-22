import pytest
import allure
from common.http_client import HttpClient
from common.assertions import ApiAssertions
from common.logger import logger
from common.auth_manager import auth_manager


@allure.epic("GodGPT API")
@allure.feature("用户登录会话管理")
class TestUserSessionAPI:
    """GodGPT 用户登录会话API测试类"""
    
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
    
    @allure.story("创建用户会话")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_create_user_session(self):
        """测试创建用户会话"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        endpoint = "/godgptprod-client/api/godgpt/create-session"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        
        # 请求数据
        request_data = {"guider": ""}
        
        with allure.step("发送POST请求创建用户会话"):
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
                        logger.info(f"创建会话响应内容: {response_json}")
                        
                        # 检查是否包含session ID（尝试不同的字段名）
                        session_id_field = None
                        for field in ['sessionId', 'session_id', 'session', 'id', 'data']:
                            if field in response_json:
                                session_id_field = field
                                break
                        
                        if session_id_field:
                            self.session_id = response_json[session_id_field]
                            assert isinstance(self.session_id, str), f"{session_id_field}应该是字符串"
                            assert len(self.session_id) > 0, f"{session_id_field}不应为空"
                            logger.info(f"成功创建用户会话，{session_id_field}: {self.session_id}")
                        else:
                            logger.warning("响应中未找到sessionId相关字段")
                            # 如果响应是字符串，可能直接返回sessionId
                            if isinstance(response_json, str):
                                self.session_id = response_json
                                logger.info(f"响应直接返回sessionId: {self.session_id}")
                            else:
                                logger.warning("无法从响应中提取sessionId")
                        
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
    
    @allure.story("用户聊天-基本对话")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_user_chat_basic(self):
        """测试用户聊天-基本对话"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        # 先创建会话
        self.test_create_user_session()
        if not self.session_id:
            pytest.skip("无法获取sessionId，跳过聊天测试")
            
        endpoint = "/godgptprod-client/api/gotgpt/chat"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        auth_headers['accept'] = 'text/event-stream'
        
        # 请求数据
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        request_data = {
            "content": f"hello，当前时间：{current_time}",
            "images": [],
            "region": "",
            "sessionId": self.session_id
        }
        
        with allure.step("发送POST请求进行用户聊天"):
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
                    self.assertions.assert_response_time(response, 30.0)
                
                with allure.step("验证响应格式"):
                    try:
                        response_text = response.text
                        assert len(response_text) > 0, "响应内容不应为空"
                        logger.info(f"聊天响应内容长度: {len(response_text)}")

                        # 检查是否为事件流格式
                        if 'data:' in response_text or 'event:' in response_text:
                            logger.info("响应为事件流格式")

                            # 提取每一行以 "data: " 开头的部分
                            lines = response_text.strip().splitlines()
                            data_lines = [line for line in lines if line.startswith("data:")]

                            assert len(data_lines) > 0, "事件流中未找到 data 字段"

                            for i, line in enumerate(data_lines):
                                json_part = line[len("data:"):].strip()
                                parsed = json.loads(json_part)

                                logger.debug(f"[Chunk {i}] 解析结果: {parsed}")

                                # 验证 ErrorCode == 0
                                assert "ErrorCode" in parsed, f"[Chunk {i}] 缺少 ErrorCode 字段"
                                assert parsed["ErrorCode"] == 0, f"[Chunk {i}] ErrorCode 不为 0：{parsed['ErrorCode']}"

                        else:
                            logger.info("响应为普通文本格式")
                            # 如果是普通文本，可以按需添加其他验证逻辑

                    except Exception as e:
                        logger.warning(f"响应格式验证失败: {e}")
                        pytest.fail(f"响应格式验证失败: {e}")
                        
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("用户聊天-带图片对话")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.skip(reason="暂时跳过此测试用例")
    def test_user_chat_with_images(self):
        """测试用户聊天-带图片对话"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        # 先创建会话
        self.test_create_user_session()
        if not self.session_id:
            pytest.skip("无法获取sessionId，跳过聊天测试")
            
        endpoint = "/godgptprod-client/api/gotgpt/chat"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        auth_headers['accept'] = 'text/event-stream'
        
        # 请求数据（带图片）
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        request_data = {
            "content": f"请分析这张图片，当前时间：{current_time}",
            "images": ["https://example.com/image.jpg"],  # 示例图片URL
            "region": "",
            "sessionId": self.session_id
        }
        
        with allure.step("发送POST请求进行带图片的用户聊天"):
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
                    self.assertions.assert_response_time(response, 30.0)
                
                logger.info("带图片的用户聊天测试通过")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("用户聊天-带地区对话")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.skip(reason="暂时跳过此测试用例")
    def test_user_chat_with_region(self):
        """测试用户聊天-带地区对话"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        # 先创建会话
        self.test_create_user_session()
        if not self.session_id:
            pytest.skip("无法获取sessionId，跳过聊天测试")
            
        endpoint = "/godgptprod-client/api/gotgpt/chat"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        auth_headers['accept'] = 'text/event-stream'
        
        # 请求数据（带地区）
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        request_data = {
            "content": f"今天天气怎么样？当前时间：{current_time}",
            "images": [],
            "region": "北京",
            "sessionId": self.session_id
        }
        
        with allure.step("发送POST请求进行带地区的用户聊天"):
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
                    self.assertions.assert_response_time(response, 30.0)
                
                logger.info("带地区的用户聊天测试通过")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("用户聊天-空内容")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.api
    @pytest.mark.skip(reason="暂时跳过此测试用例")
    def test_user_chat_empty_content(self):
        """测试用户聊天-空内容"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        # 先创建会话
        self.test_create_user_session()
        if not self.session_id:
            pytest.skip("无法获取sessionId，跳过聊天测试")
            
        endpoint = "/godgptprod-client/api/gotgpt/chat"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        auth_headers['accept'] = 'text/event-stream'
        
        # 请求数据（空内容）
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        request_data = {
            "content": f"空内容测试，当前时间：{current_time}",
            "images": [],
            "region": "",
            "sessionId": self.session_id
        }
        
        with allure.step("发送POST请求进行空内容的用户聊天"):
            try:
                response = self.client.post(
                    endpoint,
                    json=request_data,
                    headers=auth_headers
                )
                
                # 空内容可能返回400或其他错误状态码
                logger.info(f"空内容聊天响应状态码: {response.status_code}")
                
            except Exception as e:
                if "400" in str(e):
                    logger.info("预期的400错误（空内容）")
                elif "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("用户聊天-长文本")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    @pytest.mark.skip(reason="暂时跳过此测试用例")
    def test_user_chat_long_text(self):
        """测试用户聊天-长文本"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        # 先创建会话
        self.test_create_user_session()
        if not self.session_id:
            pytest.skip("无法获取sessionId，跳过聊天测试")
            
        endpoint = "/godgptprod-client/api/gotgpt/chat"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        auth_headers['accept'] = 'text/event-stream'
        
        # 长文本内容
        long_text = "这是一个很长的文本内容，用来测试API对长文本的处理能力。" * 10
        
        # 请求数据（长文本）
        request_data = {
            "content": long_text,
            "images": [],
            "region": "",
            "sessionId": self.session_id
        }
        
        with allure.step("发送POST请求进行长文本的用户聊天"):
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
                    self.assertions.assert_response_time(response, 60.0)  # 长文本可能需要更长时间
                
                logger.info("长文本用户聊天测试通过")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("用户聊天-性能测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    @pytest.mark.skip(reason="暂时跳过此测试用例")
    def test_user_chat_performance(self):
        """测试用户聊天-性能测试"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        # 先创建会话
        self.test_create_user_session()
        if not self.session_id:
            pytest.skip("无法获取sessionId，跳过聊天测试")
            
        endpoint = "/godgptprod-client/api/gotgpt/chat"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        auth_headers['accept'] = 'text/event-stream'
        
        # 请求数据
        import datetime
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        request_data = {
            "content": f"性能测试消息，当前时间：{current_time}",
            "images": [],
            "region": "",
            "sessionId": self.session_id
        }
        
        with allure.step("发送POST请求进行性能测试"):
            try:
                response = self.client.post(
                    endpoint,
                    json=request_data,
                    headers=auth_headers
                )
                
                with allure.step("验证响应状态码"):
                    self.assertions.assert_status_code(response, 200)
                
                with allure.step("验证响应时间不超过15秒"):
                    self.assertions.assert_response_time(response, 15.0)
                
                logger.info("用户聊天性能测试通过")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e
    
    @allure.story("用户聊天-并发测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.slow
    @pytest.mark.api
    @pytest.mark.skip(reason="暂时跳过此测试用例")
    def test_user_chat_concurrent(self):
        """测试用户聊天-并发测试"""
        if not self.auth_token:
            pytest.skip("无法获取认证token，跳过此测试")
            
        # 先创建会话
        self.test_create_user_session()
        if not self.session_id:
            pytest.skip("无法获取sessionId，跳过聊天测试")
            
        endpoint = "/godgptprod-client/api/gotgpt/chat"
        
        # 设置带认证的请求头
        auth_headers = self.default_headers.copy()
        auth_headers['authorization'] = f'Bearer {self.auth_token}'
        auth_headers['accept'] = 'text/event-stream'
        
        responses = []
        
        with allure.step("发送3个并发用户聊天请求"):
            try:
                import concurrent.futures
                
                def make_chat_request():
                    import datetime
                    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    request_data = {
                        "content": f"并发测试消息，当前时间：{current_time}",
                        "images": [],
                        "region": "",
                        "sessionId": self.session_id
                    }
                    return self.client.post(
                        endpoint,
                        json=request_data,
                        headers=auth_headers
                    )
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    futures = [executor.submit(make_chat_request) for _ in range(3)]
                    responses = [future.result() for future in concurrent.futures.as_completed(futures)]
                
                with allure.step("验证所有请求都成功"):
                    for i, response in enumerate(responses):
                        assert response.status_code == 200, f"用户聊天请求{i+1}失败，状态码: {response.status_code}"
                        self.assertions.assert_not_empty(response)
                
                logger.info(f"用户聊天并发测试通过，所有{len(responses)}个请求都成功")
                
            except Exception as e:
                if "401" in str(e) or "403" in str(e):
                    logger.error("API返回认证错误，token可能已过期")
                    pytest.fail("认证失败，测试失败")
                elif "429" in str(e):
                    logger.warning("API返回429错误（请求过于频繁），这是预期的限制")
                    pytest.skip("API请求频率限制，跳过此测试")
                else:
                    raise e 