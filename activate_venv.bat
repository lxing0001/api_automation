@echo off
REM 虚拟环境激活脚本 (Windows)

echo 🚀 激活虚拟环境...

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo ❌ 虚拟环境不存在，正在创建...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

echo ✅ 虚拟环境已激活
echo Python版本: 
python --version
echo pip版本: 
pip --version

REM 检查依赖是否已安装
if not exist "venv\Lib\site-packages\pytest" (
    echo 📦 安装项目依赖...
    pip install -r requirements.txt
)

echo 🎉 环境准备完成！
echo 💡 使用以下命令运行测试:
echo    python run_tests.py
echo    python run_tests.py --markers smoke
echo    python run_tests.py --open-report

pause 