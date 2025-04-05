#!/usr/bin/env python3
"""
Memos MCP服务器

这个服务器提供了与Memos API交互的功能，包括：
- 连接到用户的Memos实例
- 将API暴露为资源
- 提供搜索、删除、更新、管理等工具
- 包含用于日常操作改进的提示
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging
from dotenv import load_dotenv

from mcp.server.fastmcp import FastMCP, Context

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 获取Memos配置
MEMOS_URL = os.getenv("MEMOS_URL")
MEMOS_API_KEY = os.getenv("MEMOS_API_KEY")
DEFAULT_TAG = os.getenv("DEFAULT_TAG", "mcp")  # 默认标签，如果未设置则使用"mcp"

if not MEMOS_URL or not MEMOS_API_KEY:
    logger.error("请在.env文件中设置MEMOS_URL和MEMOS_API_KEY")
    print("错误: 请在.env文件中设置MEMOS_URL和MEMOS_API_KEY")
    print("您可以复制.env.example文件为.env并填写相应的值")
    exit(1)

# 创建MCP服务器
mcp = FastMCP(
    "Memos助手",
    description="连接到Memos API并提供搜索、管理和改进功能的MCP服务器",
    dependencies=["python-dotenv", "requests"]
)

# Memos API客户端类
class MemosClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """发送请求到Memos API"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                params=params,
                json=data
            )
            response.raise_for_status()
            if response.content:
                return response.json()
            return {}
        except requests.RequestException as e:
            logger.error(f"API请求失败: {e}")
            raise Exception(f"API请求失败: {e}")
    def get_user_id(self) -> str:
        """
        Get the user ID of the authenticated user by checking auth status.

        Returns:
            str: The user ID of the authenticated user

        Raises:
            MemosException: If there is an error retrieving the user ID
        """
        try:
            # Use the auth/status endpoint to get current user info
            response = requests.post(
                f"{self.memos_url}/api/v1/auth/status", headers=self.headers
            )
            response.raise_for_status()

            # Extract the user ID from the response
            user_data = response.json()
            user_id = user_data.get("name")

            if not user_id:
                raise MemosException("Could not retrieve user ID from auth status")

            return user_id
        except requests.RequestException as e:
            raise MemosException(f"Error getting user ID: {e}")
    # Memo相关方法
    def get_memos(self, params: Dict = None) -> List[Dict]:
        """获取备忘录列表"""
        return self._make_request("GET", "/api/v1/memos", params=params)
    
    def get_memo(self, memo_id: str) -> Dict:
        """获取单个备忘录"""
        return self._make_request("GET", f"/api/v1/memos/{memo_id}")
    
    def create_memo(self, data: Dict) -> Dict:
        """创建新备忘录"""
        return self._make_request("POST", "/api/v1/memos", data=data)
    
    def update_memo(self, memo_id: str, data: Dict) -> Dict:
        """更新备忘录"""
        return self._make_request("PATCH", f"/api/v1/memos/{memo_id}", data=data)
    
    def delete_memo(self, memo_id: str) -> Dict:
        """删除备忘录"""
        return self._make_request("DELETE", f"/api/v1/memos/{memo_id}")
    
    def search_memos(self, query: str = None, filter_expr: str = None) -> List[Dict]:
        """
        搜索备忘录
        
        Args:
            query: 搜索关键词
            filter_expr: CEL 表达式过滤器
        """
        params = {}
        if query:
            params["filter"] = f"content.contains('{query}')"
        if filter_expr:
            params["filter"] = filter_expr
        return self._make_request("GET", "/api/v1/memos", params=params)
    
    def filter_memos(self, filter_expr: str) -> List[Dict]:
        """
        使用 CEL 表达式过滤备忘录
        
        Args:
            filter_expr: CEL 表达式过滤器
        """
        return self.search_memos(filter_expr=filter_expr)
    
    # 标签相关方法
    def get_tags(self) -> List[Dict]:
        """获取所有标签"""
        return self._make_request("GET", "/api/v1/tag")
    
    def delete_memo_tag(self, memo_id: str, tag: str) -> Dict:
        """从备忘录中删除标签"""
        # 首先获取备忘录
        memo = self.get_memo(memo_id)
        
        # 从内容中移除标签
        content = memo.get("content", "")
        tag_with_hash = f"#{tag}"
        new_content = content.replace(tag_with_hash, "").strip()
        
        # 更新备忘录
        return self.update_memo(memo_id, {"content": new_content})
    


