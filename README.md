# Memos MCP 服务器

[![smithery badge](https://smithery.ai/badge/codehatcher/memos-mcp)](https://smithery.ai/server/codehatcher/memos-mcp)

一个连接到 [Memos](https://usememos.com/) 的 MCP (Model Context Protocol) 服务器，让你可以通过 AI 助手（如 Claude）与你的 Memos 实例进行交互。

## 功能特点

- 🔄 **连接到用户的 Memos 实例**：通过 API 密钥安全连接
- 📚 **将 API 暴露为资源**：提供对备忘录的结构化访问
- 🔍 **提供强大的工具**：搜索、创建、更新、删除备忘录等功能
- 🏷️ **标签管理**：自动添加标签到新备忘录
- 🔎 **高级搜索**：支持 CEL 表达式进行复杂过滤
- 📝 **提示模板**：包含用于日常操作改进的提示

## 安装与配置

你可以在配置文件中包含这个包，如下所示，就像使用其他 Python MCP 插件一样。
```json
{
  "mcpServers": {
    "memos-mcp": {
      "command": "uvx",
      "args": [
        "memos-mcp"
      ],
      "env": {
        "MEMOS_URL": "https://your-memos-instance-url",
        "MEMOS_API_KEY": "your-memos-api-key"
      }
    }
  }
}
```


### 前提条件

- Python 3.8 或更高版本
- 一个可访问的 Memos 实例
- Memos API 密钥

### 安装步骤

1. 克隆此仓库：
   ```bash
   git clone https://github.com/yourusername/memos-mcp.git
   cd memos-mcp
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 配置环境变量：
   - 复制 `.env.example` 为 `.env`
   - 编辑 `.env` 文件，填写以下信息：
     ```
     MEMOS_URL=https://your-memos-instance-url
     MEMOS_API_KEY=your-memos-api-key
     DEFAULT_TAG=mcp  # 可选，默认标签
     ```

## 使用方法

### 启动服务器

```bash
python memos_mcp_server.py
```

### 连接到 Claude Desktop

1. 安装 [Claude Desktop](https://claude.ai/download)
2. 在 Claude Desktop 中，添加 MCP 服务器
3. 使用 Claude 与你的 Memos 进行交互

### 使用 MCP 开发工具测试

```bash
mcp dev memos_mcp_server.py
```

## 可用资源

- `memos://recent` - 获取最近的备忘录
- `memos://all` - 获取所有备忘录
- `memos://memos/{memo_id}` - 获取指定 ID 的备忘录

## 可用工具

### 搜索和过滤

- `search_memos(query, filter_expr)` - 搜索备忘录
- `filter_memos(filter_expr)` - 使用 CEL 表达式过滤备忘录

### 创建和管理

- `create_memo(content, visibility, tags)` - 创建新备忘录
- `update_memo(memo_id, content, visibility)` - 更新备忘录
- `delete_memo(memo_id)` - 删除备忘录
- `delete_memo_tag(memo_id, tag)` - 从备忘录中删除标签

## 提示模板

- `daily-review` - 每日备忘录回顾
- `weekly-summary` - 每周备忘录总结
- `knowledge-extraction` - 从备忘录中提取知识
- `content-improvement` - 改进备忘录内容

## CEL 表达式示例

CEL (Common Expression Language) 表达式可用于高级过滤：

- 按内容过滤：`content.contains('关键词')`
- 按创建时间过滤：`createTime > timestamp('2023-01-01T00:00:00Z')`
- 按可见性过滤：`visibility == 'PRIVATE'`
- 组合条件：`content.contains('关键词') && visibility == 'PRIVATE'`

## 示例用法

### 搜索备忘录

```
search_memos(query="项目")
```

### 使用 CEL 表达式过滤

```
filter_memos(filter_expr="createTime > timestamp('2023-01-01T00:00:00Z') && visibility == 'PRIVATE'")
```

### 创建带标签的备忘录

```
create_memo(content="完成 MCP 服务器项目", tags=["项目", "编程"])
```

## Claude Code 和 OpenClaw Skills 支持

本项目包含一个 `skills/` 目录，支持通过 [Claude Code](https://code.claude.com) 和 OpenClaw 的 Skills 功能安装和使用。

**无需安装 MCP 服务器** — 技能内置了独立的 Python 脚本 (`scripts/memos.py`)，仅使用 Python 标准库直接调用 Memos REST API。

### Skills 目录结构

```
skills/
└── memos-mcp/
    ├── SKILL.md          # 技能元数据和使用说明
    └── scripts/
        └── memos.py      # 独立的 Memos API 客户端脚本（无需额外依赖）
```

### 在 Claude Code 中安装

**方法一：通过仓库安装**

1. 在 Claude Code 中运行以下命令，将本仓库添加为插件市场：
   ```
   /plugin marketplace add yuzhi-jiang/memos-mcp
   ```

2. 然后安装技能：
   ```
   /plugin install memos-mcp@yuzhi-jiang/memos-mcp
   ```

**方法二：手动安装**

将 `skills/memos-mcp/` 目录复制到以下位置之一：

- **全局安装**（适用于所有项目）：
  ```bash
  cp -r skills/memos-mcp ~/.claude/skills/
  ```

- **项目安装**（仅适用于当前项目）：
  ```bash
  cp -r skills/memos-mcp .claude/skills/
  ```

### 在 OpenClaw 中安装

将 `skills/memos-mcp/` 目录复制到 OpenClaw 的 skills 目录中：

```bash
cp -r skills/memos-mcp ~/.openclaw/skills/
```

### 配置凭据

安装后，设置你的 Memos 实例 URL 和 API 密钥（三选一）：

**方式 A — 环境变量：**
```bash
export MEMOS_URL=https://your-memos-instance-url
export MEMOS_API_KEY=your-memos-api-key
```

**方式 B — 配置文件 `~/.memos-config`：**
```
MEMOS_URL=https://your-memos-instance-url
MEMOS_API_KEY=your-memos-api-key
```

**方式 C — 命令行参数：**
```bash
python ~/.claude/skills/memos-mcp/scripts/memos.py --url https://... --token your-key list
```

### 技能说明

安装并配置凭据后，Claude 会通过 `scripts/memos.py` 脚本与你的 Memos 实例直接交互，支持以下自然语言指令：

- "搜索关于项目的备忘录"
- "创建一条新备忘录：今天完成了报告"
- "总结本周的备忘录"
- "删除备忘录中的草稿标签"

## 贡献

欢迎提交问题和拉取请求！

## 许可证

MIT
