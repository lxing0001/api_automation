# API自动化测试框架

基于 `pytest + requests + allure` 的API自动化测试框架，支持Jenkins集成。

## 🚀 特性

- ✅ **完整的测试框架**: 基于pytest + requests + allure
- ✅ **多环境支持**: 支持dev/test/prod环境配置
- ✅ **Jenkins集成**: 完整的Jenkins流水线配置
- ✅ **详细报告**: 使用Allure生成美观的测试报告
- ✅ **数据驱动**: 支持测试数据生成和管理
- ✅ **断言丰富**: 提供多种API断言方法
- ✅ **日志完善**: 使用loguru进行日志记录
- ✅ **重试机制**: 内置HTTP请求重试策略

## 📁 项目结构

```
auto_test/
├── common/                    # 公共模块
│   ├── __init__.py
│   ├── config.py             # 配置管理
│   ├── logger.py             # 日志管理
│   ├── http_client.py        # HTTP客户端
│   ├── assertions.py         # 断言工具
│   └── test_data.py          # 测试数据管理
├── tests/                    # 测试用例
│   ├── __init__.py
│   ├── test_users_api.py     # 用户API测试
│   ├── test_posts_api.py     # 文章API测试
│   └── test_comments_api.py  # 评论API测试
├── logs/                     # 日志文件
├── allure-results/           # Allure结果文件
├── allure-report/            # Allure报告文件
├── requirements.txt           # Python依赖
├── pytest.ini               # pytest配置
├── conftest.py              # pytest全局配置
├── config.yaml              # 项目配置
├── Jenkinsfile              # Jenkins流水线
├── run_tests.py             # 测试运行脚本
└── README.md                # 项目说明
```

## 🛠️ 环境要求

- Python 3.8+
- pip
- Allure Commandline

## 📦 安装依赖

### 方法一：使用虚拟环境（推荐）

#### macOS/Linux
```bash
# 激活虚拟环境
./activate_venv.sh

# 或者手动创建和激活
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Windows
```cmd
# 激活虚拟环境
activate_venv.bat

# 或者手动创建和激活
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 方法二：直接安装

```bash
# 安装Python依赖
pip install -r requirements.txt
```

### 安装Allure

#### macOS
```bash
brew install allure
```

#### Linux
```bash
wget -O allure-2.24.0.zip https://github.com/allure-framework/allure2/releases/download/2.24.0/allure-2.24.0.zip
unzip allure-2.24.0.zip
sudo mv allure-2.24.0 /opt/allure
export PATH=$PATH:/opt/allure/bin
```

#### Windows
```cmd
# 下载并解压Allure
# 添加到系统PATH环境变量
```

## 🚀 快速开始

### 1. 激活虚拟环境

#### macOS/Linux
```bash
./activate_venv.sh
```

#### Windows
```cmd
activate_venv.bat
```

### 2. 运行所有测试

```bash
python run_tests.py
```

### 3. 运行冒烟测试

```bash
python run_tests.py --markers smoke
```

### 4. 运行回归测试

```bash
python run_tests.py --markers regression
```

### 5. 并行执行测试

```bash
python run_tests.py --parallel
```

### 6. 指定测试环境

```bash
python run_tests.py --env test
```

### 7. 生成并打开报告

```bash
python run_tests.py --open-report
```

### 8. 安装依赖并运行测试

```bash
python run_tests.py --install
```

## 🧪 测试用例

### 认证管理测试 (`test_auth_manager.py`) # Added
- ✅ 获取认证Token
- ✅ Token有效性检查
- ✅ 强制刷新Token
- ✅ 清除Token
- ✅ Token缓存机制

### GodGPT 非登录会话API测试 (`test_guest_session_api.py`) # Updated
- ✅ 创建访客会话
- ✅ 创建带引导参数的访客会话
- ✅ 创建访客会话-空请求体
- ✅ 创建访客会话-缺少必要头部
- ✅ 创建访客会话-无效的请求方法
- ✅ 创建访客会话-验证响应格式
- ✅ 创建访客会话-性能测试
- ✅ 创建访客会话-并发测试
- ✅ 非登录聊天-基本对话
- ✅ 非登录聊天-带图片对话
- ✅ 非登录聊天-带地区对话
- ✅ 非登录聊天-空内容
- ✅ 非登录聊天-长文本
- ✅ 非登录聊天-性能测试
- ✅ 非登录聊天-并发测试

### 用户Profile API测试 (`test_user_profile_api.py`) # Added
- ✅ 查询用户Profile信息
- ✅ 查询用户Profile-无效Token
- ✅ 查询用户Profile-缺少Token
- ✅ 查询用户Profile-无效的请求方法
- ✅ 查询用户Profile-性能测试
- ✅ 查询用户Profile-并发测试

## 📊 测试报告

### Allure报告特性

- 📈 **测试趋势**: 显示测试执行趋势
- 📋 **测试详情**: 详细的测试步骤和断言
- 🔍 **失败分析**: 失败用例的详细分析
- 📊 **统计图表**: 测试结果统计图表
- 🌐 **环境信息**: 测试环境配置信息

### 查看报告

```bash
# 生成报告
allure generate allure-results -o allure-report --clean

# 打开报告
allure open allure-report
```

## 🔧 配置说明

### 认证管理系统

项目使用全局认证管理器 (`common/auth_manager.py`) 来管理API认证token：

- **自动获取**: 通过认证接口自动获取token
- **缓存机制**: token会被缓存，避免重复请求
- **自动刷新**: token过期前自动刷新
- **全局共享**: 所有需要认证的测试都可以使用同一个token