# 创建Memos客户端实例
memos_client = MemosClient(MEMOS_URL, MEMOS_API_KEY)

# 资源定义
@mcp.resource("memos://recent")
def get_recent_memos() -> str:
    """获取最近的备忘录"""
    try:
        memos = memos_client.get_memos({"limit": 10})
        return json.dumps(memos, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"获取最近备忘录失败: {e}")
        return f"获取最近备忘录失败: {e}"

@mcp.resource("memos://all")
def get_all_memos() -> str:
    """获取所有备忘录"""
    try:
        memos = memos_client.get_memos()
        return json.dumps(memos, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"获取所有备忘录失败: {e}")
        return f"获取所有备忘录失败: {e}"



@mcp.resource("memos://memos/{memo_id}")
def get_memo_by_id(memo_id: str) -> str:
    """
    获取指定ID的备忘录
    
    Args:
        memo_id: 备忘录ID  格式是{G3o72r9oijTWFxy9ueWzW7} 而不是{memos/G3o72r9oijTWFxy9ueWzW7}
    
    Returns:
        str: JSON 格式的备忘录数据
    """
    try:
        memo = memos_client.get_memo(memo_id)
        return json.dumps(memo, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"获取备忘录 {memo_id} 失败: {e}")
        return f"获取备忘录 {memo_id} 失败: {e}"


# 工具定义
@mcp.tool()
def search_memos(query: str = None, filter_expr: str = None) -> str:
    """
    搜索备忘录
    
    Args:
        query: 搜索关键词
        filter_expr: CEL 表达式过滤器，例如 "content.contains('关键词')"
    """
    try:
        results = memos_client.search_memos(query, filter_expr)
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"搜索备忘录失败: {e}")
        return f"搜索备忘录失败: {e}"

@mcp.tool()
def filter_memos(filter_expr: str) -> str:
    """
    使用 CEL 表达式过滤备忘录
    
    Args:
        filter_expr: CEL 表达式过滤器，例如 "content.contains('关键词')" 或 "createTime > timestamp('2023-01-01T00:00:00Z')"
    """
    try:
        results = memos_client.filter_memos(filter_expr)
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"过滤备忘录失败: {e}")
        return f"过滤备忘录失败: {e}"

@mcp.tool()
def create_memo(content: str, visibility: str = "PRIVATE", tags: List[str] = None) -> str:
    """
    创建新备忘录
    
    Args:
        content: 备忘录内容
        visibility: 可见性设置 (PRIVATE, PROTECTED, PUBLIC)
        tags: 标签列表，如果不提供则使用默认标签
    """
    try:
        # 处理标签
        if tags is None:
            # 使用默认标签
            if DEFAULT_TAG:
                tags = [DEFAULT_TAG]
            else:
                tags = []
        
        # 将标签添加到内容中
        content_with_tags = content+"\n"
        for tag in tags:
            if not tag.startswith("#"):
                tag = f"#{tag}"
            if tag not in content_with_tags:
                content_with_tags += f" {tag}"
        
        data = {
            "content": content_with_tags,
            "visibility": visibility
        }
        result = memos_client.create_memo(data)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"创建备忘录失败: {e}")
        return f"创建备忘录失败: {e}"

@mcp.tool()
def update_memo(memo_id: str, content: str = None, visibility: str = None) -> str:
    """
    更新备忘录
    
    Args:
        memo_id: 备忘录ID 格式是{G3o72r9oijTWFxy9ueWzW7} 而不是{memos/G3o72r9oijTWFxy9ueWzW7}
        content: 新的备忘录内容
        visibility: 新的可见性设置 (PRIVATE, PROTECTED, PUBLIC)
    """
    try:
        data = {}
        if content is not None:
            data["content"] = content
        if visibility is not None:
            data["visibility"] = visibility
            
        if not data:
            return "错误: 请提供要更新的内容或可见性"
            
        result = memos_client.update_memo(memo_id, data)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"更新备忘录失败: {e}")
        return f"更新备忘录失败: {e}"

