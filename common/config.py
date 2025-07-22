import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """配置管理类"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config = {
            "base_url": "https://jsonplaceholder.typicode.com",
            "timeout": 30,
            "retry_times": 3,
            "log_level": "INFO",
            "allure_results_dir": "./allure-results",
            "allure_report_dir": "./allure-report"
        }
        
        # 从配置文件加载
        config_path = Path(self.config_file)
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f) or {}
                config.update(file_config)
        
        # 从环境变量覆盖
        for key in config:
            env_key = f"API_TEST_{key.upper()}"
            if env_key in os.environ:
                config[key] = os.environ[env_key]
        
        return config
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self._config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        return self._config.copy() 