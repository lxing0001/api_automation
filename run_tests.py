#!/usr/bin/env python3
"""
API自动化测试运行脚本
支持命令行参数和多种运行模式
"""

import argparse
import sys
import subprocess
import os
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并处理结果"""
    print(f"\n{'='*50}")
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✅ 执行成功")
        if result.stdout:
            print("输出:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ 执行失败")
        print("错误:", e.stderr)
        return False


def activate_venv():
    """激活虚拟环境"""
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
    else:  # Unix/Linux/macOS
        activate_script = "source venv/bin/activate"
    
    return activate_script


def install_dependencies():
    """安装项目依赖"""
    print("\n📦 安装项目依赖...")
    venv_activate = activate_venv()
    return run_command(f"{venv_activate} && pip install -r requirements.txt", "安装Python依赖")


def run_tests(markers=None, parallel=False, report=True):
    """运行测试"""
    print("\n🧪 运行测试...")
    
    venv_activate = activate_venv()
    cmd = f"{venv_activate} && python -m pytest"
    
    # 添加标记过滤
    if markers and markers != "all":
        cmd += f" -m {markers}"
    
    # 添加并行执行
    if parallel:
        cmd += " -n auto"
    
    # 添加Allure报告
    if report:
        cmd += " --alluredir=./allure-results --clean-alluredir"
    
    # 添加详细输出
    cmd += " -v"
    
    success = run_command(cmd, "运行pytest测试")
    
    if success and report:
        print("\n📊 生成Allure报告...")
        run_command(f"{venv_activate} && allure generate allure-results -o allure-report --clean", "生成Allure报告")
    
    return success


def open_report():
    """打开Allure报告"""
    print("\n🌐 打开Allure报告...")
    report_path = Path("./allure-report")
    if report_path.exists():
        venv_activate = activate_venv()
        run_command(f"{venv_activate} && allure open allure-report", "打开Allure报告")
    else:
        print("❌ 报告文件不存在，请先生成报告")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="API自动化测试运行脚本")
    parser.add_argument(
        "--markers", "-m",
        choices=["all", "smoke", "regression", "api"],
        default="all",
        help="选择测试标记 (默认: all)"
    )
    parser.add_argument(
        "--parallel", "-p",
        action="store_true",
        help="并行执行测试"
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="不生成Allure报告"
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="安装依赖"
    )
    parser.add_argument(
        "--open-report",
        action="store_true",
        help="打开Allure报告"
    )
    parser.add_argument(
        "--env",
        choices=["dev", "test", "prod"],
        default="dev",
        help="测试环境 (默认: dev)"
    )
    
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ["TEST_ENV"] = args.env
    
    print("🚀 API自动化测试框架")
    print(f"测试环境: {args.env}")
    print(f"测试标记: {args.markers}")
    print(f"并行执行: {'是' if args.parallel else '否'}")
    print(f"生成报告: {'否' if args.no_report else '是'}")
    
    # 安装依赖
    if args.install:
        if not install_dependencies():
            sys.exit(1)
    
    # 打开报告
    if args.open_report:
        open_report()
        return
    
    # 运行测试
    success = run_tests(
        markers=args.markers,
        parallel=args.parallel,
        report=not args.no_report
    )
    
    if success:
        print("\n🎉 测试执行完成！")
        if not args.no_report:
            print("📊 报告已生成在 ./allure-report/ 目录")
            print("💡 使用 --open-report 参数打开报告")
    else:
        print("\n💥 测试执行失败！")
        sys.exit(1)


if __name__ == "__main__":
    main() 