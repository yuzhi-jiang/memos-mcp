# Memos MCP Server

[![smithery badge](https://smithery.ai/badge/codehatcher/memos-mcp)](https://smithery.ai/server/codehatcher/memos-mcp)

一个连接到 [Memos](https://www.usememos.com/) 的 MCP 服务器。它把 Memos 的常用能力暴露为 MCP 资源、工具和提示词，方便在 Claude、Cherry Studio、Cursor 等支持 MCP 的客户端中直接读写备忘录。

## 功能概览

- 浏览最近备忘录、全部备忘录、指定备忘录
- 搜索和过滤备忘录
- 创建、更新、删除备忘录
- 删除备忘录中的标签
- 在指定备忘录下创建评论
- 通过管理员 API 获取所有用户列表
- 提供周报总结、知识提取、内容改进等提示模板

## 新增功能

当前版本相对之前的变更重点：

- 新增“为备忘录创建评论”工具
- 新增“获取所有用户”资源和工具
- 新增 `MEMOS_ADMIN_API_KEY` 配置项，用于调用管理员接口

## 运行方式

当前服务默认使用 `stdio` 传输方式启动，适合 Claude Code、Claude Desktop 等本地 MCP 客户端。

也支持通过环境变量切换到 `streamable-http`：

```env
MCP_TRANSPORT=streamable-http
```

`streamable-http` 模式默认监听：

- Host: `0.0.0.0`
- Port: `3002`
- MCP endpoint: `http://127.0.0.1:3002/mcp`

## 环境要求

- Python `>=3.10`
- 一个可访问的 Memos 实例
- 普通 API Key
- 可选：管理员 API Key（当你需要读取所有用户时）

## 安装

### 方式一：直接运行已发布包

```bash
uvx memos-mcp
```

或：

```bash
pip install memos-mcp
memos-mcp
```

### 方式二：本地开发

```bash
git clone https://github.com/yuzhi-jiang/memos-mcp.git
cd memos-mcp
uv sync
uv run memos-mcp
```

## 配置

可以通过环境变量，或在项目目录下放置 `.env` 文件来配置：

```env
MEMOS_URL=http://localhost:5230
MEMOS_API_KEY=your-memos-api-key
MEMOS_ADMIN_API_KEY=your-memos-admin-api-key
DEFAULT_TAG=mcp
MCP_TRANSPORT=stdio
MCP_HOST=0.0.0.0
MCP_PORT=3002
MCP_STREAMABLE_HTTP_PATH=/mcp
```

变量说明：

- `MEMOS_URL`：Memos 服务地址，例如 `http://localhost:5230`
- `MEMOS_API_KEY`：普通 API Key，必填
- `MEMOS_ADMIN_API_KEY`：管理员 API Key，可选；只有在使用“获取所有用户”资源或工具时才需要
- `DEFAULT_TAG`：创建备忘录时默认追加的标签，默认为 `mcp`
- `MCP_TRANSPORT`：MCP 传输方式，默认 `stdio`，可选 `streamable-http`
- `MCP_HOST`：HTTP 模式监听地址，默认 `0.0.0.0`
- `MCP_PORT`：HTTP 模式监听端口，默认 `3002`
- `MCP_STREAMABLE_HTTP_PATH`：HTTP 模式路径，默认 `/mcp`

示例文件见 [`.env.example`](.env.example)。

## 在 MCP 客户端中接入

### Claude Code / Claude Desktop

推荐直接让客户端以 `stdio` 模式启动，不需要你手工先跑服务。

命令示例：

```bash
uv --directory /path/to/memos-mcp run memos-mcp
```

### 手工启动服务

先启动服务：

```bash
uv run memos-mcp
```

默认会以 `stdio` 模式运行。

如果你要测试 `streamable-http` 模式：

```bash
MCP_TRANSPORT=streamable-http uv run memos-mcp
```

然后在支持 HTTP MCP 的客户端中填入：

```text
http://127.0.0.1:3002/mcp
```

## 可用资源

- `memos://recent`：最近 10 条备忘录
- `memos://all`：全部备忘录
- `memos://users`：全部用户列表，需要 `MEMOS_ADMIN_API_KEY`
- `memos://memos/{memo_id}`：按 ID 获取单条备忘录

`memo_id` 传参格式应为纯 ID，例如：

```text
G3o72r9oijTWFxy9ueWzW7
```

而不是：

```text
memos/G3o72r9oijTWFxy9ueWzW7
```

## 可用工具

### 备忘录查询

- `search_memos(query, filter_expr=None)`：按关键词或 CEL 表达式搜索
- `filter_memos(filter_expr)`：按 CEL 表达式过滤

### 备忘录写入与维护

- `create_memo(content, visibility="PRIVATE", tags=None)`：创建备忘录
- `update_memo(memo_id, content=None, visibility=None)`：更新备忘录
- `delete_memo(memo_id)`：删除备忘录
- `delete_memo_tag(memo_id, tag)`：删除指定标签

### 新增工具

- `create_memo_comment(memo_id, content, visibility="PRIVATE")`：给指定备忘录创建评论
- `get_all_users_tools()`：获取所有用户列表，需要 `MEMOS_ADMIN_API_KEY`

## 提示模板

- `weekly-summary`
- `knowledge-extraction`
- `content-improvement`

## 使用示例

### 搜索备忘录

```text
search_memos(query="项目复盘")
```

### 用 CEL 过滤备忘录

```text
filter_memos(filter_expr="createTime > timestamp('2026-01-01T00:00:00Z') && visibility == 'PRIVATE'")
```

### 创建带标签的备忘录

```text
create_memo(
  content="完成 Memos MCP 发布说明",
  visibility="PRIVATE",
  tags=["release", "mcp"]
)
```

### 给备忘录添加评论

```text
create_memo_comment(
  memo_id="G3o72r9oijTWFxy9ueWzW7",
  content="这条内容我已经复核完了",
  visibility="PRIVATE"
)
```

### 获取所有用户

```text
get_all_users_tools()
```

## 开发说明

- 入口脚本定义在 [`pyproject.toml`](pyproject.toml)
- 服务实现位于 [`src/memos_cmp/server.py`](src/memos_cmp/server.py)
- 包版本定义位于 [`src/memos_cmp/__init__.py`](src/memos_cmp/__init__.py)

本地构建：

```bash
uv build
```

## 许可证

MIT
