import json
import random
import string
from typing import Dict, Any, List
from faker import Faker
from common.logger import logger

# 设置中文locale
fake = Faker(['zh_CN'])


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def random_string(length: int = 10) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def random_email() -> str:
        """生成随机邮箱"""
        return fake.email()
    
    @staticmethod
    def random_name() -> str:
        """生成随机姓名"""
        return fake.name()
    
    @staticmethod
    def random_phone() -> str:
        """生成随机手机号"""
        return fake.phone_number()
    
    @staticmethod
    def random_address() -> str:
        """生成随机地址"""
        return fake.address()
    
    @staticmethod
    def random_company() -> str:
        """生成随机公司名"""
        return fake.company()
    
    @staticmethod
    def random_job() -> str:
        """生成随机职位"""
        return fake.job()
    
    @staticmethod
    def random_text(length: int = 100) -> str:
        """生成随机文本"""
        return fake.text(max_nb_chars=length)
    
    @staticmethod
    def random_number(min_val: int = 1, max_val: int = 100) -> int:
        """生成随机数字"""
        return random.randint(min_val, max_val)
    
    @staticmethod
    def random_float(min_val: float = 0.0, max_val: float = 100.0) -> float:
        """生成随机浮点数"""
        return round(random.uniform(min_val, max_val), 2)
    
    @staticmethod
    def random_boolean() -> bool:
        """生成随机布尔值"""
        return random.choice([True, False])
    
    @staticmethod
    def random_choice(choices: List[Any]) -> Any:
        """从列表中随机选择"""
        return random.choice(choices)
    
    @staticmethod
    def random_user_data() -> Dict[str, Any]:
        """生成随机用户数据"""
        return {
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "address": fake.address(),
            "company": fake.company(),
            "job": fake.job(),
            "username": fake.user_name(),
            "password": fake.password(),
            "website": fake.url(),
            "bio": fake.text(max_nb_chars=200)
        }
    
    @staticmethod
    def random_post_data() -> Dict[str, Any]:
        """生成随机文章数据"""
        return {
            "title": fake.sentence(),
            "body": fake.text(max_nb_chars=500),
            "userId": random.randint(1, 10),
            "tags": [fake.word() for _ in range(random.randint(1, 5))],
            "category": fake.word()
        }


class DataManager:
    """测试数据管理器"""
    
    def __init__(self):
        self.generator = TestDataGenerator()
        self._test_data = {}
    
    def generate_user_data(self, count: int = 1) -> List[Dict[str, Any]]:
        """生成用户测试数据"""
        users = []
        for i in range(count):
            user_data = self.generator.random_user_data()
            user_data['id'] = i + 1
            users.append(user_data)
        
        logger.info(f"生成了 {count} 条用户测试数据")
        return users
    
    def generate_post_data(self, count: int = 1) -> List[Dict[str, Any]]:
        """生成文章测试数据"""
        posts = []
        for i in range(count):
            post_data = self.generator.random_post_data()
            post_data['id'] = i + 1
            posts.append(post_data)
        
        logger.info(f"生成了 {count} 条文章测试数据")
        return posts
    
    def save_test_data(self, key: str, data: Any) -> None:
        """保存测试数据"""
        self._test_data[key] = data
        logger.info(f"保存测试数据: {key}")
    
    def get_test_data(self, key: str) -> Any:
        """获取测试数据"""
        return self._test_data.get(key)
    
    def clear_test_data(self) -> None:
        """清空测试数据"""
        self._test_data.clear()
        logger.info("清空所有测试数据")
    
    def export_test_data(self, file_path: str) -> None:
        """导出测试数据到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self._test_data, f, ensure_ascii=False, indent=2)
        logger.info(f"测试数据已导出到: {file_path}")
    
    def import_test_data(self, file_path: str) -> None:
        """从文件导入测试数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self._test_data = json.load(f)
        logger.info(f"测试数据已从文件导入: {file_path}")


# 全局测试数据管理器实例
test_data_manager = DataManager() 