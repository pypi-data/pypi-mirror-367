# Gemini CLI MCP 配置指南

## 问题诊断

如果你遇到 "Connection closed" 错误，通常是以下几个原因之一：

### 1. 脚本入口点未正确安装

确保项目以可编辑模式安装：

```bash
cd /Users/shaojiasong/codes/google-maps-mcp
uv pip install -e .
```

### 2. API Key 未设置

确保在 MCP 配置中设置了有效的 Google Maps API Key。

### 3. 配置文件路径错误

确保 Gemini CLI 配置文件中的路径指向正确的项目目录。

## 推荐配置

### 方法 1: 使用脚本入口点（推荐）

```json
{
  "mcpServers": {
    "google-maps": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/shaojiasong/codes/google-maps-mcp",
        "google-maps-mcp"
      ],
      "env": {
        "GOOGLE_MAPS_API_KEY": "your_actual_google_maps_api_key_here"
      }
    }
  }
}
```

### 方法 2: 直接运行 Python 文件（备用）

```json
{
  "mcpServers": {
    "google-maps": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/Users/shaojiasong/codes/google-maps-mcp",
        "python",
        "google_maps_server.py"
      ],
      "env": {
        "GOOGLE_MAPS_API_KEY": "your_actual_google_maps_api_key_here"
      }
    }
  }
}
```

## 测试步骤

1. **测试手动启动：**
   ```bash
   cd /Users/shaojiasong/codes/google-maps-mcp
   GOOGLE_MAPS_API_KEY='your_api_key' uv run google-maps-mcp
   ```

2. **测试模块导入：**
   ```bash
   GOOGLE_MAPS_API_KEY='test_key' uv run python -c "from google_maps_server import mcp; print('✅ 导入成功')"
   ```

3. **重新安装项目：**
   ```bash
   uv sync
   uv pip install -e .
   ```

## 常见问题解决

### Error: "No such file or directory"
- 运行: `uv pip install -e .`
- 或使用方法 2 的配置

### Error: "Connection closed"  
- 检查 API Key 是否有效
- 确保路径指向正确的项目目录
- 验证 uv 和 Python 版本兼容性

### Error: "Module not found"
- 运行: `uv sync`
- 检查虚拟环境是否正确激活

## 验证配置

使用以下命令验证配置是否正确：

```bash
# 在项目目录中运行
cd /Users/shaojiasong/codes/google-maps-mcp
uv run python diagnose_mcp.py
```

这将运行完整的诊断并生成配置文件。

## 支持的功能

更新后的服务器现在支持：

- ✅ **Routes API**: `maps_distance_matrix` 和 `maps_directions` 现在使用最新的 Google Maps Routes API
- ✅ **实时交通**: 支持实时交通数据
- ✅ **多种输入格式**: 支持地址和坐标两种格式
- ✅ **性能优化**: 使用字段掩码减少数据传输
- ✅ **向后兼容**: 保持原有 API 接口不变

## 获取 Google Maps API Key

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用以下 API：
   - Maps JavaScript API
   - Geocoding API
   - Places API
   - Routes API (新)
   - Distance Matrix API (如果需要向后兼容)
4. 创建 API Key 并设置适当的限制