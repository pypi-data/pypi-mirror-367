#!/usr/bin/env python3
"""
Google Maps MCP Server using FastMCP
基于 FastMCP 框架的 Google Maps MCP 服务器
"""

import os
import sys
from typing import Any

import httpx
from fastmcp import Context, FastMCP
from pydantic import BaseModel


# 数据模型定义
class Location(BaseModel):
    lat: float
    lng: float


class GeocodeResult(BaseModel):
    place_id: str
    formatted_address: str
    location: Location


class PlaceSearchResult(BaseModel):
    name: str
    place_id: str
    formatted_address: str
    location: Location
    rating: float | None = None
    types: list[str]


class PlaceDetails(BaseModel):
    name: str
    place_id: str
    formatted_address: str
    formatted_phone_number: str | None = None
    website: str | None = None
    rating: float | None = None
    location: Location


class DistanceElement(BaseModel):
    status: str
    duration: dict[str, str | int] | None = None
    distance: dict[str, str | int] | None = None


class RouteMatrixElement(BaseModel):
    """Routes API 路由矩阵元素模型"""
    origin_index: int | None = None
    destination_index: int | None = None
    status: dict[str, Any] | None = None
    condition: str | None = None
    distance_meters: int | None = None
    duration: str | None = None
    static_duration: str | None = None


class ElevationResult(BaseModel):
    elevation: float
    location: Location
    resolution: float


class DirectionStep(BaseModel):
    html_instructions: str
    distance: dict[str, str | int]
    duration: dict[str, str | int]
    travel_mode: str


class DirectionRoute(BaseModel):
    summary: str
    distance: dict[str, str | int]
    duration: dict[str, str | int]
    steps: list[DirectionStep]


class RoutesApiStep(BaseModel):
    """Routes API 路线步骤模型"""
    navigation_instruction: dict[str, Any] | None = None
    distance_meters: int | None = None
    static_duration: str | None = None
    polyline: dict[str, Any] | None = None
    start_location: dict[str, Any] | None = None
    end_location: dict[str, Any] | None = None


class RoutesApiRoute(BaseModel):
    """Routes API 路线模型"""
    distance_meters: int | None = None
    duration: str | None = None
    static_duration: str | None = None
    polyline: dict[str, Any] | None = None
    legs: list[dict[str, Any]] | None = None
    description: str | None = None


def get_api_key() -> str:
    """获取 Google Maps API Key"""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("错误：GOOGLE_MAPS_API_KEY 环境变量未设置", file=sys.stderr)
        sys.exit(1)
    return api_key


# 创建 FastMCP 服务器实例
mcp = FastMCP("Google Maps MCP Server")

# 获取 API Key
GOOGLE_MAPS_API_KEY = get_api_key()


@mcp.tool
async def maps_geocode(address: str, ctx: Context) -> dict[str, Any]:
    """
    将地址转换为地理坐标

    Args:
        address: 要进行地理编码的地址

    Returns:
        包含位置信息的字典
    """
    await ctx.info(f"正在进行地理编码: {address}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={"address": address, "key": GOOGLE_MAPS_API_KEY},
            )
            data = response.json()

            if data["status"] != "OK":
                error_msg = f"地理编码失败: {data.get('error_message', data['status'])}"
                await ctx.error(error_msg)
                return {"error": error_msg}

            result = data["results"][0]
            geocode_result = GeocodeResult(
                place_id=result["place_id"],
                formatted_address=result["formatted_address"],
                location=Location(**result["geometry"]["location"]),
            )

            await ctx.info(f"地理编码成功: {geocode_result.formatted_address}")
            return geocode_result.model_dump()

        except Exception as e:
            error_msg = f"地理编码请求错误: {str(e)}"
            await ctx.error(error_msg)
            return {"error": error_msg}


