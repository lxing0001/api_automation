import json
from typing import Any, Dict, List, Union
import jsonschema
from common.logger import logger


class ApiAssertions:
    """API断言工具类"""
    
    @staticmethod
    def assert_status_code(response, expected_status_code: int) -> None:
        """断言响应状态码"""
        actual_status_code = response.status_code
        assert actual_status_code == expected_status_code, \
            f"期望状态码 {expected_status_code}, 实际状态码 {actual_status_code}"
        logger.info(f"状态码断言通过: {actual_status_code}")
    
    @staticmethod
    def assert_response_contains(response, expected_content: str) -> None:
        """断言响应内容包含指定字符串"""
        response_text = response.text
        assert expected_content in response_text, \
            f"响应内容不包含 '{expected_content}', 实际响应: {response_text[:200]}..."
        logger.info(f"响应内容包含断言通过: {expected_content}")
    
    @staticmethod
    def assert_json_contains(response, expected_key: str, expected_value: Any = None) -> None:
        """断言JSON响应包含指定键值"""
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            raise AssertionError("响应不是有效的JSON格式")
        
        assert expected_key in response_json, \
            f"JSON响应不包含键 '{expected_key}', 实际响应: {response_json}"
        
        if expected_value is not None:
            actual_value = response_json[expected_key]
            assert actual_value == expected_value, \
                f"键 '{expected_key}' 的值不匹配, 期望: {expected_value}, 实际: {actual_value}"
        
        logger.info(f"JSON包含断言通过: {expected_key}")
    
    @staticmethod
    def assert_json_schema(response, schema: Dict[str, Any]) -> None:
        """断言JSON响应符合指定schema"""
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            raise AssertionError("响应不是有效的JSON格式")
        
        try:
            jsonschema.validate(instance=response_json, schema=schema)
            logger.info("JSON Schema验证通过")
        except jsonschema.exceptions.ValidationError as e:
            raise AssertionError(f"JSON Schema验证失败: {e.message}")
    
    @staticmethod
    def assert_response_time(response, max_time: float) -> None:
        """断言响应时间不超过指定值"""
        response_time = response.elapsed.total_seconds()
        assert response_time <= max_time, \
            f"响应时间超过限制, 期望 <= {max_time}秒, 实际: {response_time}秒"
        logger.info(f"响应时间断言通过: {response_time}秒")
    
    @staticmethod
    def assert_header_contains(response, header_name: str, expected_value: str = None) -> None:
        """断言响应头包含指定值"""
        headers = response.headers
        assert header_name in headers, \
            f"响应头不包含 '{header_name}', 实际响应头: {dict(headers)}"
        
        if expected_value is not None:
            actual_value = headers[header_name]
            assert actual_value == expected_value, \
                f"响应头 '{header_name}' 的值不匹配, 期望: {expected_value}, 实际: {actual_value}"
        
        logger.info(f"响应头断言通过: {header_name}")
    
    @staticmethod
    def assert_list_length(response, expected_length: int) -> None:
        """断言响应是列表且长度符合预期"""
        try:
            response_json = response.json()
        except json.JSONDecodeError:
            raise AssertionError("响应不是有效的JSON格式")
        
        assert isinstance(response_json, list), \
            f"响应不是列表格式, 实际类型: {type(response_json)}"
        
        actual_length = len(response_json)
        assert actual_length == expected_length, \
            f"列表长度不匹配, 期望: {expected_length}, 实际: {actual_length}"
        
        logger.info(f"列表长度断言通过: {actual_length}")
    
    @staticmethod
    def assert_not_empty(response) -> None:
        """断言响应不为空"""
        response_text = response.text.strip()
        assert response_text, "响应内容为空"
        logger.info("响应非空断言通过")
    
    @staticmethod
    def assert_custom_condition(response, condition_func, description: str = "") -> None:
        """自定义断言条件"""
        try:
            result = condition_func(response)
            assert result, f"自定义断言失败: {description}"
            logger.info(f"自定义断言通过: {description}")
        except Exception as e:
            raise AssertionError(f"自定义断言异常: {description}, 错误: {str(e)}") 