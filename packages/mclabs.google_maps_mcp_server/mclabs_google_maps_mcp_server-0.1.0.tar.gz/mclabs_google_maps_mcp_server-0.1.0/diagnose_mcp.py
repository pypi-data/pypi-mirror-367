#!/usr/bin/env python3
"""
MCP 连接问题诊断脚本
"""

import os
import subprocess
import sys
from pathlib import Path


def check_environment():
    """检查环境配置"""
    print("🔍 环境诊断")
    print("=" * 50)

    # 检查 Python 版本
    python_version = sys.version.split()[0]
    print(f"🐍 Python 版本: {python_version}")

    # 检查 uv 是否安装
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"📦 uv 版本: {result.stdout.strip()}")
        else:
            print("❌ uv 未正确安装")
            return False
    except FileNotFoundError:
        print("❌ uv 未安装")
        return False

    # 检查 API Key
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key:
        print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("⚠️  未设置 GOOGLE_MAPS_API_KEY 环境变量")

    # 检查项目结构
    current_dir = Path.cwd()
    print(f"📁 当前目录: {current_dir}")

    required_files = ["google_maps_server.py", "pyproject.toml", "uv.lock"]
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} 存在")
        else:
            print(f"❌ {file} 缺失")

    return True


def test_server_import():
    """测试服务器模块导入"""
    print("\n🧪 模块导入测试")
    print("=" * 50)

    try:
        # 设置临时 API Key（如果没有的话）
        if not os.getenv("GOOGLE_MAPS_API_KEY"):
            os.environ["GOOGLE_MAPS_API_KEY"] = "test_key_for_diagnosis"

        from google_maps_server import mcp, main

        print("✅ google_maps_server 模块导入成功")
        print("✅ main 函数存在")
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False


def test_uv_run():
    """测试 uv run 命令"""
    print("\n🚀 uv run 测试")
    print("=" * 50)

    try:
        # 设置临时 API Key
        env = os.environ.copy()
        env["GOOGLE_MAPS_API_KEY"] = "test_key_for_diagnosis"

        # 测试 uv run --help
        result = subprocess.run(
            ["uv", "run", "--help"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print("✅ uv run 命令可用")
        else:
            print("❌ uv run 命令失败")
            return False

        # 测试 uv run google-maps-mcp --help (如果支持)
        result = subprocess.run(
            ["uv", "run", "google-maps-mcp", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
        )
        if result.returncode == 0:
            print("✅ google-maps-mcp 脚本可执行")
        else:
            print(f"⚠️  google-maps-mcp 脚本测试: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("⚠️  命令超时")
    except Exception as e:
        print(f"❌ uv run 测试失败: {e}")
        return False

    return True


def generate_test_config():
    """生成测试配置"""
    print("\n📝 生成测试配置")
    print("=" * 50)

    current_dir = Path.cwd()

    config = {
        "mcpServers": {
            "google-maps": {
                "command": "uv",
                "args": ["run", "--directory", str(current_dir), "google-maps-mcp"],
                "env": {"GOOGLE_MAPS_API_KEY": "your_actual_google_maps_api_key_here"},
            }
        }
    }

    import json

    config_str = json.dumps(config, indent=2)
    print("建议的 MCP 配置:")
    print(config_str)

    # 写入测试配置文件
    with open("mcp_test_config.json", "w") as f:
        f.write(config_str)
    print(f"\n✅ 配置已保存到: {current_dir}/mcp_test_config.json")


def suggest_solutions():
    """建议解决方案"""
    print("\n💡 解决方案建议")
    print("=" * 50)

    print("1. 确保 API Key 正确设置:")
    print("   export GOOGLE_MAPS_API_KEY='your_actual_api_key'")
    print()

    print("2. 确保在正确的目录中:")
    print(f"   cd {Path.cwd()}")
    print()

    print("3. 重新同步依赖:")
    print("   uv sync")
    print()

    print("4. 测试手动启动:")
    print("   GOOGLE_MAPS_API_KEY='your_key' uv run google-maps-mcp")
    print()

    print("5. 检查 Gemini CLI 配置:")
    print("   - 确保配置文件路径正确")
    print("   - 确保 'command' 和 'args' 指向正确的路径")
    print("   - 确保环境变量正确设置")
    print()

    print("6. 如果仍有问题，尝试直接运行:")
    print("   uv run python google_maps_server.py")


def main():
    """主诊断流程"""
    print("🩺 Google Maps MCP 连接问题诊断")
    print("=" * 50)

    # 运行各项检查
    checks = [
        check_environment,
        test_server_import,
        test_uv_run,
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            results.append(False)

    # 生成配置和建议
    generate_test_config()
    suggest_solutions()

    # 总结
    print("\n📊 诊断总结")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"✅ 通过检查: {passed}/{total}")

    if passed == total:
        print("🎉 环境看起来正常，问题可能在 MCP 配置或 API Key")
    else:
        print("⚠️  发现环境问题，请先解决基础环境问题")


if __name__ == "__main__":
    main()
