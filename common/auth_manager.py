import json
import time
import os
from pathlib import Path
from common.http_client import HttpClient
from common.logger import logger


class AuthManager:
    """认证管理器，用于获取和管理全局认证token"""
    
    def __init__(self):
        self.auth_token = None
        self.token_expires_at = 0
        self.auth_client = HttpClient("https://auth-station.aevatar.ai")
        
        # 认证请求头
        self.auth_headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'content-type': 'application/x-www-form-urlencoded',
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
        
        # 加载.env文件
        self._load_env_file()
        
        # 从环境变量获取认证凭据
        self.auth_credentials = {
            'grant_type': 'password',
            'client_id': 'AevatarAuthServer',
            'apple_app_id': 'com.gpt.god',
            'scope': 'Aevatar offline_access',
            'username': os.getenv('GODGPT_USERNAME'),
            'password': os.getenv('GODGPT_PASSWORD')
        }
        
        # 检查环境变量是否设置
        if not self.auth_credentials['username'] or not self.auth_credentials['password']:
            logger.error("未设置环境变量 GODGPT_USERNAME 或 GODGPT_PASSWORD")
            logger.error("请创建 .env 文件并设置认证信息")
            logger.error("参考 env.example 文件")
            raise ValueError("认证凭据未配置，请设置 GODGPT_USERNAME 和 GODGPT_PASSWORD 环境变量")
    
    def _load_env_file(self):
        """加载.env文件到环境变量"""
        env_file = Path('.env')
        if env_file.exists():
            logger.info("发现 .env 文件，正在加载环境变量")
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
                        logger.debug(f"加载环境变量: {key}")
        else:
            logger.warning("未找到 .env 文件，请创建 .env 文件并设置认证信息")
            logger.warning("参考 env.example 文件")
    
    def get_auth_token(self, force_refresh=False):
        """
        获取认证token，如果token不存在或已过期则重新获取
        
        Args:
            force_refresh (bool): 是否强制刷新token
            
        Returns:
            str: 认证token
        """
        current_time = time.time()
        
        # 检查token是否存在且未过期（预留5分钟缓冲时间）
        if (not force_refresh and 
            self.auth_token and 
            current_time < self.token_expires_at - 300):
            logger.info("使用缓存的认证token")
            return self.auth_token
        
        logger.info("开始获取新的认证token")
        
        try:
            # 构建认证请求数据
            auth_data = '&'.join([f"{k}={v}" for k, v in self.auth_credentials.items()])
            
            # 发送认证请求
            response = self.auth_client.post(
                '/connect/token',
                data=auth_data,
                headers=self.auth_headers
            )
            
            if response.status_code == 200:
                response_json = response.json()
                
                # 提取token信息
                if 'access_token' in response_json:
                    self.auth_token = response_json['access_token']
                    
                    # 计算token过期时间（如果有expires_in字段）
                    if 'expires_in' in response_json:
                        self.token_expires_at = current_time + response_json['expires_in']
                    else:
                        # 默认1小时过期
                        self.token_expires_at = current_time + 3600
                    
                    logger.info(f"成功获取认证token，过期时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.token_expires_at))}")
                    return self.auth_token
                else:
                    logger.error("认证响应中缺少access_token字段")
                    return None
            else:
                logger.error(f"认证请求失败，状态码: {response.status_code}, 响应: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"获取认证token时发生错误: {e}")
            return None
    
    def refresh_token(self):
        """强制刷新认证token"""
        return self.get_auth_token(force_refresh=True)
    
    def is_token_valid(self):
        """检查当前token是否有效"""
        current_time = time.time()
        return (self.auth_token and 
                current_time < self.token_expires_at - 300)  # 预留5分钟缓冲
    
    def clear_token(self):
        """清除当前token"""
        self.auth_token = None
        self.token_expires_at = 0
        logger.info("已清除认证token")


# 创建全局认证管理器实例
auth_manager = AuthManager() 