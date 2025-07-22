#!/bin/bash
# 虚拟环境激活脚本

echo "🚀 激活虚拟环境..."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，正在创建..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

echo "✅ 虚拟环境已激活"
echo "Python版本: $(python --version)"
echo "pip版本: $(pip --version)"

# 检查依赖是否已安装
if [ ! -f "venv/lib/python*/site-packages/pytest" ]; then
    echo "📦 安装项目依赖..."
    pip install -r requirements.txt
fi

echo "🎉 环境准备完成！"
echo "💡 使用以下命令运行测试:"
echo "   python run_tests.py"
echo "   python run_tests.py --markers smoke"
echo "   python run_tests.py --open-report" 