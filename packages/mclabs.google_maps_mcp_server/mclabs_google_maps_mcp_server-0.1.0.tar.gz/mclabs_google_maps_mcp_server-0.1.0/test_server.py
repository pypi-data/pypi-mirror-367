#!/usr/bin/env python3
"""
Google Maps MCP Server 测试脚本
"""

import asyncio
import os

from fastmcp import Client

from google_maps_server import mcp


async def test_server():
    """测试服务器功能"""
    print("🧪 Google Maps MCP Server 测试")
    print("==============================")

    # 检查 API Key
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key or api_key == "test_key_for_demo":
        print("⚠️  警告：使用测试 API Key，实际功能可能无法工作")
        print("   请设置真实的 GOOGLE_MAPS_API_KEY 进行完整测试")
    else:
        print(f"✅ 使用 API Key: {api_key[:10]}...")

    print()

    # 测试工具注册
    try:
        tools = await mcp.get_tools()
        print(f"✅ 工具注册成功: {len(tools)} 个工具")
        for name in tools:
            tool = await mcp.get_tool(name)
            print(f"  - {name}: {tool.description}")
        print()
    except Exception as e:
        print(f"❌ 工具注册失败: {e}")
        return

    # 测试资源注册
    try:
        resources = await mcp.get_resources()
        print(f"✅ 资源注册成功: {len(resources)} 个资源")
        for name in resources:
            resource = await mcp.get_resource(name)
            print(f"  - {name}: {resource.description}")
        print()
    except Exception as e:
        print(f"❌ 资源注册失败: {e}")
        return

    # 使用内存客户端测试
    print("🔄 测试客户端连接...")
    try:
        async with Client(mcp) as client:
            # 列出可用工具
            tools_list = await client.list_tools()
            tools_count = (
                len(tools_list.tools)
                if hasattr(tools_list, "tools")
                else len(tools_list)
            )
            print(f"✅ 客户端连接成功，发现 {tools_count} 个工具")

            # 测试服务器信息资源
            try:
                info = await client.read_resource("google-maps://info")
                print("✅ 服务器信息资源读取成功")
                print("📋 服务器信息:")
                print(info.contents[0].text)
            except Exception as e:
                print(f"⚠️  服务器信息读取失败: {e}")

            print("✅ 所有基础测试通过！")

    except Exception as e:
        print(f"❌ 客户端测试失败: {e}")
        return

    print()
    print("🎉 测试完成！服务器已准备好接受请求。")
    print()
    print("📝 下一步:")
    print("1. 设置真实的 GOOGLE_MAPS_API_KEY")
    print("2. 配置 Claude Desktop (参考 claude_desktop_config_example.json)")
    print("3. 启动服务器: python google_maps_server.py")


if __name__ == "__main__":
    # 设置测试 API Key（如果没有设置的话）
    if not os.getenv("GOOGLE_MAPS_API_KEY"):
        os.environ["GOOGLE_MAPS_API_KEY"] = "test_key_for_demo"

    asyncio.run(test_server())