@mcp.tool
async def maps_reverse_geocode(
    latitude: float, longitude: float, ctx: Context
) -> dict[str, Any]:
    """
    将坐标转换为地址

    Args:
        latitude: 纬度坐标
        longitude: 经度坐标

    Returns:
        包含地址信息的字典
    """
    await ctx.info(f"正在进行反向地理编码: ({latitude}, {longitude})")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params={
                    "latlng": f"{latitude},{longitude}",
                    "key": GOOGLE_MAPS_API_KEY,
                },
            )
            data = response.json()

            if data["status"] != "OK":
                error_msg = (
                    f"反向地理编码失败: {data.get('error_message', data['status'])}"
                )
                await ctx.error(error_msg)
                return {"error": error_msg}

            result = data["results"][0]
            return {
                "formatted_address": result["formatted_address"],
                "place_id": result["place_id"],
                "address_components": result["address_components"],
            }

        except Exception as e:
            error_msg = f"反向地理编码请求错误: {str(e)}"
            await ctx.error(error_msg)
            return {"error": error_msg}


@mcp.tool
async def maps_search_places(
    query: str,
    location: dict[str, float] | None = None,
    radius: int | None = None,
    ctx: Context = None,
) -> dict[str, Any]:
    """
    使用 Google Places API 搜索地点

    Args:
        query: 搜索查询
        location: 可选的搜索中心点 (包含 latitude 和 longitude)
        radius: 搜索半径（米）（最大 50000）

    Returns:
        包含搜索结果的字典
    """
    await ctx.info(f"正在搜索地点: {query}")

    params = {"query": query, "key": GOOGLE_MAPS_API_KEY}

    if location:
        params["location"] = f"{location['latitude']},{location['longitude']}"
    if radius:
        params["radius"] = str(radius)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/textsearch/json",
                params=params,
            )
            data = response.json()

            if data["status"] != "OK":
                error_msg = f"地点搜索失败: {data.get('error_message', data['status'])}"
                await ctx.error(error_msg)
                return {"error": error_msg}

            places = []
            for place in data["results"]:
                place_result = PlaceSearchResult(
                    name=place["name"],
                    place_id=place["place_id"],
                    formatted_address=place["formatted_address"],
                    location=Location(**place["geometry"]["location"]),
                    rating=place.get("rating"),
                    types=place["types"],
                )
                places.append(place_result.model_dump())

            await ctx.info(f"找到 {len(places)} 个地点")
            return {"places": places}

        except Exception as e:
            error_msg = f"地点搜索请求错误: {str(e)}"
            await ctx.error(error_msg)
            return {"error": error_msg}


@mcp.tool
async def maps_place_details(place_id: str, ctx: Context) -> dict[str, Any]:
    """
    获取特定地点的详细信息

    Args:
        place_id: 要获取详细信息的地点 ID

    Returns:
        包含地点详细信息的字典
    """
    await ctx.info(f"正在获取地点详情: {place_id}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/place/details/json",
                params={"place_id": place_id, "key": GOOGLE_MAPS_API_KEY},
            )
            data = response.json()

            if data["status"] != "OK":
                error_msg = (
                    f"地点详情请求失败: {data.get('error_message', data['status'])}"
                )
                await ctx.error(error_msg)
                return {"error": error_msg}

            result = data["result"]
            place_details = PlaceDetails(
                name=result["name"],
                place_id=result["place_id"],
                formatted_address=result["formatted_address"],
                formatted_phone_number=result.get("formatted_phone_number"),
                website=result.get("website"),
                rating=result.get("rating"),
                location=Location(**result["geometry"]["location"]),
            )

            # 添加额外的字段
            details = place_details.model_dump()
            details["reviews"] = result.get("reviews")
            details["opening_hours"] = result.get("opening_hours")

            await ctx.info(f"获取地点详情成功: {place_details.name}")
            return details

        except Exception as e:
            error_msg = f"地点详情请求错误: {str(e)}"
            await ctx.error(error_msg)
            return {"error": error_msg}