#### 环境变量配置

为了提高安全性，认证凭据通过 `.env` 文件配置：

1. **复制环境变量示例文件**:
```bash
cp env.example .env
```

2. **编辑 `.env` 文件**:
```bash
# 认证用户名
GODGPT_USERNAME=your_username@example.com

# 认证密码
GODGPT_PASSWORD=your_password
```

3. **环境变量优先级**:
- 系统环境变量 > `.env` 文件 > 默认值
- 建议使用 `.env` 文件进行本地开发
- 生产环境使用系统环境变量

4. **Jenkins 配置**:
```groovy
environment {
    GODGPT_USERNAME = credentials('godgpt-username')
    GODGPT_PASSWORD = credentials('godgpt-password')
}
```

#### 认证配置

认证凭据在 `common/auth_manager.py` 中从环境变量读取：

```python
# 自动加载 .env 文件
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

# 验证认证凭据是否配置
if not self.auth_credentials['username'] or not self.auth_credentials['password']:
    raise ValueError("认证凭据未配置，请设置 GODGPT_USERNAME 和 GODGPT_PASSWORD 环境变量")
```

#### 使用方法

在测试文件中使用认证token：

```python
from common.auth_manager import auth_manager

# 获取认证token
token = auth_manager.get_auth_token()

# 在请求头中使用
headers['authorization'] = f'Bearer {token}'
```

### 环境配置 (`config.yaml`)

```yaml
# 基础配置
base_url: "https://station-developer.aevatar.ai"
timeout: 30
retry_times: 3

# 测试环境配置
environments:
  dev:
    base_url: "https://station-developer.aevatar.ai"
    timeout: 30
  test:
    base_url: "https://station-developer.aevatar.ai"
    timeout: 30
  prod:
    base_url: "https://station-developer.aevatar.ai"
    timeout: 60
```

### pytest配置 (`pytest.ini`)

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --alluredir=./allure-results
    --clean-alluredir
markers =
    smoke: 冒烟测试
    regression: 回归测试
    api: API测试
```

## 🏭 Jenkins集成

### Jenkins流水线特性

- 🔄 **多环境支持**: 支持dev/test/prod环境
- 🏷️ **测试标记**: 支持按标记过滤测试
- 📊 **报告集成**: 自动生成和发布Allure报告
- 🧹 **环境清理**: 自动清理临时文件
- 📧 **通知机制**: 测试结果通知

### Jenkins配置

1. **安装插件**:
   - Allure Jenkins Plugin
   - Pipeline Utility Steps

2. **创建流水线**:
   - 使用项目中的 `Jenkinsfile`
   - 配置Git仓库地址

3. **运行参数**:
   - `TEST_ENV`: 选择测试环境
   - `TEST_MARKERS`: 选择测试标记
   - `GENERATE_REPORT`: 是否生成报告

### Jenkins运行示例

```groovy
// 运行冒烟测试
pipeline {
    agent any
    parameters {
        choice(name: 'TEST_MARKERS', choices: ['smoke'])
    }
    stages {
        stage('运行测试') {
            steps {
                sh 'python -m pytest -m smoke --alluredir=./allure-results'
            }
        }
    }
}
```

## 🛠️ 开发指南

### 添加新的测试用例

1. **创建测试文件**:
```python
import pytest
import allure
from common.http_client import HttpClient
from common.assertions import ApiAssertions

@allure.epic("模块名称")
@allure.feature("功能名称")
class TestNewAPI:
    @pytest.fixture(autouse=True)
    def setup(self, base_url):
        self.client = HttpClient(base_url)
        self.assertions = ApiAssertions()
    
    @allure.story("测试场景")
    @pytest.mark.api
    def test_new_function(self):
        # 测试实现
        pass
```

2. **使用断言**:
```python
# 状态码断言
self.assertions.assert_status_code(response, 200)

# JSON内容断言
self.assertions.assert_json_contains(response, "key", "value")

# 响应时间断言
self.assertions.assert_response_time(response, 5.0)
```

### 生成测试数据

```python
from common.test_data import test_data_manager

# 生成用户数据
user_data = test_data_manager.generator.random_user_data()

# 生成文章数据
post_data = test_data_manager.generator.random_post_data()
```

## 📝 命令行参数

### run_tests.py 参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--markers` | `-m` | 选择测试标记 | `all` |
| `--parallel` | `-p` | 并行执行测试 | `False` |
| `--no-report` | - | 不生成Allure报告 | `False` |
| `--install` | - | 安装依赖 | `False` |
| `--open-report` | - | 打开Allure报告 | `False` |
| `--env` | - | 测试环境 | `dev` |

### pytest 参数

```bash
# 运行特定标记的测试
pytest -m smoke

# 并行执行
pytest -n auto

# 生成Allure报告
pytest --alluredir=./allure-results

# 详细输出
pytest -v

# 失败重试
pytest --reruns 3
```

## 🐛 常见问题

### 1. Allure命令找不到

```bash
# 检查Allure安装
allure --version

# 添加到PATH
export PATH=$PATH:/path/to/allure/bin
```

### 2. 测试数据生成失败

```bash
# 检查faker安装
pip install faker

# 设置中文locale
export LC_ALL=zh_CN.UTF-8
```

### 3. Jenkins报告不显示

```bash
# 检查Allure插件安装
# 检查报告路径配置
# 检查权限设置
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

如有问题，请提交Issue或联系开发团队。 