@mcp.tool()
def delete_memo(memo_id: str) -> str:
    """
    删除备忘录
    
    Args:
        memo_id: 要删除的备忘录ID 备忘录ID 格式是{G3o72r9oijTWFxy9ueWzW7} 而不是{memos/G3o72r9oijTWFxy9ueWzW7}
    """
    try:
        memo_id=format_memos_id(memo_id)
        memos_client.delete_memo(memo_id)
        return f"成功删除备忘录 {memo_id}"
    except Exception as e:
        logger.error(f"删除备忘录失败: {e}")
        return f"删除备忘录失败: {e}"





def format_memos_id(memo_id: str) -> str:
    """
    格式化备忘录ID，确保格式正确
    
    Args:
        memo_id: 备忘录ID 格式是{G3o72r9oijTWFxy9ueWzW7} 而不是{memos/G3o72r9oijTWFxy9ueWzW7}
    Returns:
        str: 格式化后的备忘录ID
    """
    if memo_id.startswith("memos/"):
        memo_id = memo_id[6:]
    return memo_id

@mcp.tool()
def delete_memo_tag(memo_id: str, tag: str) -> str:
    """
    从备忘录中删除标签
    
    Args:
        memo_id: 备忘录ID 格式是{G3o72r9oijTWFxy9ueWzW7} 而不是{memos/G3o72r9oijTWFxy9ueWzW7}
        tag: 要删除的标签名称(不包含#符号)
    """
    try:
        if not memo_id:
            return "请提供备忘录ID"
        memo_id = format_memos_id(memo_id)
        result = memos_client.delete_memo_tag(memo_id, tag)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"删除标签失败: {e}")
        return f"删除标签失败: {e}"



@mcp.prompt("weekly-summary")
def weekly_summary_prompt() -> str:
    """每周总结提示，帮助用户总结一周的备忘录"""
    return """
    # 每周备忘录总结

    请帮我总结过去一周的备忘录，并按以下方式组织：

    1. 本周完成的主要事项
    2. 未完成的任务和下周需要关注的事项
    3. 出现的主要主题或模式
    4. 对下周的建议和改进

    请使用搜索工具查找过去一周的备忘录，并提供全面的总结和见解。
    """

@mcp.prompt("knowledge-extraction")
def knowledge_extraction_prompt() -> str:
    """知识提取提示，帮助用户从备忘录中提取知识"""
    return """
    # 知识提取助手

    请帮我从我的备忘录中提取有价值的知识和见解：

    1. 识别关键概念和定义
    2. 提取可操作的步骤或方法
    3. 汇总相关的事实和数据
    4. 组织成易于理解和引用的格式

    请使用搜索工具查找相关备忘录，并帮助我构建一个知识库。
    """



@mcp.prompt("content-improvement")
def content_improvement_prompt() -> str:
    """内容改进提示，帮助用户改进备忘录内容"""
    return """
    # 备忘录内容改进助手

    请帮我改进以下备忘录的内容质量：

    1. 提高清晰度和简洁性
    2. 改进结构和组织
    3. 添加缺失的上下文或详细信息
    4. 确保一致的格式和风格

    请分析备忘录内容，并提供具体的改进建议。
    """
def start_server():
    print(f"启动Memos MCP服务器，连接到: {MEMOS_URL}")
    print("使用Ctrl+C停止服务器")
    
    # 启动MCP服务器
    mcp.run(transport='stdio')
if __name__ == "__main__":
    print(f"启动Memos MCP服务器，连接到: {MEMOS_URL}")
    print("使用Ctrl+C停止服务器")
    
    # 启动MCP服务器
    mcp.run(transport='stdio')
