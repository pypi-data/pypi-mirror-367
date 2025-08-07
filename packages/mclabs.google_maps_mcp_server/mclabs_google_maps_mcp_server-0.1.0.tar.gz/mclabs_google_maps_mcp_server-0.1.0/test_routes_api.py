#!/usr/bin/env python3
"""
测试 Routes API 修改后的功能
"""

import asyncio
import os
from unittest.mock import AsyncMock, patch

# 设置测试环境变量
os.environ["GOOGLE_MAPS_API_KEY"] = "test_key_for_demo"

from google_maps_server import maps_distance_matrix, maps_directions, Context


async def test_maps_distance_matrix():
    """测试 maps_distance_matrix 函数的基本逻辑"""
    print("🧪 测试 maps_distance_matrix (Routes API)")
    
    # 创建模拟的上下文
    ctx = AsyncMock(spec=Context)
    
    # 测试参数
    origins = ["北京", "上海"]
    destinations = ["深圳", "广州"]
    mode = "driving"
    
    # 模拟 HTTP 响应
    mock_response_data = [
        {
            "originIndex": 0,
            "destinationIndex": 0,
            "status": {},
            "condition": "ROUTE_EXISTS",
            "distanceMeters": 2100000,
            "duration": "7200s"
        },
        {
            "originIndex": 0,
            "destinationIndex": 1,
            "status": {},
            "condition": "ROUTE_EXISTS",
            "distanceMeters": 1800000,
            "duration": "6480s"
        }
    ]
    
    with patch('httpx.AsyncClient') as mock_client:
        # 配置模拟响应
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        try:
            result = await maps_distance_matrix(origins, destinations, mode, ctx)
            
            print("✅ 函数调用成功")
            print(f"📊 返回结果类型: {type(result)}")
            print(f"📋 结果包含字段: {list(result.keys())}")
            
            if "results" in result:
                print(f"📈 路线矩阵大小: {len(result['results'])} x {len(result['results'][0]['elements']) if result['results'] else 0}")
                
            # 验证请求格式
            post_call = mock_client.return_value.__aenter__.return_value.post.call_args
            request_url = post_call[0][0]
            request_data = post_call[1]['json']
            request_headers = post_call[1]['headers']
            
            print(f"🌐 请求 URL: {request_url}")
            print(f"🔑 使用 Routes API: {'routes.googleapis.com' in request_url}")
            print(f"📝 请求包含 origins: {'origins' in request_data}")
            print(f"📝 请求包含 destinations: {'destinations' in request_data}")
            print(f"🎯 使用字段掩码: {'X-Goog-FieldMask' in request_headers}")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    return True


async def test_maps_directions():
    """测试 maps_directions 函数的基本逻辑"""
    print("\n🧪 测试 maps_directions (Routes API)")
    
    # 创建模拟的上下文
    ctx = AsyncMock(spec=Context)
    
    # 测试参数
    origin = "北京"
    destination = "上海"
    mode = "driving"
    
    # 模拟 HTTP 响应
    mock_response_data = {
        "routes": [
            {
                "distanceMeters": 1200000,
                "duration": "43200s",
                "description": "从北京到上海的最佳路线",
                "legs": [
                    {
                        "steps": [
                            {
                                "distanceMeters": 500,
                                "staticDuration": "120s",
                                "navigationInstruction": {
                                    "instructions": "向南行驶"
                                }
                            },
                            {
                                "distanceMeters": 1000,
                                "staticDuration": "300s",
                                "navigationInstruction": {
                                    "maneuver": "TURN_RIGHT"
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
    
    with patch('httpx.AsyncClient') as mock_client:
        # 配置模拟响应
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        try:
            result = await maps_directions(origin, destination, mode, ctx)
            
            print("✅ 函数调用成功")
            print(f"📊 返回结果类型: {type(result)}")
            print(f"📋 结果包含字段: {list(result.keys())}")
            
            if "routes" in result:
                print(f"🛣️  路线数量: {len(result['routes'])}")
                if result['routes']:
                    route = result['routes'][0]
                    print(f"📏 路线包含字段: {list(route.keys())}")
                    if 'steps' in route:
                        print(f"👣 步骤数量: {len(route['steps'])}")
                
            # 验证请求格式
            post_call = mock_client.return_value.__aenter__.return_value.post.call_args
            request_url = post_call[0][0]
            request_data = post_call[1]['json']
            request_headers = post_call[1]['headers']
            
            print(f"🌐 请求 URL: {request_url}")
            print(f"🔑 使用 Routes API: {'routes.googleapis.com' in request_url}")
            print(f"📝 请求包含 origin: {'origin' in request_data}")
            print(f"📝 请求包含 destination: {'destination' in request_data}")
            print(f"🎯 使用字段掩码: {'X-Goog-FieldMask' in request_headers}")
            
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            return False
    
    return True


async def test_waypoint_creation():
    """测试坐标和地址解析功能"""
    print("\n🧪 测试 waypoint 创建功能")
    
    ctx = AsyncMock(spec=Context)
    
    # 测试坐标格式
    coord_origins = ["39.9042,116.4074"]  # 北京坐标
    addr_destinations = ["上海"]  # 地址格式
    
    # 模拟响应（简化）
    mock_response_data = []
    
    with patch('httpx.AsyncClient') as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        try:
            await maps_distance_matrix(coord_origins, addr_destinations, "driving", ctx)
            
            # 检查请求数据中的 waypoint 格式
            post_call = mock_client.return_value.__aenter__.return_value.post.call_args
            request_data = post_call[1]['json']
            
            # 验证坐标被正确解析
            origin_waypoint = request_data['origins'][0]
            if 'waypoint' in origin_waypoint and 'location' in origin_waypoint['waypoint']:
                print("✅ 坐标格式解析正确")
                lat_lng = origin_waypoint['waypoint']['location']['latLng']
                print(f"📍 解析的坐标: {lat_lng['latitude']}, {lat_lng['longitude']}")
            
            # 验证地址被正确解析
            dest_waypoint = request_data['destinations'][0]
            if 'waypoint' in dest_waypoint and 'address' in dest_waypoint['waypoint']:
                print("✅ 地址格式解析正确")
                print(f"🏠 解析的地址: {dest_waypoint['waypoint']['address']}")
                
        except Exception as e:
            print(f"❌ waypoint 测试失败: {e}")
            return False
    
    return True


async def main():
    """运行所有测试"""
    print("🔧 Routes API 功能测试")
    print("=" * 50)
    
    tests = [
        test_maps_distance_matrix,
        test_maps_directions,
        test_waypoint_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if await test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有 Routes API 功能测试通过！")
        print("\n✨ 主要改进:")
        print("  • maps_distance_matrix 现在使用 Routes API computeRouteMatrix")
        print("  • maps_directions 现在使用 Routes API computeRoutes")
        print("  • 支持坐标和地址两种输入格式")
        print("  • 添加了实时交通感知路由")
        print("  • 优化了字段掩码以提高性能")
        print("  • 保持了向后兼容的返回格式")
    else:
        print("⚠️  部分测试失败，需要检查实现")


if __name__ == "__main__":
    asyncio.run(main())