@mcp.tool
async def maps_distance_matrix(
    origins: list[str],
    destinations: list[str],
    mode: str = "driving",
    ctx: Context = None,
) -> dict[str, Any]:
    """
    使用 Routes API 计算多个起点和终点之间的旅行距离和时间

    Args:
        origins: 起点地址或坐标数组
        destinations: 终点地址或坐标数组
        mode: 旅行方式 (driving, walking, bicycling, transit)

    Returns:
        包含距离矩阵结果的字典
    """
    await ctx.info(
        f"正在使用 Routes API 计算距离矩阵: {len(origins)} 个起点到 {len(destinations)} 个终点"
    )

    # 模式映射：将旧的模式名称映射到 Routes API 的 RouteTravelMode
    mode_mapping = {
        "driving": "DRIVE",
        "walking": "WALK",
        "bicycling": "BICYCLE",
        "transit": "TRANSIT"
    }

    travel_mode = mode_mapping.get(mode, "DRIVE")

    # 构建 origins 和 destinations 数组
    origins_data = []
    destinations_data = []

    def create_waypoint(location_str: str) -> dict[str, Any]:
        """根据地址字符串或坐标创建 waypoint 对象"""
        # 检查是否为经纬度坐标格式 (lat,lng)
        if ',' in location_str and location_str.replace(',', '').replace('.', '').replace('-', '').replace(' ', '').isdigit():
            try:
                coords = location_str.split(',')
                lat = float(coords[0].strip())
                lng = float(coords[1].strip())
                return {
                    "waypoint": {
                        "location": {
                            "latLng": {
                                "latitude": lat,
                                "longitude": lng
                            }
                        }
                    }
                }
            except (ValueError, IndexError):
                pass

        # 作为地址处理
        return {
            "waypoint": {
                "address": location_str
            }
        }

    for origin in origins:
        origins_data.append(create_waypoint(origin))

    for destination in destinations:
        destinations_data.append(create_waypoint(destination))

    # 构建请求体
    request_body = {
        "origins": origins_data,
        "destinations": destinations_data,
        "travelMode": travel_mode,
        "routingPreference": "TRAFFIC_AWARE" if travel_mode == "DRIVE" else None
    }

    # 移除 None 值
    request_body = {k: v for k, v in request_body.items() if v is not None}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://routes.googleapis.com/distanceMatrix/v2:computeRouteMatrix",
                json=request_body,
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
                    "X-Goog-FieldMask": "originIndex,destinationIndex,status,condition,distanceMeters,duration"
                },
            )

            if response.status_code != 200:
                error_msg = f"Routes API 请求失败: HTTP {response.status_code} - {response.text}"
                await ctx.error(error_msg)
                return {"error": error_msg}

            # Routes API 返回的是数组格式，每个元素表示一个 origin-destination 组合
            route_elements = response.json()

            # 转换为与原有 Distance Matrix API 兼容的格式
            results = []
            for i in range(len(origins)):
                elements = []
                for j in range(len(destinations)):
                    # 查找匹配的路由元素
                    route_element = None
                    for element in route_elements:
                        if element.get("originIndex") == i and element.get("destinationIndex") == j:
                            route_element = element
                            break

                    if route_element:
                        # 转换状态
                        status = "OK" if route_element.get("condition") == "ROUTE_EXISTS" else "ZERO_RESULTS"

                        # 转换距离和时间格式以兼容原有格式
                        distance = None
                        duration = None

                        if route_element.get("distanceMeters"):
                            distance = {
                                "text": f"{route_element['distanceMeters'] / 1000:.1f} km",
                                "value": route_element["distanceMeters"]
                            }

                        if route_element.get("duration"):
                            # duration 格式为 "123s"，需要转换为秒数
                            duration_str = route_element["duration"]
                            duration_seconds = int(duration_str.rstrip('s'))
                            duration = {
                                "text": f"{duration_seconds // 60} 分钟",
                                "value": duration_seconds
                            }

                        distance_element = DistanceElement(
                            status=status,
                            duration=duration,
                            distance=distance,
                        )
                    else:
                        # 没有找到对应的路由元素
                        distance_element = DistanceElement(
                            status="ZERO_RESULTS",
                            duration=None,
                            distance=None,
                        )

                    elements.append(distance_element.model_dump())
                results.append({"elements": elements})

            # 由于 Routes API 不直接返回格式化地址，我们使用原始输入
            result_data = {
                "origin_addresses": origins,
                "destination_addresses": destinations,
                "results": results,
            }

            await ctx.info("Routes API 距离矩阵计算完成")
            return result_data

        except Exception as e:
            error_msg = f"Routes API 距离矩阵请求错误: {str(e)}"
            await ctx.error(error_msg)
            return {"error": error_msg}


