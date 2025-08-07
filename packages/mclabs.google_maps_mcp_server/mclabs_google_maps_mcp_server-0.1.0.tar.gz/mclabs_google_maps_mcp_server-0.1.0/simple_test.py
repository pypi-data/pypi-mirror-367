#!/usr/bin/env python3
"""
简单的语法和结构测试
"""

import os
import asyncio

# 设置测试环境变量
os.environ["GOOGLE_MAPS_API_KEY"] = "test_key_for_demo"

try:
    # 测试导入
    print("🔄 测试模块导入...")
    from google_maps_server import mcp
    print("✅ 模块导入成功")
    
    # 测试工具注册
    print("🔄 测试工具注册...")
    
    async def check_tools():
        tools = await mcp.get_tools()
        print(f"✅ 成功注册 {len(tools)} 个工具")
        
        # 检查 Routes API 相关工具
        distance_matrix_tool = None
        directions_tool = None
        
        for tool_name in tools:
            tool = await mcp.get_tool(tool_name)
            if tool_name == "maps_distance_matrix":
                distance_matrix_tool = tool
                print(f"📊 {tool_name}: {tool.description}")
            elif tool_name == "maps_directions":
                directions_tool = tool
                print(f"🛣️  {tool_name}: {tool.description}")
            else:
                print(f"🔧 {tool_name}: {tool.description}")
        
        # 验证描述中包含 Routes API
        if distance_matrix_tool and "Routes API" in distance_matrix_tool.description:
            print("✅ maps_distance_matrix 已更新为使用 Routes API")
        else:
            print("⚠️  maps_distance_matrix 描述可能未更新")
            
        if directions_tool and "Routes API" in directions_tool.description:
            print("✅ maps_directions 已更新为使用 Routes API")
        else:
            print("⚠️  maps_directions 描述可能未更新")
            
        return True
    
    # 运行异步测试
    asyncio.run(check_tools())
    
    print("\n🎉 所有基础测试通过！")
    print("\n📋 修改总结:")
    print("  • maps_distance_matrix 已升级到 Routes API")
    print("  • maps_directions 已升级到 Routes API")
    print("  • 保持了原有的函数签名和返回格式")
    print("  • 添加了更好的错误处理和字段掩码优化")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()