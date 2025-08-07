# Google Maps MCP Server 使用指南

## 🎉 项目完成

你已经成功使用 FastMCP 框架创建了一个完整的 Google Maps MCP 服务器！这个服务器改写了原始的 JavaScript 版本，提供了所有相同的功能。

## 📁 项目结构

```
google-maps-mcp/
├── google_maps_server.py           # 主服务器文件（基于 FastMCP）
├── test_server.py                  # 测试脚本
├── start_server.sh                 # 启动脚本
├── pyproject.toml                  # Python 项目配置
├── README.md                       # 详细文档
├── USAGE.md                        # 本文件 - 使用指南
├── claude_desktop_config_example.json # Claude Desktop 配置示例
├── env.example                     # 环境变量示例
├── .gitignore                      # Git 忽略配置
└── venv/                          # Python 虚拟环境
```

## 🛠️ 可用功能

### 7个 MCP 工具

1. **maps_geocode** - 地址到坐标转换
2. **maps_reverse_geocode** - 坐标到地址转换  
3. **maps_search_places** - 地点搜索
4. **maps_place_details** - 地点详细信息
5. **maps_distance_matrix** - 距离矩阵计算
6. **maps_elevation** - 海拔数据获取
7. **maps_directions** - 路线规划

### 1个 MCP 资源

- **google-maps://info** - 服务器信息

## 🚀 快速启动

### 1. 设置 Google Maps API Key

```bash
# 方法一：环境变量
export GOOGLE_MAPS_API_KEY="your_actual_api_key_here"

# 方法二：.env 文件
echo "GOOGLE_MAPS_API_KEY=your_actual_api_key_here" > .env
```

### 2. 同步依赖

```bash
uv sync
```

### 3. 运行服务器

```bash
# 方式1：使用脚本入口点（推荐）
uv run google-maps-mcp

# 方式2：直接运行 Python 文件
uv run python google_maps_server.py

# 方式3：使用启动脚本
./start_server.sh
```

### 4. 运行测试

```bash
uv run python test_server.py
```

## 📱 与 Claude Desktop 集成

### 1. 找到 Claude Desktop 配置文件

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 2. 添加服务器配置

编辑配置文件，添加以下内容：

```json
{
  "mcpServers": {
    "google-maps": {
      "command": "uv",
      "args": ["run", "--directory", "/Users/shaojiasong/codes/google-maps-mcp", "google-maps-mcp"],
      "env": {
        "GOOGLE_MAPS_API_KEY": "your_actual_google_maps_api_key_here"
      }
    }
  }
}
```

> 注意：将路径 `/Users/shaojiasong/codes/google-maps-mcp` 替换为你的实际项目目录路径

### 3. 重启 Claude Desktop

配置完成后重启 Claude Desktop，你就可以在对话中使用 Google Maps 功能了！

## 💡 使用示例

在 Claude Desktop 中，你可以这样使用：

```
"帮我查找北京天安门广场的坐标"
"计算从北京到上海的驾车路线"
"搜索纽约附近的餐厅"
"查看东京塔的详细信息"
```

## 🔧 技术特性

### 相比原始 JavaScript 版本的改进

1. **更好的类型安全**：使用 Pydantic 进行数据验证
2. **异步支持**：所有 API 调用都是异步的
3. **更好的错误处理**：详细的错误信息和日志
4. **Context 集成**：支持 FastMCP 的 Context 功能
5. **简化的代码**：FastMCP 减少了样板代码
6. **资源支持**：添加了服务器信息资源

### 代码亮点

- ✅ 完整的类型注解
- ✅ Pydantic 数据模型
- ✅ 异步 HTTP 客户端 (httpx)
- ✅ Context 对象支持 MCP 日志记录
- ✅ 错误处理和状态检查
- ✅ 中文注释和文档

## 🔍 故障排除

### 常见问题

1. **"GOOGLE_MAPS_API_KEY 环境变量未设置"**
   - 解决：按照上述方法设置 API Key

2. **"Module not found"**
   - 解决：确保使用 uv 运行：`uv run python test_server.py`
   - 或确保已同步依赖：`uv sync`

3. **API 调用失败**
   - 检查 API Key 是否有效
   - 检查是否启用了相应的 Google Maps API
   - 检查网络连接

### 获取 Google Maps API Key

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用所需的 API：
   - Geocoding API
   - Places API
   - Distance Matrix API
   - Elevation API
   - Directions API
4. 创建 API 密钥

## 🎯 下一步

1. **扩展功能**：添加更多 Google Maps API 功能
2. **缓存优化**：添加请求缓存以提高性能
3. **速率限制**：实现 API 调用速率限制
4. **配置管理**：支持更多配置选项
5. **监控和日志**：添加更详细的监控

## 📚 相关资源

- [FastMCP 文档](https://github.com/jlowin/fastmcp)
- [Google Maps API 文档](https://developers.google.com/maps/documentation)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)

---

🎉 **恭喜！** 你已经成功创建了一个功能完整的 Google Maps MCP 服务器！ 