@mcp.tool
async def maps_elevation(
    locations: list[dict[str, float]], ctx: Context
) -> dict[str, Any]:
    """
    获取地球上位置的海拔数据

    Args:
        locations: 位置数组，每个包含 latitude 和 longitude

    Returns:
        包含海拔结果的字典
    """
    await ctx.info(f"正在获取 {len(locations)} 个位置的海拔数据")

    location_string = "|".join(
        [f"{loc['latitude']},{loc['longitude']}" for loc in locations]
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://maps.googleapis.com/maps/api/elevation/json",
                params={"locations": location_string, "key": GOOGLE_MAPS_API_KEY},
            )
            data = response.json()

            if data["status"] != "OK":
                error_msg = f"海拔请求失败: {data.get('error_message', data['status'])}"
                await ctx.error(error_msg)
                return {"error": error_msg}

            results = []
            for result in data["results"]:
                elevation_result = ElevationResult(
                    elevation=result["elevation"],
                    location=Location(**result["location"]),
                    resolution=result["resolution"],
                )
                results.append(elevation_result.model_dump())

            await ctx.info(f"获取海拔数据成功: {len(results)} 个位置")
            return {"results": results}

        except Exception as e:
            error_msg = f"海拔请求错误: {str(e)}"
            await ctx.error(error_msg)
            return {"error": error_msg}


