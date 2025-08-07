#!/bin/bash

# Google Maps MCP Server 启动脚本 (使用 uv)

echo "🗺️ Google Maps MCP Server (uv 版本)"
echo "================================="

# 检查是否安装了 uv
if ! command -v uv &> /dev/null; then
    echo "❌ 错误：uv 未安装"
    echo ""
    echo "请安装 uv："
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# 检查是否设置了 API Key
if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
    echo "❌ 错误：GOOGLE_MAPS_API_KEY 环境变量未设置"
    echo ""
    echo "请设置您的 Google Maps API Key："
    echo "export GOOGLE_MAPS_API_KEY=\"your_api_key_here\""
    echo ""
    echo "或者创建 .env 文件："
    echo "echo \"GOOGLE_MAPS_API_KEY=your_api_key_here\" > .env"
    exit 1
fi

# 同步依赖（如果需要）
echo "📦 检查依赖..."
if [ ! -f "uv.lock" ] || [ ! -d ".venv" ]; then
    echo "🔧 同步项目依赖..."
    uv sync
fi

echo "🚀 启动 Google Maps MCP 服务器..."
echo "API Key: ${GOOGLE_MAPS_API_KEY:0:10}..."
echo ""

# 使用 uv 运行服务器
uv run google-maps-mcp 