@mcp.tool
async def maps_directions(
    origin: str, destination: str, mode: str = "driving", ctx: Context = None
) -> dict[str, Any]:
    """
    使用 Routes API 获取两点之间的路线指导

    Args:
        origin: 起点地址或坐标
        destination: 终点地址或坐标
        mode: 旅行方式 (driving, walking, bicycling, transit)

    Returns:
        包含路线指导的字典
    """
    await ctx.info(f"正在使用 Routes API 获取路线: 从 {origin} 到 {destination}")

    # 模式映射：将旧的模式名称映射到 Routes API 的 RouteTravelMode
    mode_mapping = {
        "driving": "DRIVE",
        "walking": "WALK",
        "bicycling": "BICYCLE",
        "transit": "TRANSIT"
    }

    travel_mode = mode_mapping.get(mode, "DRIVE")

    def create_waypoint(location_str: str) -> dict[str, Any]:
        """根据地址字符串或坐标创建 waypoint 对象"""
        # 检查是否为经纬度坐标格式 (lat,lng)
        if ',' in location_str and location_str.replace(',', '').replace('.', '').replace('-', '').replace(' ', '').isdigit():
            try:
                coords = location_str.split(',')
                lat = float(coords[0].strip())
                lng = float(coords[1].strip())
                return {
                    "location": {
                        "latLng": {
                            "latitude": lat,
                            "longitude": lng
                        }
                    }
                }
            except (ValueError, IndexError):
                pass

        # 作为地址处理
        return {
            "address": location_str
        }

    # 构建请求体
    request_body = {
        "origin": create_waypoint(origin),
        "destination": create_waypoint(destination),
        "travelMode": travel_mode,
        "routingPreference": "TRAFFIC_AWARE" if travel_mode == "DRIVE" else None,
        "computeAlternativeRoutes": False,
        "languageCode": "zh-CN",
        "units": "METRIC"
    }

    # 移除 None 值
    request_body = {k: v for k, v in request_body.items() if v is not None}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://routes.googleapis.com/directions/v2:computeRoutes",
                json=request_body,
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
                    "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.legs.steps.navigationInstruction,routes.legs.steps.localizedValues,routes.description"
                },
            )

            if response.status_code != 200:
                error_msg = f"Routes API 路线请求失败: HTTP {response.status_code} - {response.text}"
                await ctx.error(error_msg)
                return {"error": error_msg}

            data = response.json()

            if not data.get("routes"):
                error_msg = "Routes API 未返回路线数据"
                await ctx.error(error_msg)
                return {"error": error_msg}

            routes = []
            for route in data["routes"]:
                # 获取路线的基本信息
                distance_meters = route.get("distanceMeters", 0)
                duration_str = route.get("duration", "0s")
                duration_seconds = int(duration_str.rstrip('s')) if duration_str.endswith('s') else 0

                # 转换为与原有格式兼容的距离和时间格式
                distance = {
                    "text": f"{distance_meters / 1000:.1f} km",
                    "value": distance_meters
                }
                duration = {
                    "text": f"{duration_seconds // 60} 分钟",
                    "value": duration_seconds
                }

                # 处理路线步骤
                steps = []
                if route.get("legs"):
                    for leg in route["legs"]:
                        if leg.get("steps"):
                            for step in leg["steps"]:
                                # 提取导航指令
                                html_instructions = ""
                                if step.get("navigationInstruction"):
                                    nav_instruction = step["navigationInstruction"]
                                    if nav_instruction.get("instructions"):
                                        html_instructions = nav_instruction["instructions"]
                                    elif nav_instruction.get("maneuver"):
                                        html_instructions = f"执行 {nav_instruction['maneuver']} 操作"

                                # 获取步骤距离和时间
                                step_distance_meters = step.get("distanceMeters", 0)
                                step_duration_str = step.get("staticDuration", "0s")
                                step_duration_seconds = int(step_duration_str.rstrip('s')) if step_duration_str.endswith('s') else 0

                                step_distance = {
                                    "text": f"{step_distance_meters} 米",
                                    "value": step_distance_meters
                                }
                                step_duration = {
                                    "text": f"{step_duration_seconds} 秒",
                                    "value": step_duration_seconds
                                }

                                direction_step = DirectionStep(
                                    html_instructions=html_instructions or "继续前进",
                                    distance=step_distance,
                                    duration=step_duration,
                                    travel_mode=travel_mode,
                                )
                                steps.append(direction_step.model_dump())

                direction_route = DirectionRoute(
                    summary=route.get("description", f"从 {origin} 到 {destination} 的路线"),
                    distance=distance,
                    duration=duration,
                    steps=steps,
                )
                routes.append(direction_route.model_dump())

            await ctx.info(f"Routes API 获取路线成功: {len(routes)} 条路线")
            return {"routes": routes}

        except Exception as e:
            error_msg = f"Routes API 路线请求错误: {str(e)}"
            await ctx.error(error_msg)
            return {"error": error_msg}


# 添加一个资源来显示服务器信息
@mcp.resource("google-maps://info")
async def get_server_info(ctx: Context) -> str:
    """获取 Google Maps MCP 服务器信息"""
    await ctx.info("获取服务器信息")
    return """
Google Maps MCP Server
======================
版本: 0.1.0
描述: 基于 FastMCP 框架的 Google Maps API 服务

可用工具:
- maps_geocode: 地址到坐标转换
- maps_reverse_geocode: 坐标到地址转换
- maps_search_places: 地点搜索
- maps_place_details: 地点详细信息
- maps_distance_matrix: 距离矩阵计算
- maps_elevation: 海拔数据获取
- maps_directions: 路线指导

环境要求:
- GOOGLE_MAPS_API_KEY 环境变量必须设置
"""


def main():
    """主函数入口点"""
    print("启动 Google Maps MCP 服务器...")
    mcp.run()


if __name__ == "__main__":
    main()
